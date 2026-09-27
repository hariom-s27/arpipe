from __future__ import annotations
import csv, hashlib, json, os, stat
from datetime import datetime, timezone
from pathlib import Path
BASE=Path(r"D:\gold_blind");OUT=BASE/"output"/"v0_2_2";SCR=OUT/"scratch";LOG=SCR/"write_log.csv";REPARSE=getattr(stat,"FILE_ATTRIBUTE_REPARSE_POINT",0x400);READONLY=getattr(stat,"FILE_ATTRIBUTE_READONLY",1)
def sha(path:Path)->str:
    h=hashlib.sha256()
    with path.open("rb") as f:
        for b in iter(lambda:f.read(1024*1024),b""):h.update(b)
    return h.hexdigest()
def is_rep(st:os.stat_result)->bool:return bool(getattr(st,"st_file_attributes",0)&REPARSE)
def is_ro(st:os.stat_result)->bool:return bool(getattr(st,"st_file_attributes",0)&READONLY)
def target(path:Path)->str:
    try:return os.readlink(path)
    except OSError as e:return f"UNAVAILABLE:{e.__class__.__name__}"
def snapshot()->list[list[object]]:
    rows=[]
    def visit(directory:Path)->None:
        with os.scandir(directory) as scan:entries=sorted(scan,key=lambda e:e.name.casefold())
        for entry in entries:
            path=Path(entry.path)
            if path==OUT:continue
            st=entry.stat(follow_symlinks=False);rel=path.relative_to(BASE).as_posix()
            if is_rep(st):rows.append(["reparse_dir" if entry.is_dir(follow_symlinks=False) else "reparse_file",rel,st.st_size,st.st_mtime_ns,is_ro(st),"","REPARSE_POINT",target(path)])
            elif entry.is_dir(follow_symlinks=False):visit(path)
            elif entry.is_file(follow_symlinks=False):rows.append(["file",rel,st.st_size,st.st_mtime_ns,is_ro(st),"" if path.suffix.casefold() in {".pdf",".png"} else sha(path),"",""])
    visit(BASE);return rows
def append_log(path:Path)->None:
    size=path.stat().st_size
    if size<=0:raise RuntimeError(path)
    with LOG.open("a",encoding="utf-8",newline="") as f:csv.writer(f,lineterminator="\n").writerow([path.relative_to(BASE).as_posix(),size,sha(path),datetime.now(timezone.utc).isoformat()]);f.flush();os.fsync(f.fileno())
def write_bytes(path:Path,data:bytes)->None:
    with path.open("wb") as f:f.write(data);f.flush();os.fsync(f.fileno())
    append_log(path)
def write_csv(path:Path,header:list[str],rows:list[list[object]])->None:
    with path.open("w",encoding="utf-8",newline="") as f:w=csv.writer(f,lineterminator="\n");w.writerow(header);w.writerows(rows);f.flush();os.fsync(f.fileno())
    append_log(path)
def main()->None:
    write_bytes(Path(__file__),Path(__file__).read_bytes());header=["entry_type","relative_path","size","mtime_ns","read_only","sha256","link_type","target"];end_rows=snapshot();write_csv(SCR/"snapshot_end.csv",header,end_rows)
    with (SCR/"snapshot_start.csv").open("r",encoding="utf-8",newline="") as f:start={r["relative_path"]:r for r in csv.DictReader(f)}
    end={str(r[1]):dict(zip(header,(str(v) for v in r))) for r in end_rows};changes=[];fields=["entry_type","size","mtime_ns","read_only","sha256","link_type","target"]
    for rel in sorted(set(start)|set(end),key=str.casefold):
        before=start.get(rel);after=end.get(rel)
        if before is None:changes.append(["ADDED",rel,"",json.dumps(after,ensure_ascii=False,sort_keys=True)])
        elif after is None:changes.append(["REMOVED",rel,json.dumps(before,ensure_ascii=False,sort_keys=True),""])
        else:
            changed=[x for x in fields if before[x]!=after[x]]
            if changed:changes.append(["CHANGED:"+",".join(changed),rel,json.dumps(before,ensure_ascii=False,sort_keys=True),json.dumps(after,ensure_ascii=False,sort_keys=True)])
    write_csv(OUT/"WRITE_AUDIT.csv",["change_type","relative_path","before","after"],changes);print(f"WRITE_AUDIT_CHANGES_OUTSIDE_V0_2_2={len(changes)}")
    for row in changes:print("WRITE_AUDIT_ROW="+repr(row))
    if changes:raise SystemExit(2)
if __name__=="__main__":main()
