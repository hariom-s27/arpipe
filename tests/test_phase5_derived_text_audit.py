from __future__ import annotations

import csv
import json
import os
import tempfile
from pathlib import Path

import pymupdf
import pytest

from tools.phase5.derived import text_layer_audit


@pytest.fixture
def external_root():
    with tempfile.TemporaryDirectory(prefix="phase5_text_audit_test_") as directory:
        yield Path(directory)


def _write_pdf(path: Path, pages: list[str | None]) -> None:
    document = pymupdf.open()
    for text in pages:
        page = document.new_page()
        if text is not None:
            page.insert_textbox(
                pymupdf.Rect(36, 36, page.rect.width - 36, page.rect.height - 36),
                text,
                fontname="helv",
                fontsize=11,
            )
    document.save(path)
    document.close()


def _row(**updates: str) -> dict[str, str]:
    row = {
        "document_id": "doc1",
        "start_page_0based": "0",
        "end_page_0based": "0",
        "body_title": "",
        "gap_pages": "",
        "csr_esg_pages": "",
        "split": "FIT",
    }
    row.update(updates)
    return row


def _write_input(path: Path, rows: list[dict[str, str]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=text_layer_audit.INPUT_COLUMNS, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def _case(tmp_path: Path, pages: list[str | None], row: dict[str, str]) -> tuple[Path, Path]:
    pdf_dir = tmp_path / "pdfs"
    pdf_dir.mkdir()
    _write_pdf(pdf_dir / f"{row['document_id']}.pdf", pages)
    input_csv = tmp_path / "input.csv"
    _write_input(input_csv, [row])
    return input_csv, pdf_dir


def _read_document(out: Path) -> dict[str, object]:
    payload = json.loads((out / "TEXT_LAYER_AUDIT.json").read_text(encoding="utf-8"))
    return payload["documents"][0]


def test_clean_english_page_is_not_broken_and_heading_is_found(tmp_path, external_root):
    row = _row(body_title="Management Discussion and Analysis")
    input_csv, pdf_dir = _case(
        tmp_path,
        ["MANAGEMENT DISCUSSION AND ANALYSIS\nThe company delivered resilient operating performance."],
        row,
    )
    out = external_root / "out"

    result = text_layer_audit.main(["--input", str(input_csv), "--pdf-dir", str(pdf_dir), "--out", str(out)])

    assert result == 0
    document = _read_document(out)
    assert document["text_layer_broken"] is False
    assert document["heading_in_text_layer"] is True


@pytest.mark.parametrize(
    ("page_text", "body_title"),
    [
        ("MANAGEMENT DISCUSSION\nAND ANALYSIS\nStrong demand continued.", "Management Discussion and Analysis"),
        (
            "MANAGEMENT DISCUSSION & ANALYSIS REPORT\nStrong demand continued.",
            "Management's Discussion and Analysis",
        ),
        ("MANAGEMENT DISCUSSION AND ANALYSISREPORT\nStrong demand continued.", "Management Discussion and Analysis"),
        (
            "4. MANAGEMENT DISCUSSION AND ANALYSIS REPORT 2023-24\nStrong demand continued.",
            "Annexure 1 – Management Discussion and Analysis 2023-24",
        ),
    ],
    ids=["wrapped-title", "possessive-ampersand-report", "missing-space", "item-annexure-year-labels"],
)
def test_heading_normalization_variants(tmp_path, external_root, page_text, body_title):
    row = _row(body_title=body_title)
    input_csv, pdf_dir = _case(tmp_path, [page_text], row)
    out = external_root / "out"

    text_layer_audit.run_audit(input_csv, pdf_dir, out)

    assert _read_document(out)["heading_in_text_layer"] is True


def test_financial_table_numbers_are_dropped_from_broken_text_tokens(tmp_path, external_root):
    table = "\n".join(f"Revenue {year} {year * 13:,}.50 {year * 7:,}.25" for year in range(2010, 2030))
    row = _row(body_title="Management Discussion and Analysis")
    input_csv, pdf_dir = _case(
        tmp_path,
        [f"MANAGEMENT DISCUSSION AND ANALYSIS\nRevenue and profit table\n{table}"],
        row,
    )
    out = external_root / "out"

    text_layer_audit.run_audit(input_csv, pdf_dir, out)

    document = _read_document(out)
    assert document["text_layer_broken"] is False
    assert document["latin_word_share"] == 1.0


def _font_with_glyphs(text: str) -> pymupdf.Font | None:
    constructors = [lambda: pymupdf.Font(fontname="notos")]
    windows = Path(os.environ.get("WINDIR", "C:/Windows")) / "Fonts"
    candidates = [
        windows / "Nirmala.ttf",
        windows / "mangal.ttf",
        Path("/usr/share/fonts/truetype/noto/NotoSansDevanagari-Regular.ttf"),
        Path("/usr/share/fonts/truetype/lohit-devanagari/lohit-devanagari.ttf"),
    ]
    constructors.extend(lambda candidate=candidate: pymupdf.Font(fontfile=str(candidate)) for candidate in candidates if candidate.is_file())
    required = {ord(character) for character in text if not character.isspace()}
    for constructor in constructors:
        try:
            font = constructor()
        except Exception:
            continue
        if all(font.has_glyph(codepoint) for codepoint in required):
            return font
    return None


def _replace_stream_with_actual_text(document: pymupdf.Document, content_xref: int, text: str) -> None:
    original_stream = document.xref_stream(content_xref)
    actual_text = (b"\xfe\xff" + text.encode("utf-16-be")).hex().upper().encode("ascii")
    marked_stream = b"/Span << /ActualText <" + actual_text + b"> >> BDC\n" + original_stream + b"\nEMC\n"
    document.update_stream(content_xref, marked_stream)


def test_devanagari_header_with_english_body_is_not_broken(tmp_path, external_root):
    header = "प्रबंधन चर्चा और विश्लेषण"
    font = _font_with_glyphs(header)
    if font is None:
        pytest.skip("no installed font exposes the Devanagari glyphs needed for a synthetic PyMuPDF text layer")
    pdf_dir = tmp_path / "pdfs"
    pdf_dir.mkdir()
    pdf_path = pdf_dir / "doc1.pdf"
    document = pymupdf.open()
    page = document.new_page()
    writer = pymupdf.TextWriter(page.rect)
    writer.append((72, 72), header, font=font, fontsize=11)
    writer.write_text(page)
    page.insert_text((72, 100), "The company delivered resilient operating performance", fontsize=11)
    document.save(pdf_path)
    document.close()
    input_csv = tmp_path / "input.csv"
    _write_input(input_csv, [_row()])
    out = external_root / "out"

    text_layer_audit.run_audit(input_csv, pdf_dir, out)

    assert _read_document(out)["text_layer_broken"] is False


def test_replacement_characters_make_text_layer_broken(tmp_path, external_root):
    bad_text = "\ufffd" * 40
    pdf_dir = tmp_path / "pdfs"
    pdf_dir.mkdir()
    document = pymupdf.open()
    page = document.new_page()
    page.insert_text((72, 72), "synthetic replacement text")
    content_xref = page.get_contents()[0]
    _replace_stream_with_actual_text(document, content_xref, bad_text)
    pdf_path = pdf_dir / "doc1.pdf"
    document.save(pdf_path)
    document.close()
    check = pymupdf.open(pdf_path)
    assert check[0].get_text("text").count("\ufffd") >= 1
    check.close()
    input_csv = tmp_path / "input.csv"
    _write_input(input_csv, [_row()])
    out = external_root / "out"

    text_layer_audit.run_audit(input_csv, pdf_dir, out)

    document_result = _read_document(out)
    assert document_result["text_layer_broken"] is True
    assert document_result["bad_char_share"] > 0.05


def test_image_only_page_emits_no_text(tmp_path, external_root):
    input_csv, pdf_dir = _case(tmp_path, [None], _row())
    out = external_root / "out"

    text_layer_audit.run_audit(input_csv, pdf_dir, out)

    document = _read_document(out)
    assert document["heading_in_text_layer"] == "NA"
    assert document["text_layer_broken"] == "NO_TEXT"
    assert document["bad_char_share"] == 0.0
    assert document["latin_word_share"] is None
    assert document["kept_token_count"] == 0


def test_word_counts_exclude_gaps_and_count_csr_pages_separately(tmp_path, external_root):
    row = _row(end_page_0based="2", gap_pages="1", csr_esg_pages="2")
    input_csv, pdf_dir = _case(
        tmp_path,
        ["Alpha beta 123", "Gap words are excluded", "CSR climate action 2024"],
        row,
    )
    out = external_root / "out"

    text_layer_audit.run_audit(input_csv, pdf_dir, out)

    document = _read_document(out)
    assert document["mdna_word_count"] == 5
    assert document["csr_esg_word_count"] == 3


def test_output_inside_fake_repository_is_refused(tmp_path):
    input_csv, pdf_dir = _case(tmp_path, ["Clean English body text"], _row())
    fake_repo = tmp_path / "fake_repo"
    fake_repo.mkdir()
    (fake_repo / ".git").mkdir()

    with pytest.raises(text_layer_audit.TextLayerAuditError, match="inside a git repository"):
        text_layer_audit.run_audit(input_csv, pdf_dir, fake_repo / "out")


def test_holdout_is_refused_without_author_approval(tmp_path, external_root):
    input_csv, pdf_dir = _case(tmp_path, ["Clean English body text"], _row(split="HOLDOUT"))

    with pytest.raises(text_layer_audit.TextLayerAuditError, match="HOLDOUT row refused"):
        text_layer_audit.run_audit(input_csv, pdf_dir, external_root / "out")


def test_csr_page_outside_span_is_refused(tmp_path, external_root):
    row = _row(csr_esg_pages="1")
    input_csv, pdf_dir = _case(tmp_path, ["Start page English text", "Outside page English text"], row)

    with pytest.raises(text_layer_audit.TextLayerAuditError, match="CSR/ESG page outside span"):
        text_layer_audit.run_audit(input_csv, pdf_dir, external_root / "out")


def test_two_runs_have_identical_artifact_bytes(tmp_path, external_root):
    row = _row(body_title="Management Discussion and Analysis")
    input_csv, pdf_dir = _case(
        tmp_path,
        ["MANAGEMENT DISCUSSION AND ANALYSIS\nDeterministic English body text"],
        row,
    )
    first = external_root / "first"
    second = external_root / "second"

    text_layer_audit.run_audit(input_csv, pdf_dir, first)
    text_layer_audit.run_audit(input_csv, pdf_dir, second)

    assert (first / "TEXT_LAYER_AUDIT.json").read_bytes() == (second / "TEXT_LAYER_AUDIT.json").read_bytes()
    assert (first / "TEXT_LAYER_AUDIT.csv").read_bytes() == (second / "TEXT_LAYER_AUDIT.csv").read_bytes()


def test_pure_devanagari_header_tokens_are_dropped_without_breaking_page():
    text = "प्रबंधन चर्चा और विश्लेषण\nThe company delivered resilient operating performance"

    kept = text_layer_audit._kept_tokens(text)
    broken, bad_share, latin_share, kept_count = text_layer_audit.audit_start_page_text(text, 0.05, 0.50)

    assert kept == ["The", "company", "delivered", "resilient", "operating", "performance"]
    assert broken is False
    assert bad_share == 0.0
    assert latin_share == 1.0
    assert kept_count == 6


def test_pure_bad_character_share_flags_replacement_and_private_use_text():
    text = ("\ufffd" * 40) + ("\ue000" * 40) + ("\uf8ff" * 40) + " clean English words"

    broken, bad_share, latin_share, kept_count = text_layer_audit.audit_start_page_text(text, 0.05, 0.50)

    assert bad_share > 0.05
    assert broken is True
    assert latin_share is not None
    assert kept_count > 0


def test_pure_token_filter_strips_punctuation_and_drops_digit_tokens():
    text = "Company, (CSR) FY2024 1,234.56 informa0on"

    kept = text_layer_audit._kept_tokens(text)
    broken, bad_share, latin_share, kept_count = text_layer_audit.audit_start_page_text(text, 0.05, 0.50)

    assert kept == ["Company", "CSR"]
    assert broken is False
    assert bad_share == 0.0
    assert latin_share == 1.0
    assert kept_count == 2
