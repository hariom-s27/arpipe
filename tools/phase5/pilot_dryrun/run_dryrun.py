"""Synthetic-only rehearsal of the Phase 5 FIT annotation pipeline.

All inputs and workspaces live in a temporary directory outside any repository.
The title-list bypass is explicit and limited to this synthetic runner.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import random
import tempfile
import zipfile
from pathlib import Path

from tools.phase5.annotator import annotator_core, export_role, make_bundle
from tools.phase5.custodian import build_workspaces
from tools.phase5.scoring import raw_ab_agreement


DOCUMENT_IDS = tuple(f"SYNTH_FIT_{number:02d}" for number in range(1, 5))
ROLES = ("ANNOTATOR_A", "ANNOTATOR_B")
FIXED_TIME = "2026-01-01T00:00:00+00:00"
TITLE_OVERRIDE = "SYNTHETIC_TITLE_LIST_TEST_ONLY.txt"


def _outside_repository(path: Path) -> Path:
    resolved = path.resolve()
    for parent in (resolved, *resolved.parents):
        if (parent / ".git").exists():
            raise ValueError(f"dry-run workspace must be outside a repository: {resolved}")
    return resolved


def _write_roster(root: Path, split: str = "FIT") -> tuple[Path, Path]:
    """Create opaque synthetic bytes and a matching, exact-column roster."""
    pdf_dir = root / "pdfs"
    pdf_dir.mkdir()
    roster = root / "roster.csv"
    rng = random.Random(501)
    stream = io.StringIO(newline="")
    writer = csv.writer(stream, lineterminator="\n")
    writer.writerow(build_workspaces.ROSTER_COLUMNS)
    for document_id in DOCUMENT_IDS:
        payload = bytes(rng.randrange(256) for _ in range(512))
        (pdf_dir / f"{document_id}.pdf").write_bytes(payload)
        writer.writerow([document_id, hashlib.sha256(payload).hexdigest(), 8, split])
    roster.write_text(stream.getvalue(), encoding="utf-8", newline="")
    return roster, pdf_dir


def _apply_test_title_override(workspace: Path, *, enabled: bool) -> None:
    placeholder = workspace / make_bundle.PLACEHOLDER_NAME
    if not placeholder.is_file():
        raise ValueError("bundle title-list placeholder is missing")
    if not enabled:
        raise ValueError("synthetic title-list override must be passed explicitly")
    placeholder.unlink()
    (workspace / TITLE_OVERRIDE).write_text(
        "SYNTHETIC TEST ONLY: Management Discussion and Analysis\n",
        encoding="utf-8", newline="\n",
    )


def _answer(document_id: str, role: str) -> dict:
    form = {
        "viewer_page_count": 8,
        "presence_state": "PRESENT",
        "presence_reason_code": "BODY_QUALIFYING_TITLE",
        "primary_span_viewer": (2, 4),
        "viewer_name": "Synthetic viewer",
        "viewer_version": "1",
        "no_repository_access_attested": True,
        "no_system_output_access_attested": True,
    }
    if document_id == DOCUMENT_IDS[1] or (document_id == DOCUMENT_IDS[3] and role == "ANNOTATOR_B"):
        form.update(
            presence_state="ABSENT",
            presence_reason_code="NO_QUALIFYING_BODY_SECTION",
            primary_span_viewer=None,
        )
    elif document_id == DOCUMENT_IDS[2] and role == "ANNOTATOR_B":
        form["primary_span_viewer"] = (3, 4)
    return form


def _read_export(path: Path, role: str) -> tuple[list[dict], dict[str, str]]:
    records = []
    hashes = {}
    with zipfile.ZipFile(path) as archive:
        for name in sorted(archive.namelist()):
            if not name.startswith(f"{role}/") or not name.endswith(".json"):
                continue
            data = archive.read(name)
            digest = hashlib.sha256(data).hexdigest()
            record = json.loads(data)
            if data != annotator_core.canonical_json_bytes(record):
                raise ValueError(f"exported record is not canonical: {name}")
            records.append(record)
            hashes[record["document_id"]] = digest
    if len(records) != len(DOCUMENT_IDS) or set(hashes) != set(DOCUMENT_IDS):
        raise ValueError(f"exported {role} records are incomplete")
    return records, hashes


def _report_markdown(result: dict) -> str:
    agreement = result["agreement"]
    rows = [
        "# P5-C synthetic FIT dry run",
        "",
        "**SYNTHETIC — not a result.** Four opaque byte files exercise tool interfaces only.",
        "",
        "## Steps",
        "",
    ]
    rows.extend(f"- {name}: {status}" for name, status in result["steps"].items())
    rows.extend(["", "## Record SHA-256", ""])
    for role, by_document in result["record_hashes"].items():
        for document_id, digest in by_document.items():
            rows.append(f"- {role} {document_id}: `{digest}`")
    rows.extend([
        "", "## Raw A/B agreement", "",
        f"- Exact state agreement: {agreement['exact_state_agreement']['count']}/{agreement['pair_count']} = {agreement['exact_state_agreement']['value']}",
        f"- Cohen's kappa: {agreement['cohens_kappa']}; PABAK: {agreement['pabak']}",
        f"- PRESENT/PRESENT mean inclusive IoU: {agreement['present_present']['mean_iou']}",
        f"- Full-span matches: {agreement['present_present']['exact_full_span']['count']}/{agreement['present_present']['count']}",
        "- One-page boundary difference: SYNTH_FIT_03 (B starts one viewer page later).",
        "- Presence difference: SYNTH_FIT_04 (A PRESENT, B ABSENT).",
        "", "## PILOT_PLAN §6 soft triggers", "",
    ])
    if result["soft_trigger_evaluation"]["status"] == "BLOCKED":
        rows.append(f"- BLOCKED: {result['soft_trigger_evaluation']['reason']}")
    else:
        for trigger in result["soft_triggers"]:
            rows.append(f"- {trigger['name']}: {'WOULD FIRE' if trigger['would_fire'] else 'would not fire'} — {trigger['basis']}")
    rows.extend([
        "", "## Test-only title-list handling", "",
        "The bundle starts with TITLE_LIST_NOT_YET_FROZEN.txt. This runner refuses to continue unless its explicit synthetic title-list override is enabled. It replaces the placeholder only in temporary synthetic A/B workspaces before sealing; the real tools and repository title list are untouched.",
        "", "## FINDINGS", "",
    ])
    rows.extend(f"- {finding}" for finding in result["findings"])
    return "\n".join(rows) + "\n"


def run_dryrun(report_dir: Path, *, allow_synthetic_title_override: bool = False) -> dict:
    """Run once and write deterministic reports; report_dir may be inside the repo."""
    report_dir = Path(report_dir)
    with tempfile.TemporaryDirectory(prefix="p5c-synthetic-") as temporary:
        root = _outside_repository(Path(temporary))
        roster, pdf_dir = _write_roster(root)
        steps = {"synthetic_inputs": "PASS"}
        bundle = root / "annotator_bundle.zip"
        make_bundle.build_bundle(bundle)
        steps["bundle"] = "PASS"
        workspace_root = root / "workspaces"
        manifest_sha256 = build_workspaces.build_workspaces(roster, pdf_dir, bundle, workspace_root)
        steps["workspaces"] = "PASS"
        record_hashes = {}
        exported_records = {}
        for role in ROLES:
            workspace = workspace_root / role
            _apply_test_title_override(workspace, enabled=allow_synthetic_title_override)
            assignment = annotator_core.load_assignment(workspace / "assignment.csv")
            schema = annotator_core.load_schema(workspace)
            protocol_hash = annotator_core.protocol_version_hash(workspace)
            records_dir = workspace / "records"
            (records_dir / annotator_core.WORKSPACE_ID_NAME).write_text(
                f"ws-{hashlib.sha256(role.encode('ascii')).hexdigest()[:32]}\n",
                encoding="utf-8", newline="\n",
            )
            workspace_id = annotator_core.load_or_create_workspace_id(records_dir)
            for document_id in DOCUMENT_IDS:
                assigned = assignment[document_id]
                annotator_core.verify_pdf(workspace / "pdfs" / f"{document_id}.pdf", assigned["source_pdf_sha256"])
                ctx = {
                    **assigned,
                    "annotator_role": role,
                    "workspace_id": workspace_id,
                    "protocol_version_hash": protocol_hash,
                    "started_at": FIXED_TIME,
                    "completed_at": FIXED_TIME,
                }
                record = annotator_core.build_raw_record(_answer(document_id, role), ctx)
                errors = annotator_core.validate_record(record, schema)
                if errors:
                    raise ValueError(f"{role} {document_id} invalid: {errors}")
                annotator_core.seal_raw_record(records_dir, record, schema)
            steps[f"{role}_records"] = "PASS"
            export_path = root / f"{role}.zip"
            export_role.export_role(records_dir, role, export_path)
            exported_records[role], record_hashes[role] = _read_export(export_path, role)
            steps[f"{role}_export_readback"] = "PASS"
        agreement = raw_ab_agreement(exported_records[ROLES[0]], exported_records[ROLES[1]])
        steps["raw_ab_agreement"] = "PASS"
        steps["report"] = "PASS"
        result = {
            "label": "SYNTHETIC — not a result",
            "steps": steps,
            "workspace_manifest_sha256": manifest_sha256,
            "record_hashes": record_hashes,
            "agreement": agreement,
            "soft_triggers": [],
            "soft_trigger_evaluation": {
                "status": "BLOCKED",
                "reason": "The authorized PILOT_PLAN_v0_1_1.md §6 source is absent from this checkout; trigger thresholds cannot be inferred.",
            },
            "findings": [
                "tools/phase5/annotator/make_bundle.py:36–40 ships an unfrozen-title placeholder; tools/phase5/annotator/annotator_core.py:477–496 has no title-list preflight in the direct sealing API. This synthetic runner adds an explicit temporary-workspace preflight; production tool code is unchanged.",
                "tools/phase5/scoring/__init__.py:294–353 returns no gap-set Jaccard or non-comparable counts, although docs/phase5/SAP_v0_1.md:131–140 calls for both in raw A/B agreement. The dry run records only values this API actually returns.",
            ],
        }
    report_dir.mkdir(parents=True, exist_ok=True)
    (report_dir / "DRYRUN_REPORT.json").write_bytes(annotator_core.canonical_json_bytes(result))
    (report_dir / "DRYRUN_REPORT.md").write_text(_report_markdown(result), encoding="utf-8", newline="\n")
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--report-dir", type=Path, default=Path(__file__).resolve().parent)
    parser.add_argument("--synthetic-title-override", action="store_true")
    args = parser.parse_args()
    run_dryrun(args.report_dir, allow_synthetic_title_override=args.synthetic_title_override)
    print(args.report_dir / "DRYRUN_REPORT.md")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
