import collections, csv, json, pathlib, sys
scratch=pathlib.Path.cwd().resolve().parent
r=json.loads((scratch/"preregistration.json").read_text())
mode=sys.argv[1]
ids=r["primary_documents"] if mode=="historical" else r["eligible_smoke"]
with open("dataset/corpus_freeze/development_manifest.csv",newline="",encoding="utf-8-sig") as f:
    fit={x["document_id"] for x in csv.DictReader(f) if x["split"]=="FIT"}
inputs=json.loads((scratch/"fit-inputs.json").read_text())
ABSENT=object()
def exact(a,b):
    if type(a) is not type(b):return False
    if isinstance(a,dict):return a.keys()==b.keys() and all(exact(a[k],b[k]) for k in a)
    if isinstance(a,list):return len(a)==len(b) and all(exact(x,y) for x,y in zip(a,b))
    return a==b
def script_map(value):
    if value is ABSENT:return ABSENT
    if value is None:return None
    mapped={}
    for entry in value:
        key=(type(entry["page_no"]).__name__,entry["page_no"])
        assert key not in mapped,("duplicate script page",key)
        mapped[key]=entry
    return mapped
def fields(d,m):
    span=m.get("span",ABSENT)
    f={"located":ABSENT if span is ABSENT else span is not None,
       "start_page":span.get("start_page",ABSENT) if isinstance(span,dict) else ABSENT,
       "end_page":span.get("end_page",ABSENT) if isinstance(span,dict) else ABSENT,
       "grade":m.get("confidence",ABSENT),
       "span_path_nullness":m["path"] is None if "path" in m else ABSENT,
       "per_page_kind":ABSENT,
       "script_map":script_map(d.get("script_map",ABSENT))}
    if isinstance(d.get("pages"),list) and all("page_no" in p and "kind" in p for p in d["pages"]):
        f["per_page_kind"]=[{"page_no":p["page_no"],"kind":p["kind"]} for p in d["pages"]]
    return f
def candidate(phase,docid):
    p=scratch/phase/docid
    paths=list((p/"companies").glob("*/*/document.json"))
    assert len(paths)==1,(phase,docid,paths)
    d=json.loads(paths[0].read_text())
    m=json.loads((paths[0].parent/"mda.json").read_text())
    assert d["company_id"]+"_"+str(d["fy_end"])==docid
    return fields(d,m)
def safe(value):
    if value is ABSENT:return {"unavailable":True}
    if isinstance(value,dict):return {str(k):safe(v) for k,v in value.items()}
    if isinstance(value,list):return [safe(v) for v in value]
    return value
counts={f:collections.Counter() for f in r["fields"]}
documents=[]
for docid in ids:
    assert docid in fit
    if mode=="historical":
        p=pathlib.Path(inputs[docid]["directory"])
        a=fields(json.loads((p/"document.json").read_text()),json.loads((p/"mda.json").read_text()))
        b=candidate("primary",docid)
    else:
        a=candidate("smoke-a",docid);b=candidate("smoke-b",docid)
    results={};differences={}
    for field in r["fields"]:
        av,bv=a[field],b[field]
        if av is ABSENT:
            status="UNAVAILABLE_BOTH" if bv is ABSENT else "NOT_COMPARABLE_HISTORICAL_ABSENCE"
        elif bv is ABSENT:
            status="SCHEMA_RECONSTRUCTION_DIFFERENCE"
        else:
            status="EXACT" if exact(av,bv) else "DIFFERENT"
        results[field]=status;counts[field][status]+=1
        if status in {"DIFFERENT","SCHEMA_RECONSTRUCTION_DIFFERENCE"}:
            if field=="script_map" and isinstance(av,dict) and isinstance(bv,dict):
                pages=[];keys=collections.Counter();numeric_deltas=collections.defaultdict(list)
                for page in sorted(av.keys()|bv.keys(),key=str):
                    left,right=av.get(page,ABSENT),bv.get(page,ABSENT)
                    if exact(left,right):continue
                    changes={}
                    if isinstance(left,dict) and isinstance(right,dict):
                        for key in sorted(left.keys()|right.keys()):
                            lv,rv=left.get(key,ABSENT),right.get(key,ABSENT)
                            if not exact(lv,rv):
                                keys[key]+=1;changes[key]={"historical":safe(lv),"candidate":safe(rv)}
                                if type(lv) in (int,float) and type(rv) in (int,float):numeric_deltas[key].append(abs(rv-lv))
                    else:changes={"page":{"historical":safe(left),"candidate":safe(right)}}
                    pages.append({"page_key":page,"changes":changes})
                differences[field]={"differing_pages":len(pages),"changed_keys":dict(keys),
                                    "max_absolute_numeric_delta":{k:max(v) for k,v in numeric_deltas.items()},"pages":pages}
            else:
                differences[field]={"historical":safe(av),"candidate":safe(bv)}
                if type(av) in (int,float) and type(bv) in (int,float):differences[field]["delta"]=bv-av
    comparable=sum(v in {"EXACT","DIFFERENT"} for v in results.values())
    documents.append({"document_id":docid,"field_results":results,"comparable_fields":comparable,
                      "differences":differences,"attribution":"UNATTRIBUTED" if differences else None})
summary={"mode":mode,"documents_compared":len(documents),
         "fully_comparable_documents":sum(d["comparable_fields"]==7 for d in documents),
         "fully_comparable_exact_matches":sum(d["comparable_fields"]==7 and not d["differences"] for d in documents),
         "exact_on_all_available_comparable_fields":sum(not d["differences"] for d in documents),
         "documents_with_differences":sum(bool(d["differences"]) for d in documents),
         "field_counts":{k:dict(v) for k,v in counts.items()},"documents":documents}
(scratch/(mode+"-comparison.json")).write_text(json.dumps(summary,indent=2),encoding="utf-8")
display={k:v for k,v in summary.items() if k!="documents"}
display["differences"]=[{"document_id":d["document_id"],"differences":{k:({x:y for x,y in v.items() if x!="pages"}) for k,v in d["differences"].items()},"attribution":d["attribution"]} for d in documents if d["differences"]]
print(json.dumps(display,indent=2))
