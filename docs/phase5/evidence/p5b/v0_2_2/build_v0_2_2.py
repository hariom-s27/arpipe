from __future__ import annotations

import csv
import hashlib
import json
import os
from datetime import datetime, timezone
from pathlib import Path

BASE = Path(r"D:\gold_blind")
OUT = BASE / "output" / "v0_2_2"
SCRATCH = OUT / "scratch"
SOURCE = BASE / "output" / "v0_2"
WRITE_LOG = SCRATCH / "write_log.csv"
FRAME_OBS_ID = "OBS_INE00FF01025_2015_p0000_BODY_occ1_dd9826bd"

def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""): h.update(chunk)
    return h.hexdigest()

def append_log(path: Path) -> None:
    size = path.stat().st_size
    if size <= 0: raise RuntimeError(f"ZERO_BYTE_WRITE path={path!s}")
    digest = sha256_file(path)
    with WRITE_LOG.open("a", encoding="utf-8", newline="") as f:
        csv.writer(f, lineterminator="\n").writerow([path.relative_to(BASE).as_posix(), size, digest, datetime.now(timezone.utc).isoformat()])
        f.flush(); os.fsync(f.fileno())

def durable_bytes(path: Path, data: bytes) -> None:
    with path.open("wb") as f: f.write(data); f.flush(); os.fsync(f.fileno())
    append_log(path)

def durable_csv(path: Path, fields: list[str], rows: list[dict[str, str]], lineterminator: str = "\n") -> None:
    with path.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields, dialect="excel", lineterminator=lineterminator); w.writeheader(); w.writerows(rows)
        f.flush(); os.fsync(f.fileno())
    append_log(path)

def read_csv(path: Path) -> tuple[list[str], list[dict[str, str]], str]:
    raw = path.read_bytes(); ending = "\r\n" if b"\r\n" in raw else "\n"
    with path.open("r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f, dialect="excel"); return list(reader.fieldnames or []), list(reader), ending

def fail(reason: str, value: object) -> None:
    print(f"STOP={reason}"); print(f"OFFENDING_REPR={value!r}"); print(f"OFFENDING_LEN={len(value) if hasattr(value, '__len__') else 'NA'}"); raise SystemExit(2)

def main() -> None:
    durable_bytes(Path(__file__), Path(__file__).read_bytes())
    ledger_fields, ledger, ledger_ending = read_csv(SOURCE / "TITLE_EVIDENCE_LEDGER_v0_2.csv")
    frame_rows = [r for r in ledger if "FRAME_ANOMALY" in r["flags"]]
    if len(frame_rows) != 1 or frame_rows[0]["obs_id"] != FRAME_OBS_ID: fail("FRAME_ROW_COUNT", frame_rows)
    frame = frame_rows[0]; retained = [r for r in ledger if r["obs_id"] != FRAME_OBS_ID]
    durable_csv(OUT / "TITLE_EVIDENCE_LEDGER_v0_2_2.csv", ledger_fields, retained, ledger_ending)
    retained_by_id = {r["obs_id"]: r for r in retained}
    differences = [r["obs_id"] for r in ledger if r["obs_id"] != FRAME_OBS_ID and retained_by_id.get(r["obs_id"]) != r]
    if len(retained) != 3215 or differences: fail("LEDGER_TRANSFORMATION_MISMATCH", {"rows": len(retained), "differences": differences})

    index_fields, index_rows, index_ending = read_csv(SOURCE / "EVIDENCE_INDEX.csv")
    frame_evidence = [r for r in index_rows if r["obs_id"] == FRAME_OBS_ID]
    if len(frame_evidence) != 1: fail("FRAME_EVIDENCE_COUNT", frame_evidence)
    ev = frame_evidence[0]
    frame_out = [{"document_id": frame["document_id"], "pdf_sha256": frame["pdf_sha256"], "frame_status": "NOT_AN_ANNUAL_REPORT", "status_basis": frame["note"], "status_label": "INFERRED_AI_READING; pending human confirmation", "evidence_obs_id": frame["obs_id"], "evidence_page_0based": frame["page_0based"], "evidence_png": ev["png"], "evidence_png_sha256": ev["sha256"]}]
    durable_csv(OUT / "FRAME_STATUS_v0_2_2.csv", list(frame_out[0]), frame_out)

    enriched = []
    for row in index_rows:
        item = dict(row); item["evidence_type"] = "FRAME_STATUS_EVIDENCE" if row["obs_id"] == FRAME_OBS_ID else "STRUCTURAL_TITLE_EVIDENCE"; item["png_location"] = "output/v0_2/evidence_pages/" + row["png"]; enriched.append(item)
    durable_csv(OUT / "EVIDENCE_INDEX_v0_2_2.csv", index_fields + ["evidence_type", "png_location"], enriched, index_ending)
    durable_bytes(OUT / "PROVENANCE_v0_2_2.csv", (SOURCE / "PROVENANCE_v0_2.csv").read_bytes())
    change = [{"obs_id": FRAME_OBS_ID, "action": "MOVED_TO_FRAME_STATUS", "from": "TITLE_LEDGER/UNRESOLVED", "to": "FRAME_STATUS/NOT_AN_ANNUAL_REPORT", "reason": "document status is not a printed title"}]
    durable_csv(OUT / "CHANGE_LOG_v0_2_2.csv", list(change[0]), change)

    _, provenance, _ = read_csv(SOURCE / "PROVENANCE_v0_2.csv")
    viewed = sum(int(r["sheets_viewed_logged"]) for r in provenance); required = sum(int(r["sheets_required"]) for r in provenance); pct = 100 * viewed / required
    classes = {r["obs_id"]: r["assigned_class"] for r in retained}
    text_only = sum(1 for r in index_rows if r["page_provenance"] == "TEXT_LAYER_ONLY" and classes.get(r["obs_id"]) in {"EQUIVALENT", "CONDITIONAL"})
    line = f"Logged visual coverage of the underlying reading: {viewed}/{required} contact sheets ({pct:.2f}%); {text_only} EQUIVALENT/CONDITIONAL rows are text-layer-only."
    result = {"source_ledger_rows": len(ledger), "retained_ledger_rows": len(retained), "frame_rows": len(frame_rows), "retained_field_differences": len(differences), "evidence_index_rows": len(index_rows), "coverage": {"viewed": viewed, "required": required, "pct": round(pct, 2), "text_layer_only_equivalent_conditional_rows": text_only, "line": line, "columns": {"viewed": "PROVENANCE_v0_2_2.csv:sheets_viewed_logged", "required": "PROVENANCE_v0_2_2.csv:sheets_required", "text_layer_only": "EVIDENCE_INDEX_v0_2_2.csv:page_provenance joined by obs_id to TITLE_EVIDENCE_LEDGER_v0_2_2.csv:assigned_class"}}}
    durable_bytes(SCRATCH / "build_results.json", (json.dumps(result, indent=2, ensure_ascii=False) + "\n").encode())
    print(json.dumps(result, indent=2, ensure_ascii=False))

if __name__ == "__main__": main()
