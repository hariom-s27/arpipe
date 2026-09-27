from __future__ import annotations

"""Carry over and reconcile the curated catalog without changing its decisions.

L1 normalization case-folds, collapses whitespace, and maps curly quotation marks
to straight quotation marks. L2 applies L1, strips leading numeric/Roman/letter
labels, strips a trailing page number, changes ampersands to ``and``, removes
Unicode punctuation, and removes a generic leading Annexure label.
"""

import argparse
import csv
import hashlib
import json
import os
import re
import unicodedata
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path

CONDITIONAL_CONTEXTS = {
    "Management Discussion and Analysis": "Observable context: Heading appears as an embedded major subsection within the Directors’ Report; contains multi-page operational and financial review where no standalone MD&A section exists.",
    "MANAGEMENT DISCUSSION AND ANALYSIS": "Observable context: All-caps heading appears as an embedded major subsection within the Directors’ Report.",
    "MANAGEMENT'S DISCUSSIONS AND ANALYSIS": "Observable context: Possessive plural heading appears as an embedded major content-bearing subsection within the Directors’ Report.",
    "5. Management Discussion and Analysis": "Observable context: Numbered subsection heading within Directors’ Report followed immediately by a short referral sentence pointing to Annexure 2.",
    "34. Management Discussion and Analysis Report": "Observable context: Numbered subsection heading within Board’s Report containing a single referral sentence pointing to separate section.",
    "21. Management Discussion and Analysis Report:": "Observable context: Numbered subsection heading with trailing colon within Directors’ Report pointing to separate section.",
    "17. MANAGEMENT DISCUSSION AND ANALYSIS REPORT:": "Observable context: Numbered all-caps subsection heading with trailing colon within Directors’ Report pointing to separate section.",
    "J. MANAGEMENT'S DISCUSSION AND ANALYSIS REPORT": "Observable context: Lettered all-caps subsection heading within Directors’ Report containing statutory cross-reference statement.",
    "Management Discussion and Analysis Report": "Observable context: Subsection heading within Directors’ Report or Board’s Report containing referral sentence to separate annexure.",
    "CORPORATE GOVERNANCE AND MANAGEMENT DISCUSSIONS & ANALYSIS": "Observable context: Joint heading combining Corporate Governance and MD&A in Directors’ Report.",
    "Management Discussion & Analysis Report (MD&A Report) –": "Observable context: Cross-reference subsection heading within Corporate Governance Report.",
    "Business Environment": "Observable context: Appears as the top-level opening chapter heading of the operational review section where the section opens directly under Business Environment without a preceding Management Discussion and Analysis heading.",
}
SECTOR_TERMS = ("bank", "banking", "institution", "PSU")
BASE = Path(r"D:\gold_blind")
WRITE_LOG = BASE / "output" / "v0_2_2" / "scratch" / "write_log.csv"
ENTRY_RE = re.compile(r"^- `(.+)`\s*$")
CLASS_RE = re.compile(r"\*\*Class\*\*:\s*([^|]+?)(?:\s*\||\s*$)")
COUNT_RE = re.compile(r"\*\*Docs\*\*:\s*(\d+)\s*\|\s*\*\*TOC\*\*:\s*(\d+)\s*\|\s*\*\*BODY\*\*:\s*(\d+)")
CONTEXT_RE = re.compile(r"^\s+- \*\*Context\*\*:\s*(.*)$")
EXPECTED_SPLIT = {"EQUIVALENT": 21, "CONDITIONAL": 12, "NOT EQUIVALENT BUT CONFUSABLE": 47, "UNRESOLVED": 1}

def l1(text: str) -> str:
    mapped = text.translate(str.maketrans({"’": "'", "‘": "'", "“": '"', "”": '"'}))
    return " ".join(mapped.casefold().split())

def l2(text: str) -> str:
    value = l1(text)
    value = re.sub(r"^\s*(?:\([ivxlcdm]+\)|[ivxlcdm]+[.)]|[a-z][.)]|\d+[.)])\s*", "", value, count=1)
    value = re.sub(r"\s+\d+\s*$", "", value, count=1)
    value = value.replace("&", "and")
    value = re.sub(r"^annexure\s+(?:[-–—]\s*)?(?:[a-z0-9]+)(?:\s*[-–—:/]\s*)?", "", value, count=1)
    value = "".join(" " if unicodedata.category(ch).startswith("P") else ch for ch in value)
    return " ".join(value.split())

def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""): h.update(chunk)
    return h.hexdigest()

def log_write(path: Path) -> None:
    size = path.stat().st_size
    if size <= 0: raise RuntimeError(f"ZERO_BYTE_WRITE path={path!s}")
    digest = sha256_file(path)
    with WRITE_LOG.open("a", encoding="utf-8", newline="") as f:
        csv.writer(f, lineterminator="\n").writerow([path.relative_to(BASE).as_posix(), size, digest, datetime.now(timezone.utc).isoformat()])
        f.flush(); os.fsync(f.fileno())

