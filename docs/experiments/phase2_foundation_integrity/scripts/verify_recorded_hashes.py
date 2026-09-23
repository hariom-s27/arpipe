# Phase-2 READ_ONLY hash verifier: recompute sha256 of Git blobs at the closure commit and compare with every
# recorded (path, sha256) pair in frozen manifests. Writes only to stdout / a JSON in the scratchpad.
import json, re, subprocess, hashlib, sys, collections, csv, io, os

CLOSURE = '63e3c047a09044d9c3bd9c61e3b56a01612f3d11'
OUT = sys.argv[1] if len(sys.argv) > 1 else None


def blob(path, commit=CLOSURE):
    r = subprocess.run(['git', 'show', f'{commit}:{path}'], capture_output=True)
    return r.stdout if r.returncode == 0 else None


def sha(b):
    return hashlib.sha256(b).hexdigest()


results = []


def rec(source, path, recorded, note=''):
    b = blob(path)
    if b is None:
        results.append(dict(source=source, path=path, recorded=recorded, actual=None, status='UNVERIFIED_HASH:path_not_in_tree', note=note))
        return
    a = sha(b)
    results.append(dict(source=source, path=path, recorded=recorded, actual=a, status='MATCH' if a == recorded else 'MISMATCH', note=note))


# 1. T0 hashes/*.sha256
for f in ['challenge', 'corpus_inventory', 'development', 'holdout', 'validation']:
    src = f'dataset/corpus_freeze/hashes/{f}.sha256'
    h, name = blob(src).decode().split()
    rec(src, f'dataset/corpus_freeze/{name}', h)
# 2. audit_config.sha256 (two locations)
for src in ['configs/audit_config.sha256', 'dataset/corpus_gap_audit/audit_config.sha256']:
    h, name = blob(src).decode().split()
    rec(src, os.path.dirname(src) + '/' + name, h)
# 3. T0.1 input_hashes.json (bare filenames: try corpus_freeze then corpus_gap_audit)
for src in ['dataset/corpus_gap_audit/input_hashes.json', 'dataset/corpus_gap_audit/run_01/input_hashes.json', 'dataset/corpus_gap_audit/run_02/input_hashes.json']:
    d = json.loads(blob(src))
    for name, h in d.items():
        cand = [p for p in (f'dataset/corpus_freeze/{name}', f'dataset/corpus_gap_audit/{name}') if blob(p) is not None]
        rec(src, cand[0] if cand else f'dataset/corpus_freeze/{name}', h)
# 4. raw_input_manifest.json
src = 'dataset/corpus_gap_audit/reconciled/raw_input_manifest.json'
d = json.loads(blob(src))
for i in d['inputs']:
    rec(src, i['artifact_path'], i['sha256'], note='source_commit=' + str(i.get('source_commit')))
# 5. reconciliation_manifest.json
src = 'dataset/corpus_gap_audit/reconciled/reconciliation_manifest.json'
d = json.loads(blob(src))
for name, h in d['config_files'].items():
    rec(src, f'configs/t0_1r/{name}', h)
for name, h in d['derived_output_hashes'].items():
    rec(src, f'dataset/corpus_gap_audit/reconciled/{name}', h)
# 6. T0.2 / T0.3A / R1 immutable manifests
for src in ['dataset/corpus_gap_audit/t0_2_robustness_gate/t0_2_immutable_input_manifest.json',
            'dataset/corpus_gap_audit/t0_3a_document_coverage/t0_3a_immutable_input_manifest.json',
            'dataset/corpus_gap_audit/t0_3a_r1_document_coverage/t0_3a_r1_immutable_input_manifest.json']:
    d = json.loads(blob(src))
    for i in d['inputs']:
        rec(src, i['path'], i['sha256'])
# 7. T0.4 config_hashes.json
src = 'artifacts/t0_4/config_hashes.json'
d = json.loads(blob(src))
for p, h in d['files'].items():
    rec(src, p, h)
# 8. T0.4 setup_audit + closure record scalar hashes
sa = json.loads(blob('artifacts/t0_4/setup_audit.json'))
rec('artifacts/t0_4/setup_audit.json', 'artifacts/t0_4/benchmark_manifest.json', sa['manifest_sha256'], note='manifest_sha256')
rec('artifacts/t0_4/setup_audit.json', 'artifacts/t0_4/benchmark_manifest.json', sa['deterministic_repeat_sha256'], note='deterministic_repeat_sha256')
cl = json.loads(blob('artifacts/t0_4/final_closure_audit.json'))
print("closure record top-level keys:", list(cl.keys()))


def walk(o, trail=''):
    if isinstance(o, dict):
        for k, v in o.items():
            yield from walk(v, trail + '/' + str(k))
    elif isinstance(o, list):
        for i, v in enumerate(o[:5]):
            yield from walk(v, trail + f'[{i}]')
    else:
        yield trail, o


for k in ['corpus_manifest_hash', 'sampling_config_hash', 'sampling_manifest_hash']:
    if k in cl:
        print('closure', k, cl[k])
# 9. Manifest 'source_hashes' inside the benchmark manifest
bm = json.loads(blob('artifacts/t0_4/benchmark_manifest.json'))
for p, h in bm['source_hashes'].items():
    rec('artifacts/t0_4/benchmark_manifest.json:source_hashes', p, h)
# 10. closure record: source_metadata table if present
def find_source_meta(o):
    if isinstance(o, dict):
        if 'source_metadata' in o: return o['source_metadata']
        for v in o.values():
            r = find_source_meta(v)
            if r is not None: return r
    elif isinstance(o, list):
        for v in o:
            r = find_source_meta(v)
            if r is not None: return r
    return None
sm = find_source_meta(cl)
print("closure source_metadata found:", type(sm).__name__, (list(sm)[:6] if isinstance(sm, (dict, list)) else sm))

# ---- Phase-1 report claims
p1 = subprocess.run(['git', 'show', 'e52166f:docs/experiments/PHASE1_FROZEN_FOUNDATION_VERIFICATION.md'], capture_output=True, text=True, encoding='utf-8').stdout
rows = re.findall(r'^\|\s*`([^`]+)`\s*\|\s*`([0-9a-f]{64})`', p1, flags=re.M)
for path, h in rows:
    rec('PHASE1_report_table', path, h)

# ---- summarise
c = collections.Counter(r['status'] for r in results)
print('\nTOTAL recorded (path,hash) pairs checked:', len(results), dict(c))
bysrc = collections.defaultdict(collections.Counter)
for r in results:
    bysrc[r['source']][r['status']] += 1
for s, cc in bysrc.items():
    print(f'  {s:100s}', dict(cc))
print('\n--- MISMATCH / UNVERIFIED detail ---')
for r in results:
    if r['status'] != 'MATCH':
        print(f"[{r['status']}] {r['source']}\n    path={r['path']}\n    recorded={r['recorded']}\n    actual  ={r['actual']}  {r['note']}")
if OUT:
    json.dump(results, open(OUT, 'w', encoding='utf-8'), indent=1)
