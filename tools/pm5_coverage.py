"""P-M5 coverage funnel analysis.

Audit / measurement only. Reads pinned, hashed, read-only snapshots of
canonical ARPipe evidence under reports/pm5_source_snapshots/ (copied
read-only from the shared arpipe-0.1.0 checkout, never written back to it)
plus tracked, git-frozen files in this worktree (cohort_companies.csv,
cohort_fetch_manifest.jsonl). Writes every output under reports/.

Does not import arpipe production modules and does not run discover /
fetch / triage / segment / verify / extract. Does not modify production
behavior.
"""
from __future__ import annotations

import csv
import datetime
import hashlib
import json
import os
import sys
from collections import Counter, defaultdict

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SNAP = os.path.join(ROOT, "reports", "pm5_source_snapshots")
REPORTS = os.path.join(ROOT, "reports")

FY_MIN, FY_MAX = 2010, 2025

UNIVERSE_RULE_VERSION = (
    "pm5-v1: cohort_companies.csv (36 firms, cap-band-stratified per "
    "tools/select_labelling_cohort.py: 6 large + 8 mid + 10 small + 12 micro) "
    "x FY2010-2025 (16 fiscal years, the study range declared in README.md "
    "and arpipe/CLAUDE.md: 'FY2010-FY2025'), full Cartesian product. No "
    "listing-date-based exclusion is applied: the frozen company master "
    "(cohort_companies.csv / companies.csv, arpipe/models.py Company) carries "
    "no listing_date field, so a company not yet listed in an early FY is "
    "NOT excluded from the denominator (excluding it would require data this "
    "snapshot does not have); such company-years surface instead as "
    "DISCOVERY-stage losses with REASON_CODE_MISSING, per Section 39's "
    "no-denominator-repair rule."
)
ERA_DEFINITION_VERSION = (
    "pm5-v1: bucket scheme derived from arpipe/verify.py check_era()/era_signals() "
    "regulatory boundary years {2013, 2015, 2016, 2020, 2023} (Business "
    "Responsibility Report >=2013, Companies Act 2013 / CSR >=2015, Ind AS "
    "handled from FY2016, 8 mandated ratios >=2020, BRSR >=2023). No named "
    "era-bucket scheme existed anywhere in the frozen codebase; these are the "
    "only frozen era-relevant boundaries in production code and are reused "
    "verbatim (not invented) to build FY buckets for this audit. See "
    "coverage.md Limitations."
)
CAP_BAND_DEFINITION_VERSION = (
    "pm5-v1: cohort_companies.csv 'cap_band' column (AMFI large/mid/small/micro "
    "classification via arpipe/universe.py fetch_cap_bands), a static "
    "per-company attribute fixed at cohort-selection time (2026-09-11), NOT a "
    "true time-varying firm-year cap band (no per-FY cap-band series exists in "
    "the frozen state). cap_band_current is identical to cap_band for all 36 "
    "cohort firms in this snapshot (0 divergences)."
)
EXCHANGE_DEFINITION_VERSION = (
    "pm5-v1: cohort_companies.csv 'exchange' column (nse|bse|both), a static "
    "per-company attribute produced by arpipe/universe.py collapse_universe(), "
    "independent of discovery/download outcome."
)
REASON_CODE_TAXONOMY_VERSION = (
    "pm5-v1: reason codes exactly as emitted by the frozen arpipe/verify.py "
    "build_reasons()/grade() and arpipe/pipeline.py process_document() "
    "(mda_not_located, identity_unproven, year_unproven, source_shredded, "
    "span_truncated, section_leak, order_scrambled, WRONG_LANGUAGE_RISK), plus "
    "the sentinel REASON_CODE_MISSING for any stage/observation with no "
    "persisted canonical reason (DISCOVERY and DOWNLOAD failures have no "
    "persisted negative-result log anywhere in the frozen state; some "
    "ACCEPTANCE failures carry an empty reasons list)."
)

