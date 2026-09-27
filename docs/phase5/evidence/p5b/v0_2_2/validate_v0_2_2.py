from __future__ import annotations
import csv, hashlib, json, os, re
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path

BASE=Path(r"D:\gold_blind"); OUT=BASE/"output"/"v0_2_2"; SCR=OUT/"scratch"; V02=BASE/"output"/"v0_2"; LOG=SCR/"write_log.csv"; FRAME_ID="OBS_INE00FF01025_2015_p0000_BODY_occ1_dd9826bd"
F_REPRO="HISTORICAL: prior audit reported that v0.2 builder output differs from v0.2 .md; not re-run in P5-B.2.2 by design."
CLASS_ORDER=["EQUIVALENT","CONDITIONAL","NOT EQUIVALENT BUT CONFUSABLE","UNRESOLVED"]
def sha(path:Path)->str:
    h=hashlib.sha256()
    with path.open("rb") as f:
        for b in iter(lambda:f.read(1024*1024),b""):h.update(b)
    return h.hexdigest()
def log(path:Path)->None:
    size=path.stat().st_size
    if size<=0:raise RuntimeError(f"ZERO_BYTE_WRITE {path}")
    with LOG.open("a",encoding="utf-8",newline="") as f:csv.writer(f,lineterminator="\n").writerow([path.relative_to(BASE).as_posix(),size,sha(path),datetime.now(timezone.utc).isoformat()]);f.flush();os.fsync(f.fileno())
def write_bytes(path:Path,data:bytes)->None:
    with path.open("wb") as f:f.write(data);f.flush();os.fsync(f.fileno())
    log(path)
def write_text(path:Path,text:str)->None:write_bytes(path,text.encode("utf-8"))
def read_csv(path:Path)->tuple[list[str],list[dict[str,str]]]:
    with path.open("r",encoding="utf-8",newline="") as f:
        r=csv.DictReader(f);return list(r.fieldnames or []),list(r)
def check(cid:str,expected:object,measured:object,passed:bool)->dict[str,object]:return {"id":cid,"expected":expected,"measured":measured,"status":"PASS" if passed else "FAIL"}
def majority(distribution:dict[str,int])->str:
    if not distribution:return "NONE"
    high=max(distribution.values());leaders=sorted(k for k,v in distribution.items() if v==high)
    return leaders[0] if len(leaders)==1 else "TIE:"+"|".join(leaders)
def integrity_markdown(summary:dict[str,object])->str:
    lines=["# INTEGRITY_REPORT_v0_2_2.md","",f"Verdict: **{summary['verdict']}**","","| Check | Expected | Measured | Status |","|---|---|---|---|"]
    for c in summary["checks"]:
        e=json.dumps(c["expected"],ensure_ascii=False,sort_keys=True) if not isinstance(c["expected"],str) else c["expected"]
        m=json.dumps(c["measured"],ensure_ascii=False,sort_keys=True) if not isinstance(c["measured"],str) else c["measured"]
        lines.append(f"| {c['id']} | {e.replace('|','/')} | {m.replace('|','/')} | {c['status']} |")
    lines.extend(["","## Reconciliation findings","",f"- Match levels: `{json.dumps(summary['e3']['match_level_counts'],sort_keys=True)}`",f"- Class status: `{json.dumps(summary['e3']['class_status_counts'],sort_keys=True)}`",f"- Overlap entries: `{summary['e3']['overlap_entries']}`",f"- Unmatched ledger rows: `{json.dumps(summary['e3']['unmatched_ledger_rows_by_class'],sort_keys=True)}`",f"- Majority-ledger-class split: `{json.dumps(summary['e3']['majority_ledger_class_split'],sort_keys=True)}`",""])
    return "\n".join(lines)
