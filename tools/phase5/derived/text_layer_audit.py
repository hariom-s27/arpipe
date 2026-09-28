"""Derive post-seal text-layer audit fields from sealed Gold spans and PDFs."""

from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import math
import re
import sys
import unicodedata
from dataclasses import dataclass
from pathlib import Path
from typing import Sequence

import pymupdf


INPUT_COLUMNS = [
    "document_id",
    "start_page_0based",
    "end_page_0based",
    "body_title",
    "gap_pages",
    "csr_esg_pages",
    "split",
]
INPUT_COLUMNS_WITH_END_SHARED = [*INPUT_COLUMNS, "end_page_shared"]
RESULT_COLUMNS = [
    "document_id",
    "pdf_sha256",
    "start_page_0based",
    "end_page_0based",
    "heading_in_text_layer",
    "text_layer_broken",
    "bad_char_share",
    "latin_word_share",
    "kept_token_count",
    "mdna_word_count",
    "csr_esg_word_count",
    "quality_page_0based",
    "quality_page_fallback",
    "broken_text_group",
    "dictionary_word_share",
    "start_page_shared",
    "end_page_shared",
    "word_count_scope",
]
DOCUMENT_ID_RE = re.compile(r"[A-Za-z0-9._-]+\Z")
ASCII_LATIN_WORD_RE = re.compile(r"[A-Za-z]+(?:['-][A-Za-z]+)*\Z")
YEAR_RANGE_RE = re.compile(r"(?<!\d)(?:19|20)\d{2}\s*[-/\u2013\u2014]\s*\d{2}(?!\d)")
REMOVED_TITLE_WORD_RE = re.compile(r"(?<!\w)(?:report|annexure)(?!\w)")
DIRECTORS_PHRASE_RE = re.compile(r"(?<!\w)to\s+the\s+directors['\u2019](?!\w)")
LEADING_ITEM_RE = re.compile(
    r"^\s*(?:"
    r"(?:[a-z]|\d+|[ivxlcdm]+)\s*[.):\-\u2013\u2014]\s*"
    r"|[-\u2013\u2014]\s*(?:\d+|[ivxlcdm]+)\s*(?:[.):])?\s*"
    r")",
)


class TextLayerAuditError(ValueError):
    """Raised when an input or safety invariant is violated."""


@dataclass(frozen=True)
class InputRow:
    document_id: str
    start_page: int
    end_page: int
    body_title: str
    gap_pages: tuple[int, ...]
    csr_esg_pages: tuple[int, ...]
    split: str
    end_page_shared: str = ""


def _sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _check_output_path(out: Path) -> Path:
    if out.exists() or out.is_symlink():
        raise TextLayerAuditError("output already exists")
    resolved = out.resolve(strict=False)
    if resolved.exists() or resolved.is_symlink():
        raise TextLayerAuditError("output already exists")
    for directory in (resolved, *resolved.parents):
        marker = directory / ".git"
        if marker.exists() or marker.is_symlink():
            raise TextLayerAuditError("output is inside a git repository")
    if not resolved.parent.is_dir():
        raise TextLayerAuditError("output parent directory does not exist")
    return resolved


def _parse_nonnegative_int(value: str, field: str, line_no: int) -> int:
    stripped = value.strip()
    if re.fullmatch(r"[0-9]+", stripped) is None:
        raise TextLayerAuditError(f"input line {line_no}: invalid {field}")
    return int(stripped)


def _parse_page_list(value: str, field: str, line_no: int) -> tuple[int, ...]:
    if not value.strip():
        return ()
    pieces = value.split(";")
    if any(not piece.strip() for piece in pieces):
        raise TextLayerAuditError(f"input line {line_no}: invalid {field}")
    pages = tuple(_parse_nonnegative_int(piece, field, line_no) for piece in pieces)
    if len(pages) != len(set(pages)):
        raise TextLayerAuditError(f"input line {line_no}: duplicate page in {field}")
    if pages != tuple(sorted(pages)):
        raise TextLayerAuditError(f"input line {line_no}: {field} must be sorted")
    return pages


