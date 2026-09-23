"""RESEARCH_ONLY. NOT GOLD. Reads ONLY frozen setup metadata (manifest, corpus inventory).
Opens no PDF, runs no engine, reads no benchmark result, creates no label.

Produces small tables used by the T0.4-GOLD method research documents:
  burden_frozen_counts.csv      unit counts that drive annotation burden
  overlap_interval_widths.csv   Wilson 95% interval half-widths for an agreement proportion
  hash_slice_demo.csv           why an oracle/overlap hash slice needs a seed independent of selection_rank
  analysis_summary.json
"""
from __future__ import annotations

import csv
import hashlib
import json
import math
import os
import statistics
from collections import Counter, defaultdict

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
OUT = os.path.dirname(os.path.abspath(__file__))
manifest = json.load(open(os.path.join(ROOT, "artifacts", "t0_4", "benchmark_manifest.json"), encoding="utf-8"))
A = manifest["track_a"]["units"]
B = manifest["track_b"]["units"]
inv = {r["document_id"]: r for r in csv.DictReader(open(os.path.join(ROOT, "dataset", "corpus_freeze", "corpus_inventory.csv"), encoding="utf-8"))}


def wilson(k: int, n: int, z: float = 1.959964) -> tuple[float, float]:
    if n == 0:
        return (float("nan"), float("nan"))
    p = k / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return (c - h, c + h)


rows = []
# ---- Track A page units
for split in ("FIT", "VALIDATION", "HOLDOUT", "ALL"):
    us = [u for u in A if split == "ALL" or u["split"] == split]
    rows.append(("track_a_pages", split, len(us), ""))
    rows.append(("track_a_documents", split, len({u["document_id"] for u in us}), ""))
    rows.append(("track_a_issuers", split, len({u["issuer_id"] for u in us}), ""))
for k, v in sorted(Counter(u["representation_class"] for u in A).items()):
    rows.append(("track_a_pages_by_representation_class", k, v,
                 "blank => empty reference => CER denominator 0 unless a rule is frozen" if k == "blank" else ""))
for k, v in sorted(Counter(u["sampling_stratum"] for u in A).items()):
    rows.append(("track_a_pages_by_primary_stratum", k, v, ""))
for k, v in sorted(Counter(l for u in A for l in u["condition_labels"]).items()):
    rows.append(("track_a_pages_by_condition_label", k, v, "labels overlap; a page can carry several"))
# ---- Track B document units
prof = [u for u in B if u["input_status"] == "PROFILED_LOCAL_INPUT"]
for split in ("FIT", "VALIDATION", "HOLDOUT", "UNASSIGNED_HISTORICAL", "ALL"):
    us = [u for u in prof if split == "ALL" or u["split"] == split]
    pages = [int(inv[u["document_id"]]["page_count"]) for u in us if (inv[u["document_id"]].get("page_count") or "").isdigit()]
    rows.append(("track_b_annotatable_documents", split, len(us), f"pages total={sum(pages)}; median={statistics.median(pages) if pages else 'NA'}; max={max(pages) if pages else 'NA'}"))
    rows.append(("track_b_issuers_with_annotatable_docs", split, len({u["issuer_id"] for u in us}), ""))
rows.append(("track_b_input_unavailable_documents", "ALL", sum(1 for u in B if u["input_status"] != "PROFILED_LOCAL_INPUT"),
             "no PDF bytes => DocumentGold cannot be annotated; must stay INPUT_UNAVAILABLE in denominators"))
docs_per_issuer = Counter(u["issuer_id"] for u in prof)
rows.append(("track_b_docs_per_issuer", "distribution", "", json.dumps(sorted(Counter(docs_per_issuer.values()).items()))))
with open(os.path.join(OUT, "burden_frozen_counts.csv"), "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f)
    w.writerow(["measure", "group", "value", "note"])
    w.writerows(rows)

# ---- Wilson half-widths: what does an agreement estimate from n double-annotated units support?
wrows = []
for n in (10, 20, 30, 40, 50, 75, 100, 150, 194):
    for p in (0.70, 0.80, 0.90, 0.95):
        k = round(p * n)
        lo, hi = wilson(k, n)
        wrows.append((n, f"{k / n:.3f}", f"{lo:.3f}", f"{hi:.3f}", f"{(hi - lo) / 2:.3f}"))
with open(os.path.join(OUT, "overlap_interval_widths.csv"), "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f)
    w.writerow(["n_double_annotated_units", "observed_proportion", "wilson95_low", "wilson95_high", "half_width"])
    w.writerows(wrows)

# ---- hash slice demo: selection_rank is the MIN over a cell => its leading hex digit is skewed toward 0
lit = {"scanned", "broken_text", "vector_text", "legacy_font_candidate", "native_clean_control"}
sub = [u for u in A if u["split"] in ("FIT", "VALIDATION") and lit & set(u["condition_labels"])]


def frac_0123(hexes):
    return sum(1 for h in hexes if h[0] in "0123") / len(hexes)


demo = []
for label, units in (("all_475_selected_pages", A), ("oracle_literal_subset_79", sub)):
    ranks = [u["selection_rank"] for u in units]
    demo.append((label, len(units), "selection_rank (min-rank-biased)", round(frac_0123(ranks), 4)))
    for seed in ("DEMO_SEED_NOT_FOR_USE_1", "DEMO_SEED_NOT_FOR_USE_2", "DEMO_SEED_NOT_FOR_USE_3"):
        hs = [hashlib.sha256(f"{seed}\0{u['document_id']}\0{u['page_number']}".encode()).hexdigest() for u in units]
        demo.append((label, len(units), f"independent hash, {seed}", round(frac_0123(hs), 4)))
with open(os.path.join(OUT, "hash_slice_demo.csv"), "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f)
    w.writerow(["population", "n_units", "hash_source", "fraction_leading_hex_0_to_3 (nominal 0.25)"])
    w.writerows(demo)
hist = Counter(u["selection_rank"][0] for u in A)

summary = {
    "label": "RESEARCH_ONLY",
    "track_a_pages": len(A), "track_b_units": len(B), "track_b_annotatable_documents": len(prof),
    "oracle_literal_subset_units": len(sub),
    "selection_rank_leading_hex_histogram": dict(sorted(hist.items())),
    "note": "Demonstrative seeds are labelled DEMO_SEED_NOT_FOR_USE: no seed is proposed or frozen here (B4 is an author decision).",
}
json.dump(summary, open(os.path.join(OUT, "analysis_summary.json"), "w", encoding="utf-8"), indent=2, sort_keys=True)
print(json.dumps(summary, indent=1))
print(open(os.path.join(OUT, "hash_slice_demo.csv"), encoding="utf-8").read())
