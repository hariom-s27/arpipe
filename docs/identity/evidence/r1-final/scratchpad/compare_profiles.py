"""Step 3 comparison. Governing: T0.4-base triage vs candidate triage, per FIT/VALIDATION page.
Secondary diagnostic: page kinds vs dataset/corpus_freeze/page_profile.csv (rows of FIT and
VALIDATION documents only; every other row is skipped on its document_id without inspection)."""
import collections
import csv
import json
import pathlib
import sys

S = pathlib.Path(sys.argv[1])
base = json.loads((S / "profile_base.json").read_text(encoding="utf-8"))
cand = json.loads((S / "profile_cand.json").read_text(encoding="utf-8"))
universe = json.loads((S / "universe.json").read_text(encoding="utf-8"))
split_of = {d["document_id"]: d["split"] for d in universe["documents"]}
assert set(base["documents"]) == set(cand["documents"]) == set(split_of), "document sets differ"

report = {"thresholds_equal": base["thresholds_after_configure"] == cand["thresholds_after_configure"],
          "needs_ocr_kinds_equal": base["needs_ocr_kinds"] == cand["needs_ocr_kinds"],
          "thresholds_after_configure": cand["thresholds_after_configure"], "needs_ocr_kinds": cand["needs_ocr_kinds"]}

# ---------------------------------------------------------------- governing comparison
per_split = {s: collections.Counter() for s in ("FIT", "VALIDATION")}
kind_mismatch, ocr_page_mismatch, ocr_doc_mismatch, errors, structural = [], [], [], [], []
field_mismatch = []
for docid in sorted(split_of):
    s = split_of[docid]
    b, c = base["documents"][docid], cand["documents"][docid]
    per_split[s]["documents"] += 1
    if "error" in b or "error" in c:
        errors.append({"document_id": docid, "base": b.get("error"), "candidate": c.get("error")})
        continue
    if b["n_pages"] != c["n_pages"] or len(b["pages"]) != len(c["pages"]):
        structural.append({"document_id": docid, "base_pages": len(b["pages"]), "candidate_pages": len(c["pages"])})
        continue
    per_split[s]["pages"] += len(b["pages"])
    if set(b["ocr_pages"]) != set(c["ocr_pages"]):
        ocr_doc_mismatch.append({"document_id": docid, "base_only": sorted(set(b["ocr_pages"]) - set(c["ocr_pages"])),
                                 "candidate_only": sorted(set(c["ocr_pages"]) - set(b["ocr_pages"]))})
    else:
        per_split[s]["ocr_doc_matches"] += 1
    for pb, pc in zip(b["pages"], c["pages"]):
        assert pb["page_no"] == pc["page_no"]
        if pb["kind"] == pc["kind"]:
            per_split[s]["kind_matches"] += 1
        else:
            kind_mismatch.append({"document_id": docid, "page": pb["page_no"], "base": pb["kind"], "candidate": pc["kind"]})
        in_b, in_c = pb["page_no"] in set(b["ocr_pages"]), pc["page_no"] in set(c["ocr_pages"])
        assert in_b == pb["needs_ocr"] and in_c == pc["needs_ocr"], "needs_ocr flag disagrees with ocr_page_numbers"
        if in_b == in_c:
            per_split[s]["ocr_page_matches"] += 1
        else:
            ocr_page_mismatch.append({"document_id": docid, "page": pb["page_no"], "base": in_b, "candidate": in_c})
        if pb != pc:
            field_mismatch.append({"document_id": docid, "page": pb["page_no"],
                                   "fields": [k for k in pb if pb[k] != pc.get(k)]})

report["governing"] = {
    "FIT": dict(per_split["FIT"]), "VALIDATION": dict(per_split["VALIDATION"]),
    "total_documents": sum(v["documents"] for v in per_split.values()),
    "total_pages": sum(v["pages"] for v in per_split.values()),
    "pagekind_matches": sum(v["kind_matches"] for v in per_split.values()),
    "pagekind_mismatches": len(kind_mismatch),
    "ocr_page_matches": sum(v["ocr_page_matches"] for v in per_split.values()),
    "ocr_page_mismatches": len(ocr_page_mismatch),
    "ocr_set_document_matches": sum(v["ocr_doc_matches"] for v in per_split.values()),
    "ocr_set_document_mismatches": len(ocr_doc_mismatch),
    "document_errors": errors, "structural_mismatches": structural,
    "kind_mismatch_list": kind_mismatch, "ocr_page_mismatch_list": ocr_page_mismatch, "ocr_doc_mismatch_list": ocr_doc_mismatch,
    "supplementary_all_fields_except_script_meta_identical_pages": sum(v["pages"] for v in per_split.values()) - len(field_mismatch),
    "supplementary_field_mismatch_pages": len(field_mismatch), "supplementary_field_mismatch_sample": field_mismatch[:10],
}

