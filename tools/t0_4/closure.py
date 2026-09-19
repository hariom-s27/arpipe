"""T0.4-CLOSE: final pre-execution closure audit.

Every input is read from git objects of an audited commit, so the working
tree, timestamps, hostnames, UUIDs and absolute paths cannot influence a
result. No PDF is opened, no page is rendered, and no engine or API is
invoked; the four checks only read frozen metadata, configuration and text.
"""
from __future__ import annotations

import hashlib
import itertools
import re
import statistics
import subprocess
import tempfile
from collections import Counter
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence

from .core import (
    BASE_COMMIT,
    SOURCE_FILES,
    SetupInvariantError,
    _length_category,
    _page_auxiliary_sets,
    _page_conditions,
    _representation_class,
    _sampling_stratum,
    build_manifest,
    canonical_json,
    config_hash_manifest,
    contains_absolute_path,
    file_sha256,
    read_csv,
    read_json,
)

SCHEMA_VERSION = "1.0.0"
CLOSURE_TASK_ID = "T0.4-CLOSE"
PRE_CLOSURE_COMMIT = "b937b58298930114de08d9b0236714c564c6da02"

PASS = "PASS"
PASS_SPARSE = "PASS_WITH_DOCUMENTED_SPARSE_CELLS"
UNRESOLVED = "UNRESOLVED"
FAIL = "FAIL"
CLOSED = "CLOSED_FOR_GOLD_PHASE"
OPEN = "OPEN"

PREREGISTRATION = "docs/experiments/T0.4_ocr_benchmark_preregistration.md"
SAMPLING_SPEC = "configs/t0_4/sampling_spec.json"
MANIFEST_SCHEMA = "configs/t0_4/benchmark_manifest_schema.json"
CONFIG_HASHES = "artifacts/t0_4/config_hashes.json"
MANIFEST = "artifacts/t0_4/benchmark_manifest.json"
CORPUS_INVENTORY = "dataset/corpus_freeze/corpus_inventory.csv"
CORPUS_INVENTORY_RECORDED_HASH = "dataset/corpus_freeze/hashes/corpus_inventory.sha256"
PAGE_PROFILE = "dataset/corpus_freeze/page_profile.csv"
ISSUER_SPLIT = "dataset/corpus_freeze/issuer_split.csv"
CONDITION_PAGE_MAP = "dataset/corpus_gap_audit/condition_page_map.csv"
TABLE_CANDIDATES = "dataset/corpus_gap_audit/table_candidates.csv"
LANGUAGE_CANDIDATES = "dataset/corpus_gap_audit/language_candidates.csv"

CLOSURE_RECORD_FILES = (
    "artifacts/t0_4/final_closure_audit.json",
    "docs/experiments/T0.4_final_closure_audit.md",
    "tests/t0_4/test_t0_4_closure_record.py",
)
CLOSURE_CODE_FILES = frozenset({
    "tools/t0_4/closure.py",
    "tools/audit_t0_4_final_closure.py",
    "tests/t0_4/test_t0_4_final_closure.py",
    "tests/t0_4/test_t0_4_closure_record.py",
})

# The only paths the closure work may change relative to the audited base.
ALLOWED_CLOSURE_CHANGES = frozenset({
    PREREGISTRATION,
    "docs/experiments/T0.4_p-x1_reuse_audit.md",
    "tools/audit_t0_4_final_closure.py",
    "tools/audit_t0_4_setup.py",
    "tools/t0_4/README.md",
    "tools/t0_4/closure.py",
    "tests/t0_4/test_t0_4_final_closure.py",
    *CLOSURE_RECORD_FILES,
})

SNAPSHOT_PATHS = (
    "arpipe/CLAUDE.md",
    "arpipe/README.md",
    "arpipe/configs/default.yaml",
    "arpipe/models.py",
    "arpipe/triage.py",
    "artifacts/t0_4",
    "configs/t0_4",
    "docs/experiments",
    "tests/t0_4",
    "tools/audit_t0_4_final_closure.py",
    "tools/audit_t0_4_setup.py",
    "tools/build_t0_4_manifest.py",
    "tools/t0_4",
    CORPUS_INVENTORY_RECORDED_HASH,
    *SOURCE_FILES,
)

CELL_FIELDS = ("issuer_id", "sampling_stratum", "era", "representation_class", "length_category")
UNDECLARED_KIND = "__undeclared_page_kind__"

_SHA1 = re.compile(r"[0-9a-f]{40}")


# --------------------------------------------------------------------------
# git access
# --------------------------------------------------------------------------

def _git(repo_root: Path, *args: str) -> bytes:
    return subprocess.run(
        ["git", "-C", str(repo_root), *args], check=True, capture_output=True
    ).stdout


def resolve_commit(repo_root: Path, rev: str) -> str:
    commit = _git(repo_root, "rev-parse", "--verify", f"{rev}^{{commit}}").decode("ascii").strip()
    if not _SHA1.fullmatch(commit):
        raise SetupInvariantError(f"revision does not resolve to a 40-character commit: {rev!r}")
    return commit


