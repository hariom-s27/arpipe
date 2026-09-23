"""T0.4-LF B1/B2 evidence tests.

These assert facts about the frozen detector, router, corpus metadata and T0.4
configuration that the T0.4-LF blocker record relies on. They read committed
files only: no PDF is opened, no engine or API is called, no gold is created.
They state what the frozen record contains; they do not decide what it should
contain, so they remain true whichever way B1/B2 are later resolved.
"""
from __future__ import annotations

import ast
import csv
import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CONFIG_DIR = ROOT / "configs/t0_4"
ROUTE_WORDS = {"NATIVE", "LEGACY", "OCR", "REMAP"}


def _json(rel: str):
    return json.loads((ROOT / rel).read_text(encoding="utf-8"))


def _pagekind_members() -> dict[str, str]:
    tree = ast.parse((ROOT / "arpipe/models.py").read_text(encoding="utf-8"))
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef) and node.name == "PageKind":
            return {
                stmt.targets[0].id: stmt.value.value
                for stmt in node.body
                if isinstance(stmt, ast.Assign) and isinstance(stmt.value, ast.Constant)
            }
    raise AssertionError("PageKind not found")


def _needs_ocr_members() -> set[str]:
    tree = ast.parse((ROOT / "arpipe/triage.py").read_text(encoding="utf-8"))
    for node in tree.body:
        if isinstance(node, ast.Assign) and getattr(node.targets[0], "id", "") == "NEEDS_OCR":
            return {elt.attr for elt in node.value.elts}
    raise AssertionError("NEEDS_OCR not found")


def _page_profile() -> list[dict[str, str]]:
    with (ROOT / "dataset/corpus_freeze/page_profile.csv").open(encoding="utf-8", newline="") as fh:
        return list(csv.DictReader(fh))


def _walk_pairs(value, path=()):
    if isinstance(value, dict):
        for key, child in value.items():
            yield path + (key,), child
            yield from _walk_pairs(child, path + (key,))
    elif isinstance(value, list):
        for index, child in enumerate(value):
            yield from _walk_pairs(child, path + (index,))


# ---------------------------------------------------------------- B1


def test_b1_frozen_detector_has_no_legacy_font_class():
    assert _pagekind_members() == {
        "DIGITAL": "digital", "SCANNED": "scanned", "HYBRID": "hybrid",
        "BROKEN_TEXT": "broken_text", "VECTOR_TEXT": "vector_text", "BLANK": "blank",
    }


def test_b1_frozen_router_has_no_legacy_or_remap_route():
    assert _needs_ocr_members() == {"SCANNED", "BROKEN_TEXT", "VECTOR_TEXT", "HYBRID"}
    production = "\n".join(p.read_text(encoding="utf-8").lower() for p in (ROOT / "arpipe").glob("*.py"))
    assert "remap" not in production


def test_b1_legacy_indicator_is_definitionally_broken_text():
    source = (ROOT / "tools/freeze_extraction_corpus.py").read_text(encoding="utf-8")
    assert '"cid_or_broken_text_indicator": p["kind"] == "broken_text"' in source
    rows = _page_profile()
    assert len(rows) == 37917
    table = Counter((r["kind"], r["cid_or_broken_text_indicator"]) for r in rows)
    assert table[("broken_text", "True")] == 803
    assert sum(n for (kind, flag), n in table.items() if flag == "True") == 803
    assert sum(n for (kind, flag), n in table.items() if kind == "broken_text") == 803


def test_b1_manifest_legacy_label_coincides_with_broken_text_class():
    units = _json("artifacts/t0_4/benchmark_manifest.json")["track_a"]["units"]
    both = [u for u in units
            if "legacy_font_candidate" in u["condition_labels"] and u["representation_class"] == "broken_text"]
    label_only = [u for u in units
                  if "legacy_font_candidate" in u["condition_labels"] and u["representation_class"] != "broken_text"]
    class_only = [u for u in units
                  if "legacy_font_candidate" not in u["condition_labels"] and u["representation_class"] == "broken_text"]
    assert (len(both), len(label_only), len(class_only)) == (20, 0, 0)


def test_b1_no_frozen_config_maps_legacy_font_to_a_route():
    for path in sorted(CONFIG_DIR.glob("*.json")):
        for keys, child in _walk_pairs(json.loads(path.read_text(encoding="utf-8"))):
            named_legacy = any(isinstance(k, str) and "legacy" in k.lower() for k in keys[-1:])
            if named_legacy and isinstance(child, str):
                assert child not in ROUTE_WORDS, (path.name, keys, child)
            if isinstance(child, dict) and "legacy_font" in child:
                assert child["legacy_font"] not in ROUTE_WORDS, (path.name, keys)
    metrics = _json("configs/t0_4/metrics_spec.json")
    oracle = _json("configs/t0_4/oracle_routing_spec.json")
    # The two registers exist side by side but are never joined by a mapping.
    assert {"legacy_font", "broken_text"} <= set(metrics["levels"]["ROUTING"]["classes"])
    assert oracle["gold_routes"] == ["NATIVE", "LEGACY", "OCR"]
    assert not any("class_to_route" in str(k).lower() or "route_by_class" in str(k).lower()
                   for path in CONFIG_DIR.glob("*.json")
                   for keys, _ in _walk_pairs(json.loads(path.read_text(encoding="utf-8"))) for k in keys)


# ---------------------------------------------------------------- B2


def test_b2_the_two_concepts_coincide_on_every_frozen_page():
    rows = _page_profile()
    broken = {(r["document_id"], r["physical_page"]) for r in rows if r["kind"] == "broken_text"}
    flagged = {(r["document_id"], r["physical_page"]) for r in rows if r["cid_or_broken_text_indicator"] == "True"}
    assert broken == flagged and len(broken) == 803


def test_b2_only_a_sampling_scoped_ordering_names_both_concepts():
    sampling = _json("configs/t0_4/sampling_spec.json")
    order = sampling["sampling_stratum_priority"]
    assert order.index("legacy_font_candidate") < order.index("broken_text")
    holders = []
    for path in sorted(CONFIG_DIR.glob("*.json")):
        for keys, child in _walk_pairs(json.loads(path.read_text(encoding="utf-8"))):
            if isinstance(child, list) and {"legacy_font_candidate", "broken_text"} <= set(map(str, child)):
                holders.append((path.name, keys))
            if isinstance(child, list) and {"legacy_font", "broken_text"} <= set(map(str, child)):
                holders.append((path.name, keys))
    assert sorted(holders) == [
        ("metrics_spec.json", ("levels", "ROUTING", "classes")),
        ("sampling_spec.json", ("sampling_stratum_priority",)),
    ]
    # Neither list is a routing precedence: ROUTING.classes states no ordering semantics,
    # and the sampling list is a priority for choosing one primary sampling stratum.
    for name in ("metrics_spec.json", "oracle_routing_spec.json", "benchmark_config.json"):
        assert "precedence" not in (CONFIG_DIR / name).read_text(encoding="utf-8").lower()
    assert "priority" not in json.dumps(_json("configs/t0_4/metrics_spec.json")).lower()