def _read_input(path: Path, author_approved: bool) -> list[InputRow]:
    try:
        stream = path.open("r", encoding="utf-8", newline="")
    except OSError as exc:
        raise TextLayerAuditError("cannot read input CSV") from exc
    rows: list[InputRow] = []
    seen: set[str] = set()
    try:
        with stream:
            reader = csv.DictReader(stream, strict=True)
            if reader.fieldnames != INPUT_COLUMNS and reader.fieldnames != INPUT_COLUMNS_WITH_END_SHARED:
                raise TextLayerAuditError("input columns do not match the required schema")
            has_end_shared = reader.fieldnames == INPUT_COLUMNS_WITH_END_SHARED
            required_cols = INPUT_COLUMNS_WITH_END_SHARED if has_end_shared else INPUT_COLUMNS
            for line_no, raw in enumerate(reader, start=2):
                if None in raw or any(raw[column] is None for column in required_cols):
                    raise TextLayerAuditError(f"input line {line_no}: malformed row")
                document_id = raw["document_id"].strip()
                if DOCUMENT_ID_RE.fullmatch(document_id) is None:
                    raise TextLayerAuditError(f"input line {line_no}: invalid document_id")
                if document_id in seen:
                    raise TextLayerAuditError(f"input line {line_no}: duplicate document_id {document_id}")
                seen.add(document_id)
                start_page = _parse_nonnegative_int(raw["start_page_0based"], "start_page_0based", line_no)
                end_page = _parse_nonnegative_int(raw["end_page_0based"], "end_page_0based", line_no)
                if start_page > end_page:
                    raise TextLayerAuditError(f"input line {line_no}: start page exceeds end page for {document_id}")
                gap_pages = _parse_page_list(raw["gap_pages"], "gap_pages", line_no)
                csr_esg_pages = _parse_page_list(raw["csr_esg_pages"], "csr_esg_pages", line_no)
                split = raw["split"].strip()
                if split not in {"FIT", "VALIDATION", "HOLDOUT"}:
                    raise TextLayerAuditError(f"input line {line_no}: invalid split for {document_id}")
                if split == "HOLDOUT" and not author_approved:
                    raise TextLayerAuditError(f"HOLDOUT row refused without author approval: {document_id}")
                end_page_shared = ""
                if has_end_shared:
                    end_page_shared = raw["end_page_shared"].strip()
                    if end_page_shared not in {"Y", "N", ""}:
                        raise TextLayerAuditError(f"input line {line_no}: invalid end_page_shared for {document_id}")
                rows.append(
                    InputRow(
                        document_id=document_id,
                        start_page=start_page,
                        end_page=end_page,
                        body_title=raw["body_title"],
                        gap_pages=gap_pages,
                        csr_esg_pages=csr_esg_pages,
                        split=split,
                        end_page_shared=end_page_shared,
                    )
                )
    except (csv.Error, UnicodeError) as exc:
        raise TextLayerAuditError("malformed UTF-8 CSV input") from exc
    if not rows:
        raise TextLayerAuditError("input CSV has no documents")
    return rows


def normalize_heading(value: str) -> str:
    """Apply the frozen heading comparison normalization."""

    normalized = unicodedata.normalize("NFKC", value).casefold()
    normalized = normalized.replace("&", "and")
    normalized = normalized.replace("'s", "").replace("\u2019s", "")
    normalized = DIRECTORS_PHRASE_RE.sub(" ", normalized)
    normalized = REMOVED_TITLE_WORD_RE.sub(" ", normalized)
    normalized = YEAR_RANGE_RE.sub(" ", normalized)
    normalized = LEADING_ITEM_RE.sub("", normalized, count=1)
    return "".join(
        character
        for character in normalized
        if not character.isspace() and not unicodedata.category(character).startswith("P")
    )