def is_ancestor(repo_root: Path, older: str, newer: str) -> bool:
    result = subprocess.run(
        ["git", "-C", str(repo_root), "merge-base", "--is-ancestor", older, newer],
        capture_output=True,
    )
    return result.returncode == 0


def changed_paths(repo_root: Path, before: str, after: str) -> list[str]:
    raw = _git(repo_root, "diff", "--name-only", "--no-renames", "-z", before, after)
    return sorted(item for item in raw.decode("utf-8").split("\0") if item)


def last_touching_commit(repo_root: Path, commit: str, rel: str) -> str:
    found = _git(repo_root, "log", "-1", "--format=%H", commit, "--", rel).decode("ascii").strip()
    if not _SHA1.fullmatch(found):
        raise SetupInvariantError(f"source metadata is not committed at the audited commit: {rel}")
    return found


def materialize_snapshot(repo_root: Path, commit: str, destination: Path) -> list[str]:
    raw = _git(repo_root, "ls-tree", "-r", "-z", "--name-only", commit, "--", *SNAPSHOT_PATHS)
    files = sorted(item for item in raw.decode("utf-8").split("\0") if item)
    for rel in files:
        target = destination / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(_git(repo_root, "cat-file", "blob", f"{commit}:{rel}"))
    return files


def _text(root: Path, rel: str) -> str:
    return (root / rel).read_text(encoding="utf-8")


# --------------------------------------------------------------------------
# Check 1: vector_text route
# --------------------------------------------------------------------------

_ROUTE_WORDS = re.compile(r"\b(NATIVE|LEGACY|REMAP)\b|native (?:extraction|text)")
_ROUTE_MAPPING = re.compile(r"""["']vector_text["']\s*[:=]\s*["'](NATIVE|LEGACY|OCR|REMAP)["']""")
_PREREG_ROUTE = re.compile(r"`vector_text` is routed to OCR")


def _json_mapping_keys(value: Any, token: str, pointer: str = "") -> Iterable[str]:
    if isinstance(value, dict):
        for key, child in value.items():
            if key == token:
                yield f"{pointer}/{key}"
            yield from _json_mapping_keys(child, token, f"{pointer}/{key}")
    elif isinstance(value, list):
        for index, child in enumerate(value):
            yield from _json_mapping_keys(child, token, f"{pointer}/{index}")


def _json_string_mentions(value: Any, token: str, pointer: str = "") -> Iterable[tuple[str, str]]:
    if isinstance(value, dict):
        for key, child in value.items():
            yield from _json_string_mentions(child, token, f"{pointer}/{key}")
    elif isinstance(value, list):
        for index, child in enumerate(value):
            yield from _json_string_mentions(child, token, f"{pointer}/{index}")
    elif isinstance(value, str) and token in value:
        yield pointer, value


