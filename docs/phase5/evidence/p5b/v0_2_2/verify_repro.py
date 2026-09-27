from __future__ import annotations
import csv, hashlib, json, os
from datetime import datetime, timezone
from pathlib import Path
BASE=Path(r"D:\gold_blind"); OUT=BASE/"output"/"v0_2_2"; SCR=OUT/"scratch"; LOG=SCR/"write_log.csv"
def sha(path: Path)->str:
    h=hashlib.sha256()
    with path.open("rb") as f:
        for b in iter(lambda:f.read(1024*1024),b""): h.update(b)
    return h.hexdigest()
def write(path:Path,data:bytes)->None:
    with path.open("wb") as f:f.write(data);f.flush();os.fsync(f.fileno())
    size=path.stat().st_size
    if size<=0:raise RuntimeError(path)
    with LOG.open("a",encoding="utf-8",newline="") as f:csv.writer(f,lineterminator="\n").writerow([path.relative_to(BASE).as_posix(),size,sha(path),datetime.now(timezone.utc).isoformat()]);f.flush();os.fsync(f.fileno())
def main()->None:
    write(Path(__file__),Path(__file__).read_bytes())
    paths=[OUT/"TITLE_EQUIVALENCE_v0_2_2.md",SCR/"repro"/"run1.md",SCR/"repro"/"run2.md"]
    values=[sha(p) for p in paths]; result={"paths":[p.relative_to(BASE).as_posix() for p in paths],"sha256":values,"reproducible":len(set(values))==1}
    write(SCR/"repro_results.json",(json.dumps(result,indent=2)+"\n").encode())
    print(json.dumps(result,indent=2))
    if not result["reproducible"]: print(f"STOP=NOT_REPRODUCIBLE\nOFFENDING_REPR={result!r}\nOFFENDING_LEN={len(result)}");raise SystemExit(2)
if __name__=="__main__":main()
