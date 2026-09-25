import concurrent.futures, json, pathlib, subprocess, sys, time
scratch=pathlib.Path.cwd().resolve().parent
phase=sys.argv[1]
r=json.loads((scratch/"preregistration.json").read_text())
ids=r["primary_documents"] if phase=="primary" else r["eligible_smoke"]
logdir=scratch/(phase+"-logs")
logdir.mkdir(exist_ok=False)
def run(docid):
    cmd=[sys.executable,"-c","import runpy; runpy.run_path("+repr(str(scratch/"run_document.py"))+", run_name='__main__')",phase,docid]
    with (logdir/(docid+".log")).open("w",encoding="utf-8") as out:
        p=subprocess.run(cmd,stdout=out,stderr=subprocess.STDOUT)
    return docid,p.returncode
# Bounded independent subprocesses; every document scheduled exactly once.
failures=[]
workers=1 if phase.startswith("smoke") else 3
with concurrent.futures.ThreadPoolExecutor(max_workers=workers) as pool:
    futures={pool.submit(run,d):d for d in ids}
    for future in concurrent.futures.as_completed(futures):
        docid,rc=future.result()
        print(json.dumps({"document_id":docid,"exit_code":rc}),flush=True)
        if rc:
            failures.append(docid)
            for f in futures: f.cancel()
            break
summary={"phase":phase,"scheduled":len(ids),"failures":failures}
(scratch/(phase+"-batch.json")).write_text(json.dumps(summary,indent=2),encoding="utf-8")
assert not failures,summary