def _strip_edge_punctuation(token: str) -> str:
    start = 0
    end = len(token)
    while start < end and unicodedata.category(token[start]).startswith("P"):
        start += 1
    while end > start and unicodedata.category(token[end - 1]).startswith("P"):
        end -= 1
    return token[start:end]


def _is_latin_letter(character: str) -> bool:
    return unicodedata.category(character).startswith("L") and "LATIN" in unicodedata.name(character, "")


def _is_only_non_latin_letters(token: str) -> bool:
    saw_letter = False
    for character in token:
        category = unicodedata.category(character)
        if category.startswith("L"):
            saw_letter = True
            if _is_latin_letter(character):
                return False
        elif category.startswith("M"):
            continue
        else:
            return False
    return saw_letter


def _kept_tokens(text: str) -> list[str]:
    kept: list[str] = []
    for raw_token in text.split():
        token = _strip_edge_punctuation(raw_token)
        if any(character.isdigit() for character in token):
            continue
        if _is_only_non_latin_letters(token):
            continue
        if len(token) >= 3:
            kept.append(token)
    return kept


def _is_bad_character(character: str) -> bool:
    if character == "\ufffd" or "\ue000" <= character <= "\uf8ff":
        return True
    return unicodedata.category(character) == "Cc" and character not in "\n\r\t"


def audit_start_page_text(
    text: str,
    max_bad_char_share: float,
    min_latin_word_share: float,
) -> tuple[bool | str, float, float | None, int]:
    """Return broken status, bad share, Latin share, and kept-token count."""

    bad_char_share = sum(_is_bad_character(character) for character in text) / len(text) if text else 0.0
    kept = _kept_tokens(text)
    if not kept:
        return "NO_TEXT", bad_char_share, None, 0
    latin_count = sum(ASCII_LATIN_WORD_RE.fullmatch(token) is not None for token in kept)
    latin_word_share = latin_count / len(kept)
    broken = bad_char_share > max_bad_char_share or latin_word_share < min_latin_word_share
    return broken, bad_char_share, latin_word_share, len(kept)


def count_words(text: str) -> int:
    """Count whitespace tokens that contain an ASCII letter after edge punctuation stripping."""

    return sum(
        any("A" <= character <= "Z" or "a" <= character <= "z" for character in _strip_edge_punctuation(token))
        for token in text.split()
    )


def count_raw_tokens(text: str) -> int:
    """Count whitespace tokens that, after stripping edge punctuation, have length >= 3."""
    count = 0
    for raw_token in text.split():
        token = _strip_edge_punctuation(raw_token)
        if len(token) >= 3:
            count += 1
    return count


def check_start_page_shared(page: pymupdf.Page, body_title: str) -> bool | str:
    """Determine whether the heading on the start page starts below 20% of page height."""
    if not body_title.strip():
        return "NA"
    normalized_title = normalize_heading(body_title)
    if not normalized_title:
        return "NA"

    page_dict = page.get_text("dict")
    lines_with_pos: list[tuple[str, float]] = []
    for block in page_dict.get("blocks", []):
        for line in block.get("lines", []):
            line_text = "".join(span.get("text", "") for span in line.get("spans", []))
            line_top = float(line["bbox"][1])
            lines_with_pos.append((line_text, line_top))

    num_lines = len(lines_with_pos)
    for i in range(num_lines):
        line_i = lines_with_pos[i][0]
        if normalized_title in normalize_heading(line_i):
            return lines_with_pos[i][1] > 0.20 * page.rect.height
        if i + 1 < num_lines:
            combo_2 = f"{line_i} {lines_with_pos[i + 1][0]}"
            if normalized_title in normalize_heading(combo_2):
                return lines_with_pos[i][1] > 0.20 * page.rect.height
        if i + 2 < num_lines:
            combo_3 = f"{line_i} {lines_with_pos[i + 1][0]} {lines_with_pos[i + 2][0]}"
            if normalized_title in normalize_heading(combo_3):
                return lines_with_pos[i][1] > 0.20 * page.rect.height
    return "NA"


