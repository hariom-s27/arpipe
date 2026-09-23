"""RESEARCH_ONLY. NON-GOLD. NOT A PROTOCOL.

Guideline stress test for the MD&A boundary casebook (T0.4-GOLD-MD&A-ANNOTATION-RESEARCH).
The DRAFT rules below are a recommendation pending author approval. Each casebook case
is described only by features an annotator can observe from the document itself. The
check asks two mechanical questions:

  1. TOTALITY   - does the draft rule set reach a definite outcome (or an explicit
                  UNRESOLVED / AMBIGUOUS outcome) for every case, i.e. is any case left
                  with no applicable rule?
  2. DETERMINISM - if the rules are evaluated in any order, is the outcome unchanged?
                  (two applicable rules that disagree = an operational conflict).

It says nothing about real documents and creates no label. No corpus PDF is read.
"""
from __future__ import annotations

import csv
import json
import os
import random

HERE = os.path.dirname(os.path.abspath(__file__))

# ---------------------------------------------------------------- observable features per case
# heading:   standalone | in_directors_report_subheading | combined_heading | none
# heading_pos: top | mid | bottom_no_body   (position of the designating heading on its page)
# occurrence_kind: body | toc_only | pointer_only | running_header_only
# next_boundary: top_level_mid_page | top_level_next_page | annexure_top_level | end_of_document | unclear
# n_candidates: number of distinct designated headings that head real body text
CASES = {
    "CASE-01": dict(heading="standalone", heading_pos="top", occurrence_kind="body", next_boundary="top_level_next_page", n_candidates=1, bilingual=False),
    "CASE-02": dict(heading="in_directors_report_subheading", heading_pos="mid", occurrence_kind="body", next_boundary="top_level_next_page", n_candidates=1, bilingual=False),
    "CASE-03": dict(heading="standalone", heading_pos="mid", occurrence_kind="body", next_boundary="top_level_next_page", n_candidates=1, bilingual=False),
    "CASE-04": dict(heading="standalone", heading_pos="top", occurrence_kind="body", next_boundary="top_level_next_page", n_candidates=1, bilingual=False, spans_pages=True),
    "CASE-05": dict(heading="standalone", heading_pos="top", occurrence_kind="body", next_boundary="top_level_mid_page", n_candidates=1, bilingual=False),
    "CASE-06": dict(heading="standalone", heading_pos="mid", occurrence_kind="body", next_boundary="annexure_top_level", n_candidates=1, bilingual=False),
    "CASE-07": dict(heading="standalone", heading_pos="top", occurrence_kind="body", next_boundary="top_level_next_page", n_candidates=2, bilingual=False),
    "CASE-08": dict(heading="standalone", heading_pos="mid", occurrence_kind="body", next_boundary="top_level_next_page", n_candidates=1, bilingual=False, toc_page_disagrees=True),
    "CASE-09": dict(heading="standalone", heading_pos="top", occurrence_kind="body", next_boundary="top_level_next_page", n_candidates=1, bilingual=True),
    "CASE-10": dict(heading="standalone", heading_pos="top", occurrence_kind="body", next_boundary="unclear", n_candidates=1, bilingual=False),
    # extra probes used only to test rule totality (not part of the ten required cases)
    "PROBE-A_toc_only": dict(heading="none", heading_pos="top", occurrence_kind="toc_only", next_boundary="end_of_document", n_candidates=0, bilingual=False),
    "PROBE-B_pointer_only": dict(heading="none", heading_pos="top", occurrence_kind="pointer_only", next_boundary="end_of_document", n_candidates=0, bilingual=False),
    "PROBE-C_combined_heading": dict(heading="combined_heading", heading_pos="top", occurrence_kind="body", next_boundary="top_level_next_page", n_candidates=1, bilingual=False),
    "PROBE-D_heading_at_page_bottom": dict(heading="standalone", heading_pos="bottom_no_body", occurrence_kind="body", next_boundary="end_of_document", n_candidates=1, bilingual=False),
}

