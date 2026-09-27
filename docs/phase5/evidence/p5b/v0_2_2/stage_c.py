from __future__ import annotations

import csv
import hashlib
import json
import os
import re
import stat
from datetime import datetime, timezone
from pathlib import Path

BASE = Path(r"D:\gold_blind")
OUT = BASE / "output" / "v0_2_2"
SCRATCH = OUT / "scratch"
WRITE_LOG = SCRATCH / "write_log.csv"
EXPECTED_FILE = BASE / "P5B22_EXPECTED_HASHES_v2.txt"
EXPECTED_SIZE = 2172
EXPECTED_SHA_LITERAL = "cf8561e833d1b642eca9fa1076f014e47b97ae9808b43123b96df538f2b08b28"
REPARSE = getattr(stat, "FILE_ATTRIBUTE_REPARSE_POINT", 0x400)
READONLY = getattr(stat, "FILE_ATTRIBUTE_READONLY", 0x1)

def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()

def append_log(path: Path, size: int, digest: str) -> None:
    new = not WRITE_LOG.exists()
    with WRITE_LOG.open("a", encoding="utf-8", newline="") as f:
        w = csv.writer(f, lineterminator="\n")
        if new:
            w.writerow(["path", "bytes", "sha256", "utc_time"])
        w.writerow([path.relative_to(BASE).as_posix(), size, digest, datetime.now(timezone.utc).isoformat()])
        f.flush(); os.fsync(f.fileno())

def verify_log(path: Path) -> tuple[int, str]:
    size = path.stat().st_size
    if size <= 0:
        raise RuntimeError(f"ZERO_BYTE_WRITE path={path!s}")
    digest = sha256_file(path)
    append_log(path, size, digest)
    return size, digest

def durable_bytes(path: Path, data: bytes) -> tuple[int, str]:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("wb") as f:
        f.write(data); f.flush(); os.fsync(f.fileno())
    return verify_log(path)

def durable_csv(path: Path, header: list[str], rows: list[list[object]]) -> tuple[int, str]:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as f:
        w = csv.writer(f, lineterminator="\n"); w.writerow(header); w.writerows(rows)
        f.flush(); os.fsync(f.fileno())
    return verify_log(path)

def is_reparse(st: os.stat_result) -> bool:
    return bool(getattr(st, "st_file_attributes", 0) & REPARSE)

def is_readonly(st: os.stat_result) -> bool:
    return bool(getattr(st, "st_file_attributes", 0) & READONLY)

def link_target(path: Path) -> str:
    try:
        return os.readlink(path)
    except OSError as exc:
        return f"UNAVAILABLE:{exc.__class__.__name__}"

def snapshot_rows(root: Path, excluded: Path) -> list[list[object]]:
    rows: list[list[object]] = []
    def visit(directory: Path) -> None:
        with os.scandir(directory) as scan:
            entries = sorted(scan, key=lambda e: e.name.casefold())
        for entry in entries:
            path = Path(entry.path)
            if path == excluded:
                continue
            st = entry.stat(follow_symlinks=False)
            rel = path.relative_to(root).as_posix()
            if is_reparse(st):
                rows.append(["reparse_dir" if entry.is_dir(follow_symlinks=False) else "reparse_file", rel, st.st_size, st.st_mtime_ns, is_readonly(st), "", "REPARSE_POINT", link_target(path)])
            elif entry.is_dir(follow_symlinks=False):
                visit(path)
            elif entry.is_file(follow_symlinks=False):
                digest = "" if path.suffix.casefold() in {".pdf", ".png"} else sha256_file(path)
                rows.append(["file", rel, st.st_size, st.st_mtime_ns, is_readonly(st), digest, "", ""])
    visit(root)
    return rows