def compute_broken_text_group(
    text_layer_broken: bool | str,
    heading_in_text_layer: bool | str,
) -> bool | str:
    """Combine text layer broken and heading signals into a unified broken group."""
    if text_layer_broken is True or heading_in_text_layer is False:
        return True
    if text_layer_broken is False and (heading_in_text_layer is True or heading_in_text_layer == "NA"):
        return False
    if text_layer_broken == "NO_TEXT" and heading_in_text_layer is not False:
        return "NO_TEXT"
    raise TextLayerAuditError(
        f"unexpected broken combination: text_layer_broken={text_layer_broken}, "
        f"heading_in_text_layer={heading_in_text_layer}"
    )


def _load_wordlist(path: Path) -> set[str]:
    try:
        content = path.read_text(encoding="utf-8-sig")
    except OSError as exc:
        raise TextLayerAuditError("cannot read wordlist file") from exc
    except UnicodeDecodeError as exc:
        raise TextLayerAuditError("wordlist file is not valid UTF-8") from exc

    lines = content.splitlines()
    if not lines:
        return set()

    first_line = lines[0]
    words: set[str] = set()
    if "," in first_line:
        header_cells = next(csv.reader([first_line]), [])
        word_col_idx = None
        for idx, cell in enumerate(header_cells):
            if cell.strip().casefold() == "word":
                word_col_idx = idx
                break
        if word_col_idx is not None:
            reader = csv.reader(lines[1:])
            for row in reader:
                if len(row) > word_col_idx:
                    cleaned = row[word_col_idx].strip().casefold()
                    if cleaned:
                        words.add(cleaned)
            return words

    # Otherwise read one word per line
    for line in lines:
        cleaned = line.strip().casefold()
        if cleaned:
            words.add(cleaned)
    return words


def _validate_pages(row: InputRow, page_count: int) -> None:
    referenced = (row.start_page, row.end_page, *row.gap_pages, *row.csr_esg_pages)
    if any(page < 0 or page >= page_count for page in referenced):
        raise TextLayerAuditError(f"page outside PDF for {row.document_id}")
    if any(page <= row.start_page or page >= row.end_page for page in row.gap_pages):
        raise TextLayerAuditError(f"gap page outside the strict span interior for {row.document_id}")
    gap_set = set(row.gap_pages)
    if any(page < row.start_page or page > row.end_page for page in row.csr_esg_pages):
        raise TextLayerAuditError(f"CSR/ESG page outside span for {row.document_id}")
    if any(page in gap_set for page in row.csr_esg_pages):
        raise TextLayerAuditError(f"CSR/ESG page is also a gap page for {row.document_id}")