# ---------------------------------------------------------------- DRAFT rules (each: id, dimension, predicate, outcome)
RULES = [
    # presence
    ("P1", "presence", lambda c: c["heading"] in ("standalone", "in_directors_report_subheading") and c["occurrence_kind"] == "body", "PRESENT"),
    ("P2", "presence", lambda c: c["heading"] == "combined_heading", "PRESENT_STRUCTURE_COMBINED"),
    ("P3", "presence", lambda c: c["occurrence_kind"] in ("toc_only", "pointer_only", "running_header_only") and c["heading"] == "none", "NOT_ESTABLISHED_BY_OCCURRENCE"),
    # start (a TOC/bookmark/pointer occurrence never defines a start)
    ("S1", "start", lambda c: c["heading"] == "standalone" and c["occurrence_kind"] == "body" and c["heading_pos"] in ("top", "mid"), "START=heading_page"),
    ("S2", "start", lambda c: c["heading"] == "in_directors_report_subheading" and c["occurrence_kind"] == "body", "START=heading_page_of_designated_subheading"),
    ("S3", "start", lambda c: c["heading"] == "standalone" and c["heading_pos"] == "bottom_no_body", "START=heading_page_AND_flag_substantive_start_next_page"),
    ("S4", "start", lambda c: c["heading"] == "combined_heading", "START=UNRESOLVED_combined_section"),
    ("S5", "start", lambda c: c["heading"] == "none", "START=NONE"),
    # end (inclusive: last page that still carries MD&A content). Gated on a start existing:
    # an end rule that fires with no start is incoherent (defect found by the first run of this check).
    ("E0", "end", lambda c: c["heading"] == "none", "END=NONE_(no_start)"),
    ("E1", "end", lambda c: c["heading"] != "none" and c["next_boundary"] == "top_level_next_page", "END=page_before_next_top_level_heading"),
    ("E2", "end", lambda c: c["heading"] != "none" and c["next_boundary"] == "top_level_mid_page", "END=page_of_next_heading_(MD&A_text_precedes_it_on_that_page)"),
    ("E3", "end", lambda c: c["heading"] != "none" and c["next_boundary"] == "annexure_top_level", "END=page_before_annexure_heading_or_its_page_if_MD&A_text_precedes"),
    ("E4", "end", lambda c: c["heading"] != "none" and c["next_boundary"] == "end_of_document", "END=last_content_page"),
    ("E5", "end", lambda c: c["heading"] != "none" and c["next_boundary"] == "unclear", "END=AMBIGUOUS_TRANSITION_(record_both_admissible)"),
    # multiplicity
    ("M1", "multiplicity", lambda c: c["n_candidates"] == 1, "SINGLE_PRIMARY"),
    ("M2", "multiplicity", lambda c: c["n_candidates"] >= 2, "PRIMARY_SPAN_RULE_UNRESOLVED"),
    ("M3", "multiplicity", lambda c: c["n_candidates"] == 0, "NO_CANDIDATE"),
    # secondary flags (do not change the primary outcome)
    ("F1", "flag", lambda c: c.get("bilingual"), "FLAG_BILINGUAL_HEADING"),
    ("F2", "flag", lambda c: c.get("toc_page_disagrees"), "FLAG_TOC_BODY_DISAGREE(TOC_ignored)"),
]


def evaluate(case: dict, rules) -> dict:
    out: dict[str, list[str]] = {}
    for rid, dim, pred, res in rules:
        if pred(case):
            out.setdefault(dim, []).append(f"{rid}:{res}")
    return out


def classify(res: dict) -> tuple[str, list[str]]:
    problems = []
    for dim in ("presence", "start", "end", "multiplicity"):
        n = len(res.get(dim, []))
        if n == 0:
            problems.append(f"NO_RULE_FOR_{dim}")
        elif n > 1:
            problems.append(f"CONFLICT_{dim}:{'|'.join(res[dim])}")
    if problems:
        return "RULE_SET_DEFECT", problems
    tags = [res[d][0] for d in ("presence", "start", "end", "multiplicity")]
    text = " ".join(tags)
    if "UNRESOLVED" in text or "AMBIGUOUS" in text or "NOT_ESTABLISHED" in text:
        return "EXPLICIT_UNRESOLVED_OR_AMBIGUOUS", []
    return "DETERMINATE", []


def main():
    rng = random.Random(20260920)
    rows = []
    defects = 0
    for cid, feat in CASES.items():
        base = evaluate(feat, RULES)
        status, problems = classify(base)
        # order independence: shuffled evaluation must give the identical result
        stable = True
        for _ in range(200):
            shuffled = RULES[:]
            rng.shuffle(shuffled)
            r2 = evaluate(feat, shuffled)
            if {k: sorted(v) for k, v in r2.items()} != {k: sorted(v) for k, v in base.items()}:
                stable = False
        if status == "RULE_SET_DEFECT":
            defects += 1
        rows.append({"case": cid, "status": status, "order_independent": stable, "fired": base, "problems": problems})
    summary = {
        "label": "RESEARCH_ONLY_NON_GOLD",
        "n_cases": len(rows),
        "rule_set_defects": defects,
        "explicit_unresolved_or_ambiguous": [r["case"] for r in rows if r["status"] == "EXPLICIT_UNRESOLVED_OR_AMBIGUOUS"],
        "determinate": [r["case"] for r in rows if r["status"] == "DETERMINATE"],
        "all_order_independent": all(r["order_independent"] for r in rows),
        "results": rows,
        "interpretation": "A DETERMINATE/EXPLICIT_UNRESOLVED outcome means the draft rules give one answer or one explicit 'cannot decide' answer; it does NOT show two humans will agree. Agreement must be measured in the pilot on real documents.",
    }
    json.dump(summary, open(os.path.join(HERE, "casebook_rule_check_results.json"), "w", encoding="utf-8"), indent=2, sort_keys=True)
    print(json.dumps({k: v for k, v in summary.items() if k != "results"}, indent=1))
    for r in rows:
        print(r["case"], r["status"], "|", "; ".join(sum(r["fired"].values(), [])) if r["fired"] else "", r["problems"] or "")


if __name__ == "__main__":
    main()