def count_readonly(root: Path, excluded: Path) -> int:
    count = 0
    def visit(directory: Path) -> None:
        nonlocal count
        with os.scandir(directory) as scan:
            entries = sorted(scan, key=lambda e: e.name.casefold())
        for entry in entries:
            path = Path(entry.path); st = entry.stat(follow_symlinks=False)
            if path == excluded:
                continue
            if is_reparse(st):
                if entry.is_file(follow_symlinks=False) and is_readonly(st): count += 1
            elif entry.is_dir(follow_symlinks=False):
                visit(path)
            elif entry.is_file(follow_symlinks=False) and is_readonly(st):
                count += 1
    visit(root)
    return count

def stop(reason: str, values: object, hashed: list[tuple[Path, str]]) -> None:
    rows = []
    for path, prior in hashed:
        actual = sha256_file(path); rows.append([path.relative_to(BASE).as_posix(), prior, actual, actual == prior])
    payload = {"verdict": f"P5_B22_BLOCKED:{reason}", "offending_repr": repr(values), "offending_len": len(values) if hasattr(values, "__len__") else None, "rehash": rows, "unchanged": f"{sum(r[3] for r in rows)} of {len(rows)}"}
    durable_bytes(SCRATCH / "STOP.json", (json.dumps(payload, indent=2, ensure_ascii=False) + "\n").encode())
    print(json.dumps(payload, indent=2, ensure_ascii=False)); raise SystemExit(2)