def evaluate_vector_text_route(root: Path) -> dict[str, Any]:
    """Trace `vector_text` through detector, routing config, prereg, configs and harness."""
    triage = _text(root, "arpipe/triage.py")
    models = _text(root, "arpipe/models.py")
    contract = _text(root, "arpipe/CLAUDE.md")
    readme = _text(root, "arpipe/README.md")
    default_cfg = _text(root, "arpipe/configs/default.yaml")
    prereg = _text(root, PREREGISTRATION)
    contradictions: list[str] = []

    needs_ocr = re.search(r"NEEDS_OCR\s*=\s*\{([^}]*)\}", triage)
    members = sorted(set(re.findall(r"PageKind\.([A-Z_]+)", needs_ocr.group(1)))) if needs_ocr else []
    router_uses_set = bool(re.search(
        r"def ocr_page_numbers\(.*?\n\s+return \[[^\]]*\bin NEEDS_OCR\]", triage, re.S))
    classifier_branch = bool(re.search(
        r"n_drawings >= VECTOR_PATH_TEXT_THRESHOLD:\s*\n\s*return PageKind\.VECTOR_TEXT", triage))
    enum_comment = re.search(r'VECTOR_TEXT\s*=\s*"vector_text"\s*#\s*(.+)', models)
    threshold_comment = re.search(r"VECTOR_PATH_TEXT_THRESHOLD\s*=\s*\d+\s*#\s*(.+)", triage)
    contract_line = re.search(r"^vector-text\s+(.+?)\s+->\s+(\w+)\s*$", contract, re.MULTILINE)

    detector_route = "OCR" if ("VECTOR_TEXT" in members and router_uses_set) else None
    declared = {
        "arpipe/models.py": (re.search(r"->\s*(\w+)", enum_comment.group(1)).group(1)
                             if enum_comment and "->" in enum_comment.group(1) else None),
        "arpipe/CLAUDE.md": contract_line.group(2) if contract_line else None,
    }
    for path, route in declared.items():
        if route is not None and route != detector_route:
            contradictions.append(f"{path} declares {route} but the detector routes {detector_route}")

    threshold_lines = [line for line in default_cfg.splitlines() if "vector" in line.lower()]
    routing_config = {
        "sources": ["arpipe/configs/default.yaml"],
        "stance": "DETECTION_THRESHOLD_ONLY_NO_ROUTE_TABLE",
        "vector_keys": sorted(line.split(":", 1)[0].strip() for line in threshold_lines),
    }

    prereg_route = bool(_PREREG_ROUTE.search(prereg))
    for sentence in re.split(r"(?<=[.;])\s+", prereg):
        if "`vector_text`" in sentence and _ROUTE_WORDS.search(sentence):
            contradictions.append("preregistration sentence pairs vector_text with a non-OCR route word")

    config_mentions: list[dict[str, str]] = []
    for path in sorted((root / "configs/t0_4").glob("*.json")):
        parsed = read_json(path)
        rel = path.relative_to(root).as_posix()
        for pointer in _json_mapping_keys(parsed, "vector_text"):
            contradictions.append(f"{rel} maps vector_text to a value at {pointer}")
        for pointer, text in _json_string_mentions(parsed, "vector_text"):
            if _ROUTE_WORDS.search(text):
                contradictions.append(f"{rel}{pointer} pairs vector_text with a non-OCR route word")
        text = path.read_text(encoding="utf-8")
        if "vector_text" in text:
            config_mentions.append({"path": rel, "role": "CLASS_STRATUM_OR_LABEL_NOT_A_ROUTE"})

    harness_files: list[str] = []
    for path in sorted((root / "tools/t0_4").glob("*.py")):
        if path.name == "closure.py":
            continue
        source = path.read_text(encoding="utf-8")
        for match in _ROUTE_MAPPING.finditer(source):
            if match.group(1) != "OCR":
                contradictions.append(f"{path.name} routes vector_text to {match.group(1)}")
        if "vector_text" in source:
            harness_files.append(path.relative_to(root).as_posix())

    if contradictions:
        status = FAIL
    elif detector_route is None:
        status = UNRESOLVED
    elif prereg_route:
        status = PASS
    else:
        status = UNRESOLVED

    return {
        "status": status,
        "registered_route": detector_route,
        "source_of_registered_route": [
            "arpipe/triage.py#NEEDS_OCR",
            "arpipe/models.py#PageKind.VECTOR_TEXT",
        ],
        "frozen_rationale": {
            "arpipe/models.py": enum_comment.group(1).strip() if enum_comment else None,
            "arpipe/CLAUDE.md": (f"{contract_line.group(1)} -> {contract_line.group(2)}"
                                 if contract_line else None),
            "arpipe/triage.py": threshold_comment.group(1).strip() if threshold_comment else None,
        },
        "layers": {
            "text_layer_detector_definition": {
                "sources": ["arpipe/models.py", "arpipe/triage.py"],
                "stance": "EXPLICIT_ROUTE" if detector_route else "NO_ROUTE",
                "route": detector_route,
                "needs_ocr_members": members,
                "router_returns_needs_ocr_pages": router_uses_set,
                "classifier_branch_present": classifier_branch,
            },
            "project_design_contract": {
                "sources": ["arpipe/CLAUDE.md", "arpipe/README.md"],
                "stance": "EXPLICIT_ROUTE" if declared["arpipe/CLAUDE.md"] else "NO_ROUTE",
                "route": declared["arpipe/CLAUDE.md"],
                "readme_lists_vector_text_as_router_class": "vector-text" in readme,
            },
            "routing_configuration": routing_config,
            "t0_4_preregistration": {
                "sources": [PREREGISTRATION],
                "stance": "EXPLICIT_ROUTE" if prereg_route else "CLASS_LISTED_ROUTE_NOT_STATED",
                "route": "OCR" if prereg_route else None,
            },
            "t0_4_benchmark_configuration": {
                "sources": [item["path"] for item in config_mentions],
                "stance": "CLASS_STRATUM_OR_LABEL_ONLY_NO_ROUTE_MAPPING",
                "gold_route_vocabulary_contains_ocr": "OCR" in read_json(
                    root / "configs/t0_4/oracle_routing_spec.json")["gold_routes"],
            },
            "t0_4_execution_harness": {
                "sources": harness_files,
                "stance": "SETUP_ONLY_NO_ROUTE_DISPATCH",
            },
        },
        "contradictions": sorted(contradictions),
        "all_representations_agree": not contradictions and detector_route == "OCR" and prereg_route,
    }


# --------------------------------------------------------------------------
# Check 2: sampling-cell inspection
# --------------------------------------------------------------------------

def _rank(seed: str, document_id: str, page_number: int) -> str:
    payload = b"\x00".join((seed.encode("utf-8"), document_id.encode("utf-8"), str(page_number).encode("ascii")))
    return hashlib.sha256(payload).hexdigest()