# ---------------------------------------------------------------- secondary: page_profile.csv
profile_csv = S / "cand-t04" / "dataset/corpus_freeze/page_profile.csv"
wanted = set(split_of)
pp, pp_pagecount = {}, {}
with profile_csv.open(newline="", encoding="utf-8-sig") as fh:
    for row in csv.DictReader(fh):
        if row["document_id"] not in wanted:
            continue
        pp[(row["document_id"], int(row["physical_page"]))] = row["kind"]
        pp_pagecount[row["document_id"]] = int(row["page_count"])
min_page = min(k[1] for k in pp)
assert min_page in (0, 1), min_page
# PageProfile.page_no is 0-based. physical_page == page_no + offset, with offset == min physical_page.
offset = min_page


def against_profile(run):
    out = {"FIT": collections.Counter(), "VALIDATION": collections.Counter()}
    mism, missing_rows, extra_rows = [], [], []
    seen = set()
    for docid in sorted(split_of):
        s = split_of[docid]
        d = run["documents"][docid]
        if "error" in d:
            continue
        if pp_pagecount.get(docid) != d["n_pages"]:
            missing_rows.append({"document_id": docid, "profile_page_count": pp_pagecount.get(docid), "n_pages": d["n_pages"]})
        for p in d["pages"]:
            key = (docid, p["page_no"] + offset)
            seen.add(key)
            out[s]["pages"] += 1
            if key not in pp:
                extra_rows.append({"document_id": docid, "page": p["page_no"]})
            elif pp[key] == p["kind"]:
                out[s]["matches"] += 1
            else:
                mism.append({"document_id": docid, "page": p["page_no"], "page_profile": pp[key], "candidate": p["kind"]})
    unmatched_profile_rows = [k for k in pp if k not in seen]
    return out, mism, missing_rows, extra_rows, unmatched_profile_rows


sec = {"physical_page_convention": "1-based" if offset == 1 else "0-based", "min_physical_page": min_page, "profile_rows_for_fit_validation": len(pp)}
for name, run in (("candidate", cand), ("base", base)):
    out, mism, pc, extra, unmatched = against_profile(run)
    confusion = collections.Counter((m["page_profile"], m["candidate"]) for m in mism)
    sec[name] = {
        "FIT": dict(out["FIT"]), "VALIDATION": dict(out["VALIDATION"]),
        "matches": sum(v["matches"] for v in out.values()), "mismatches": len(mism),
        "confusion_page_profile_to_run": {f"{a}->{b}": n for (a, b), n in confusion.most_common()},
        "page_count_disagreements": pc, "pages_without_profile_row": len(extra), "profile_rows_without_page": len(unmatched),
        "mismatch_list": mism,
    }
sec["candidate_and_base_mismatch_sets_identical"] = (
    {(m["document_id"], m["page"], m["page_profile"], m["candidate"]) for m in sec["candidate"]["mismatch_list"]}
    == {(m["document_id"], m["page"], m["page_profile"], m["candidate"]) for m in sec["base"]["mismatch_list"]})
report["secondary_page_profile"] = sec

(S / "comparison.json").write_text(json.dumps(report, indent=1), encoding="utf-8")
g = report["governing"]
print(json.dumps({k: v for k, v in g.items() if not k.endswith("_list") and k != "supplementary_field_mismatch_sample"}, indent=1))
print("thresholds equal:", report["thresholds_equal"], " needs_ocr kinds equal:", report["needs_ocr_kinds_equal"], report["needs_ocr_kinds"])
brief = {k: v for k, v in sec.items() if k not in ("candidate", "base")}
for name in ("candidate", "base"):
    brief[name] = {k: v for k, v in sec[name].items() if k != "mismatch_list" and k != "page_count_disagreements"}
    brief[name]["page_count_disagreements"] = len(sec[name]["page_count_disagreements"])
print(json.dumps(brief, indent=1))