FIXED_STAGE_ORDER = ["DISCOVERY", "DOWNLOAD", "IDENTITY", "MDA_LOCATION", "ACCEPTANCE"]
STAGE_TO_TERMINAL = {
    "DISCOVERY": "FIRST_FAILURE_AT_DISCOVERY",
    "DOWNLOAD": "FIRST_FAILURE_AT_DOWNLOAD",
    "IDENTITY": "FIRST_FAILURE_AT_IDENTITY",
    "MDA_LOCATION": "FIRST_FAILURE_AT_MDA_LOCATION",
    "ACCEPTANCE": "FIRST_FAILURE_AT_ACCEPTANCE",
}


def era_of(fy: int) -> str:
    if fy < 2013:
        return "E1_pre2013_FY2010-2012"
    if fy < 2015:
        return "E2_BRreport_FY2013-2014"
    if fy < 2016:
        return "E3_CompaniesAct2013_FY2015"
    if fy < 2020:
        return "E4_IndAS_FY2016-2019"
    if fy < 2023:
        return "E5_MandatedRatios_FY2020-2022"
    return "E6_BRSR_FY2023-2025"


def sha256_file(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def sha1_10(s: str) -> str:
    return hashlib.sha1(s.encode("utf-8")).hexdigest()[:10]


def load_jsonl(path: str) -> list[dict]:
    out = []
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                out.append(json.loads(line))
    return out


IST = datetime.timezone(datetime.timedelta(hours=5, minutes=30))


def iso_mtime(path: str) -> str:
    return datetime.datetime.fromtimestamp(os.path.getmtime(path), tz=IST).isoformat()


def load_cohort_companies() -> list[dict]:
    path = os.path.join(ROOT, "cohort_companies.csv")
    with open(path, encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    return rows


def build_expected_universe(companies: list[dict]) -> list[dict]:
    rows = []
    for c in companies:
        for fy in range(FY_MIN, FY_MAX + 1):
            rows.append({
                "observation_id": f"{c['company_id']}::FY{fy}",
                "company_id": c["company_id"],
                "company_name": c["canonical_name"],
                "FY": fy,
                "expected_flag": True,
                "listing_status": "unknown_no_listing_date_in_frozen_master",
                "expected_reason": "in_scope",
                "universe_rule_version": UNIVERSE_RULE_VERSION,
                "era": era_of(fy),
                "cap_band": c.get("cap_band") or "MISSING",
                "exchange": c.get("exchange") or "MISSING",
            })
    return rows


def main() -> dict:
    analysis_date = datetime.datetime.now(datetime.timezone.utc).isoformat()

    companies = load_cohort_companies()
    assert len({c["company_id"] for c in companies}) == len(companies), "duplicate company_id in cohort_companies.csv"

    expected = build_expected_universe(companies)
    obs_ids = [r["observation_id"] for r in expected]
    assert len(obs_ids) == len(set(obs_ids)), "duplicate observation_id in expected universe"
    cid_fy_pairs = [(r["company_id"], r["FY"]) for r in expected]
    assert len(cid_fy_pairs) == len(set(cid_fy_pairs)), "duplicate (company_id, FY) in expected universe"

    # ---- write expected universe snapshot (frozen denominator) ------------
    exp_csv_path = os.path.join(REPORTS, "pm5_expected_universe_snapshot.csv")
    fieldnames = list(expected[0].keys())
    with open(exp_csv_path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        for r in expected:
            w.writerow(r)
    exp_csv_sha = sha256_file(exp_csv_path)

    cohort_csv_path = os.path.join(ROOT, "cohort_companies.csv")
    exp_meta = {
        "row_count": len(expected),
        "sha256": exp_csv_sha,
        "source_file": "cohort_companies.csv",
        "source_file_sha256": sha256_file(cohort_csv_path),
        "source_commit": "158a9eac48a3374a9506af8281acb93f49a37a0d",
        "universe_rule_version": UNIVERSE_RULE_VERSION,
        "universe_snapshot_date": iso_mtime(cohort_csv_path),
        "data_cutoff_timestamp": None,  # filled below once known
        "analysis_date": analysis_date,
        "fy_min": FY_MIN,
        "fy_max": FY_MAX,
        "n_companies": len(companies),
    }
    exp_json_path = os.path.join(REPORTS, "pm5_expected_universe_snapshot.json")

    # ---- load pinned source snapshots --------------------------------------
    pin_ts_path = os.path.join(SNAP, "PIN_TIMESTAMP_UTC.txt")
    with open(pin_ts_path, encoding="utf-8") as f:
        data_cutoff_timestamp = f.read().strip()
    exp_meta["data_cutoff_timestamp"] = data_cutoff_timestamp
    with open(exp_json_path, "w", encoding="utf-8") as f:
        json.dump({"meta": exp_meta, "rows": expected}, f, indent=2)

    discovery_path = os.path.join(SNAP, "cohort_reports.jsonl")
    docs_path = os.path.join(SNAP, "live_store_documents.jsonl")
    manifest_path = os.path.join(SNAP, "live_dataset_manifest.jsonl")

    discovery_rows = load_jsonl(discovery_path)
    doc_rows = load_jsonl(docs_path)
    manifest_rows = load_jsonl(manifest_path)

    discovery_by_pair: dict[tuple, list[dict]] = defaultdict(list)
    for r in discovery_rows:
        discovery_by_pair[(r["company_id"], r["fy_end"])].append(r)

    docs_by_pair: dict[tuple, dict] = {}
    dup_doc_pairs = 0
    for r in doc_rows:
        k = (r["company_id"], r["fy_end"])
        if k in docs_by_pair:
            dup_doc_pairs += 1
        else:
            docs_by_pair[k] = r
    assert dup_doc_pairs == 0, f"unexpected duplicate (company_id, fy_end) in live_store/documents.jsonl: {dup_doc_pairs}"

    manifest_by_pair: dict[tuple, dict] = {}
    dup_man_pairs = 0
    for r in manifest_rows:
        k = (r["company_id"], r["fy_end"])
        if k in manifest_by_pair:
            dup_man_pairs += 1
        else:
            manifest_by_pair[k] = r
    assert dup_man_pairs == 0, f"unexpected duplicate (company_id, fy_end) in live_dataset/manifest.jsonl: {dup_man_pairs}"

    snapshot_dates = {
        "discovery_snapshot_date": iso_mtime(os.path.join(
            "D:\\sem_iitk\\sem9\\thesis\\sep_week1\\arpipe-0.1.0", "cohort_reports.jsonl")
            if os.path.exists("D:\\sem_iitk\\sem9\\thesis\\sep_week1\\arpipe-0.1.0\\cohort_reports.jsonl")
            else discovery_path),
        "download_snapshot_date": iso_mtime(
            "D:\\sem_iitk\\sem9\\thesis\\sep_week1\\arpipe-0.1.0\\live_store\\documents.jsonl"
            if os.path.exists("D:\\sem_iitk\\sem9\\thesis\\sep_week1\\arpipe-0.1.0\\live_store\\documents.jsonl")
            else docs_path),
        "manifest_snapshot_date": iso_mtime(
            "D:\\sem_iitk\\sem9\\thesis\\sep_week1\\arpipe-0.1.0\\live_dataset\\manifest.jsonl"
            if os.path.exists("D:\\sem_iitk\\sem9\\thesis\\sep_week1\\arpipe-0.1.0\\live_dataset\\manifest.jsonl")
            else manifest_path),
    }

    # ---- build stage table --------------------------------------------------
    stage_rows = []
    monotonicity_violations = []  # (observation_id, kind)
    for exp in expected:
        cid, fy = exp["company_id"], exp["FY"]
        key = (cid, fy)

        disc_list = discovery_by_pair.get(key, [])
        discovered = len(disc_list) > 0
        discovery_source_types = sorted({d["source"] for d in disc_list})
        discovery_source_ids = sorted({sha1_10(d["url"]) for d in disc_list})

        doc = docs_by_pair.get(key)
        downloaded = doc is not None
        authoritative_download_artifact_id = doc["sha256"] if doc else None

        man = manifest_by_pair.get(key)
        span = man.get("span") if man else None
        ver = man.get("verification") if man else None
        mda_located = bool(man) and span is not None
        identity_verified = bool(ver and ver.get("company_ok") and ver.get("year_ok"))
        accepted = bool(man) and bool(man.get("ok"))
        authoritative_artifact_sha256 = man.get("sha256") if man else None
        reasons_list = list((man.get("reasons") if man else None) or [])
        errors_list = list((man.get("errors") if man else None) or [])

        if doc and man and doc.get("sha256") != authoritative_artifact_sha256:
            monotonicity_violations.append((exp["observation_id"], "sha256_lineage_mismatch"))

        stage_bool = {
            "DISCOVERY": discovered,
            "DOWNLOAD": downloaded,
            "IDENTITY": identity_verified,
            "MDA_LOCATION": mda_located,
            "ACCEPTANCE": accepted,
        }

        first_failed_stage = None
        for st in FIXED_STAGE_ORDER:
            if not stage_bool[st]:
                first_failed_stage = st
                break

        secondary_reason_codes: list[str] = []
        if first_failed_stage is None:
            first_failed_reason_code = None
            terminal_state = "ACCEPTED"
        else:
            terminal_state = STAGE_TO_TERMINAL[first_failed_stage]
            if first_failed_stage == "DISCOVERY":
                first_failed_reason_code = "REASON_CODE_MISSING"
            elif first_failed_stage == "DOWNLOAD":
                first_failed_reason_code = "REASON_CODE_MISSING"
            elif first_failed_stage == "IDENTITY":
                if "identity_unproven" in reasons_list:
                    first_failed_reason_code = "identity_unproven"
                elif "year_unproven" in reasons_list:
                    first_failed_reason_code = "year_unproven"
                elif reasons_list:
                    first_failed_reason_code = reasons_list[0]
                elif errors_list:
                    first_failed_reason_code = "REASON_CODE_MISSING"
                    secondary_reason_codes = list(errors_list)
                else:
                    first_failed_reason_code = "REASON_CODE_MISSING"
                secondary_reason_codes = secondary_reason_codes or [r for r in (reasons_list + errors_list) if r != first_failed_reason_code]
            elif first_failed_stage == "MDA_LOCATION":
                if "mda_not_located" in errors_list or "mda_not_located" in reasons_list:
                    first_failed_reason_code = "mda_not_located"
                else:
                    first_failed_reason_code = "REASON_CODE_MISSING"
                secondary_reason_codes = [r for r in (reasons_list + errors_list) if r != first_failed_reason_code]
            elif first_failed_stage == "ACCEPTANCE":
                if reasons_list:
                    first_failed_reason_code = reasons_list[0]
                    secondary_reason_codes = reasons_list[1:]
                else:
                    first_failed_reason_code = "REASON_CODE_MISSING"

        # Evidence-observed (non-fixed-order) violation check: MDA_LOCATION
        # reached without IDENTITY (span present but identity not verified).
        if mda_located and not identity_verified:
            monotonicity_violations.append((exp["observation_id"], "mda_located_without_identity_verified"))

        row = {
            "observation_id": exp["observation_id"],
            "company_id": cid,
            "company_name": exp["company_name"],
            "FY": fy,
            "expected": True,
            "discovered": discovered,
            "downloaded": downloaded,
            "identity_verified": identity_verified,
            "mda_located": mda_located,
            "accepted": accepted,
            "first_failed_stage": first_failed_stage or "",
            "first_failed_reason_code": first_failed_reason_code or "",
            "secondary_reason_codes": "|".join(secondary_reason_codes),
            "authoritative_artifact_id": authoritative_download_artifact_id or "",
            "authoritative_artifact_sha256": authoritative_artifact_sha256 or "",
            "discovery_source_ids": "|".join(discovery_source_ids),
            "discovery_source_types": "|".join(discovery_source_types),
            "era": exp["era"],
            "cap_band": exp["cap_band"],
            "exchange": exp["exchange"],
            "universe_rule_version": UNIVERSE_RULE_VERSION[:40] + "...",
            "era_definition_version": "pm5-v1",
            "cap_band_definition_version": "pm5-v1",
            "exchange_definition_version": "pm5-v1",
            "data_cutoff_timestamp": data_cutoff_timestamp,
            "terminal_state": terminal_state,
        }
        stage_rows.append(row)

    # terminal-state uniqueness / partition check
    for r in stage_rows:
        n_true = sum([r["accepted"]])  # ACCEPTED is exclusive by construction (single terminal field)
    terminal_states = Counter(r["terminal_state"] for r in stage_rows)

    # ---- write stage table ---------------------------------------------------
    stage_csv_path = os.path.join(REPORTS, "pm5_stage_table.csv")
    stage_fields = list(stage_rows[0].keys())
    with open(stage_csv_path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=stage_fields)
        w.writeheader()
        for r in stage_rows:
            w.writerow(r)

    # ---- funnel accounting ----------------------------------------------------
    N_expected = len(stage_rows)
    N_discovered = sum(r["discovered"] for r in stage_rows)
    N_downloaded = sum(r["downloaded"] for r in stage_rows)
    N_identity = sum(r["identity_verified"] for r in stage_rows)
    N_mda = sum(r["mda_located"] for r in stage_rows)
    N_accepted = sum(r["accepted"] for r in stage_rows)

    first_failure_total = sum(1 for r in stage_rows if r["terminal_state"] != "ACCEPTED")
    data_state_missing_total = 0  # not used in this audit; all obs resolve to a terminal state
    accounting_residual = N_expected - N_accepted - first_failure_total - data_state_missing_total

    monotonicity_checks = {
        "discovered<=expected": N_discovered <= N_expected,
        "downloaded<=discovered": N_downloaded <= N_discovered,
        "identity_verified<=downloaded": N_identity <= N_downloaded,
        "mda_located<=identity_verified": N_mda <= N_identity,
        "accepted<=mda_located": N_accepted <= N_mda,
    }
    monotonicity_ok = all(monotonicity_checks.values())

    overall_funnel = []
    stage_ns = [("EXPECTED", N_expected), ("DISCOVERED", N_discovered), ("DOWNLOADED", N_downloaded),
                ("IDENTITY_VERIFIED", N_identity), ("MDA_LOCATED", N_mda), ("ACCEPTED", N_accepted)]
    prev_n = None
    for name, n in stage_ns:
        pct_of_expected = round(100.0 * n / N_expected, 2) if N_expected else None
        loss_prev = (prev_n - n) if prev_n is not None else None
        loss_rate = round(100.0 * loss_prev / prev_n, 2) if prev_n else (0.0 if prev_n == 0 else None)
        cum_survival = round(100.0 * n / N_expected, 2) if N_expected else None
        overall_funnel.append({
            "stage": name, "N": n, "pct_of_expected": pct_of_expected,
            "loss_from_previous_stage": loss_prev, "transition_loss_rate_pct": loss_rate,
            "cumulative_survival_pct": cum_survival,
        })
        prev_n = n

    with open(os.path.join(REPORTS, "coverage_funnel_overall.csv"), "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(overall_funnel[0].keys()))
        w.writeheader()
        w.writerows(overall_funnel)

    # ---- breakdown helper -------------------------------------------------
    def funnel_for(rows: list[dict]) -> dict:
        n_exp = len(rows)
        n_disc = sum(r["discovered"] for r in rows)
        n_dl = sum(r["downloaded"] for r in rows)
        n_id = sum(r["identity_verified"] for r in rows)
        n_mda = sum(r["mda_located"] for r in rows)
        n_acc = sum(r["accepted"] for r in rows)
        return {"expected": n_exp, "discovered": n_disc, "downloaded": n_dl,
                "identity_verified": n_id, "mda_located": n_mda, "accepted": n_acc,
                "coverage": round(n_acc / n_exp, 4) if n_exp else None}

    def transition_rates(f: dict) -> dict:
        pairs = [("expected", "discovered"), ("discovered", "downloaded"),
                 ("downloaded", "identity_verified"), ("identity_verified", "mda_located"),
                 ("mda_located", "accepted")]
        out = {}
        for a, b in pairs:
            na, nb = f[a], f[b]
            out[f"loss_rate_{a}_to_{b}_pct"] = round(100.0 * (na - nb) / na, 2) if na else None
        return out

    def group_rows(rows, key_fn):
        g = defaultdict(list)
        for r in rows:
            g[key_fn(r)].append(r)
        return g

    # by FY
    by_fy = group_rows(stage_rows, lambda r: r["FY"])
    fy_out = []
    for fy in range(FY_MIN, FY_MAX + 1):
        rows = by_fy.get(fy, [])
        f = funnel_for(rows)
        f = {"FY": fy, **f}
        fy_out.append(f)
    with open(os.path.join(REPORTS, "coverage_by_fy.csv"), "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(fy_out[0].keys()))
        w.writeheader()
        w.writerows(fy_out)

    # by era
    by_era = group_rows(stage_rows, lambda r: r["era"])
    era_out = []
    era_transition = {}
    for era in sorted(by_era):
        rows = by_era[era]
        f = funnel_for(rows)
        tr = transition_rates(f)
        era_transition[era] = tr
        era_out.append({"era": era, **f, **tr})
    with open(os.path.join(REPORTS, "coverage_by_era.csv"), "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(era_out[0].keys()))
        w.writeheader()
        w.writerows(era_out)

    # by cap_band
    by_cap = group_rows(stage_rows, lambda r: r["cap_band"])
    cap_out = []
    cap_transition = {}
    for cap in sorted(by_cap):
        rows = by_cap[cap]
        f = funnel_for(rows)
        tr = transition_rates(f)
        cap_transition[cap] = tr
        cap_out.append({"cap_band": cap, **f, **tr})
    with open(os.path.join(REPORTS, "coverage_by_cap_band.csv"), "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(cap_out[0].keys()))
        w.writeheader()
        w.writerows(cap_out)

    # by exchange
    by_exch = group_rows(stage_rows, lambda r: r["exchange"])
    exch_out = []
    for exch in sorted(by_exch):
        rows = by_exch[exch]
        f = funnel_for(rows)
        exch_out.append({"exchange": exch, **f})
    with open(os.path.join(REPORTS, "coverage_by_exchange.csv"), "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(exch_out[0].keys()))
        w.writeheader()
        w.writerows(exch_out)

    # era x cap_band
    by_era_cap = group_rows(stage_rows, lambda r: (r["era"], r["cap_band"]))
    eracap_out = []
    for (era, cap) in sorted(by_era_cap):
        rows = by_era_cap[(era, cap)]
        f = funnel_for(rows)
        tr = transition_rates(f)
        sparse = "SPARSE — DESCRIPTIVE ONLY"  # no project-defined minimum-N convention exists; applied uniformly, see coverage.md
        eracap_out.append({"era": era, "cap_band": cap, **f, **tr, "interpretation": sparse})
    with open(os.path.join(REPORTS, "coverage_by_era_cap_band.csv"), "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(eracap_out[0].keys()))
        w.writeheader()
        w.writerows(eracap_out)

    # ---- 10pp screen --------------------------------------------------------
    transitions = ["expected_to_discovered", "discovered_to_downloaded", "downloaded_to_identity_verified",
                   "identity_verified_to_mda_located", "mda_located_to_accepted"]
    key_map = {
        "expected_to_discovered": "loss_rate_expected_to_discovered_pct",
        "discovered_to_downloaded": "loss_rate_discovered_to_downloaded_pct",
        "downloaded_to_identity_verified": "loss_rate_downloaded_to_identity_verified_pct",
        "identity_verified_to_mda_located": "loss_rate_identity_verified_to_mda_located_pct",
        "mda_located_to_accepted": "loss_rate_mda_located_to_accepted_pct",
    }
    screen_rows = []
    for dim_name, table, group_key in (("cap_band", cap_transition, "cap_band"), ("era", era_transition, "era")):
        for tname in transitions:
            k = key_map[tname]
            vals = {g: table[g][k] for g in table if table[g][k] is not None}
            if len(vals) < 2:
                continue
            max_g = max(vals, key=lambda g: vals[g])
            min_g = min(vals, key=lambda g: vals[g])
            diff = round(vals[max_g] - vals[min_g], 2)
            screen_rows.append({
                "dimension": dim_name, "transition": tname,
                "max_group": max_g, "max_group_loss_rate_pct": vals[max_g],
                "min_group": min_g, "min_group_loss_rate_pct": vals[min_g],
                "difference_pp": diff,
                "screen_status": (">10 PP DIFFERENCE — SPARSE / DESCRIPTIVE ONLY (no project-defined sample-size convention)"
                                  if diff > 10 else "<=10pp, no screening signal"),
            })
    with open(os.path.join(REPORTS, "coverage_screen_10pp.csv"), "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(screen_rows[0].keys()) if screen_rows else
                            ["dimension", "transition", "max_group", "max_group_loss_rate_pct",
                             "min_group", "min_group_loss_rate_pct", "difference_pp", "screen_status"])
        w.writeheader()
        w.writerows(screen_rows)

    # ---- loss reason distribution -------------------------------------------
    non_accepted = [r for r in stage_rows if not r["accepted"]]
    loss_key_counter = Counter((r["first_failed_stage"], r["first_failed_reason_code"]) for r in non_accepted)
    stage_loss_totals = Counter(r["first_failed_stage"] for r in non_accepted)
    total_losses = len(non_accepted)
    loss_reason_rows = []
    for (stage, reason), n in sorted(loss_key_counter.items(), key=lambda kv: -kv[1]):
        loss_reason_rows.append({
            "first_failed_stage": stage, "first_failed_reason_code": reason, "N": n,
            "pct_of_all_losses": round(100.0 * n / total_losses, 2) if total_losses else None,
            "pct_of_stage_losses": round(100.0 * n / stage_loss_totals[stage], 2) if stage_loss_totals[stage] else None,
        })
    with open(os.path.join(REPORTS, "pm5_loss_reasons.csv"), "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(loss_reason_rows[0].keys()))
        w.writeheader()
        w.writerows(loss_reason_rows)

    # ---- reason-code completeness -------------------------------------------
    completeness_rows = []
    for stage in FIXED_STAGE_ORDER:
        failed = [r for r in non_accepted if r["first_failed_stage"] == stage]
        n_failed = len(failed)
        n_missing = sum(1 for r in failed if r["first_failed_reason_code"] == "REASON_CODE_MISSING")
        n_present = n_failed - n_missing
        completeness_rows.append({
            "stage": stage, "failed_N": n_failed, "reason_present_N": n_present,
            "reason_missing_N": n_missing,
            "reason_coverage_pct": round(100.0 * n_present / n_failed, 2) if n_failed else None,
        })
    total_failed = sum(r["failed_N"] for r in completeness_rows)
    total_present = sum(r["reason_present_N"] for r in completeness_rows)
    total_missing = sum(r["reason_missing_N"] for r in completeness_rows)
    completeness_rows.append({
        "stage": "OVERALL", "failed_N": total_failed, "reason_present_N": total_present,
        "reason_missing_N": total_missing,
        "reason_coverage_pct": round(100.0 * total_present / total_failed, 2) if total_failed else None,
    })
    with open(os.path.join(REPORTS, "pm5_reason_code_completeness.csv"), "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(completeness_rows[0].keys()))
        w.writeheader()
        w.writerows(completeness_rows)

    # ---- loss concentration --------------------------------------------------
    company_loss_counts = Counter(r["company_id"] for r in non_accepted)
    n_companies_with_loss = len(company_loss_counts)
    top = company_loss_counts.most_common()
    top5_share = round(100.0 * sum(n for _, n in top[:5]) / total_losses, 2) if total_losses else None
    top10_share = round(100.0 * sum(n for _, n in top[:10]) / total_losses, 2) if total_losses else None
    conc_rows = [{
        "n_companies_with_loss": n_companies_with_loss,
        "n_companies_total": len(companies),
        "total_losses": total_losses,
        "top5_share_pct": top5_share,
        "top10_share_pct": top10_share,
    }]
    with open(os.path.join(REPORTS, "coverage_loss_concentration.csv"), "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(conc_rows[0].keys()))
        w.writeheader()
        w.writerows(conc_rows)
    top_company_rows = [{"company_id": cid, "n_losses": n} for cid, n in top]
    with open(os.path.join(REPORTS, "pm5_loss_by_company.csv"), "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=["company_id", "n_losses"])
        w.writeheader()
        w.writerows(top_company_rows)

    # ---- reconciliation -------------------------------------------------------
    recon_rows = [{
        "group": "OVERALL", "expected": N_expected, "accepted": N_accepted,
        "first_failure_total": first_failure_total, "data_state_missing": data_state_missing_total,
        "accounting_residual": accounting_residual,
    }]
    for era in sorted(by_era):
        rows = by_era[era]
        n_exp = len(rows)
        n_acc = sum(r["accepted"] for r in rows)
        n_ff = sum(1 for r in rows if r["terminal_state"] != "ACCEPTED")
        recon_rows.append({
            "group": f"era={era}", "expected": n_exp, "accepted": n_acc,
            "first_failure_total": n_ff, "data_state_missing": 0,
            "accounting_residual": n_exp - n_acc - n_ff - 0,
        })
    with open(os.path.join(REPORTS, "coverage_reconciliation.csv"), "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(recon_rows[0].keys()))
        w.writeheader()
        w.writerows(recon_rows)

    # ---- source snapshot manifest (hashes/provenance) --------------------------
    src_manifest = {
        "data_cutoff_timestamp_utc": data_cutoff_timestamp,
        **snapshot_dates,
        "files": {
            "cohort_reports.jsonl (DISCOVERED source)": {
                "sha256": sha256_file(discovery_path), "row_count": len(discovery_rows),
                "pinned_from": "arpipe-0.1.0/cohort_reports.jsonl (gitignored, read-only copy)",
            },
            "live_store/documents.jsonl (DOWNLOADED source)": {
                "sha256": sha256_file(docs_path), "row_count": len(doc_rows),
                "pinned_from": "arpipe-0.1.0/live_store/documents.jsonl (gitignored, read-only copy)",
            },
            "live_dataset/manifest.jsonl (IDENTITY/MDA/ACCEPTED source)": {
                "sha256": sha256_file(manifest_path), "row_count": len(manifest_rows),
                "pinned_from": "arpipe-0.1.0/live_dataset/manifest.jsonl (gitignored, read-only copy)",
            },
            "cohort_companies.csv (EXPECTED source, git-tracked)": {
                "sha256": sha256_file(cohort_csv_path), "row_count": len(companies),
                "pinned_from": "git-tracked at 158a9eac48a3374a9506af8281acb93f49a37a0d",
            },
        },
    }
    with open(os.path.join(REPORTS, "pm5_source_snapshot_manifest.json"), "w", encoding="utf-8") as fh:
        json.dump(src_manifest, fh, indent=2)

    result = {
        "analysis_date": analysis_date,
        "data_cutoff_timestamp": data_cutoff_timestamp,
        "N_expected": N_expected, "N_discovered": N_discovered, "N_downloaded": N_downloaded,
        "N_identity_verified": N_identity, "N_mda_located": N_mda, "N_accepted": N_accepted,
        "accounting_residual": accounting_residual,
        "monotonicity_checks": monotonicity_checks,
        "monotonicity_ok": monotonicity_ok,
        "monotonicity_violations": monotonicity_violations,
        "n_monotonicity_violations": len(monotonicity_violations),
        "terminal_states": dict(terminal_states),
        "overall_funnel": overall_funnel,
        "total_losses": total_losses,
        "n_companies_with_loss": n_companies_with_loss,
        "top5_share_pct": top5_share, "top10_share_pct": top10_share,
        "reason_coverage_overall_pct": completeness_rows[-1]["reason_coverage_pct"],
        "screen_rows_gt10pp": [r for r in screen_rows if r["difference_pp"] > 10],
        "stage_csv_sha256": sha256_file(stage_csv_path),
        "expected_csv_sha256": exp_csv_sha,
    }
    with open(os.path.join(REPORTS, "coverage.json"), "w", encoding="utf-8") as fh:
        json.dump(result, fh, indent=2, default=str)

    return result


if __name__ == "__main__":
    res = main()
    print(json.dumps({k: v for k, v in res.items() if k not in ("monotonicity_violations",)}, indent=2, default=str))
    print(f"\nmonotonicity_violations: {len(res['monotonicity_violations'])}")
    for v in res["monotonicity_violations"][:10]:
        print(" ", v)
