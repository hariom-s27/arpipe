"""P5-B intake pack builder (mechanical, no classification).

Reads only files under docs/phase5/evidence/p5b/ (v0_2_2 package + inputs_ref) and writes
only into docs/phase5/evidence/p5b/intake/. It makes NO class decisions: it re-verifies the
package, audits the format of the ledger heading fields, extracts back-quoted strings,
and lays out a per-document worksheet for the human rules reviewer.

Run from the repository root:
    python docs/phase5/evidence/p5b/intake/build_intake_pack.py
Deterministic: output depends only on the input bytes (explicit sorting, no time stamps).
"""
import csv
import hashlib
import json
import re
from collections import Counter, defaultdict
from pathlib import Path

BASE = Path("docs/phase5/evidence/p5b")
PKG = BASE / "v0_2_2"
REF = BASE / "inputs_ref"
OUT = BASE / "intake"
KEY = ("EQUIVALENT", "CONDITIONAL")
CLASSES = ("EQUIVALENT", "CONDITIONAL", "NOT EQUIVALENT BUT CONFUSABLE")
QUOTE = re.compile(r"`([^`]+)`")
# Heuristic, report-only flag: wording that describes a cross-reference or a mention
# inside running text rather than a printed heading. Never used to change a class.
MENTION_WORDS = re.compile(r"\b(states|forms part of|within paragraph|mentions?|refers? to|reference)\b", re.I)


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def read_csv(p):
    with p.open(encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def write_csv(p, fields, rows):
    with p.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields, lineterminator="\n")
        w.writeheader()
        w.writerows(rows)


def field_format(text):
    t = text.strip()
    if re.fullmatch(r"`[^`]+`", t):
        return "CLEAN_QUOTED"
    if QUOTE.search(t):
        return "QUOTED_IN_NOTE"
    return "NO_QUOTE"


