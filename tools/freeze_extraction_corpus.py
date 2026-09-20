"""T0: freeze a maximum-diversity extraction corpus and issuer-separated splits.

This tool does NOT run any part of the ARPipe extraction pipeline (no OCR, no
remapping, no reading order, no heading detection, no candidate generation, no
span resolution, no verification). It only:

  1. inventories the locally available annual-report PDFs (live_store/, already
     fetched by earlier, frozen ARPipe pipeline stages -- fetch/triage),
  2. re-verifies cheap facts about them (SHA-256, openability, page count,
     PDF metadata, page geometry, font names) directly from the PDF bytes,
  3. reuses the already-committed page/document text-layer profile
     (live_store/profiles.jsonl, produced by arpipe.triage/textlayer during
     an earlier, frozen pipeline stage) as KNOWN-FROM-PRIOR evidence,
  4. derives a diversity condition vector per document from that evidence,
  5. builds issuer-grouped FIT/VALIDATION/HOLDOUT splits,
  6. greedily selects a diversity-maximised development set from FIT issuers,
  7. selects a challenge-coverage set and a blinded annotation roster,
  8. writes every manifest, matrix, hash and report the freeze protocol needs.

Every non-identity fact is tagged with one of the evidence states in
EVIDENCE_STATES (see the T0 brief, section 19). Nothing here invents a
condition without local evidence, and nothing here writes new MD&A gold
labels (mda_present / mda_start_page / mda_end_page stay blank in the
annotation roster).

Usage (from the freeze worktree root)::

    <venv>/python tools/freeze_extraction_corpus.py --seed 20260918

The `--live-store-root` default points at the shared `arpipe-0.1.0` worktree's
`live_store/` (the canonical local PDF store; ~1.4 GB, gitignored, so it is
read in place rather than copied into this worktree -- see freeze_protocol.md).
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
import random
import re
import statistics
import sys
from collections import Counter, defaultdict
from dataclasses import dataclass, field

import pymupdf

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEFAULT_LIVE_STORE = os.path.abspath(
    os.path.join(REPO_ROOT, "..", "arpipe-0.1.0", "live_store")
)
OUT_DIR = os.path.join(REPO_ROOT, "dataset", "corpus_freeze")
HASH_DIR = os.path.join(OUT_DIR, "hashes")

EVIDENCE_STATES = (
    "OBSERVED",
    "INFERRED",
    "KNOWN_FROM_PRIOR",
    "HUMAN_CONFIRMED",
    "GOLD",
    "UNKNOWN",
)

# Thresholds reused verbatim from arpipe/config.py (triage section) so our
# image-area heuristics stay consistent with what the frozen pipeline itself
# treats as "image-heavy" / "hybrid". We do not invent new thresholds for
# signals the pipeline already defines.
BIG_IMAGE_AREA_FRAC = 0.55       # triage.big_image_area_frac
HYBRID_IMAGE_AREA_FRAC = 0.25    # triage.hybrid_image_area_frac

DEVANAGARI_RE = re.compile(r"[ऀ-ॿ]")
LONG_REPORT_PAGES = 150
SHORT_REPORT_PAGES = 30

# Documents whose SHA-256 / basic identity check fails to open with any
# cheap library are excluded from selection but retained in the raw
# inventory per section 6 of the brief.
FONT_SAMPLE_MAX_PAGES = 12

CONDITIONS = [
    "native", "scanned", "mixed",
    "legacy_font", "OCR_layer", "hidden_text", "duplicate_text",
    "bilingual", "Devanagari",
    "two_column", "multi_column",
    "full_width_header", "full_width_footer",
    "table_heavy", "figure_heavy", "image_heavy",
    "toc_present", "toc_absent", "toc_offset",
    "bookmark_present", "bookmark_absent",
    "deep_hierarchy",
    "annexure", "combined_mda", "unusual_heading",
    "long_report", "short_report",
    "mixed_orientation", "mixed_page_sizes",
    "visual_text_disagreement",
    "vector_text_pages",
    "semantic_impostor",
]

# conditions we could not evaluate with any cheap local signal in this pass.
UNKNOWN_CORPUS_WIDE = {"full_width_header", "full_width_footer", "table_heavy",
                       "toc_offset", "duplicate_text"}

INTERACTION_PAIRS_REQUIRED = [
    ("legacy_font", "bilingual"),
    ("legacy_font", "scanned_or_mixed"),
    ("OCR_layer", "two_column"),
    ("OCR_layer", "table_heavy"),
    ("scanned", "Devanagari"),
    ("two_column", "full_width_footer"),
    ("two_column", "table_heavy"),
    ("two_column", "figure_heavy"),
    ("long_report", "scanned"),
    ("long_report", "deep_hierarchy"),
    ("toc_offset", "unusual_heading"),
    ("annexure", "unusual_heading"),
]


# ---------------------------------------------------------------------------
# loading
# ---------------------------------------------------------------------------

def sha256_file(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while True:
            chunk = f.read(1 << 20)
            if not chunk:
                break
            h.update(chunk)
    return h.hexdigest()


def load_jsonl(path: str) -> list[dict]:
    rows = []
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def load_csv(path: str) -> list[dict]:
    with open(path, encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


# ---------------------------------------------------------------------------
# fresh, cheap, non-rendering PDF introspection
# ---------------------------------------------------------------------------

@dataclass
class FreshProfile:
    openable: bool
    open_error: str | None = None
    page_count_observed: int | None = None
    page_count_matches_manifest: bool | None = None
    pdf_format: str | None = None
    encrypted_observed: bool | None = None
    outline_present: bool | None = None
    outline_depth: int | None = None
    page_sizes: list[tuple[float, float]] = field(default_factory=list)
    mixed_page_sizes: bool | None = None
    font_names: set[str] = field(default_factory=set)
    font_types: set[str] = field(default_factory=set)
    subset_font_count: int = 0
    total_font_samples: int = 0
    has_devanagari_text: bool | None = None
    parser_warnings: list[str] = field(default_factory=list)


def sample_page_indices(n_pages: int, k: int = FONT_SAMPLE_MAX_PAGES) -> list[int]:
    if n_pages <= k:
        return list(range(n_pages))
    # first 3, quartiles, last 3, deterministic (no RNG -- purely positional)
    idx = {0, 1, 2, n_pages - 1, n_pages - 2, n_pages - 3}
    for q in (0.25, 0.5, 0.75):
        idx.add(int(n_pages * q))
    return sorted(i for i in idx if 0 <= i < n_pages)


def fresh_profile_pdf(path: str, manifest_n_pages: int) -> FreshProfile:
    pymupdf.TOOLS.mupdf_display_errors(False)
    pymupdf.TOOLS.mupdf_display_warnings(False)
    pymupdf.TOOLS.reset_mupdf_warnings()
    try:
        doc = pymupdf.open(path)
    except Exception as exc:  # noqa: BLE001 -- any backend failure is "not openable"
        return FreshProfile(openable=False, open_error=f"{type(exc).__name__}: {exc}",
                             parser_warnings=list(pymupdf.TOOLS.mupdf_warnings()))

    fp = FreshProfile(openable=True)
    try:
        fp.page_count_observed = doc.page_count
        fp.page_count_matches_manifest = (doc.page_count == manifest_n_pages)
        fp.pdf_format = doc.metadata.get("format") if doc.metadata else None
        fp.encrypted_observed = bool(doc.is_encrypted)
        toc = doc.get_toc(simple=False)
        fp.outline_present = len(toc) > 0
        fp.outline_depth = len({t[0] for t in toc}) if toc else 0

        sizes = []
        for page in doc:
            r = page.rect
            sizes.append((round(r.width, 1), round(r.height, 1)))
        fp.page_sizes = sizes
        distinct = {s for s in sizes}
        fp.mixed_page_sizes = len(distinct) > 1

        sample_idx = sample_page_indices(doc.page_count)
        devanagari_hit = False
        for i in sample_idx:
            page = doc[i]
            try:
                for f_ in page.get_fonts(full=True):
                    # (xref, ext, type, basefont, name, encoding, referencer)
                    basefont = f_[3] or ""
                    ftype = f_[2] or ""
                    fp.font_names.add(basefont)
                    fp.font_types.add(ftype)
                    fp.total_font_samples += 1
                    if re.match(r"^[A-Z]{6}\+", basefont):
                        fp.subset_font_count += 1
            except Exception:
                pass
            try:
                txt = page.get_text("text")
                if DEVANAGARI_RE.search(txt):
                    devanagari_hit = True
            except Exception:
                pass
        fp.has_devanagari_text = devanagari_hit
        fp.parser_warnings = list(pymupdf.TOOLS.mupdf_warnings())
    finally:
        doc.close()
    return fp


# ---------------------------------------------------------------------------
# document record assembly
# ---------------------------------------------------------------------------

@dataclass(eq=False)  # identity-based hash/eq: records are put into sets by object identity
class DocRecord:
    document_id: str
    company_id: str
    issuer: str
    fiscal_year: int
    sha256: str
    sha256_verified: bool
    file_size_bytes: int
    page_count: int
    source_locator: str
    producer: str
    pdf_version: str | None
    is_encrypted: bool
    fresh: FreshProfile
    profile: dict | None  # KNOWN-FROM-PRIOR doc profile from profiles.jsonl
    label_row: dict | None  # KNOWN-FROM-PRIOR gold, if this doc was ever labelled
    to_label_row: dict | None
    company_row: dict | None
    conditions: dict = field(default_factory=dict)      # name -> True/False/None
    evidence: dict = field(default_factory=dict)         # name -> evidence state
    notes: list = field(default_factory=list)


def build_doc_records(live_store_root: str, worktree_root: str) -> list[DocRecord]:
    documents = load_jsonl(os.path.join(live_store_root, "documents.jsonl"))
    profiles = {p["sha256"]: p for p in load_jsonl(os.path.join(live_store_root, "profiles.jsonl"))}
    companies = {c["company_id"]: c for c in load_csv(os.path.join(worktree_root, "companies.csv"))}
    labels = {r["sha256"]: r for r in load_csv(os.path.join(worktree_root, "labels.csv"))}
    to_label = {r["sha256"]: r for r in load_csv(os.path.join(worktree_root, "to_label.csv"))}

    # sort for a deterministic, reproducible inventory order regardless of
    # documents.jsonl append order (which reflects fetch time, not identity)
    documents.sort(key=lambda d: (d["company_id"], d["fy_end"], d["sha256"]))

    records: list[DocRecord] = []
    for d in documents:
        abspath = os.path.join(live_store_root, d["path"].replace("/", os.sep))
        sha_ok = os.path.exists(abspath) and sha256_file(abspath) == d["sha256"]
        fresh = fresh_profile_pdf(abspath, d["n_pages"]) if os.path.exists(abspath) else FreshProfile(
            openable=False, open_error="file missing at recorded path"
        )
        company_row = companies.get(d["company_id"])
        issuer = (company_row or {}).get("canonical_name") or d["company_id"]
        doc_id = f"{d['company_id']}_{d['fy_end']}"
        rec = DocRecord(
            document_id=doc_id,
            company_id=d["company_id"],
            issuer=issuer,
            fiscal_year=int(d["fy_end"]),
            sha256=d["sha256"],
            sha256_verified=sha_ok,
            file_size_bytes=d["n_bytes"],
            page_count=d["n_pages"],
            source_locator=f"{abspath} (live_store root={live_store_root})",
            producer=d.get("pdf_producer") or "",
            pdf_version=fresh.pdf_format,
            is_encrypted=d.get("is_encrypted", False),
            fresh=fresh,
            profile=profiles.get(d["sha256"]),
            label_row=labels.get(d["sha256"]),
            to_label_row=to_label.get(d["sha256"]),
            company_row=company_row,
        )
        if fresh.openable and rec.is_encrypted != fresh.encrypted_observed:
            rec.notes.append(
                f"CONFLICT: documents.jsonl is_encrypted={rec.is_encrypted} "
                f"vs freshly-observed is_encrypted={fresh.encrypted_observed}"
            )
        if fresh.openable and fresh.page_count_matches_manifest is False:
            rec.notes.append(
                f"CONFLICT: documents.jsonl n_pages={rec.page_count} "
                f"vs freshly-observed page_count={fresh.page_count_observed}"
            )
        if rec.label_row is not None:
            lk = rec.label_row.get("doc_kind")
            pk = (rec.profile or {}).get("doc_kind")
            if lk and pk and lk != pk:
                rec.notes.append(f"CONFLICT: labels.csv doc_kind={lk} vs profiles.jsonl doc_kind={pk}")
            ts, te = rec.label_row.get("true_start"), rec.label_row.get("true_end")
            if ts and te and rec.page_count:
                frac = int(ts) / max(rec.page_count, 1)
                bucket = "front" if frac < 0.33 else ("middle" if frac < 0.66 else "late")
                rec.notes.append(
                    f"KNOWN-FROM-PRIOR historical_ground_truth label: true_start={ts} true_end={te} "
                    f"position_bucket={bucket} (frozen labels.csv, not re-derived here; NOT copied into "
                    f"annotation_roster.csv gold fields)"
                )
        records.append(rec)

    # section 6 / section 5: a PDF must never be silently excluded because it
    # is missing. labels.csv carries 20 historically gold-labelled documents;
    # cross-check finds only some of their sha256 values still have bytes in
    # live_store/ (see stratification_report.md). The rest are recorded here
    # as explicitly-missing rows -- present in the census, excluded from every
    # split/selection because there is nothing local to profile or verify.
    present_shas = {d["sha256"] for d in documents}
    for sha, lrow in labels.items():
        if sha in present_shas:
            continue
        company_row = companies.get(lrow.get("company_id", ""))
        issuer = (company_row or {}).get("canonical_name") or lrow.get("company_id", "UNKNOWN")
        doc_id = f"{lrow.get('company_id','UNKNOWN')}_{lrow.get('fy_end','UNKNOWN')}_MISSING"
        rec = DocRecord(
            document_id=doc_id,
            company_id=lrow.get("company_id", "UNKNOWN"),
            issuer=issuer,
            fiscal_year=int(lrow["fy_end"]) if lrow.get("fy_end") else 0,
            sha256=sha,
            sha256_verified=False,
            file_size_bytes=0,
            page_count=int(lrow["total_pages"]) if lrow.get("total_pages") else 0,
            source_locator="MISSING: no file at this sha256 anywhere under live_store/",
            producer="",
            pdf_version=None,
            is_encrypted=False,
            fresh=FreshProfile(openable=False, open_error="PDF bytes not present in live_store"),
            profile=None,
            label_row=lrow,
            to_label_row=None,
            company_row=company_row,
        )
        rec.notes.append(
            "MISSING_FROM_LIVE_STORE: this sha256 has a historical_ground_truth row in labels.csv "
            f"(true_start={lrow.get('true_start')}, true_end={lrow.get('true_end')}) but no PDF bytes "
            "are present anywhere in the local live_store/ -- a pre-existing acquisition/store gap, "
            "not investigated or repaired in T0 (STRICTLY LOCAL rule: not re-fetched)."
        )
        for name in CONDITIONS:
            rec.conditions[name] = None
            rec.evidence[name] = "UNKNOWN"
        records.append(rec)
    return records


# ---------------------------------------------------------------------------
# diversity condition derivation
# ---------------------------------------------------------------------------

OCR_PRODUCER_HINTS = ("ABBYY", "OmniPage", "Paper Capture", "Readiris", "Tesseract")


def derive_conditions(rec: DocRecord) -> None:
    prof = rec.profile
    fresh = rec.fresh
    cond = rec.conditions
    ev = rec.evidence

    def setc(name: str, value, state: str) -> None:
        cond[name] = value
        ev[name] = state

    if prof is None:
        for name in CONDITIONS:
            setc(name, None, "UNKNOWN")
        rec.notes.append("no live_store/profiles.jsonl entry for this sha256")
        return

    doc_kind = prof.get("doc_kind")
    setc("native", doc_kind == "digital", "KNOWN_FROM_PRIOR")
    setc("scanned", doc_kind == "scanned", "KNOWN_FROM_PRIOR")
    setc("mixed", doc_kind == "mixed", "KNOWN_FROM_PRIOR")

    pages = prof.get("pages", [])
    kinds = Counter(p["kind"] for p in pages)
    n_columns = [p["n_columns"] for p in pages]
    scripts = Counter(p["script"] for p in pages)
    rotations = {p["rotation"] for p in pages}
    image_fracs = [p["image_area_frac"] for p in pages]

    broken_text_present = kinds.get("broken_text", 0) > 0
    setc("legacy_font", broken_text_present, "INFERRED")  # broken_text = mojibake text layer, classic legacy/CID-font symptom

    ocr_producer = any(h.lower() in (rec.producer or "").lower() for h in OCR_PRODUCER_HINTS)
    setc("OCR_layer", ocr_producer, "INFERRED")

    hidden_text = any(p["kind"] == "scanned" and p["n_chars"] > 50 for p in pages)
    setc("hidden_text", hidden_text, "INFERRED")

    setc("duplicate_text", None, "UNKNOWN")  # no cheap overlap-detection signal available

    setc("bilingual", bool(prof.get("bilingual")), "KNOWN_FROM_PRIOR")
    devanagari_pages = scripts.get("devanagari", 0) > 0
    devanagari_fresh = bool(fresh.has_devanagari_text) if fresh.openable else None
    setc("Devanagari", devanagari_pages or (devanagari_fresh or False),
         "KNOWN_FROM_PRIOR" if devanagari_pages else ("OBSERVED" if fresh.openable else "UNKNOWN"))

    setc("two_column", any(c == 2 for c in n_columns), "KNOWN_FROM_PRIOR")
    setc("multi_column", any(c >= 3 for c in n_columns), "KNOWN_FROM_PRIOR")

    setc("full_width_header", None, "UNKNOWN")
    setc("full_width_footer", None, "UNKNOWN")
    setc("table_heavy", None, "UNKNOWN")

    figure_heavy = any(HYBRID_IMAGE_AREA_FRAC <= f < BIG_IMAGE_AREA_FRAC for f in image_fracs)
    setc("figure_heavy", figure_heavy, "INFERRED")
    image_heavy = any(f >= BIG_IMAGE_AREA_FRAC for f in image_fracs)
    setc("image_heavy", image_heavy, "INFERRED")

    has_outline = bool(prof.get("has_outline"))
    setc("toc_present", has_outline, "KNOWN_FROM_PRIOR")
    setc("toc_absent", not has_outline, "KNOWN_FROM_PRIOR")
    setc("toc_offset", None, "UNKNOWN")  # requires segment.py's offset solver -- out of scope for T0

    setc("bookmark_present", has_outline, "KNOWN_FROM_PRIOR")
    setc("bookmark_absent", not has_outline, "KNOWN_FROM_PRIOR")

    titles = [t[1] for t in prof.get("outline_titles", [])]
    depth = len({t[0] for t in prof.get("outline_titles", [])})
    setc("deep_hierarchy", depth >= 3, "KNOWN_FROM_PRIOR")

    lower_titles = [t.lower() for t in titles]
    annexure = any("annexure" in t for t in lower_titles)
    setc("annexure", annexure if has_outline else None, "INFERRED" if has_outline else "UNKNOWN")

    discussion_titles = [t for t in lower_titles if "discussion" in t or "md&a" in t or "md & a" in t]
    combined = any(
        ("discussion" in t) and any(k in t for k in ("governance", "annexure", "report on"))
        for t in lower_titles
    )
    setc("combined_mda", combined if has_outline else None, "INFERRED" if has_outline else "UNKNOWN")

    canonical = {"management discussion and analysis", "management discussion & analysis",
                 "management discussion and analysis report", "management's discussion and analysis"}
    unusual_heading = any(
        t for t in discussion_titles if t.strip() not in canonical
    ) if discussion_titles else None
    setc("unusual_heading", bool(unusual_heading) if discussion_titles else (False if has_outline else None),
         "INFERRED" if has_outline else "UNKNOWN")

    setc("long_report", rec.page_count >= LONG_REPORT_PAGES, "INFERRED")
    setc("short_report", rec.page_count <= SHORT_REPORT_PAGES, "INFERRED")

    setc("mixed_orientation", len(rotations) > 1, "KNOWN_FROM_PRIOR")
    if fresh.openable:
        setc("mixed_page_sizes", bool(fresh.mixed_page_sizes), "OBSERVED")
    else:
        setc("mixed_page_sizes", None, "UNKNOWN")

    setc("visual_text_disagreement", broken_text_present, "INFERRED")

    setc("vector_text_pages", kinds.get("vector_text", 0) > 0, "KNOWN_FROM_PRIOR")

    setc("semantic_impostor", (len(discussion_titles) >= 2) if has_outline else None,
         "INFERRED" if has_outline else "UNKNOWN")

    rec.notes.append(f"mda_heading_in_outline={len(discussion_titles) > 0} (n_matches={len(discussion_titles)})")


# ---------------------------------------------------------------------------
# issuer-level aggregation + issuer-grouped splits
# ---------------------------------------------------------------------------

RARE_CONDITIONS_FOR_STRATIFICATION = [
    "scanned", "legacy_font", "vector_text_pages", "deep_hierarchy", "mixed_orientation",
]


def issuer_condition_flag(docs: list[DocRecord], cond: str) -> bool:
    return any(d.conditions.get(cond) is True for d in docs)


def assign_splits(by_issuer: dict[str, list[DocRecord]], seed: int) -> dict[str, str]:
    """Issuer-grouped FIT/VALIDATION/HOLDOUT assignment, ~50/25/25 by issuer
    count, stratified so that rare conditions get spread across splits
    wherever their issuer count allows it (most-constrained conditions are
    processed first so they get first claim on the round-robin cycle)."""
    pattern = ["FIT", "FIT", "VALIDATION", "HOLDOUT"]
    assignment: dict[str, str] = {}
    cycle = [0]  # single global pointer, shared across every stratification pass

    def assign_remaining(issuer_ids: list[str], rng: random.Random) -> None:
        remaining = [i for i in issuer_ids if i not in assignment]
        rng.shuffle(remaining)
        for iid in remaining:
            assignment[iid] = pattern[cycle[0] % len(pattern)]
            cycle[0] += 1

    all_issuers = sorted(by_issuer.keys())
    # (condition, issuer_list) pairs, most-constrained (fewest issuers) first
    strata = []
    for cond in RARE_CONDITIONS_FOR_STRATIFICATION:
        issuers = sorted(i for i in all_issuers if issuer_condition_flag(by_issuer[i], cond))
        if issuers:
            strata.append((cond, issuers))
    strata.sort(key=lambda kv: len(kv[1]))

    for cond, issuers in strata:
        rng = random.Random(f"{seed}:{cond}")
        assign_remaining(issuers, rng)

    rng = random.Random(f"{seed}:remainder")
    assign_remaining(all_issuers, rng)
    return assignment


# ---------------------------------------------------------------------------
# development set: greedy diversity-maximising selection
# ---------------------------------------------------------------------------

def greedy_diversity_select(pool: list[DocRecord], target_n: int, seed: int,
                             condition_names: list[str]) -> tuple[list[DocRecord], dict]:
    """Greedy diversity-maximising selection (NOT a globally optimal solver:
    a straightforward greedy weighted set-cover heuristic). At each step pick
    the not-yet-selected document that covers the most still-uncovered
    conditions, weighting rarer conditions higher; ties are broken by
    preferring an issuer not yet represented, then by a seeded deterministic
    shuffle order fixed once up front."""
    rng = random.Random(seed)
    ordered_pool = pool[:]
    rng.shuffle(ordered_pool)  # fixes the deterministic tie-break order

    # rarity weight = 1 / (num docs in pool with that condition True), so a
    # condition observed in only 2 docs is worth far more than one in 150
    doc_true_conditions = {
        id(d): {c for c in condition_names if d.conditions.get(c) is True}
        for d in ordered_pool
    }
    freq = Counter()
    for s in doc_true_conditions.values():
        freq.update(s)
    weight = {c: 1.0 / freq[c] for c in freq if freq[c] > 0}

    covered: set[str] = set()
    selected: list[DocRecord] = []
    selected_issuers: set[str] = set()
    remaining = list(ordered_pool)
    reasons: dict[str, str] = {}

    while remaining and len(selected) < target_n:
        best = None
        best_score = None
        for d in remaining:
            new_conditions = doc_true_conditions[id(d)] - covered
            score = sum(weight.get(c, 0.0) for c in new_conditions)
            issuer_bonus = 0.0001 if d.company_id not in selected_issuers else 0.0
            score += issuer_bonus
            key = (score, d.company_id not in selected_issuers)
            if best_score is None or key > best_score:
                best_score = key
                best = d
        assert best is not None
        new_conditions = doc_true_conditions[id(best)] - covered
        if new_conditions:
            reasons[best.document_id] = "adds new conditions: " + ", ".join(sorted(new_conditions))
        elif best.company_id not in selected_issuers:
            reasons[best.document_id] = "adds issuer diversity (no new conditions left to add)"
        else:
            reasons[best.document_id] = "fills remaining development-set budget"
        covered |= doc_true_conditions[id(best)]
        selected.append(best)
        selected_issuers.add(best.company_id)
        remaining.remove(best)

    uncovered = {c for c in condition_names if c in freq} - covered
    summary = {
        "target_n": target_n,
        "achieved_n": len(selected),
        "conditions_covered": sorted(covered),
        "conditions_available_but_uncovered": sorted(uncovered),
        "distinct_issuers": len(selected_issuers),
    }
    return selected, {"reasons": reasons, "summary": summary}


CHALLENGE_CONDITIONS = [
    "scanned", "legacy_font", "OCR_layer", "hidden_text", "bilingual", "Devanagari",
    "vector_text_pages", "mixed_orientation", "mixed_page_sizes", "deep_hierarchy",
    "annexure", "unusual_heading", "semantic_impostor", "combined_mda",
]


def select_challenge_set(all_docs: list[DocRecord], max_n: int = 45) -> tuple[list[DocRecord], dict]:
    scored = []
    for d in all_docs:
        reasons = [c for c in CHALLENGE_CONDITIONS if d.conditions.get(c) is True]
        if d.page_count <= 3:
            reasons.append("degenerate_short_document")
        if reasons:
            scored.append((d, reasons))
    # prioritise documents covering rarer conditions first (same rarity idea
    # as the development selector), then cap at max_n
    freq = Counter()
    for _, reasons in scored:
        freq.update(reasons)
    scored.sort(key=lambda dr: -sum(1.0 / freq[r] for r in dr[1]))
    chosen = scored[:max_n]
    reason_map = {d.document_id: reasons for d, reasons in chosen}
    return [d for d, _ in chosen], reason_map


ROSTER_AXES = ["native", "scanned", "mixed", "legacy_font", "two_column", "multi_column",
               "toc_absent", "deep_hierarchy", "unusual_heading", "annexure",
               "combined_mda", "long_report", "short_report", "semantic_impostor"]


def select_annotation_roster(development: list[DocRecord], target_n: int, seed: int) -> tuple[list[DocRecord], dict]:
    selected, info = greedy_diversity_select(development, target_n, seed=f"{seed}:roster", condition_names=ROSTER_AXES)
    return selected, info


# ---------------------------------------------------------------------------
# writers
# ---------------------------------------------------------------------------

def w(s):
    return "" if s is None else s


def write_csv(path: str, fieldnames: list[str], rows: list[dict]) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for r in rows:
            writer.writerow(r)


def condition_value_str(v) -> str:
    if v is True:
        return "True"
    if v is False:
        return "False"
    return "UNKNOWN"


def corpus_inventory_rows(records: list[DocRecord]) -> tuple[list[str], list[dict]]:
    base_fields = [
        "document_id", "issuer", "company_id", "fiscal_year", "pdf_sha256",
        "sha256_verified", "file_size_bytes", "page_count", "source_locator",
        "duplicate_group", "producer", "pdf_version", "is_encrypted",
        "openable", "open_error", "page_count_matches_manifest", "parser_warning_count",
        "has_outline", "outline_depth", "doc_kind_prior", "conflicts", "notes",
    ]
    cond_fields = []
    for c in CONDITIONS:
        cond_fields.append(c)
        cond_fields.append(f"{c}_evidence")
    fieldnames = base_fields + cond_fields
    rows = []
    for r in records:
        row = {
            "document_id": r.document_id,
            "issuer": r.issuer,
            "company_id": r.company_id,
            "fiscal_year": r.fiscal_year,
            "pdf_sha256": r.sha256,
            "sha256_verified": r.sha256_verified,
            "file_size_bytes": r.file_size_bytes,
            "page_count": r.page_count,
            "source_locator": r.source_locator,
            "duplicate_group": f"{r.company_id}_{r.fiscal_year}_singleton",
            "producer": r.producer,
            "pdf_version": r.pdf_version or "",
            "is_encrypted": r.is_encrypted,
            "openable": r.fresh.openable,
            "open_error": r.fresh.open_error or "",
            "page_count_matches_manifest": w(r.fresh.page_count_matches_manifest),
            "parser_warning_count": len(r.fresh.parser_warnings),
            "has_outline": w((r.profile or {}).get("has_outline")),
            "outline_depth": len({t[0] for t in (r.profile or {}).get("outline_titles", [])}),
            "doc_kind_prior": (r.profile or {}).get("doc_kind", ""),
            "conflicts": " | ".join(n for n in r.notes if n.startswith("CONFLICT:")),
            "notes": " | ".join(n for n in r.notes if not n.startswith("CONFLICT:")),
        }
        for c in CONDITIONS:
            row[c] = condition_value_str(r.conditions.get(c))
            row[f"{c}_evidence"] = r.evidence.get(c, "UNKNOWN")
        rows.append(row)
    return fieldnames, rows


def issuer_split_rows(by_issuer: dict[str, list[DocRecord]], assignment: dict[str, str]) -> tuple[list[str], list[dict]]:
    fieldnames = ["issuer_id", "issuer_name", "split", "num_documents", "num_years",
                  "fiscal_years", "diversity_summary"]
    rows = []
    for iid in sorted(by_issuer):
        docs = by_issuer[iid]
        flags = sorted(c for c in CONDITIONS if issuer_condition_flag(docs, c))
        rows.append({
            "issuer_id": iid,
            "issuer_name": docs[0].issuer,
            "split": assignment[iid],
            "num_documents": len(docs),
            "num_years": len({d.fiscal_year for d in docs}),
            "fiscal_years": ";".join(str(y) for y in sorted({d.fiscal_year for d in docs})),
            "diversity_summary": ";".join(flags),
        })
    return fieldnames, rows


def split_partition_manifest_rows(docs: list[DocRecord], split_name: str) -> tuple[list[str], list[dict]]:
    """validation_manifest.csv / holdout_manifest.csv: the full issuer-level
    partition for that split (not a curated subset -- see freeze_protocol.md)."""
    fieldnames = ["document_id", "issuer", "company_id", "fiscal_year", "pdf_sha256", "split",
                  "development", "selection_seed", "selection_reason", "condition_coverage_summary"]
    rows = []
    for d in docs:
        true_conditions = sorted(c for c in CONDITIONS if d.conditions.get(c) is True)
        rows.append({
            "document_id": d.document_id, "issuer": d.issuer, "company_id": d.company_id,
            "fiscal_year": d.fiscal_year, "pdf_sha256": d.sha256, "split": split_name,
            "development": False, "selection_seed": "", "selection_reason": "",
            "condition_coverage_summary": ";".join(true_conditions),
        })
    return fieldnames, rows


def development_manifest_rows(docs: list[DocRecord], seed: int,
                               reasons: dict[str, str]) -> tuple[list[str], list[dict]]:
    """development_manifest.csv: the curated diversity-maximised subset of FIT."""
    fieldnames = ["document_id", "issuer", "company_id", "fiscal_year", "pdf_sha256", "split",
                  "development", "selection_seed", "selection_reason", "condition_coverage_summary"]
    rows = []
    for d in docs:
        true_conditions = sorted(c for c in CONDITIONS if d.conditions.get(c) is True)
        rows.append({
            "document_id": d.document_id, "issuer": d.issuer, "company_id": d.company_id,
            "fiscal_year": d.fiscal_year, "pdf_sha256": d.sha256, "split": "FIT",
            "development": True, "selection_seed": seed,
            "selection_reason": reasons.get(d.document_id, ""),
            "condition_coverage_summary": ";".join(true_conditions),
        })
    return fieldnames, rows


def challenge_manifest_rows(docs: list[DocRecord], challenge_reasons: dict[str, list[str]]) -> tuple[list[str], list[dict]]:
    fieldnames = ["document_id", "issuer", "company_id", "fiscal_year", "pdf_sha256",
                  "challenge_reason", "conditions_covered"]
    rows = []
    for d in docs:
        reasons = challenge_reasons.get(d.document_id, [])
        rows.append({
            "document_id": d.document_id, "issuer": d.issuer, "company_id": d.company_id,
            "fiscal_year": d.fiscal_year, "pdf_sha256": d.sha256,
            "challenge_reason": "; ".join(reasons),
            "conditions_covered": "; ".join(reasons),
        })
    return fieldnames, rows


def annotation_roster_rows(docs: list[DocRecord]) -> tuple[list[str], list[dict]]:
    fieldnames = ["document_id", "issuer", "fiscal_year", "pdf_sha256", "mda_present",
                  "mda_start_page", "mda_end_page", "heading_text_verbatim", "heading_form",
                  "boundary_ambiguous", "ambiguity_reason", "excluded_neighbours", "language",
                  "per_page_text_quality", "annotator_id", "annotation_date", "minutes_spent",
                  "saw_pipeline_output"]
    rows = []
    for d in docs:
        rows.append({k: "" for k in fieldnames} | {
            "document_id": d.document_id, "issuer": d.issuer, "fiscal_year": d.fiscal_year,
            "pdf_sha256": d.sha256,
        })
    return fieldnames, rows


def diversity_matrix_rows(records: list[DocRecord], by_issuer: dict[str, list[DocRecord]],
                           assignment: dict[str, str], fit_ids: set, val_ids: set,
                           hold_ids: set, dev_ids: set, chall_ids: set) -> tuple[list[str], list[dict]]:
    fieldnames = ["condition", "evidence_status", "num_documents", "num_issuers",
                  "fit_coverage", "validation_coverage", "holdout_coverage", "challenge_coverage",
                  "example_document_ids"]
    rows = []
    for c in CONDITIONS:
        docs_true = [r for r in records if r.conditions.get(c) is True]
        if c in UNKNOWN_CORPUS_WIDE:
            rows.append({
                "condition": c, "evidence_status": "UNKNOWN", "num_documents": len(docs_true),
                "num_issuers": len({d.company_id for d in docs_true}),
                "fit_coverage": sum(1 for d in docs_true if d.document_id in fit_ids),
                "validation_coverage": sum(1 for d in docs_true if d.document_id in val_ids),
                "holdout_coverage": sum(1 for d in docs_true if d.document_id in hold_ids),
                "challenge_coverage": sum(1 for d in docs_true if d.document_id in chall_ids),
                "example_document_ids": ";".join(d.document_id for d in docs_true[:5]),
            })
            continue
        # evidence tag reflects the METHOD used to evaluate this condition,
        # taken across all records (not just the True ones) so a genuinely
        # zero-count condition still reports how it was checked rather than
        # a meaningless default.
        evidence_states = {r.evidence.get(c) for r in records} - {"UNKNOWN"}
        if not evidence_states:
            ev = "UNKNOWN"
        elif len(evidence_states) == 1:
            ev = next(iter(evidence_states))
        else:
            ev = "MIXED(" + ",".join(sorted(evidence_states)) + ")"
        rows.append({
            "condition": c,
            "evidence_status": ev,
            "num_documents": len(docs_true),
            "num_issuers": len({d.company_id for d in docs_true}),
            "fit_coverage": sum(1 for d in docs_true if d.document_id in fit_ids),
            "validation_coverage": sum(1 for d in docs_true if d.document_id in val_ids),
            "holdout_coverage": sum(1 for d in docs_true if d.document_id in hold_ids),
            "challenge_coverage": sum(1 for d in docs_true if d.document_id in chall_ids),
            "example_document_ids": ";".join(d.document_id for d in docs_true[:5]),
        })
    return fieldnames, rows


def interaction_matrix_rows(records: list[DocRecord]) -> tuple[list[str], list[dict]]:
    fieldnames = ["condition_A", "condition_B", "evidence_status", "num_documents",
                  "num_issuers", "example_document_ids"]
    rows = []

    def docs_for(cond_name: str) -> set:
        if cond_name == "scanned_or_mixed":
            return {r for r in records if r.conditions.get("scanned") is True or r.conditions.get("mixed") is True}
        return {r for r in records if r.conditions.get(cond_name) is True}

    def unknownish(cond_name: str) -> bool:
        base = cond_name if cond_name != "scanned_or_mixed" else "scanned"
        return cond_name in UNKNOWN_CORPUS_WIDE or base in UNKNOWN_CORPUS_WIDE

    seen_pairs = set()
    for a, b in INTERACTION_PAIRS_REQUIRED:
        seen_pairs.add((a, b))
        if unknownish(a) or unknownish(b):
            rows.append({"condition_A": a, "condition_B": b, "evidence_status": "UNKNOWN",
                         "num_documents": "", "num_issuers": "",
                         "example_document_ids": "insufficient cheap local evidence for one or both conditions in T0"})
            continue
        both = docs_for(a) & docs_for(b)
        rows.append({
            "condition_A": a, "condition_B": b,
            "evidence_status": "OBSERVED" if both else "NOT_OBSERVED",
            "num_documents": len(both),
            "num_issuers": len({d.company_id for d in both}),
            "example_document_ids": ";".join(sorted(d.document_id for d in both)[:5]),
        })

    # discover additional high-frequency interactions among all pairs of
    # conditions that DO have local evidence (skip the UNKNOWN_CORPUS_WIDE set)
    evaluable = [c for c in CONDITIONS if c not in UNKNOWN_CORPUS_WIDE]
    extra = []
    for i, a in enumerate(evaluable):
        for b in evaluable[i + 1:]:
            if (a, b) in seen_pairs or (b, a) in seen_pairs:
                continue
            both = docs_for(a) & docs_for(b)
            if len(both) >= 3:
                extra.append((a, b, both))
    extra.sort(key=lambda t: -len(t[2]))
    for a, b, both in extra[:15]:
        rows.append({
            "condition_A": a, "condition_B": b, "evidence_status": "OBSERVED",
            "num_documents": len(both), "num_issuers": len({d.company_id for d in both}),
            "example_document_ids": ";".join(sorted(d.document_id for d in both)[:5]),
        })
    return fieldnames, rows


def rare_condition_register_rows(records: list[DocRecord], by_issuer: dict[str, list[DocRecord]],
                                  assignment: dict[str, str], rare_threshold: int = 10) -> tuple[list[str], list[dict]]:
    fieldnames = ["condition", "evidence_status", "num_documents", "num_issuers",
                  "affected_issuers", "example_document_ids", "split_availability", "notes"]
    rows = []
    for c in CONDITIONS:
        docs_true = [r for r in records if r.conditions.get(c) is True]
        if c in UNKNOWN_CORPUS_WIDE:
            continue
        if 0 < len(docs_true) <= rare_threshold:
            issuers = sorted({d.company_id for d in docs_true})
            splits_hit = sorted({assignment[i] for i in issuers})
            note = ""
            if len(issuers) == 1:
                note = f"condition confined to issuer {issuers[0]}; unavailable outside split {assignment[issuers[0]]}"
            elif len(splits_hit) < 3:
                missing = sorted({"FIT", "VALIDATION", "HOLDOUT"} - set(splits_hit))
                note = f"condition present in {len(issuers)} issuers but absent from split(s): {', '.join(missing)}"
            rows.append({
                "condition": c,
                "evidence_status": (docs_true[0].evidence.get(c, "UNKNOWN") if docs_true else "UNKNOWN"),
                "num_documents": len(docs_true),
                "num_issuers": len(issuers),
                "affected_issuers": ";".join(issuers),
                "example_document_ids": ";".join(d.document_id for d in docs_true),
                "split_availability": ";".join(splits_hit),
                "notes": note,
            })
    return fieldnames, rows


def hash_file(path: str) -> str:
    return sha256_file(path)


def write_hash(manifest_csv_path: str, hash_out_path: str) -> None:
    os.makedirs(os.path.dirname(hash_out_path), exist_ok=True)
    digest = hash_file(manifest_csv_path)
    with open(hash_out_path, "w", encoding="utf-8") as f:
        f.write(f"{digest}  {os.path.basename(manifest_csv_path)}\n")


def page_profile_rows(records: list[DocRecord]) -> tuple[list[str], list[dict]]:
    fieldnames = [
        "document_id", "physical_page", "page_count", "char_count", "word_count",
        "image_area_frac", "text_area_frac", "n_images", "n_columns", "orientation",
        "page_width", "page_height", "kind", "script", "mojibake_ratio",
        "dpi_estimate", "cid_or_broken_text_indicator", "u_fffd_indicator_unavailable",
        "render_mode_ocr_layer_indicator", "hidden_duplicate_text_indicator",
        "evidence_status",
    ]
    rows = []
    for r in records:
        prof = r.profile
        if prof is None:
            continue
        sizes = r.fresh.page_sizes if r.fresh.openable else []
        for p in prof.get("pages", []):
            pn = p["page_no"]
            width, height = (sizes[pn] if pn < len(sizes) else (None, None))
            rows.append({
                "document_id": r.document_id,
                "physical_page": pn,
                "page_count": r.page_count,
                "char_count": p["n_chars"],
                "word_count": p["n_words"],
                "image_area_frac": p["image_area_frac"],
                "text_area_frac": p["text_area_frac"],
                "n_images": p["n_images"],
                "n_columns": p["n_columns"],
                "orientation": p["rotation"],
                "page_width": w(width),
                "page_height": w(height),
                "kind": p["kind"],
                "script": p["script"],
                "mojibake_ratio": p["mojibake_ratio"],
                "dpi_estimate": w(p["dpi_estimate"]),
                "cid_or_broken_text_indicator": p["kind"] == "broken_text",
                "u_fffd_indicator_unavailable": "UNKNOWN",
                "render_mode_ocr_layer_indicator": p["kind"] == "scanned" and p["n_chars"] > 50,
                "hidden_duplicate_text_indicator": "UNKNOWN",
                "evidence_status": "KNOWN_FROM_PRIOR" if width is None else "OBSERVED+KNOWN_FROM_PRIOR",
            })
    return fieldnames, rows


# ---------------------------------------------------------------------------
# main
# ---------------------------------------------------------------------------

def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--seed", type=int, default=20260918, help="deterministic selection seed")
    ap.add_argument("--live-store-root", default=DEFAULT_LIVE_STORE)
    ap.add_argument("--worktree-root", default=REPO_ROOT)
    ap.add_argument("--out-dir", default=OUT_DIR)
    ap.add_argument("--development-target", type=int, default=60)
    ap.add_argument("--roster-target", type=int, default=25)
    ap.add_argument("--challenge-max", type=int, default=45)
    args = ap.parse_args()

    out_dir = args.out_dir
    hash_dir = os.path.join(out_dir, "hashes")

    print(f"[1/9] loading + verifying inventory from {args.live_store_root}", file=sys.stderr)
    records = build_doc_records(args.live_store_root, args.worktree_root)
    print(f"      {len(records)} documents, "
          f"{sum(1 for r in records if r.sha256_verified)} sha256-verified, "
          f"{sum(1 for r in records if r.fresh.openable)} openable", file=sys.stderr)

    n_missing = sum(1 for r in records if r.profile is None)
    if n_missing:
        print(f"      + {n_missing} historically-labelled document(s) recorded as MISSING "
              f"(no PDF bytes in live_store) -- kept in corpus_inventory.csv, excluded from "
              f"splits/selection", file=sys.stderr)

    print("[2/9] deriving diversity conditions", file=sys.stderr)
    for r in records:
        derive_conditions(r)

    # splits/development/challenge/roster/matrices only ever consider
    # documents we actually have bytes for; the MISSING rows exist solely
    # for corpus_inventory.csv's completeness/audit trail (section 6).
    profiled = [r for r in records if r.profile is not None]

    by_issuer: dict[str, list[DocRecord]] = defaultdict(list)
    for r in profiled:
        by_issuer[r.company_id].append(r)

    print("[3/9] issuer-grouped FIT/VALIDATION/HOLDOUT split", file=sys.stderr)
    assignment = assign_splits(by_issuer, args.seed)
    for r in profiled:
        r.notes.append(f"split={assignment[r.company_id]}")
    for r in records:
        if r.profile is None:
            r.notes.append("not split-assigned: excluded from FIT/VALIDATION/HOLDOUT (no local PDF)")
    fit_docs = [r for r in profiled if assignment[r.company_id] == "FIT"]
    val_docs = [r for r in profiled if assignment[r.company_id] == "VALIDATION"]
    hold_docs = [r for r in profiled if assignment[r.company_id] == "HOLDOUT"]
    print(f"      issuers: FIT={sum(1 for v in assignment.values() if v=='FIT')} "
          f"VALIDATION={sum(1 for v in assignment.values() if v=='VALIDATION')} "
          f"HOLDOUT={sum(1 for v in assignment.values() if v=='HOLDOUT')} "
          f"| docs: FIT={len(fit_docs)} VALIDATION={len(val_docs)} HOLDOUT={len(hold_docs)}",
          file=sys.stderr)

    print("[4/9] greedy diversity-maximising development selection from FIT", file=sys.stderr)
    development, dev_info = greedy_diversity_select(fit_docs, args.development_target, args.seed, CONDITIONS)
    print(f"      development={len(development)} docs, "
          f"{dev_info['summary']['distinct_issuers']} distinct issuers, "
          f"{len(dev_info['summary']['conditions_covered'])} conditions covered", file=sys.stderr)

    print("[5/9] challenge coverage set", file=sys.stderr)
    challenge, challenge_reasons = select_challenge_set(profiled, args.challenge_max)
    print(f"      challenge={len(challenge)} docs", file=sys.stderr)

    print("[6/9] blinded annotation roster", file=sys.stderr)
    roster, roster_info = select_annotation_roster(development, args.roster_target, args.seed)
    print(f"      roster={len(roster)} docs", file=sys.stderr)

    fit_ids = {d.document_id for d in fit_docs}
    val_ids = {d.document_id for d in val_docs}
    hold_ids = {d.document_id for d in hold_docs}
    dev_ids = {d.document_id for d in development}
    chall_ids = {d.document_id for d in challenge}
    roster_ids = {d.document_id for d in roster}

    print("[7/9] writing manifests, matrices, registers", file=sys.stderr)
    outputs: list[tuple[str, list[str], list[dict]]] = []
    outputs.append(("corpus_inventory.csv", *corpus_inventory_rows(records)))
    outputs.append(("page_profile.csv", *page_profile_rows(records)))
    outputs.append(("issuer_split.csv", *issuer_split_rows(by_issuer, assignment)))
    outputs.append(("development_manifest.csv", *development_manifest_rows(development, args.seed, dev_info["reasons"])))
    outputs.append(("validation_manifest.csv", *split_partition_manifest_rows(val_docs, "VALIDATION")))
    outputs.append(("holdout_manifest.csv", *split_partition_manifest_rows(hold_docs, "HOLDOUT")))
    outputs.append(("challenge_coverage_manifest.csv", *challenge_manifest_rows(challenge, challenge_reasons)))
    outputs.append(("annotation_roster.csv", *annotation_roster_rows(roster)))
    outputs.append(("diversity_matrix.csv", *diversity_matrix_rows(
        profiled, by_issuer, assignment, fit_ids, val_ids, hold_ids, dev_ids, chall_ids)))
    outputs.append(("interaction_matrix.csv", *interaction_matrix_rows(profiled)))
    outputs.append(("rare_condition_register.csv", *rare_condition_register_rows(profiled, by_issuer, assignment)))

    for fname, fieldnames, rows in outputs:
        path = os.path.join(out_dir, fname)
        write_csv(path, fieldnames, rows)
        print(f"      wrote {path} ({len(rows)} rows)", file=sys.stderr)

    print("[8/9] hashing manifests", file=sys.stderr)
    for fname in ("corpus_inventory.csv", "development_manifest.csv", "validation_manifest.csv",
                  "holdout_manifest.csv", "challenge_coverage_manifest.csv"):
        stem = {
            "corpus_inventory.csv": "corpus_inventory",
            "development_manifest.csv": "development",
            "validation_manifest.csv": "validation",
            "holdout_manifest.csv": "holdout",
            "challenge_coverage_manifest.csv": "challenge",
        }[fname]
        write_hash(os.path.join(out_dir, fname), os.path.join(hash_dir, f"{stem}.sha256"))

    print("[9/9] writing freeze_summary.json", file=sys.stderr)
    summary = {
        "seed": args.seed,
        "live_store_root": args.live_store_root,
        "worktree_root": args.worktree_root,
        "counts": {
            "documents_total": len(records),
            "documents_with_local_pdf": len(profiled),
            "documents_missing_from_live_store": n_missing,
            "documents_sha256_verified": sum(1 for r in records if r.sha256_verified),
            "documents_openable": sum(1 for r in records if r.fresh.openable),
            "issuers_total": len(by_issuer),
            "issuers_fit": sum(1 for v in assignment.values() if v == "FIT"),
            "issuers_validation": sum(1 for v in assignment.values() if v == "VALIDATION"),
            "issuers_holdout": sum(1 for v in assignment.values() if v == "HOLDOUT"),
            "docs_fit": len(fit_docs),
            "docs_validation": len(val_docs),
            "docs_holdout": len(hold_docs),
            "development": len(development),
            "challenge": len(challenge),
            "annotation_roster": len(roster),
        },
        "development_selection": dev_info["summary"],
        "roster_selection": roster_info["summary"],
        "issuer_disjoint_check": {
            "fit_val_empty": len(fit_ids & val_ids) == 0,
            "fit_hold_empty": len(fit_ids & hold_ids) == 0,
            "val_hold_empty": len(val_ids & hold_ids) == 0,
        },
        "subset_checks": {
            "development_subset_of_fit": dev_ids.issubset(fit_ids),
            "roster_subset_of_development": roster_ids.issubset(dev_ids),
        },
    }
    with open(os.path.join(out_dir, "freeze_summary.json"), "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2, sort_keys=True)

    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
