from __future__ import annotations
import csv, hashlib, json, os
from datetime import datetime, timezone
from pathlib import Path
BASE=Path(r"D:\gold_blind");OUT=BASE/"output"/"v0_2_2";SCR=OUT/"scratch";LOG=SCR/"write_log.csv"
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
    expected=[]
    for line in (OUT/"HASHES_v0_2_2.txt").read_text(encoding="utf-8").splitlines():
        digest,size,rel=line.split("  ",2);expected.append((digest,int(size),rel))
    mismatches=[]
    for digest,size,rel in expected:
        path=OUT/Path(rel);actual_size=path.stat().st_size if path.exists() else None;actual_hash=sha(path) if path.exists() else None
        if actual_size!=size or actual_hash!=digest:mismatches.append({"path":rel,"expected_size":size,"actual_size":actual_size,"expected_hash":digest,"actual_hash":actual_hash})
    zero=[p.relative_to(OUT).as_posix() for p in OUT.rglob("*") if p.is_file() and p.stat().st_size==0]
    stage=json.loads((SCR/"stage_c_results.json").read_text(encoding="utf-8"));inputs=[]
    for item in stage["c5_inputs"]:
        actual=sha(BASE/Path(item["path"]));inputs.append({"path":item["path"],"unchanged":actual==item["sha256"]})
    result={"manifest_entries":len(expected),"manifest_mismatches":mismatches,"zero_byte_files":zero,"c5_unchanged":sum(r["unchanged"] for r in inputs),"c5_total":len(inputs),"c5_inputs":inputs}
    write(SCR/"i3_results.json",(json.dumps(result,indent=2)+"\n").encode())
    print(f"I3_MANIFEST_ENTRIES={len(expected)}");print(f"I3_MANIFEST_MISMATCHES={len(mismatches)}");print(f"I3_ZERO_BYTE_FILES={len(zero)}");print(f"unchanged: {result['c5_unchanged']} of {result['c5_total']}")
    if mismatches or zero or result["c5_unchanged"]!=result["c5_total"]:raise SystemExit(2)
if __name__=="__main__":main()