def _process_row(
    row: InputRow,
    pdf_dir: Path,
    max_bad_char_share: float,
    min_latin_word_share: float,
    wordlist_set: set[str] | None,
) -> dict[str, object]:
    pdf_path = pdf_dir / f"{row.document_id}.pdf"
    if not pdf_path.is_file():
        raise TextLayerAuditError(f"PDF does not exist for {row.document_id}")
    pdf_sha256 = _sha256_file(pdf_path)
    try:
        document = pymupdf.open(pdf_path)
    except Exception as exc:
        raise TextLayerAuditError(f"cannot open PDF for {row.document_id}") from exc
    try:
        _validate_pages(row, document.page_count)
        start_page_obj = document.load_page(row.start_page)
        start_page_shared = check_start_page_shared(start_page_obj, row.body_title)
        page_text: dict[int, str] = {}
        pages_needed = set(range(row.start_page, row.end_page + 1)) | set(row.csr_esg_pages)
        for page_number in sorted(pages_needed):
            page_text[page_number] = document.load_page(page_number).get_text("text")
    except TextLayerAuditError:
        raise
    except Exception as exc:
        raise TextLayerAuditError(f"cannot extract text for {row.document_id}") from exc
    finally:
        document.close()

    start_text = page_text[row.start_page]
    normalized_title = normalize_heading(row.body_title)
    heading_in_text_layer: bool | str
    if not row.body_title.strip():
        heading_in_text_layer = "NA"
    else:
        heading_in_text_layer = bool(normalized_title) and normalized_title in normalize_heading(start_text)

    gap_set = set(row.gap_pages)
    quality_page = row.start_page
    quality_page_fallback = True
    for page in range(row.start_page, row.end_page + 1):
        if page in gap_set:
            continue
        if count_raw_tokens(page_text[page]) >= 50:
            quality_page = page
            quality_page_fallback = False
            break

    quality_text = page_text[quality_page]
    broken, bad_share, latin_share, kept_count = audit_start_page_text(
        quality_text,
        max_bad_char_share,
        min_latin_word_share,
    )
    quality_kept = _kept_tokens(quality_text)
    if wordlist_set is None or not quality_kept:
        dictionary_word_share: float | str = "NA"
    else:
        dict_match = sum(token.casefold() in wordlist_set for token in quality_kept)
        dictionary_word_share = dict_match / len(quality_kept)

    broken_text_group = compute_broken_text_group(broken, heading_in_text_layer)

    if row.end_page_shared == "Y":
        end_page_shared: bool | str = True
    elif row.end_page_shared == "N":
        end_page_shared = False
    else:
        end_page_shared = "NA"

    mdna_word_count = sum(
        count_words(page_text[page])
        for page in range(row.start_page, row.end_page + 1)
        if page not in gap_set
    )
    csr_esg_word_count = sum(count_words(page_text[page]) for page in row.csr_esg_pages)
    return {
        "document_id": row.document_id,
        "pdf_sha256": pdf_sha256,
        "start_page_0based": row.start_page,
        "end_page_0based": row.end_page,
        "heading_in_text_layer": heading_in_text_layer,
        "text_layer_broken": broken,
        "bad_char_share": bad_share,
        "latin_word_share": latin_share,
        "kept_token_count": kept_count,
        "mdna_word_count": mdna_word_count,
        "csr_esg_word_count": csr_esg_word_count,
        "quality_page_0based": quality_page,
        "quality_page_fallback": quality_page_fallback,
        "broken_text_group": broken_text_group,
        "dictionary_word_share": dictionary_word_share,
        "start_page_shared": start_page_shared,
        "end_page_shared": end_page_shared,
        "word_count_scope": "PAGE_LEVEL",
    }


def _csv_scalar(value: object) -> object:
    if isinstance(value, bool):
        return "true" if value else "false"
    if value is None:
        return ""
    if isinstance(value, float):
        return json.dumps(value, allow_nan=False)
    return value


def _csv_bytes(header: dict[str, object], documents: list[dict[str, object]]) -> bytes:
    stream = io.StringIO(newline="")
    writer = csv.writer(stream, lineterminator="\n")
    writer.writerow(["header_key", "header_value"])
    writer.writerow(["audit_version", header["audit_version"]])
    writer.writerow(["script_sha256", header["script_sha256"]])
    writer.writerow(["pymupdf_version", header["pymupdf_version"]])
    thresholds = header["thresholds"]
    assert isinstance(thresholds, dict)
    writer.writerow(["max_bad_char_share", _csv_scalar(thresholds["max_bad_char_share"])])
    writer.writerow(["min_latin_word_share", _csv_scalar(thresholds["min_latin_word_share"])])
    writer.writerow(["input_sha256", header["input_sha256"]])
    writer.writerow(["wordlist_sha256", _csv_scalar(header["wordlist_sha256"])])
    writer.writerow([])
    writer.writerow(RESULT_COLUMNS)
    for document in documents:
        writer.writerow([_csv_scalar(document[column]) for column in RESULT_COLUMNS])
    return stream.getvalue().encode("utf-8")


