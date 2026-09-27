from __future__ import annotations
import csv, hashlib, os, subprocess
from datetime import datetime, timezone
from pathlib import Path
BASE=Path(r"D:\gold_blind");OUT=BASE/"output"/"v0_2_2";LOG=OUT/"scratch"/"write_log.csv";SOURCE=OUT/"HASHES_v0_2_2.txt";DEST=OUT/"HASHES_v0_2_2_OS.txt"
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
def parse(line:str)->tuple[str,int,str]:
    digest,size,rel=line.rstrip("\r\n").split("  ",2);return digest,int(size),rel
def main()->None:
    write(Path(__file__),Path(__file__).read_bytes())
    expected=[parse(line) for line in SOURCE.read_text(encoding="utf-8").splitlines()]
    rows=[]
    for _,size,rel in expected:
        path=OUT/Path(rel)
        quoted=str(path).replace("'","''")
        command=f"(Get-FileHash -Algorithm SHA256 -LiteralPath '{quoted}').Hash"
        proc=subprocess.run(["powershell","-NoProfile","-Command",command],capture_output=True,text=True,check=True)
        rows.append((proc.stdout.strip().lower(),size,rel))
    write(DEST,("\n".join(f"{d}  {s}  {r}" for d,s,r in rows)+"\n").encode("utf-8"))
    agree=len(expected)==len(rows) and all(a[0].casefold()==b[0].casefold() and a[1:]==b[1:] for a,b in zip(expected,rows))
    print(f"OS_HASH_ENTRIES={len(rows)}");print(f"HASH_LISTS_AGREE={agree}")
    if not agree:raise SystemExit(2)
if __name__=="__main__":main()
