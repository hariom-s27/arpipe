from __future__ import annotations
import csv, hashlib, os
from datetime import datetime, timezone
from pathlib import Path

BASE = Path(r"D:\gold_blind"); OUT = BASE / "output" / "v0_2_2"; REPRO = OUT / "scratch" / "repro"; LOG = OUT / "scratch" / "write_log.csv"
def digest(path: Path) -> str:
    h=hashlib.sha256()
    with path.open("rb") as f:
        for b in iter(lambda:f.read(1024*1024),b""): h.update(b)
    return h.hexdigest()
def write(path: Path, data: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("wb") as f: f.write(data); f.flush(); os.fsync(f.fileno())
    size=path.stat().st_size
    if size<=0: raise RuntimeError(path)
    with LOG.open("a",encoding="utf-8",newline="") as f:
        csv.writer(f,lineterminator="\n").writerow([path.relative_to(BASE).as_posix(),size,digest(path),datetime.now(timezone.utc).isoformat()]); f.flush(); os.fsync(f.fileno())
def main() -> None:
    write(Path(__file__),Path(__file__).read_bytes())
    write(REPRO / "build_title_equivalence_v0_2_2.py",(OUT / "build_title_equivalence_v0_2_2.py").read_bytes())
    write(REPRO / "TITLE_EVIDENCE_LEDGER_v0_2_2.csv",(OUT / "TITLE_EVIDENCE_LEDGER_v0_2_2.csv").read_bytes())
    write(REPRO / "TITLE_EQUIVALENCE_v0_2.md",(BASE / "output" / "v0_2" / "TITLE_EQUIVALENCE_v0_2.md").read_bytes())
    print("REPRO_PREPARED")
if __name__=="__main__": main()