def method_note(summary:dict[str,object])->str:
    source=(V02/"METHOD_NOTE_v0_2.md").read_text(encoding="utf-8").splitlines()
    key_start=next(i for i,l in enumerate(source) if l.startswith("In accordance with protocol standards, observation identity"))
    key_end=next(i for i in range(key_start+1,len(source)) if source[i].startswith("#### Ledger Schema"))
    key_block="\n".join(source[key_start:key_end]).strip()
    rule=next(l for l in source if "If the independent human spot-check finds more than 5%" in l).strip()
    zeros=summary["v0_2_1_zero_byte_files"]; cond=[x["title"] for x in summary["single_document_titles"] if x["catalog_class"]=="CONDITIONAL"]
    attempts=summary["attempt_blocked_folders"]
    counts=summary["findings"]["F-COUNTS"]
    lines=["# METHOD_NOTE_v0_2_2.md","","## Change from v0.2","","One ledger row was moved to frame status. The catalog builder now carries over catalog entries and records L1/L2 reconciliation findings without changing titles or classes. The leak check covers the title document and builder source. Reproducibility is checked against two copied runs.","","## Observation identity","",key_block,"","## Quality-control fallback rule","",rule,"","## Coverage computation","",f"The coverage line uses `{summary['coverage']['columns']['viewed']}` and `{summary['coverage']['columns']['required']}`. Text-layer-only rows use `{summary['coverage']['columns']['text_layer_only']}`.","",summary["coverage"]["line"],"","## Known issues","",f"- K-A — v0.2.1 FAILED: `V0_2_1_FAILURE_RECORD.csv` lists the zero-byte files: {json.dumps(zeros,ensure_ascii=False)}.","- K-B — INFERRED: an earlier audit executed the v0.2 builder inside `v0_2`, overwrote `TITLE_EQUIVALENCE_v0_2.md`, and edited it back. Its current bytes passed C5.","- K-C — INFERRED: earlier runs read Claude Code session logs under `C:\\Users\\hario\\.claude\\projects\\` without disclosing that access in their reports.",f"- K-D — INFERRED: {F_REPRO} The prior builder contained a document ID in a text string. F-BUILDER-DRIFT: {summary['findings']['F-BUILDER-DRIFT']}",f"- K-E — F-COUNTS: {json.dumps(counts,ensure_ascii=False,sort_keys=True)}.",f"- K-F — {summary['coverage']['text_layer_only_equivalent_conditional_rows']} EQUIVALENT/CONDITIONAL rows are text-layer-only.",f"- K-G — Single-document CONDITIONAL titles needing a rules-reviewer decision: {json.dumps(cond,ensure_ascii=False)}.",f"- K-H — Attempt 1 stopped at INVALID_EXPECTED_HASH; attempt 2 stopped at OUTPUT_NOT_EMPTY; attempt 3 stopped at INPUT_HASH_MISMATCH. Read-only flags at C3: {summary['read_only_flag_count']}. Snapshot-only blocked-attempt folders: {json.dumps(attempts,ensure_ascii=False)}.","- K-J — VERIFIED by attempts 4–5: the v0.2 title list is a curated catalog and cannot be re-derived by grouping ledger headings. Attempt 4 began inventing a selection rule and stopped. Attempt 5 stopped at the first untraceable entry. This run carries over and reconciles the catalog; mismatches go to the rules reviewer.","- K-K — Class-count history: P5-B.2 reported 24/11/45/1; P5-B.2.1 and re-intake reported 28/6/46; verified catalog tags are 21/12/47/1. The first two are not catalog-tag counts. The majority-ledger-class split is recorded in `P5B22_SUMMARY.json`.",f"- K-L — Logged visual coverage is {summary['coverage']['viewed']}/{summary['coverage']['required']} = {summary['coverage']['pct']}%; an earlier document quoted 22.5% for the same numerator and denominator.","- K-I — VERIFIED by hashes; cause INFERRED: four v0.2 non-data files — `METHOD_NOTE_v0_2.md`, `build_title_equivalence.py`, `run_leak_check.py`, and `validate_integrity.py` — have LastWriteTime 2026-09-27 13:42 and differ from hashes printed in the P5-B.2 chat report while matching `output/v0_2/HASHES_v0_2.txt`, which passed C5. All v0.2 data inputs used here match both records. The rewriting session is not established. The copied rule and key text come from the current version.",""]
    return "\n".join(lines)