def cell_identifier(key: Sequence[str]) -> str:
    return "|".join(key)


def declared_category_levels(root: Path) -> dict[str, list[str]]:
    """Levels declared by frozen sources: partition file, sampling spec, schema, detector."""
    spec = read_json(root / SAMPLING_SPEC)
    unit_props = read_json(root / MANIFEST_SCHEMA)["properties"]["track_a"]["properties"]["units"]["items"]["properties"]
    models = _text(root, "arpipe/models.py")
    block = re.search(r"class PageKind\(.*?\):(.*?)(?=^class )", models, re.S | re.M).group(1)
    kinds = re.findall(r'^\s+[A-Z_]+\s*=\s*"([a-z_]+)"', block, re.M)
    representations = {_representation_class(kind) for kind in kinds} | {_representation_class(UNDECLARED_KIND)}
    return {
        "issuer_id": sorted({row["issuer_id"] for row in read_csv(root / ISSUER_SPLIT)}),
        "sampling_stratum": sorted(spec["sampling_stratum_priority"]),
        "era": sorted(unit_props["era"]["enum"]),
        "representation_class": sorted(representations),
        "length_category": sorted(unit_props["length_category"]["enum"]),
    }


def analyze_cells(root: Path) -> dict[str, Any]:
    """Independently group every profiled page into its coverage cell and rank it."""
    spec = read_json(root / SAMPLING_SPEC)
    seed = spec["sampling_seed"]
    documents = {row["document_id"]: row for row in read_csv(root / CORPUS_INVENTORY)}
    issuer_split = {row["issuer_id"]: row["split"] for row in read_csv(root / ISSUER_SPLIT)}
    auxiliary, table_pages, language_pages = _page_auxiliary_sets(root)

    available: Counter[tuple[str, ...]] = Counter()
    best: dict[tuple[str, ...], tuple[str, str, int]] = {}
    pages: dict[tuple[str, int], dict[str, Any]] = {}
    for profile in read_csv(root / PAGE_PROFILE):
        document_id = profile["document_id"]
        doc = documents[document_id]
        page_number = int(profile["physical_page"])
        fiscal_year = int(doc["fiscal_year"])
        key = (document_id, page_number)
        if key in pages:
            raise SetupInvariantError(f"page profile repeats physical page {key}")
        labels, _ = _page_conditions(
            profile, fiscal_year, auxiliary.get(key, set()), key in table_pages, language_pages.get(key, set())
        )
        cell = (
            doc["company_id"],
            _sampling_stratum(labels),
            "pre_2015" if fiscal_year < 2015 else "post_2015",
            _representation_class(profile.get("kind", "other")),
            _length_category(doc),
        )
        rank = _rank(seed, document_id, page_number)
        available[cell] += 1
        if cell not in best or (rank, document_id, page_number) < best[cell]:
            best[cell] = (rank, document_id, page_number)
        pages[key] = {
            "cell": cell, "rank": rank, "fiscal_year": fiscal_year, "labels": labels,
            "split": issuer_split[doc["company_id"]],
        }
    return {
        "seed": seed,
        "available": available,
        "best": best,
        "pages": pages,
        "auxiliary": auxiliary,
        "table_pages": table_pages,
        "language_pages": language_pages,
        "issuer_split": issuer_split,
        "selection_rule_id": spec["sample_size_rule"]["type"],
    }


def _selection_status(available: int, selected: int) -> str:
    if selected == 0:
        return "VIOLATION_NO_PAGE_SELECTED"
    if selected > 1:
        return "VIOLATION_MULTIPLE_PAGES_SELECTED"
    return "SELECTED_EXACTLY_ONE_SINGLETON_CELL" if available == 1 else "SELECTED_EXACTLY_ONE"


def _cell_key_of(unit: Mapping[str, Any]) -> tuple[str, ...]:
    return tuple(str(unit[field]) for field in CELL_FIELDS)


