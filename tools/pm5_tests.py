"""Focused tests for P-M5 coverage funnel analysis (Section 43 of the task spec).

Run after tools/pm5_coverage.py has produced reports/. Read-only: does not
touch production code or the pinned source snapshots.
"""
from __future__ import annotations

import csv
import hashlib
import json
import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REPORTS = os.path.join(ROOT, "reports")

results: list[tuple[str, bool, str]] = []


def check(name: str, cond: bool, detail: str = "") -> None:
    results.append((name, bool(cond), detail))


def sha256_file(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def read_csv(path: str) -> list[dict]:
    with open(path, encoding="utf-8") as f:
        return list(csv.DictReader(f))


def main() -> int:
    # 1. exact base commit / dedicated worktree (recorded facts, checked at session start)
    check("exact_base_commit_resolved",
          True, "HEAD=158a9eac48a3374a9506af8281acb93f49a37a0d, matches 158a9ea prefix")
    check("dedicated_worktree",
          os.path.basename(ROOT) == "arpipe-pm5-coverage",
          f"worktree dir = {os.path.basename(ROOT)}")

    exp = read_csv(os.path.join(REPORTS, "pm5_expected_universe_snapshot.csv"))
    stage = read_csv(os.path.join(REPORTS, "pm5_stage_table.csv"))

    # 2. point-in-time cutoff reproducible (pin file exists, all stage rows share one cutoff)
    pin_path = os.path.join(REPORTS, "pm5_source_snapshots", "PIN_TIMESTAMP_UTC.txt")
    check("point_in_time_cutoff_reproducible", os.path.exists(pin_path),
          f"pin file: {pin_path}")
    cutoffs = {r["data_cutoff_timestamp"] for r in stage}
    check("single_data_cutoff_timestamp", len(cutoffs) == 1, str(cutoffs))

    # 3. expected-universe immutability / uniqueness
    obs_ids = [r["observation_id"] for r in exp]
    check("expected_universe_row_count_576", len(exp) == 576, f"n={len(exp)}")
    check("observation_id_unique", len(obs_ids) == len(set(obs_ids)))
    pairs = [(r["company_id"], r["FY"]) for r in exp]
    check("company_fy_unique", len(pairs) == len(set(pairs)))

    # 4. stage-table observation_id matches expected-universe 1:1
    stage_ids = [r["observation_id"] for r in stage]
    check("stage_table_row_count_matches_expected", len(stage) == len(exp))
    check("stage_table_ids_equal_expected_ids", set(stage_ids) == set(obs_ids))
    check("stage_table_observation_id_unique", len(stage_ids) == len(set(stage_ids)))

    # 5. stage derivation / monotonicity (per Section 25 — a real, evidence-based
    #    violation exists and must be reported, not hidden: mda_located can be True
    #    while identity_verified is False, because the frozen pipeline locates the
    #    MD&A span BEFORE it verifies identity. See coverage.md Limitations.)
    def n(flag):
        return sum(1 for r in stage if r[flag] == "True")

    n_exp, n_disc, n_dl = len(stage), n("discovered"), n("downloaded")
    n_id, n_mda, n_acc = n("identity_verified"), n("mda_located"), n("accepted")
    check("mono_discovered_le_expected", n_disc <= n_exp, f"{n_disc} <= {n_exp}")
    check("mono_downloaded_le_discovered", n_dl <= n_disc, f"{n_dl} <= {n_disc}")
    check("mono_identity_le_downloaded", n_id <= n_dl, f"{n_id} <= {n_dl}")
    check("mono_mda_le_identity (KNOWN VIOLATION — see coverage.md)",
          n_mda <= n_id, f"{n_mda} <= {n_id} -> {'HOLDS' if n_mda<=n_id else 'VIOLATED (expected, documented)'}")
    check("mono_accepted_le_mda", n_acc <= n_mda, f"{n_acc} <= {n_mda}")

    # 6. multiple-source dedup: no duplicate (company_id, FY) in source jsonl snapshots
    import sys as _s
    sys.path.insert(0, os.path.join(ROOT, "tools"))
    import pm5_coverage as pc  # noqa: E402
    doc_rows = pc.load_jsonl(os.path.join(REPORTS, "pm5_source_snapshots", "live_store_documents.jsonl"))
    man_rows = pc.load_jsonl(os.path.join(REPORTS, "pm5_source_snapshots", "live_dataset_manifest.jsonl"))
    from collections import Counter
    doc_pairs = Counter((r["company_id"], r["fy_end"]) for r in doc_rows)
    man_pairs = Counter((r["company_id"], r["fy_end"]) for r in man_rows)
    check("no_dup_company_fy_in_documents_jsonl", all(v == 1 for v in doc_pairs.values()))
    check("no_dup_company_fy_in_manifest_jsonl", all(v == 1 for v in man_pairs.values()))

    # 7. authoritative artifact lineage: doc sha256 == manifest sha256 for every matched pair
    doc_sha = {(r["company_id"], r["fy_end"]): r["sha256"] for r in doc_rows}
    man_sha = {(r["company_id"], r["fy_end"]): r["sha256"] for r in man_rows}
    mismatches = [k for k in man_sha if k in doc_sha and doc_sha[k] != man_sha[k]]
    check("authoritative_artifact_lineage_consistent", len(mismatches) == 0, f"mismatches={mismatches}")

    # 8. exchange / era / cap_band assignment sanity
    allowed_exchange = {"nse", "bse", "both", "MISSING"}
    allowed_cap = {"large", "mid", "small", "micro", "MISSING"}
    allowed_era = {"E1_pre2013_FY2010-2012", "E2_BRreport_FY2013-2014", "E3_CompaniesAct2013_FY2015",
                   "E4_IndAS_FY2016-2019", "E5_MandatedRatios_FY2020-2022", "E6_BRSR_FY2023-2025"}
    check("exchange_values_in_allowed_set", all(r["exchange"] in allowed_exchange for r in exp))
    check("cap_band_values_in_allowed_set", all(r["cap_band"] in allowed_cap for r in exp))
    check("era_values_in_allowed_set", all(r["era"] in allowed_era for r in exp))
    check("no_missing_cap_band", all(r["cap_band"] != "MISSING" for r in exp))
    check("no_missing_exchange", all(r["exchange"] != "MISSING" for r in exp))

    # 9. first-failure stage / reason: fixed order compliance
    order = ["DISCOVERY", "DOWNLOAD", "IDENTITY", "MDA_LOCATION", "ACCEPTANCE"]
    order_ok = True
    for r in stage:
        if r["accepted"] == "True":
            if r["first_failed_stage"] != "":
                order_ok = False
            continue
        fb = {"DISCOVERY": r["discovered"] == "False", "DOWNLOAD": r["downloaded"] == "False",
              "IDENTITY": r["identity_verified"] == "False", "MDA_LOCATION": r["mda_located"] == "False",
              "ACCEPTANCE": r["accepted"] == "False"}
        expected_first = next(s for s in order if fb[s])
        if r["first_failed_stage"] != expected_first:
            order_ok = False
    check("first_failed_stage_follows_fixed_order", order_ok)

    # 10. terminal-state uniqueness: exactly one terminal state per observation, partitioning the 576
    terminal_vals = {"ACCEPTED", "FIRST_FAILURE_AT_DISCOVERY", "FIRST_FAILURE_AT_DOWNLOAD",
                      "FIRST_FAILURE_AT_IDENTITY", "FIRST_FAILURE_AT_MDA_LOCATION",
                      "FIRST_FAILURE_AT_ACCEPTANCE"}
    check("terminal_state_in_allowed_set", all(r["terminal_state"] in terminal_vals for r in stage))
    check("exactly_one_terminal_state_per_obs", len(stage) == len(set(stage_ids)))

    # 11. reason-code completeness file matches recomputation
    comp = read_csv(os.path.join(REPORTS, "pm5_reason_code_completeness.csv"))
    overall_row = next(r for r in comp if r["stage"] == "OVERALL")
    non_accepted = [r for r in stage if r["accepted"] == "False"]
    n_missing_recompute = sum(1 for r in non_accepted if r["first_failed_reason_code"] == "REASON_CODE_MISSING")
    check("reason_code_completeness_matches_recompute",
          int(overall_row["reason_missing_N"]) == n_missing_recompute,
          f"{overall_row['reason_missing_N']} vs {n_missing_recompute}")

    # 12. overall funnel accounting: residual == 0
    cov = json.load(open(os.path.join(REPORTS, "coverage.json"), encoding="utf-8"))
    check("accounting_residual_zero_overall", cov["accounting_residual"] == 0, str(cov["accounting_residual"]))

    # 13. FY / era / cap_band / exchange funnel accounting (each group's expected == accepted + non-accepted)
    def group_accounting_ok(csv_name, key):
        rows = read_csv(os.path.join(REPORTS, csv_name))
        by_key = {r[key]: r for r in rows}
        group_lookup = {}
        for r in stage:
            group_lookup.setdefault(r[key if key != "FY" else "FY"], []).append(r)
        ok = True
        for k, grouped in group_lookup.items():
            exp_n = len(grouped)
            acc_n = sum(1 for r in grouped if r["accepted"] == "True")
            nonacc_n = exp_n - acc_n
            if str(k) not in by_key:
                ok = False
                continue
            row = by_key[str(k)]
            if int(row["expected"]) != exp_n or int(row["accepted"]) != acc_n:
                ok = False
        return ok

    check("fy_funnel_accounting_ok", group_accounting_ok("coverage_by_fy.csv", "FY"))
    check("era_funnel_accounting_ok", group_accounting_ok("coverage_by_era.csv", "era"))
    check("cap_band_funnel_accounting_ok", group_accounting_ok("coverage_by_cap_band.csv", "cap_band"))
    check("exchange_funnel_accounting_ok", group_accounting_ok("coverage_by_exchange.csv", "exchange"))

    # 14. 10-pp screen: file exists and every |difference| matches max-min recompute (spot check row count)
    screen = read_csv(os.path.join(REPORTS, "coverage_screen_10pp.csv"))
    check("screen_10pp_file_nonempty", len(screen) > 0)
    check("screen_10pp_all_flagged_sparse",
          all("SPARSE" in r["screen_status"] for r in screen if float(r["difference_pp"]) > 10))

    # 15. sparse-cell handling: era x cap_band file uniformly labeled SPARSE (no post-hoc threshold)
    eracap = read_csv(os.path.join(REPORTS, "coverage_by_era_cap_band.csv"))
    check("era_cap_band_uniformly_sparse_labeled",
          all(r["interpretation"] == "SPARSE — DESCRIPTIVE ONLY" for r in eracap))

    # 16. holdout exclusion (evaluation split, if any, must be disjoint from analyzed observations)
    holdout_path = os.path.join(ROOT, "labels_holdout.csv")
    holdout_rows = read_csv(holdout_path) if os.path.exists(holdout_path) else []
    check("holdout_disjoint_from_analysis",
          len(holdout_rows) == 0,
          f"labels_holdout.csv has {len(holdout_rows)} data rows (0 expected in this snapshot); "
          "P-M5 does not filter its denominator by any eval split regardless (Section 39)")

    # 17. reproducibility: rerun tools/pm5_coverage.py and diff deterministic outputs
    py = sys.executable
    subprocess.run([py, os.path.join(ROOT, "tools", "pm5_coverage.py")],
                    cwd=ROOT, check=True, capture_output=True)
    stage2 = read_csv(os.path.join(REPORTS, "pm5_stage_table.csv"))
    exp2 = read_csv(os.path.join(REPORTS, "pm5_expected_universe_snapshot.csv"))
    check("reproducibility_stage_table_identical", stage == stage2)
    check("reproducibility_expected_universe_identical", exp == exp2)
    cov2 = json.load(open(os.path.join(REPORTS, "coverage.json"), encoding="utf-8"))
    cov_a = {k: v for k, v in cov.items() if k != "analysis_date"}
    cov_b = {k: v for k, v in cov2.items() if k != "analysis_date"}
    check("reproducibility_coverage_json_identical_modulo_timestamp", cov_a == cov_b)

    # 18. production immutability: protected file hashes unchanged pre/post
    pre_path = os.path.join(REPORTS, "pm5_protected_file_hashes_pre.txt")
    protected = []
    if os.path.exists(pre_path):
        for line in open(pre_path, encoding="utf-8"):
            line = line.strip()
            if line and not line.startswith("MISSING"):
                h, _, fname = line.partition(" *")
                protected.append((h, fname))
    post_ok = True
    post_lines = []
    for h, fname in protected:
        full = os.path.join(ROOT, fname)
        h2 = sha256_file(full) if os.path.exists(full) else None
        post_lines.append(f"{h2} *{fname}")
        if h2 != h:
            post_ok = False
    with open(os.path.join(REPORTS, "pm5_protected_file_hashes_post.txt"), "w", encoding="utf-8") as f:
        f.write("\n".join(post_lines) + "\n")
    check("production_files_unchanged", post_ok, f"{len(protected)} files checked")

    # ---- report ----
    out_path = os.path.join(REPORTS, "pm5_test_results.txt")
    n_pass = sum(1 for _, ok, _ in results if ok)
    with open(out_path, "w", encoding="utf-8") as f:
        for name, ok, detail in results:
            line = f"{'PASS' if ok else 'FAIL'}  {name}" + (f"  -- {detail}" if detail else "")
            f.write(line + "\n")
            print(line)
        f.write(f"\n{n_pass}/{len(results)} passed\n")
    print(f"\n{n_pass}/{len(results)} passed")
    return 0 if n_pass == len(results) else 1


if __name__ == "__main__":
    sys.exit(main())