def main()->None:
    write_bytes(Path(__file__),Path(__file__).read_bytes())
    source_fields,source=read_csv(V02/"TITLE_EVIDENCE_LEDGER_v0_2.csv"); fields,ledger=read_csv(OUT/"TITLE_EVIDENCE_LEDGER_v0_2_2.csv"); _,frame=read_csv(OUT/"FRAME_STATUS_v0_2_2.csv"); _,prov=read_csv(OUT/"PROVENANCE_v0_2_2.csv"); idx_fields,index=read_csv(OUT/"EVIDENCE_INDEX_v0_2_2.csv"); _,recon=read_csv(OUT/"TITLE_CATALOG_RECONCILIATION_v0_2_2.csv"); _,mapping=read_csv(OUT/"TITLE_CATALOG_MAP_v0_2_2.csv"); _,failure_record=read_csv(OUT/"V0_2_1_FAILURE_RECORD.csv")
    stage=json.loads((SCR/"stage_c_results.json").read_text(encoding="utf-8")); build=json.loads((SCR/"build_results.json").read_text(encoding="utf-8")); leak=json.loads((OUT/"LEAK_CHECK_v0_2_2.json").read_text(encoding="utf-8")); repro=json.loads((SCR/"repro_results.json").read_text(encoding="utf-8"))
    retained_source=[r for r in source if r["obs_id"]!=FRAME_ID]; new_by={r["obs_id"]:r for r in ledger}; diffs=[r["obs_id"] for r in retained_source if new_by.get(r["obs_id"])!=r]; removed=sorted(set(r["obs_id"] for r in source)-set(new_by))
    checks=[];checks.append(check("G1",{"ledger_rows":3215,"frame_rows":1,"source_rows":3216},{"ledger_rows":len(ledger),"frame_rows":len(frame),"sum":len(ledger)+len(frame),"source_rows":len(source)},len(ledger)==3215 and len(frame)==1 and len(ledger)+len(frame)==len(source)==3216))
    provenance_copy=sha(OUT/"PROVENANCE_v0_2_2.csv")==sha(V02/"PROVENANCE_v0_2.csv")
    d4_same=all({k:v for k,v in row.items() if k not in {"evidence_type","png_location"}}==source_row for row,source_row in zip(index,read_csv(V02/"EVIDENCE_INDEX.csv")[1]))
    checks.append(check("G2",{"retained_field_differences":0,"only_removed_obs_id":FRAME_ID,"provenance_byte_copy":True,"evidence_other_fields_differences":0},{"retained_field_differences":len(diffs),"removed_obs_ids":removed,"provenance_byte_copy":provenance_copy,"evidence_other_fields_differences":0 if d4_same else 1},not diffs and removed==[FRAME_ID] and provenance_copy and d4_same))
    with (BASE/"FIT_BLIND_MANIFEST.csv").open("r",encoding="utf-8-sig",newline="") as f: manifest=list(csv.DictReader(f))
    manifest_map={r["document_id"]:r["source_pdf_sha256"] for r in manifest}; all_docs={r["document_id"]:r["pdf_sha256"] for r in ledger}; all_docs.update({r["document_id"]:r["pdf_sha256"] for r in frame}); hash_mismatch={d:{"actual":h,"manifest":manifest_map.get(d)} for d,h in all_docs.items() if manifest_map.get(d)!=h}
    checks.append(check("G3",{"documents":60,"manifest_hash_mismatches":0},{"documents":len(all_docs),"manifest_hash_mismatches":hash_mismatch},len(all_docs)==60 and not hash_mismatch and set(all_docs)==set(manifest_map)))
    keys=[(r["document_id"],r["page_0based"],r["location"],r["heading_text_verbatim"],r["occurrence_index"]) for r in ledger]; key_dupes=len(keys)-len(set(keys)); ids=[r["obs_id"] for r in ledger]; id_dupes=len(ids)-len(set(ids)); pages={r["document_id"]:int(r["page_count"]) for r in prov}; bad_pages=[r["obs_id"] for r in ledger if not (0<=int(r["page_0based"])<pages[r["document_id"]])]
    checks.append(check("G4",{"key_duplicates":0,"obs_id_duplicates":0,"out_of_range_pages":0},{"key_duplicates":key_dupes,"obs_id_duplicates":id_dupes,"out_of_range_pages":len(bad_pages)},key_dupes==0 and id_dupes==0 and not bad_pages))
    type_counts=Counter(r["evidence_type"] for r in index); evid_ids={r["obs_id"] for r in index}; ec_missing=[r["obs_id"] for r in ledger if r["assigned_class"] in {"EQUIVALENT","CONDITIONAL"} and r["obs_id"] not in evid_ids]; pngs={r["png"]:r["sha256"] for r in index}; png_bad=[name for name,d in pngs.items() if sha(V02/"evidence_pages"/name)!=d]
    checks.append(check("G5",{"rows":259,"types":{"STRUCTURAL_TITLE_EVIDENCE":258,"FRAME_STATUS_EVIDENCE":1},"missing_equivalent_conditional":0,"distinct_pngs":146,"png_hash_mismatches":0},{"rows":len(index),"types":dict(type_counts),"missing_equivalent_conditional":len(ec_missing),"distinct_pngs":len(pngs),"png_hash_mismatches":len(png_bad)},len(index)==259 and type_counts==Counter({"STRUCTURAL_TITLE_EVIDENCE":258,"FRAME_STATUS_EVIDENCE":1}) and not ec_missing and len(pngs)==146 and not png_bad))
    catalog_split=Counter(r["catalog_class"] for r in recon); checks.append(check("G6",{"entries":80,"class_split":{"EQUIVALENT":21,"CONDITIONAL":12,"NOT EQUIVALENT BUT CONFUSABLE":47}},{"entries":len(recon),"class_split":dict(catalog_split)},len(recon)==80 and catalog_split==Counter({"EQUIVALENT":21,"CONDITIONAL":12,"NOT EQUIVALENT BUT CONFUSABLE":47})))
    obs_counts=Counter(r["assigned_class"] for r in ledger); expected_obs={"EQUIVALENT":150,"CONDITIONAL":66,"NOT EQUIVALENT BUT CONFUSABLE":2999}; checks.append(check("G7",expected_obs,dict(obs_counts),dict(obs_counts)==expected_obs))
    level_counts=Counter(r["match_level"] for r in recon); status_counts=Counter(r["class_status"] for r in recon); overlap_entries=sum(r["overlap"]=="TRUE" for r in recon); complete=len(recon)==80 and all(r["match_level"] in {"L1","L2","NONE"} and r["class_status"] in {"AGREES","CONFLICT","NONE"} for r in recon)
    mapped_ids={r["obs_id"] for r in mapping}; unmatched=Counter(r["assigned_class"] for r in ledger if r["obs_id"] not in mapped_ids); majority_split=Counter(majority({k:int(v) for k,v in json.loads(r["ledger_class_distribution"]).items()}) for r in recon)
    e3={"match_level_counts":dict(sorted(level_counts.items())),"class_status_counts":dict(sorted(status_counts.items())),"overlap_entries":overlap_entries,"unmatched_ledger_rows_by_class":dict(sorted(unmatched.items())),"majority_ledger_class_split":dict(sorted(majority_split.items()))}
    checks.append(check("G8",{"entries_reconciled":80,"each_has_match_level_and_class_status":True},{"entries_reconciled":len(recon),**e3},complete))
    checks.append(check("G9",{"blocking_hits":0},{"blocking_hits":leak["blocking_count"],"possible_hits":leak["possible_hits"]},leak["blocking_count"]==0))
    checks.append(check("G10",{"reproducible":True,"historical_finding_recorded":True},{"reproducible":repro["reproducible"],"F-V02-REPRO":F_REPRO},bool(repro["reproducible"])))
    source_md=(V02/"TITLE_EQUIVALENCE_v0_2.md").read_text(encoding="utf-8"); tags=Counter(m.group(1).strip() for m in re.finditer(r"\*\*Class\*\*:\s*([^|\r\n]+)",source_md)); claim={"EQUIVALENT":24,"CONDITIONAL":11,"NOT EQUIVALENT BUT CONFUSABLE":45,"UNRESOLVED":1}; fcounts={"catalog_tag_counts":dict(tags),"p5_b2_report_counts":claim,"p5_b2_report_correct":dict(tags)==claim}
    checks.append(check("G11",{"catalog_class_tags_counted":True,"report_24_11_45_1_assessed":True},fcounts,sum(tags.values())==81 and not fcounts["p5_b2_report_correct"]))
    zero_before=[p.relative_to(BASE).as_posix() for p in OUT.rglob("*") if p.is_file() and p.stat().st_size==0]
    checks.append(check("G12",{"zero_byte_files":0},{"zero_byte_files":zero_before},not zero_before))
    singles=[{"entry_no":int(r["entry_no"]),"title":r["title"],"catalog_class":r["catalog_class"]} for r in recon if int(r["matched_documents"])==1]
    review=[{"entry_no":int(r["entry_no"]),"title":r["title"],"catalog_class":r["catalog_class"],"match_level":r["match_level"],"class_status":r["class_status"],"overlap":r["overlap"],"ledger_class_distribution":json.loads(r["ledger_class_distribution"])} for r in recon if r["class_status"] in {"NONE","CONFLICT"} or r["overlap"]=="TRUE"]
    snap_paths=[]
    with (SCR/"snapshot_start.csv").open("r",encoding="utf-8",newline="") as f:
        for r in csv.DictReader(f):
            m=re.match(r"output/(v0_2_2_attempt[^/]*_blocked)(?:/|$)",r["relative_path"])
            if m and m.group(1) not in snap_paths:snap_paths.append(m.group(1))
    all_pass=all(c["status"]=="PASS" for c in checks); review_items=status_counts.get("NONE",0)+status_counts.get("CONFLICT",0)>0
    verdict="P5_B22_PASS_WITH_REVIEW_ITEMS" if all_pass and review_items else ("P5_B22_PASS" if all_pass else "P5_B22_BLOCKED:VALIDATION_FAILED")
    zero_failure_files=[r["relative_path"] for r in failure_record if r["entry_type"]=="file" and r["is_zero_bytes"].casefold()=="true"]
    summary={"verdict":verdict,"checks":checks,"findings":{"F-BUILDER-DRIFT":stage["F-BUILDER-DRIFT"],"F-V02-REPRO":F_REPRO,"F-COUNTS":fcounts},"e3":e3,"review_entries":review,"single_document_titles":singles,"coverage":build["coverage"],"leak_check":leak,"read_only_flag_count":stage["read_only_flag_count_under_output"],"v0_2_1_zero_byte_files":zero_failure_files,"attempt_blocked_folders":snap_paths,"write_audit":None,"nothing_running":None}
    write_text(OUT/"P5B22_SUMMARY.json",json.dumps(summary,indent=2,ensure_ascii=False)+"\n")
    write_text(OUT/"INTEGRITY_REPORT_v0_2_2.md",integrity_markdown(summary))
    write_text(OUT/"METHOD_NOTE_v0_2_2.md",method_note(summary))
    final_zeros=[p.relative_to(BASE).as_posix() for p in OUT.rglob("*") if p.is_file() and p.stat().st_size==0]
    checks[-1]=check("G12",{"zero_byte_files":0},{"zero_byte_files":final_zeros},not final_zeros)
    all_pass=all(c["status"]=="PASS" for c in checks); summary["checks"]=checks; summary["verdict"]="P5_B22_PASS_WITH_REVIEW_ITEMS" if all_pass and review_items else ("P5_B22_PASS" if all_pass else "P5_B22_BLOCKED:VALIDATION_FAILED")
    write_text(OUT/"P5B22_SUMMARY.json",json.dumps(summary,indent=2,ensure_ascii=False)+"\n");write_text(OUT/"INTEGRITY_REPORT_v0_2_2.md",integrity_markdown(summary));write_text(OUT/"METHOD_NOTE_v0_2_2.md",method_note(summary))
    print(json.dumps(summary,indent=2,ensure_ascii=False))
    if not all_pass:raise SystemExit(2)
if __name__=="__main__":main()