def inspect_sampling_cells(root: Path, analysis: Mapping[str, Any]) -> dict[str, Any]:
    manifest = read_json(root / MANIFEST)
    units = manifest["track_a"]["units"]
    available: Mapping[tuple[str, ...], int] = analysis["available"]
    levels = declared_category_levels(root)
    selected: dict[tuple[str, ...], list[tuple[str, int]]] = {}
    for unit in units:
        selected.setdefault(_cell_key_of(unit), []).append((unit["document_id"], unit["page_number"]))

    violations: list[dict[str, Any]] = []
    cells: list[dict[str, Any]] = []
    for key in sorted(available):
        chosen = sorted(selected.get(key, []))
        status = _selection_status(available[key], len(chosen))
        if status.startswith("VIOLATION"):
            violations.append({"cell_id": cell_identifier(key), "status": status})
        expected = analysis["best"][key]
        if len(chosen) == 1 and chosen[0] != (expected[1], expected[2]):
            violations.append({"cell_id": cell_identifier(key), "status": "VIOLATION_NOT_MINIMUM_RANK_PAGE"})
        cells.append({
            "cell_id": cell_identifier(key),
            "issuer_id": key[0],
            "sampling_stratum": key[1],
            "era": key[2],
            "representation_class": key[3],
            "length_category": key[4],
            "available_physical_pages": available[key],
            "selected_physical_page_count": len(chosen),
            "selected_pages": [[document_id, page] for document_id, page in chosen],
            "selection_status": status,
        })
    for key in sorted(set(selected) - set(available)):
        violations.append({"cell_id": cell_identifier(key), "status": "VIOLATION_SELECTED_IN_ZERO_AVAILABILITY_CELL"})

    physical = [(unit["document_id"], unit["page_number"]) for unit in units]
    if len(physical) != len(set(physical)):
        violations.append({"cell_id": "*", "status": "VIOLATION_DUPLICATE_PHYSICAL_PAGE"})

    counts = sorted(available.values())
    observed = set(available)
    product = itertools.product(*(levels[field] for field in CELL_FIELDS))
    zero_digest = hashlib.sha256()
    zero_count = declared_count = 0
    for key in product:
        declared_count += 1
        if key not in observed:
            zero_count += 1
            zero_digest.update(cell_identifier(key).encode("utf-8") + b"\n")

    singleton_keys = [key for key in observed if available[key] == 1]
    return {
        "definitions": {
            "observed_cell": (
                "A (issuer_id, sampling_stratum, era, representation_class, length_category) "
                "combination that occurs on at least one profiled physical page of the frozen corpus metadata."
            ),
            "zero_availability_cell": (
                "A combination in the Cartesian product of the declared category levels that contains "
                "zero physical pages; it is never called observed and is never filled."
            ),
            "physical_page_key": ["document_id", "page_number"],
        },
        "declared_levels": {
            "issuer_id_count": len(levels["issuer_id"]),
            "sampling_stratum": levels["sampling_stratum"],
            "era": levels["era"],
            "representation_class": levels["representation_class"],
            "length_category": levels["length_category"],
        },
        "declared_cell_count": declared_count,
        "observed_cell_count": len(observed),
        "zero_availability_cell_count": zero_count,
        "zero_availability_cells_sha256": zero_digest.hexdigest(),
        "declared_levels_with_no_observed_page": {
            field: sorted(set(levels[field]) - {key[index] for key in observed})
            for index, field in enumerate(CELL_FIELDS) if field != "issuer_id"
        },
        "singleton_observed_cell_count": len(singleton_keys),
        "singleton_observed_cells_by_stratum": dict(sorted(Counter(key[1] for key in singleton_keys).items())),
        "singleton_observed_cells_by_split": dict(sorted(
            Counter(analysis["issuer_split"][key[0]] for key in singleton_keys).items())),
        "available_pages": {
            "minimum": counts[0],
            "median": statistics.median(counts),
            "maximum": counts[-1],
        },
        "selected_page_count_distribution": dict(sorted(Counter(
            str(cell["selected_physical_page_count"]) for cell in cells).items())),
        "total_unique_selected_physical_pages": len(set(physical)),
        "units_with_multiple_condition_labels": sum(1 for unit in units if len(unit["condition_labels"]) >= 2),
        "invariant_each_observed_cell_selects_exactly_one_page": not violations,
        "violations": violations,
        "cells": cells,
    }


# --------------------------------------------------------------------------
# Check 3: sampling metadata provenance
# --------------------------------------------------------------------------