def durable_text(path: Path, text: str) -> None:
    with path.open("w", encoding="utf-8", newline="") as f: f.write(text); f.flush(); os.fsync(f.fileno())
    log_write(path)

def durable_csv(path: Path, fields: list[str], rows: list[dict[str, object]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields, lineterminator="\n"); w.writeheader(); w.writerows(rows); f.flush(); os.fsync(f.fileno())
    log_write(path)

def parse_catalog(path: Path) -> list[dict[str, object]]:
    lines = path.read_text(encoding="utf-8").splitlines(); entries = []
    for index, line in enumerate(lines):
        title_match = ENTRY_RE.match(line)
        if not title_match: continue
        class_value = None; context = ""; variants: list[str] = []; printed_counts = {"docs": None, "toc": None, "body": None}
        for later in lines[index + 1:]:
            if ENTRY_RE.match(later) or later.startswith("#### ") or later == "---":
                break
            if class_value is None and (match := CLASS_RE.search(later)): class_value = match.group(1).strip()
            if match := COUNT_RE.search(later): printed_counts = {"docs": int(match.group(1)), "toc": int(match.group(2)), "body": int(match.group(3))}
            if match := CONTEXT_RE.match(later): context = match.group(1).strip()
            if "**Variants**:" in later or "**Observed forms**:" in later:
                variants.extend(part.strip().strip("`") for part in later.split(":", 1)[1].split(",") if part.strip())
        if class_value is not None:
            entries.append({"title": title_match.group(1), "class": class_value, "variants": variants, "printed_counts": printed_counts, "context": context, "source_line": index + 1})
    return entries

def clean_conditional(entry_no: int, title: str, original: str) -> tuple[str, dict[str, object] | None]:
    candidate = CONDITIONAL_CONTEXTS.get(title, original)
    cleaned = candidate
    for term in SECTOR_TERMS:
        cleaned = re.sub(rf"\b{re.escape(term)}\b", "", cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r"\s{2,}", " ", cleaned).strip()
    edit = None if cleaned == original else {"entry_no": entry_no, "before": original, "after": cleaned}
    return cleaned, edit

def fail(reason: str, value: object) -> None:
    print(f"STOP={reason}"); print(f"OFFENDING_REPR={value!r}"); print(f"OFFENDING_LEN={len(value) if hasattr(value, '__len__') else 'NA'}"); raise SystemExit(2)

def main() -> None:
    parser = argparse.ArgumentParser(); parser.add_argument("--ledger", required=True, type=Path); parser.add_argument("--catalog", required=True, type=Path); parser.add_argument("--out", required=True, type=Path); parser.add_argument("--coverage-line", required=True); args = parser.parse_args()
    entries = parse_catalog(args.catalog); split = Counter(str(e["class"]) for e in entries)
    print(f"PARSED_ENTRY_COUNT={len(entries)}"); print("PARSED_CLASS_SPLIT=" + ";".join(f"{key}={split[key]}" for key in sorted(split)))
    frame = [e for e in entries if e["class"] == "UNRESOLVED" and "FRAME_ANOMALY" in str(e["title"]) and "NOT_AN_ANNUAL_REPORT" in str(e["title"])]
    if len(entries) != 81 or dict(split) != EXPECTED_SPLIT or len(frame) != 1: fail("CATALOG_PARSE_MISMATCH", {"entries": entries, "split": dict(split), "frame": frame})
    active = [e for e in entries if e is not frame[0]]
    with args.ledger.open("r", encoding="utf-8", newline="") as f: ledger = list(csv.DictReader(f))

    matches_by_entry: dict[int, list[dict[str, str]]] = {}; levels: dict[int, str] = {}
    for entry_no, entry in enumerate(active, 1):
        forms = [str(entry["title"])] + [str(v) for v in entry["variants"]]
        keys1 = {l1(v) for v in forms}; match1 = [r for r in ledger if l1(r["heading_text_visual"]) in keys1]
        if match1: levels[entry_no] = "L1"; matches_by_entry[entry_no] = match1
        else:
            keys2 = {l2(v) for v in forms}; match2 = [r for r in ledger if l2(r["heading_text_visual"]) in keys2]
            levels[entry_no] = "L2" if match2 else "NONE"; matches_by_entry[entry_no] = match2

    owners: dict[str, list[int]] = defaultdict(list)
    for entry_no in range(1, len(active) + 1):
        for row in matches_by_entry[entry_no]: owners[row["obs_id"]].append(entry_no)

    reconciliation = []; map_rows = []; text_edits = []; singles = []; review_entries = []
    md = ["# TITLE_EQUIVALENCE_v0_2_2.md", "", "This list classifies titles only. Presence, boundaries, states and reason codes follow the Gold protocol.", "", "Produced without access to the ARPipe repository or its heading patterns.", "", "Produced by an isolated AI-assisted reading, combining PDF text extraction and contact-sheet viewing, of the 60 FIT DEVELOPMENT documents, without access to the ARPipe repository or its heading patterns; classes assigned by a rule script; pending independent human spot-verification.", "", args.coverage_line, "", "Entries with match_level NONE or class_status CONFLICT are listed as found in the v0.2 catalog and require a rules-reviewer decision before use.", "", "## Curated catalog reconciliation", ""]
    last_class = None
    for entry_no, entry in enumerate(active, 1):
        rows = matches_by_entry[entry_no]; distribution = Counter(r["assigned_class"] for r in rows)
        class_status = "NONE" if not rows else ("AGREES" if set(distribution) == {entry["class"]} else "CONFLICT")
        overlap = any(len(owners[r["obs_id"]]) > 1 for r in rows)
        documents = len({r["document_id"] for r in rows}); toc = sum(r["location"] == "TOC" for r in rows); body = sum(r["location"] == "BODY" for r in rows)
        distribution_text = json.dumps(dict(sorted(distribution.items())), ensure_ascii=False, sort_keys=True)
        rec = {"entry_no": entry_no, "title": entry["title"], "catalog_class": entry["class"], "catalog_docs": entry["printed_counts"]["docs"], "catalog_toc": entry["printed_counts"]["toc"], "catalog_body": entry["printed_counts"]["body"], "match_level": levels[entry_no], "matched_rows": len(rows), "matched_documents": documents, "ledger_class_distribution": distribution_text, "class_status": class_status, "overlap": str(overlap).upper()}
        reconciliation.append(rec)
        for row in rows: map_rows.append({"entry_no": entry_no, "title": entry["title"], "catalog_class": entry["class"], "obs_id": row["obs_id"], "match_level": levels[entry_no], "ledger_class": row["assigned_class"]})
        if documents == 1: singles.append(str(entry["title"]))
        if class_status in {"NONE", "CONFLICT"}: review_entries.append((str(entry["title"]), class_status))
        if entry["class"] != last_class: md.extend([f"### {entry['class']}", ""]); last_class = str(entry["class"])
        marker = " [single document — rules reviewer decides]" if documents == 1 else ""
        md.append(f"- `{entry['title']}`{marker}"); md.append(f"  - **Class**: {entry['class']} | **Match level**: {levels[entry_no]} | **Class status**: {class_status} | **Documents**: {documents} | **TOC**: {toc} | **BODY**: {body}")
        context = str(entry["context"])
        if entry["class"] == "CONDITIONAL":
            context, edit = clean_conditional(entry_no, str(entry["title"]), context)
            if edit is not None: text_edits.append(edit)
        if context: md.append(f"  - **Context**: {context}")
        if class_status in {"NONE", "CONFLICT"}: print("REVIEW_ENTRY=" + json.dumps(rec, ensure_ascii=False, sort_keys=True))

    decision_titles = []
    for title in singles + [title for title, _ in review_entries]:
        if title not in decision_titles: decision_titles.append(title)
    md.extend(["", "## Needs rules-reviewer decision", ""]); md.extend(f"- `{title}`" for title in decision_titles); md.append("")
    markdown = "\n".join(md)
    forbidden = ["FRAME_ANOMALY", "NOT_AN_ANNUAL_REPORT", "definitive", "annotation procedure"]
    hits = [word for word in forbidden if word.casefold() in markdown.casefold()]
    if hits: fail("FORBIDDEN_OUTPUT_TEXT", hits)
    out_dir = args.out.parent
    durable_text(args.out, markdown)
    durable_csv(out_dir / "TITLE_CATALOG_RECONCILIATION_v0_2_2.csv", list(reconciliation[0]), reconciliation)
    durable_csv(out_dir / "TITLE_CATALOG_MAP_v0_2_2.csv", ["entry_no", "title", "catalog_class", "obs_id", "match_level", "ledger_class"], map_rows)
    durable_csv(out_dir / "CATALOG_TEXT_EDITS_v0_2_2.csv", ["entry_no", "before", "after"], text_edits)
    unmatched = Counter(r["assigned_class"] for r in ledger if r["obs_id"] not in owners)
    print(f"OUTPUT_ENTRY_COUNT={len(active)}"); print("OUTPUT_CLASS_SPLIT=" + ";".join(f"{key}={Counter(str(e['class']) for e in active)[key]}" for key in sorted(set(str(e['class']) for e in active))))
    print("MATCH_LEVEL_COUNTS=" + json.dumps(dict(sorted(Counter(levels.values()).items())), sort_keys=True)); print("CLASS_STATUS_COUNTS=" + json.dumps(dict(sorted(Counter(r['class_status'] for r in reconciliation).items())), sort_keys=True)); print(f"OVERLAP_ENTRIES={sum(r['overlap'] == 'TRUE' for r in reconciliation)}"); print("UNMATCHED_LEDGER_ROWS_BY_CLASS=" + json.dumps(dict(sorted(unmatched.items())), sort_keys=True)); print(f"SINGLE_DOCUMENT_TITLES={len(singles)}"); print(f"TEXT_EDITS={len(text_edits)}")

if __name__ == "__main__": main()