def _json_bytes(header: dict[str, object], documents: list[dict[str, object]]) -> bytes:
    payload = {"documents": documents, "header": header}
    return (
        json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False) + "\n"
    ).encode("utf-8")


def run_audit(
    input_csv: Path,
    pdf_dir: Path,
    out: Path,
    *,
    max_bad_char_share: float = 0.05,
    min_latin_word_share: float = 0.50,
    wordlist: Path | None = None,
    author_approved: bool = False,
) -> tuple[dict[str, object], list[dict[str, object]]]:
    """Validate, derive, and write deterministic audit artifacts."""

    if not math.isfinite(max_bad_char_share) or not 0.0 <= max_bad_char_share <= 1.0:
        raise TextLayerAuditError("max bad-character share must be between 0 and 1")
    if not math.isfinite(min_latin_word_share) or not 0.0 <= min_latin_word_share <= 1.0:
        raise TextLayerAuditError("minimum Latin-word share must be between 0 and 1")
    output_path = _check_output_path(out)
    try:
        input_payload = input_csv.read_bytes()
    except OSError as exc:
        raise TextLayerAuditError("cannot read input CSV") from exc
    rows = _read_input(input_csv, author_approved)
    if not pdf_dir.is_dir():
        raise TextLayerAuditError("PDF directory does not exist")
    wordlist_sha256: str | None = None
    wordlist_set: set[str] | None = None
    if wordlist is not None:
        wordlist_path = Path(wordlist)
        if not wordlist_path.is_file():
            raise TextLayerAuditError(f"wordlist file does not exist: {wordlist_path}")
        wordlist_sha256 = _sha256_file(wordlist_path)
        wordlist_set = _load_wordlist(wordlist_path)
    documents = sorted(
        (
            _process_row(row, pdf_dir, max_bad_char_share, min_latin_word_share, wordlist_set)
            for row in rows
        ),
        key=lambda document: str(document["document_id"]),
    )
    header: dict[str, object] = {
        "audit_version": "0.2",
        "script_sha256": _sha256_file(Path(__file__)),
        "pymupdf_version": str(pymupdf.VersionBind),
        "thresholds": {
            "max_bad_char_share": max_bad_char_share,
            "min_latin_word_share": min_latin_word_share,
        },
        "input_sha256": _sha256_bytes(input_payload),
        "wordlist_sha256": wordlist_sha256,
    }
    csv_payload = _csv_bytes(header, documents)
    json_payload = _json_bytes(header, documents)
    try:
        output_path.mkdir()
        (output_path / "TEXT_LAYER_AUDIT.csv").write_bytes(csv_payload)
        (output_path / "TEXT_LAYER_AUDIT.json").write_bytes(json_payload)
    except OSError as exc:
        raise TextLayerAuditError("cannot create output artifacts") from exc
    return header, documents


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", required=True, type=Path)
    parser.add_argument("--pdf-dir", required=True, type=Path)
    parser.add_argument("--out", required=True, type=Path)
    parser.add_argument("--max-bad-char-share", type=float, default=0.05)
    parser.add_argument("--min-latin-word-share", type=float, default=0.50)
    parser.add_argument("--wordlist", type=Path, default=None)
    parser.add_argument("--i-have-author-approval", action="store_true")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    try:
        header, documents = run_audit(
            args.input,
            args.pdf_dir,
            args.out,
            max_bad_char_share=args.max_bad_char_share,
            min_latin_word_share=args.min_latin_word_share,
            wordlist=args.wordlist,
            author_approved=args.i_have_author_approval,
        )
    except TextLayerAuditError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2
    for document in documents:
        print(
            f"{document['document_id']} "
            f"kept={document['kept_token_count']} "
            f"mdna={document['mdna_word_count']} "
            f"csr_esg={document['csr_esg_word_count']} "
            f"pdf_sha256={document['pdf_sha256']}"
        )
    print(
        f"documents={len(documents)} "
        f"input_sha256={header['input_sha256']} "
        f"script_sha256={header['script_sha256']}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