def verify_sampling_provenance(
    root: Path, repo_root: Path, commit: str, analysis: Mapping[str, Any]
) -> dict[str, Any]:
    manifest = read_json(root / MANIFEST)
    problems: list[dict[str, str]] = []

    source_metadata = {
        rel: {"sha256": file_sha256(root / rel), "last_commit": last_touching_commit(repo_root, commit, rel)}
        for rel in sorted(SOURCE_FILES)
    }
    for rel, record in source_metadata.items():
        if manifest["source_hashes"].get(rel) != record["sha256"]:
            problems.append({"severity": FAIL, "message": f"manifest source hash differs from committed blob: {rel}"})

    recorded = (root / CORPUS_INVENTORY_RECORDED_HASH).read_text(encoding="ascii").split()[0]
    corpus_hash = source_metadata[CORPUS_INVENTORY]["sha256"]
    if recorded != corpus_hash:
        problems.append({"severity": FAIL, "message": "corpus inventory hash differs from its recorded freeze hash"})

    sampling_config_hash = file_sha256(root / SAMPLING_SPEC)
    if read_json(root / CONFIG_HASHES)["files"].get(SAMPLING_SPEC) != sampling_config_hash:
        problems.append({"severity": FAIL, "message": "sampling config hash differs from the config hash manifest"})
    manifest_hash = file_sha256(root / MANIFEST)

    rebuilt = canonical_json(build_manifest(root))
    if (root / MANIFEST).read_text(encoding="utf-8") != rebuilt:
        problems.append({"severity": FAIL, "message": "committed benchmark manifest is not the deterministic build"})
    if config_hash_manifest(root) != read_json(root / CONFIG_HASHES):
        problems.append({"severity": FAIL, "message": "committed config hash manifest is stale"})

    seed = analysis["seed"]
    rule_id = analysis["selection_rule_id"]
    records: list[dict[str, Any]] = []
    for unit in sorted(manifest["track_a"]["units"], key=lambda item: cell_identifier(_cell_key_of(item))):
        document_id, page_number = unit["document_id"], unit["page_number"]
        page = analysis["pages"].get((document_id, page_number))
        cell = _cell_key_of(unit)
        if page is None:
            problems.append({"severity": UNRESOLVED, "message": f"selected page has no source row: {document_id}:{page_number}"})
            continue
        checks = {
            "cell": page["cell"] == cell,
            "rank": page["rank"] == unit["selection_rank"] == _rank(seed, document_id, page_number),
            "fiscal_year": page["fiscal_year"] == unit["fiscal_year"],
            "split": page["split"] == unit["split"],
            "condition_labels": page["labels"] == unit["condition_labels"],
            "minimum_rank_in_cell": analysis["best"][cell][1:] == (document_id, page_number),
        }
        for name, ok in checks.items():
            if not ok:
                problems.append({"severity": FAIL, "message": f"{name} not derivable from committed metadata: {document_id}:{page_number}"})
        key = (document_id, page_number)
        supporting = [f"{CORPUS_INVENTORY}#{document_id}", f"{ISSUER_SPLIT}#{unit['issuer_id']}"]
        if key in analysis["auxiliary"]:
            supporting.append(f"{CONDITION_PAGE_MAP}#{document_id}:{page_number}")
        if key in analysis["table_pages"]:
            supporting.append(f"{TABLE_CANDIDATES}#{document_id}:{page_number}")
        if key in analysis["language_pages"]:
            supporting.append(f"{LANGUAGE_CANDIDATES}#{document_id}:{page_number}")
        records.append({
            "cell_id": cell_identifier(cell),
            "document_id": document_id,
            "issuer_id": unit["issuer_id"],
            "page_number": page_number,
            "fiscal_year": unit["fiscal_year"],
            "split": unit["split"],
            "sampling_stratum": unit["sampling_stratum"],
            "condition_labels": unit["condition_labels"],
            "representation_class": unit["representation_class"],
            "era": unit["era"],
            "length_category": unit["length_category"],
            "selection_rule_id": rule_id,
            "selection_rank": unit["selection_rank"],
            "cell_available_pages": analysis["available"][cell],
            "source_metadata_identifier": f"{PAGE_PROFILE}#{document_id}:{page_number}",
            "source_metadata_commit": source_metadata[PAGE_PROFILE]["last_commit"],
            "source_metadata_hash": source_metadata[PAGE_PROFILE]["sha256"],
            "supporting_source_identifiers": supporting,
            "sampling_config_hash": sampling_config_hash,
        })

    severities = {problem["severity"] for problem in problems}
    status = FAIL if FAIL in severities else UNRESOLVED if UNRESOLVED in severities else PASS
    return {
        "status": status,
        "selection_rule": {
            "selection_rule_id": rule_id,
            "sampling_seed": seed,
            "rank_function": "SHA-256 over UTF-8(sampling_seed) NUL UTF-8(document_id) NUL ASCII(decimal page_number)",
            "ordering_key": ["selection_rank", "document_id", "page_number"],
            "selection": "smallest ordering key within each observed coverage cell",
            "source": SAMPLING_SPEC,
        },
        "corpus_manifest_hash": corpus_hash,
        "sampling_config_hash": sampling_config_hash,
        "sampling_manifest_hash": manifest_hash,
        "source_metadata": source_metadata,
        "selected_pages_with_complete_provenance": len(records) if not problems else 0,
        "selected_pages_total": len(manifest["track_a"]["units"]),
        "problems": problems,
        "selected_pages": records,
    }


# --------------------------------------------------------------------------
# Check 4: held-out / holdout / unseen / unobserved terminology
# --------------------------------------------------------------------------

_TERM = re.compile(r"held[-_ ]?out|hold[-_ ]?out|unseen|unobserved", re.IGNORECASE)
_TOKEN = re.compile(r"[A-Za-z0-9_]+")
_CLAUSE_MARKS = ".;,:|"
_COVERAGE_CONTEXT = re.compile(r"\b(cells?|coverage|unavailable)\b", re.IGNORECASE)
_SPLIT_CONTEXT = re.compile(r"FIT|VALIDATION|HOLDOUT|development|freeze|partition|split|tuning|protect", re.IGNORECASE)

