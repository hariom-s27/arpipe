from __future__ import annotations
import csv, hashlib, os
from datetime import datetime, timezone
from pathlib import Path
BASE=Path(r"D:\gold_blind");OUT=BASE/"output"/"v0_2_2";LOG=OUT/"scratch"/"write_log.csv";MANIFEST=OUT/"HASHES_v0_2_2.txt"
def sha(path:Path)->str:
    h=hashlib.sha256()
    with path.open("rb") as f:
        for b in iter(lambda:f.read(1024*1024),b""):h.update(b)
    return h.hexdigest()
def log(path:Path)->None:
    size=path.stat().st_size
    if size<=0:raise RuntimeError(path)
    with LOG.open("a",encoding="utf-8",newline="") as f:csv.writer(f,lineterminator="\n").writerow([path.relative_to(BASE).as_posix(),size,sha(path),datetime.now(timezone.utc).isoformat()]);f.flush();os.fsync(f.fileno())
def write(path:Path,data:bytes)->None:
    with path.open("wb") as f:f.write(data);f.flush();os.fsync(f.fileno())
    log(path)
def main()->None:
    write(Path(__file__),Path(__file__).read_bytes())
    files=[]
    for path in OUT.rglob("*"):
        if not path.is_file() or path==MANIFEST or OUT/"scratch" in path.parents:continue
        files.append(path)
    files.sort(key=lambda p:p.relative_to(OUT).as_posix())
    lines=[f"{sha(p)}  {p.stat().st_size}  {p.relative_to(OUT).as_posix()}" for p in files]
    write(MANIFEST,("\n".join(lines)+"\n").encode("utf-8"))
    print(f"HASH_MANIFEST_ENTRIES={len(lines)}")
if __name__=="__main__":main()