def main() -> None:
    durable_bytes(Path(__file__), Path(__file__).read_bytes())
    header = ["entry_type", "relative_path", "size", "mtime_ns", "read_only", "sha256", "link_type", "target"]
    start = snapshot_rows(BASE, OUT)
    durable_csv(SCRATCH / "snapshot_start.csv", header, start)
    ro_count = count_readonly(BASE / "output", OUT)
    durable_bytes(SCRATCH / "c3_metadata.json", (json.dumps({"read_only_flag_count_under_output": ro_count}, indent=2) + "\n").encode())
    print(f"C3_SNAPSHOT_ROWS={len(start)}"); print(f"C3_READ_ONLY_FLAG_COUNT={ro_count}")

    print(f"C4_LITERAL_REPR={EXPECTED_SHA_LITERAL!r}"); print(f"C4_LITERAL_LEN={len(EXPECTED_SHA_LITERAL)}")
    size = EXPECTED_FILE.stat().st_size; actual_sha = sha256_file(EXPECTED_FILE)
    if size != EXPECTED_SIZE or actual_sha != EXPECTED_SHA_LITERAL:
        stop("EXPECTED_FILE_MISMATCH", {"path": str(EXPECTED_FILE), "literal_repr": repr(EXPECTED_SHA_LITERAL), "literal_len": len(EXPECTED_SHA_LITERAL), "actual_size": size, "actual_hash": actual_sha}, [(EXPECTED_FILE, actual_sha)])
    print(f"C4_ACTUAL_SIZE={size}"); print(f"C4_ACTUAL_SHA256={actual_sha}")

    raw = EXPECTED_FILE.read_text(encoding="utf-8"); lines = raw.splitlines(keepends=True)
    expected: list[tuple[Path, str]] = []
    if len(lines) != 22:
        stop("INVALID_EXPECTED_HASH", {"line_number": None, "repr": repr(raw), "len": len(lines), "path": str(EXPECTED_FILE)}, [(EXPECTED_FILE, actual_sha)])
    for line_no, raw_line in enumerate(lines, 1):
        clean = raw_line.rstrip("\r\n")
        if "  " not in clean:
            stop("INVALID_EXPECTED_HASH", {"line_number": line_no, "repr": repr(clean), "len": len(clean), "path": ""}, [(EXPECTED_FILE, actual_sha)] + expected)
        digest, rel = clean.split("  ", 1)
        if re.fullmatch(r"[0-9a-f]{64}", digest) is None:
            stop("INVALID_EXPECTED_HASH", {"line_number": line_no, "repr": repr(digest), "len": len(digest), "path": rel}, [(EXPECTED_FILE, actual_sha)] + expected)
        path = BASE / Path(rel); got = sha256_file(path)
        if got != digest:
            stop("INPUT_HASH_MISMATCH", {"line_number": line_no, "repr": repr(digest), "len": len(digest), "path": rel, "expected": digest, "actual": got}, [(EXPECTED_FILE, actual_sha)] + expected + [(path, got)])
        expected.append((path, got))
    print(f"C5_MATCHED_INPUTS={len(expected)}")

    index_path = BASE / "output" / "v0_2" / "EVIDENCE_INDEX.csv"
    with index_path.open("r", encoding="utf-8", newline="") as f: index_rows = list(csv.DictReader(f))
    evidence_dir = BASE / "output" / "v0_2" / "evidence_pages"; mismatches = []
    st = evidence_dir.stat(follow_symlinks=False)
    referenced: dict[str, str] = {}
    if is_reparse(st): mismatches.append({"path": str(evidence_dir), "reason": "reparse_point", "target": link_target(evidence_dir)})
    else:
        for row_no, row in enumerate(index_rows, 2):
            name, digest = row["png"], row["sha256"]
            if name in referenced and referenced[name] != digest: mismatches.append({"row": row_no, "png": name, "reason": "inconsistent_hash"})
            referenced[name] = digest
        for name, digest in sorted(referenced.items()):
            path = evidence_dir / name
            if not path.is_file(): mismatches.append({"png": name, "reason": "missing"})
            else:
                got = sha256_file(path)
                if got != digest: mismatches.append({"png": name, "reason": "hash", "expected": digest, "actual": got})
        actual_pngs = sorted(p.name for p in evidence_dir.iterdir() if p.is_file() and p.suffix.casefold() == ".png")
        for name in sorted(set(actual_pngs) - set(referenced)): mismatches.append({"png": name, "reason": "extra"})
        if len(index_rows) != 259 or len(referenced) != 146: mismatches.append({"reason": "count", "rows": len(index_rows), "distinct": len(referenced)})
    if mismatches: stop("EVIDENCE_PNG_MISMATCH", mismatches, [(EXPECTED_FILE, actual_sha)] + expected)
    print(f"C5_EVIDENCE_ROWS={len(index_rows)}"); print(f"C5_DISTINCT_PNGS={len(referenced)}")

    failure_root = BASE / "output" / "v0_2_1"; failure_rows = []
    def visit_failure(directory: Path) -> None:
        with os.scandir(directory) as scan: entries = sorted(scan, key=lambda e: e.name.casefold())
        for entry in entries:
            path = Path(entry.path); fst = entry.stat(follow_symlinks=False); rel = path.relative_to(failure_root).as_posix()
            if is_reparse(fst): failure_rows.append([rel, fst.st_size, "", fst.st_size == 0, "REPARSE_POINT", link_target(path)])
            elif entry.is_dir(follow_symlinks=False): visit_failure(path)
            elif entry.is_file(follow_symlinks=False): failure_rows.append([rel, fst.st_size, sha256_file(path), fst.st_size == 0, "file", ""])
    visit_failure(failure_root)
    durable_csv(OUT / "V0_2_1_FAILURE_RECORD.csv", ["relative_path", "bytes", "sha256", "is_zero_bytes", "entry_type", "target"], failure_rows)
    results = {"git_output": "fatal: not a git repository (or any of the parent directories): .git", "c5_input_count": len(expected), "c5_inputs": [{"path": p.relative_to(BASE).as_posix(), "sha256": h} for p, h in expected], "evidence_index_rows": len(index_rows), "distinct_evidence_pngs": len(referenced), "read_only_flag_count_under_output": ro_count, "failure_record_rows": len(failure_rows), "failure_record_zero_byte_files": [r[0] for r in failure_rows if r[3]], "F-BUILDER-DRIFT": "RESOLVED AS K-I: expected list now taken from output/v0_2/HASHES_v0_2.txt; see K-I"}
    durable_bytes(SCRATCH / "stage_c_results.json", (json.dumps(results, indent=2, ensure_ascii=False) + "\n").encode())
    print(f"C6_FAILURE_RECORD_ROWS={len(failure_rows)}"); print("STAGE_C=PASS")

if __name__ == "__main__": main()