SCOPE_GLOBS = (
    "docs/experiments/T0.4_*.md",
    "tools/t0_4/*.md",
    "tools/t0_4/*.py",
    "tools/*t0_4*.py",
    "configs/t0_4/*.json",
    "artifacts/t0_4/*.json",
    "tests/t0_4/*.py",
)
SCOPE_EXCLUDED = frozenset({
    "tools/t0_4/closure.py",
    "tools/audit_t0_4_final_closure.py",
    "tests/t0_4/test_t0_4_final_closure.py",
    "tests/t0_4/test_t0_4_closure_record.py",
    "artifacts/t0_4/final_closure_audit.json",
    "docs/experiments/T0.4_final_closure_audit.md",
})
LISTED_ROLES = frozenset({
    "SPLIT_PROSE", "COVERAGE_TERM", "FINAL_HELD_OUT_EVALUATION", "AMBIGUOUS_HELD_OUT", "AMBIGUOUS_COVERAGE_TERM",
})


def _clause_at(line: str, position: int) -> str:
    """The clause around `position`; table-cell bars and punctuation both end a clause."""
    start = max(line.rfind(mark, 0, position) for mark in _CLAUSE_MARKS) + 1
    ends = [line.find(mark, position) for mark in _CLAUSE_MARKS]
    end = min((item for item in ends if item != -1), default=len(line))
    return line[start:end]


def classify_occurrence(line: str, match: re.Match[str]) -> str:
    term = match.group(0)
    lowered = term.lower()
    if lowered in {"unobserved", "unseen"}:
        return "COVERAGE_TERM" if _COVERAGE_CONTEXT.search(line) else "AMBIGUOUS_COVERAGE_TERM"
    clause = _clause_at(line, match.start())
    if re.fullmatch(r"held[-_ ]?out", lowered):
        only_holdout = "HOLDOUT" in clause and not re.search(r"\b(FIT|VALIDATION|development)\b", clause)
        final = re.search(r"final held[- ]out evaluation", clause, re.IGNORECASE)
        return "FINAL_HELD_OUT_EVALUATION" if (only_holdout and final) else "AMBIGUOUS_HELD_OUT"
    token = next(item.group(0) for item in _TOKEN.finditer(line) if item.start() <= match.start() < item.end())
    if token.isupper():
        return "SPLIT_LABEL"
    if "_" in token:
        return "SPLIT_IDENTIFIER"
    if "VALIDATION" in clause or not _SPLIT_CONTEXT.search(line):
        return "AMBIGUOUS_HELD_OUT"
    return "SPLIT_PROSE"


def scan_terminology(root: Path) -> dict[str, Any]:
    scoped = sorted({
        path.relative_to(root).as_posix()
        for pattern in SCOPE_GLOBS for path in root.glob(pattern) if path.is_file()
    } - SCOPE_EXCLUDED)
    totals: Counter[str] = Counter()
    per_file: dict[str, Counter[str]] = {}
    listed: list[dict[str, Any]] = []
    for rel in scoped:
        counter = per_file.setdefault(rel, Counter())
        for number, line in enumerate(_text(root, rel).splitlines(), start=1):
            for match in _TERM.finditer(line):
                role = classify_occurrence(line, match)
                counter[role] += 1
                totals[role] += 1
                if role in LISTED_ROLES:
                    listed.append({"path": rel, "line": number, "term": match.group(0).lower(), "role": role})
    ambiguous = [item for item in listed if item["role"].startswith("AMBIGUOUS")]
    return {
        "status": FAIL if ambiguous else PASS,
        "terms_searched": ["held-out", "holdout", "unseen", "unobserved"],
        "scope_files": scoped,
        "occurrence_totals_by_role": dict(sorted(totals.items())),
        "occurrences_by_file_and_role": {rel: dict(sorted(counter.items())) for rel, counter in per_file.items() if counter},
        "listed_occurrences": listed,
        "ambiguous_occurrences": ambiguous,
        "unseen_occurrences": sum(1 for item in listed if item["term"] == "unseen"),
    }


# --------------------------------------------------------------------------
# Static non-execution guards
# --------------------------------------------------------------------------

_FORBIDDEN_IMPORT = re.compile(
    r"^\s*(?:import|from)\s+(?:pytesseract|paddleocr|paddlex|paddle|surya|boto3|google|requests|urllib|httpx|pymupdf|fitz|PIL)\b",
    re.MULTILINE,
)


def scan_static_non_execution(root: Path, files: Sequence[str]) -> dict[str, Any]:
    """Closure code must not import an OCR engine, network client, or PDF library."""
    code_hits = sorted(
        rel for rel in files
        if rel in CLOSURE_CODE_FILES and _FORBIDDEN_IMPORT.search(_text(root, rel))
    )
    pdfs = sorted(rel for rel in files if rel.lower().endswith(".pdf"))
    results = sorted(
        path.name for path in (root / "artifacts/t0_4").glob("*")
        if path.is_file() and path.name not in {
            "benchmark_manifest.json", "config_hashes.json", "setup_audit.json", "final_closure_audit.json"}
    )
    return {"engine_or_api_imports": code_hits, "pdf_files_in_snapshot": pdfs, "unexpected_result_artifacts": results}


