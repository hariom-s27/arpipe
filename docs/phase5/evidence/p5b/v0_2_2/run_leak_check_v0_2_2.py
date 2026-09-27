from __future__ import annotations
import csv, hashlib, json, os, re
from datetime import datetime, timezone
from pathlib import Path
BASE=Path(r"D:\gold_blind"); OUT=BASE/"output"/"v0_2_2"; LOG=OUT/"scratch"/"write_log.csv"
DOC_RE=re.compile(r"\bIN[A-Z0-9]{10}(?:_\d{4})?\b"); HEX_RE=re.compile(r"\b[0-9a-fA-F]{64}\b"); PAGE_RE=re.compile(r"\b(?:p|pg|page)\.?\s?\d+\b",re.I); SECTOR_RE=re.compile(r"\b(?:bank|banking|institution|PSU)\b",re.I)
def sha(path:Path)->str:
    h=hashlib.sha256()
    with path.open("rb") as f:
        for b in iter(lambda:f.read(1024*1024),b""):h.update(b)
    return h.hexdigest()
def write(path:Path,data:bytes)->None:
    with path.open("wb") as f:f.write(data);f.flush();os.fsync(f.fileno())
    size=path.stat().st_size
    if size<=0:raise RuntimeError(path)
    with LOG.open("a",encoding="utf-8",newline="") as f:csv.writer(f,lineterminator="\n").writerow([path.relative_to(BASE).as_posix(),size,sha(path),datetime.now(timezone.utc).isoformat()]);f.flush();os.fsync(f.fileno())
def company_names()->list[str]:
    manifest=BASE/"FIT_BLIND_MANIFEST.csv"
    with manifest.open("r",encoding="utf-8",newline="") as f:
        reader=csv.DictReader(f); fields=list(reader.fieldnames or []); rows=list(reader)
    name_field=next((field for field in fields if "name" in field.casefold()),None)
    if name_field:return sorted({r[name_field].strip() for r in rows if r[name_field].strip()},key=str.casefold)
    names=[]
    for path in sorted((BASE/"output"/".p5b_work"/"pass1").glob("*.md"),key=lambda p:p.name.casefold()):
        with path.open("r",encoding="utf-8",errors="replace") as f:first=f.readline().strip()
        match=re.search(r"IN[A-Z0-9]{10}_\d{4}",first)
        tail=first[match.end():] if match else first
        tail=re.sub(r"^[\s#|:;–—-]+","",tail).strip()
        if tail:names.append(tail)
    return sorted(set(names),key=str.casefold)
def title_text(line:str)->str|None:
    m=re.match(r"^- `(.+)`(?:\s|$)",line);return m.group(1) if m else None
def main()->None:
    write(Path(__file__),Path(__file__).read_bytes())
    names=company_names(); name_patterns=[(name,re.compile(r"(?<!\w)"+re.escape(name)+r"(?!\w)",re.I)) for name in names]
    blocking=[]; possible=[]
    targets=[OUT/"TITLE_EQUIVALENCE_v0_2_2.md",OUT/"build_title_equivalence_v0_2_2.py"]
    for path in targets:
        lines=path.read_text(encoding="utf-8").splitlines(); conditional_section=False; dict_section=False
        for number,line in enumerate(lines,1):
            if path.suffix==".md" and line.startswith("### "):conditional_section=line=="### CONDITIONAL"
            if path.suffix==".py" and line.startswith("CONDITIONAL_CONTEXTS = {"):dict_section=True
            elif path.suffix==".py" and dict_section and line=="}":dict_section=False
            for label,pattern in (("document_id_or_isin",DOC_RE),("sha256_literal",HEX_RE),("page_reference",PAGE_RE)):
                for match in pattern.finditer(line):blocking.append({"file":path.relative_to(BASE).as_posix(),"line":number,"pattern":label,"match":match.group(0),"text_origin":"title" if title_text(line) is not None else "builder_or_prose"})
            for name,pattern in name_patterns:
                for match in pattern.finditer(line):blocking.append({"file":path.relative_to(BASE).as_posix(),"line":number,"pattern":"company_name","match":match.group(0),"text_origin":"title" if title_text(line) is not None else "builder_or_prose"})
            is_context=(path.suffix==".md" and conditional_section and "**Context**:" in line) or (path.suffix==".py" and dict_section and ": " in line)
            if is_context:
                for match in SECTOR_RE.finditer(line):blocking.append({"file":path.relative_to(BASE).as_posix(),"line":number,"pattern":"sector_in_conditional_context","match":match.group(0),"text_origin":"conditional_context"})
            title=title_text(line)
            if title is not None:
                for name in names:
                    first=name.split()[0] if name.split() else ""
                    if first and re.search(r"(?<!\w)"+re.escape(first)+r"(?!\w)",title,re.I):possible.append({"file":path.relative_to(BASE).as_posix(),"line":number,"pattern":"company_first_word_in_title","match":first,"title":title,"company_name":name})
    result={"blocking_count":len(blocking),"blocking_hits":blocking,"possible_count":len(possible),"possible_hits":possible,"company_names_loaded":len(names),"builder_text_changes":[]}
    write(OUT/"LEAK_CHECK_v0_2_2.json",(json.dumps(result,indent=2,ensure_ascii=False)+"\n").encode())
    for hit in blocking:print("BLOCKING="+json.dumps(hit,ensure_ascii=False,sort_keys=True))
    for hit in possible:print("POSSIBLE="+json.dumps(hit,ensure_ascii=False,sort_keys=True))
    print(f"BLOCKING_HITS={len(blocking)}");print(f"POSSIBLE_HITS={len(possible)}")
    if blocking:
        if any(h["text_origin"]=="title" for h in blocking):print("STOP=LEAK_IN_LEDGER_TEXT");raise SystemExit(2)
        raise SystemExit(3)
if __name__=="__main__":main()