def main():
    OUT.mkdir(exist_ok=True)
    summary = {}

    # 1. Package verification against HASHES_v0_2_2.txt
    bad = []
    lines = (PKG / "HASHES_v0_2_2.txt").read_text(encoding="utf-8").splitlines()
    for line in lines:
        h, size, rel = line.split("  ")
        p = PKG / rel
        if not p.exists() or sha(p) != h or p.stat().st_size != int(size):
            bad.append(rel)
    summary["package_files_listed"] = len(lines)
    summary["package_files_bad"] = bad
    summary["hashes_file_sha256"] = sha(PKG / "HASHES_v0_2_2.txt")

    ledger = read_csv(PKG / "TITLE_EVIDENCE_LEDGER_v0_2_2.csv")
    frame = read_csv(PKG / "FRAME_STATUS_v0_2_2.csv")
    evid = read_csv(PKG / "EVIDENCE_INDEX_v0_2_2.csv")
    prov = read_csv(PKG / "PROVENANCE_v0_2_2.csv")
    manifest = read_csv(REF / "FIT_BLIND_MANIFEST.csv")

    # 2. Independent re-checks (subset of G1-G5)
    man_sha = {r["document_id"]: r["source_pdf_sha256"] for r in manifest}
    pages = {r["document_id"]: int(r["page_count"]) for r in prov}
    keys = Counter((r["document_id"], r["page_0based"], r["location"], r["heading_text_verbatim"], r["occurrence_index"]) for r in ledger)
    docs = {r["document_id"] for r in ledger} | {r["document_id"] for r in frame}
    summary["recheck"] = {
        "ledger_rows": len(ledger),
        "frame_rows": len(frame),
        "documents": len(docs),
        "manifest_sha_mismatch": sorted({r["document_id"] for r in ledger if man_sha.get(r["document_id"]) != r["pdf_sha256"]}),
        "key_duplicates": sum(1 for v in keys.values() if v > 1),
        "obs_id_duplicates": len(ledger) - len({r["obs_id"] for r in ledger}),
        "pages_out_of_range": sum(1 for r in ledger if not 0 <= int(r["page_0based"]) < pages[r["document_id"]]),
        "class_counts": {c: sum(1 for r in ledger if r["assigned_class"] == c) for c in CLASSES},
        "evidence_rows": len(evid),
        "evidence_types": dict(sorted(Counter(r["evidence_type"] for r in evid).items())),
        "evidence_distinct_png": len({r["png"] for r in evid}),
    }

    # 3. Field-format audit (mechanical)
    audit = defaultdict(Counter)
    for r in ledger:
        audit[r["assigned_class"]][field_format(r["heading_text_verbatim"])] += 1
        audit[r["assigned_class"]]["visual_equals_verbatim" if r["heading_text_visual"] == r["heading_text_verbatim"] else "visual_differs"] += 1
        if MENTION_WORDS.search(r["heading_text_verbatim"]):
            audit[r["assigned_class"]]["mention_wording_flag"] += 1
    summary["field_format_audit"] = {c: dict(sorted(audit[c].items())) for c in CLASSES}

    # 4. Candidates: every EQUIVALENT/CONDITIONAL row with extracted back-quoted strings
    ev_by_obs = defaultdict(list)
    for r in evid:
        ev_by_obs[r["obs_id"]].append(r)
    cand = []
    for r in sorted((r for r in ledger if r["assigned_class"] in KEY), key=lambda r: (r["document_id"], int(r["page_0based"]), r["location"], r["obs_id"])):
        e = ev_by_obs.get(r["obs_id"], [])
        cand.append({
            "obs_id": r["obs_id"],
            "document_id": r["document_id"],
            "page_0based": r["page_0based"],
            "location": r["location"],
            "assigned_class": r["assigned_class"],
            "field_format": field_format(r["heading_text_verbatim"]),
            "mention_wording_flag": "Y" if MENTION_WORDS.search(r["heading_text_verbatim"]) else "N",
            "quoted_strings": " || ".join(QUOTE.findall(r["heading_text_verbatim"])),
            "heading_field_as_recorded": r["heading_text_verbatim"],
            "evidence_png": ";".join(sorted({x["png"] for x in e})),
            "evidence_provenance": ";".join(sorted({x["page_provenance"] for x in e})),
        })
    write_csv(OUT / "KEY_ROW_CANDIDATES_v0_2_2.csv", list(cand[0].keys()), cand)

    # 5. Distinct quoted strings among key rows (inventory; no grouping beyond exact text)
    inv = defaultdict(lambda: {"rows": 0, "docs": set(), "classes": Counter()})
    for c in cand:
        for s in dict.fromkeys(QUOTE.findall(c["heading_field_as_recorded"])):
            inv[s]["rows"] += 1
            inv[s]["docs"].add(c["document_id"])
            inv[s]["classes"][c["assigned_class"]] += 1
    inv_rows = [
        {"quoted_string": s, "rows": v["rows"], "documents": len(v["docs"]),
         "EQUIVALENT_rows": v["classes"]["EQUIVALENT"], "CONDITIONAL_rows": v["classes"]["CONDITIONAL"]}
        for s, v in inv.items()
    ]
    inv_rows.sort(key=lambda x: (-x["documents"], -x["rows"], x["quoted_string"]))
    write_csv(OUT / "KEY_QUOTED_STRING_INVENTORY_v0_2_2.csv", list(inv_rows[0].keys()), inv_rows)
    summary["key_rows"] = len(cand)
    summary["key_distinct_quoted_strings"] = len(inv_rows)
    summary["key_rows_without_quote"] = sum(1 for c in cand if c["field_format"] == "NO_QUOTE")

    # 6. Per-document worksheet for the human reviewer (blank decision columns)
    frame_ids = {r["document_id"]: r["frame_status"] for r in frame}
    by_doc = defaultdict(list)
    for c in cand:
        by_doc[c["document_id"]].append(c)
    ws = []
    for d in sorted(man_sha):
        cs = by_doc.get(d, [])
        ws.append({
            "document_id": d,
            "page_count": pages.get(d, ""),
            "frame_status_ai": frame_ids.get(d, ""),
            "key_rows": len(cs),
            "toc_pages_0based": ";".join(sorted({c["page_0based"] for c in cs if c["location"] == "TOC"}, key=int)),
            "body_pages_0based": ";".join(sorted({c["page_0based"] for c in cs if c["location"] == "BODY"}, key=int)),
            "ai_quoted_strings": " || ".join(sorted({s for c in cs for s in QUOTE.findall(c["heading_field_as_recorded"])})),
            "evidence_png": ";".join(sorted({p for c in cs for p in c["evidence_png"].split(";") if p})),
            "REVIEWER_mdna_present(Y/N/NOT_AR)": "",
            "REVIEWER_toc_title_verbatim": "",
            "REVIEWER_body_title_verbatim": "",
            "REVIEWER_body_start_page_0based": "",
            "REVIEWER_notes": "",
        })
    write_csv(OUT / "DOCUMENT_WORKSHEET_v0_2_2.csv", list(ws[0].keys()), ws)
    summary["worksheet_documents"] = len(ws)
    summary["worksheet_documents_without_key_rows"] = sorted(r["document_id"] for r in ws if r["key_rows"] == 0)

    # 7. Catalog reconciliation roll-up (copied counts, no edits)
    rec = read_csv(PKG / "TITLE_CATALOG_RECONCILIATION_v0_2_2.csv")
    summary["catalog_reconciliation"] = {
        "entries": len(rec),
        "match_level": dict(sorted(Counter(r["match_level"] for r in rec).items())),
        "class_status": dict(sorted(Counter(r["class_status"] for r in rec).items())),
    }

    (OUT / "INTAKE_SUMMARY.json").write_text(json.dumps(summary, indent=2, ensure_ascii=False, sort_keys=True) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