# --------------------------------------------------------------------------
# Orchestration
# --------------------------------------------------------------------------

def decide_closure(statuses: Mapping[str, str]) -> str:
    ok = (
        statuses["vector_text_route"] == PASS
        and statuses["sampling_cell_inspection"] in {PASS, PASS_SPARSE}
        and statuses["sampling_metadata_provenance"] == PASS
        and statuses["held_out_terminology"] == PASS
    )
    return CLOSED if ok else OPEN


def run_closure_audit(repo_root: Path, audited_rev: str = "HEAD") -> dict[str, Any]:
    repo_root = repo_root.resolve()
    after = resolve_commit(repo_root, audited_rev)
    before = resolve_commit(repo_root, PRE_CLOSURE_COMMIT)
    for older, newer in ((BASE_COMMIT, before), (before, after)):
        if not is_ancestor(repo_root, older, newer):
            raise SetupInvariantError(f"{older} is not an ancestor of {newer}")
    changed = changed_paths(repo_root, before, after)
    unexpected = sorted(set(changed) - ALLOWED_CLOSURE_CHANGES)
    if unexpected:
        raise SetupInvariantError(f"closure changed paths outside its allowance: {unexpected}")

    with tempfile.TemporaryDirectory() as scratch:
        snap_after, snap_before = Path(scratch, "after"), Path(scratch, "before")
        after_files = materialize_snapshot(repo_root, after, snap_after)
        materialize_snapshot(repo_root, before, snap_before)

        route = evaluate_vector_text_route(snap_after)
        route_before = evaluate_vector_text_route(snap_before)
        analysis = analyze_cells(snap_after)
        cells = inspect_sampling_cells(snap_after, analysis)
        provenance = verify_sampling_provenance(snap_after, repo_root, after, analysis)
        terminology = scan_terminology(snap_after)
        terminology_before = scan_terminology(snap_before)
        guards = scan_static_non_execution(snap_after, after_files)

    cell_status = FAIL if cells["violations"] else PASS_SPARSE if cells["singleton_observed_cell_count"] else PASS
    statuses = {
        "vector_text_route": route["status"],
        "sampling_cell_inspection": cell_status,
        "sampling_metadata_provenance": provenance["status"],
        "held_out_terminology": terminology["status"],
    }
    unchanged = {
        "frozen_corpus_unchanged": not any(p.startswith(("dataset/corpus_freeze/", "dataset/corpus_gap_audit/")) for p in changed),
        "t0_4_configs_unchanged": not any(p.startswith("configs/t0_4/") for p in changed),
        "t0_4_manifests_unchanged": not any(p in {MANIFEST, CONFIG_HASHES, "artifacts/t0_4/setup_audit.json"} for p in changed),
        "production_arpipe_unchanged": not any(p.startswith("arpipe/") for p in changed),
    }
    clean_guards = not (guards["engine_or_api_imports"] or guards["pdf_files_in_snapshot"] or guards["unexpected_result_artifacts"])
    report = {
        "schema_version": SCHEMA_VERSION,
        "task_id": CLOSURE_TASK_ID,
        "base_commit": BASE_COMMIT,
        "final_commit_before_audit": before,
        "final_commit_after_audit": after,
        "corpus_manifest_hash": provenance["corpus_manifest_hash"],
        "sampling_config_hash": provenance["sampling_config_hash"],
        "sampling_manifest_hash": provenance["sampling_manifest_hash"],
        **statuses,
        "closure_decision": decide_closure(statuses) if clean_guards and all(unchanged.values()) else OPEN,
        "changes_since_final_commit_before_audit": {"changed_paths": changed, **unchanged},
        "corrections": {
            "vector_text_route": {
                "status_at_final_commit_before_audit": route_before["status"],
                "status_at_final_commit_after_audit": route["status"],
            },
            "held_out_terminology": {
                "ambiguous_occurrences_at_final_commit_before_audit": terminology_before["ambiguous_occurrences"],
                "ambiguous_occurrences_at_final_commit_after_audit": terminology["ambiguous_occurrences"],
            },
        },
        "execution_attestations": {
            "api_calls_made": False,
            "benchmark_executed": False,
            "benchmark_results_generated": False,
            "ocr_engines_executed": False,
            "pdfs_acquired": False,
            "pdfs_opened_or_rendered": False,
            "production_behavior_modified": not unchanged["production_arpipe_unchanged"],
        },
        "static_guards": guards,
        "evidence": {
            "vector_text_route": route,
            "sampling_cell_inspection": cells,
            "sampling_metadata_provenance": provenance,
            "held_out_terminology": terminology,
        },
    }
    if contains_absolute_path(canonical_json(report)):
        raise SetupInvariantError("absolute machine path leaked into the closure audit")
    return report
