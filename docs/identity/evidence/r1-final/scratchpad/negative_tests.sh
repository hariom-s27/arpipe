#!/usr/bin/env bash
# R1-FINAL Step 2E negative tests. Everything happens in a scratch clone under $S.
# The candidate worktree is only read (its Step-2 files are copied out); never written.
set -u
S=/c/Users/hario/AppData/Local/Temp/claude/d--sem-iitk-sem9-thesis/948b3666-670c-4ce4-951f-ff0d9a9b4562/scratchpad
CAND=/d/sem_iitk/sem9/thesis/sep_week1/r1-final
MAIN=/d/sem_iitk/sem9/thesis/sep_week1/arpipe-0.1.0
PY=/d/sem_iitk/sem9/thesis/sep_week1/arpipe-0.1.0/arpipe/.venv/Scripts/python.exe
export PYTHONPATH="$(cygpath -w $S/test-deps)"
N=$S/neg-clone
case "$N" in "$S"/*) ;; *) echo "REFUSING: scratch path not under scratchpad"; exit 9;; esac
rm -rf "$N"
START=$(git -C "$CAND" rev-parse HEAD)
git clone -q --shared -c core.autocrlf=false "$MAIN" "$N"
cd "$N" || exit 9
git checkout -q --detach "$START"
cp "$CAND/conftest.py" conftest.py
cp "$CAND/tests/test_t0_4_amendment_01.py" tests/test_t0_4_amendment_01.py
cp "$CAND/tests/test_phase2_1_semantic_conformance.py" tests/test_phase2_1_semantic_conformance.py
echo "scratch clone: $(pwd)   HEAD=$(git rev-parse HEAD)"
echo "candidate worktree HEAD (untouched)=$(git -C "$CAND" rev-parse HEAD)"
T=tests/test_t0_4_amendment_01.py

echo; echo "=== CONTROL: enforcement tests in the unmodified scratch copy ==="
$PY -m pytest -q -p no:cacheprovider $T 2>&1 | tail -3

echo; echo "=== ROBUSTNESS CONTROL: same tests in a clone with core.autocrlf=true (CRLF working files, LF blobs) ==="
N2=$S/neg-clone-crlf
case "$N2" in "$S"/*) ;; *) echo "REFUSING"; exit 9;; esac
rm -rf "$N2"
git clone -q --shared -c core.autocrlf=true "$MAIN" "$N2"
( cd "$N2" && git checkout -q --detach "$START"   && cp "$CAND/conftest.py" conftest.py && cp "$CAND/tests/test_t0_4_amendment_01.py" tests/   && cp "$CAND/tests/test_phase2_1_semantic_conformance.py" tests/   && printf 'working-file CRLF check: '; $PY -c "print(open('arpipe/triage.py','rb').read().count(b'\r\n'))"   && $PY -m pytest -q -p no:cacheprovider tests/test_t0_4_amendment_01.py 2>&1 | tail -3 )
rm -rf "$N2"
cd "$N" || exit 9

echo; echo "=== NEGATIVE (i): flip exactly one byte of the protected _classify source ==="
$PY - <<'EOF'
import ast, pathlib
p = pathlib.Path("arpipe/triage.py"); data = p.read_bytes()
fn = next(n for n in ast.parse(data).body if isinstance(n, ast.FunctionDef) and n.name == "_classify")
lines = data.split(b"\n")
off = sum(len(l) + 1 for l in lines[: fn.lineno - 1])
seg = b"\n".join(lines[fn.lineno - 1 : fn.end_lineno])
i = seg.index(b"<")
pos = off + i
mut = bytearray(data); mut[pos] = ord(">")
diff = [k for k in range(len(data)) if data[k] != mut[k]]
assert len(mut) == len(data) and len(diff) == 1
p.write_bytes(bytes(mut))
line_no = data[:pos].count(b"\n") + 1
print(f"changed exactly {len(diff)} byte at offset {pos} (file line {line_no}, inside _classify lines {fn.lineno}-{fn.end_lineno})")
print("  before:", lines[line_no - 1].decode().rstrip())
print("  after: ", mut.split(b"\n")[line_no - 1].decode().rstrip())
EOF
$PY -m pytest -q -p no:cacheprovider $T 2>&1 | grep -E '^FAILED|passed|failed'
git checkout -q -- arpipe/triage.py

echo; echo "=== NEGATIVE (ii-a): modify exactly one fifth arpipe/ path (arpipe/verify.py), COMMITTED ==="
$PY - <<'EOF'
import pathlib
p = pathlib.Path("arpipe/verify.py"); b = bytearray(p.read_bytes())
i = b.index(b"a"); orig = b[i]; b[i] = ord("b"); p.write_bytes(bytes(b))
print(f"changed 1 byte in arpipe/verify.py at offset {i}: {chr(orig)!r} -> 'b'")
EOF
git -c user.name=scratch -c user.email=scratch@example.invalid commit -q -am "scratch: fifth path"
$PY -m pytest -q -p no:cacheprovider $T -k "exactly_the_four" 2>&1 | grep -E '^FAILED|passed|failed|unauthorized' | head -5
git reset -q --hard "$START"

echo; echo "=== NEGATIVE (ii-b): ADD one new fifth arpipe/ path (untracked file) ==="
printf 'X = 1\n' > arpipe/zz_fifth_path.py
$PY -m pytest -q -p no:cacheprovider $T -k "exactly_the_four" 2>&1 | grep -E '^FAILED|passed|failed|untracked files' | head -5
rm -f arpipe/zz_fifth_path.py

echo; echo "=== NEGATIVE (ii-c): modify one fifth arpipe/ path, UNCOMMITTED ==="
$PY - <<'EOF'
import pathlib
p = pathlib.Path("arpipe/verify.py"); b = bytearray(p.read_bytes()); i = b.index(b"a"); b[i] = ord("b"); p.write_bytes(bytes(b))
EOF
$PY -m pytest -q -p no:cacheprovider $T -k "exactly_the_four" 2>&1 | grep -E '^FAILED|passed|failed|working tree changes' | head -5
git checkout -q -- arpipe/verify.py

echo; echo "=== EXTRA (iii): guard UNEXPECTEDLY PASSES (arpipe restored to the T0.4 base) -> must be XPASS(strict) failure ==="
git checkout -q ff030d97c13c8a2a977521bf91be2aca0cbf3034 -- arpipe/
$PY -m pytest -q -p no:cacheprovider --rootdir=. \
  "tests/t0_4/test_t0_4_setup.py::test_frozen_corpus_and_history_are_unchanged" \
  "tests/t0_4/test_t0_4_setup.py::test_fail_closed_setup_audit_passes" \
  "tests/t0_4/test_t0_4_closure_record.py::test_frozen_inputs_are_unchanged_since_the_audited_commit" -rxXf 2>&1 | grep -E 'XPASS|FAILED|passed|failed|xfailed' | cut -c1-200
git reset -q --hard "$START"; git clean -qfd -e conftest.py -e tests/test_t0_4_amendment_01.py

echo; echo "=== EXTRA (iv): UNRELATED failure (fifth path also changed) -> guards must FAIL, not XFAIL ==="
cp "$CAND/conftest.py" conftest.py
cp "$CAND/tests/test_t0_4_amendment_01.py" tests/test_t0_4_amendment_01.py
cp "$CAND/tests/test_phase2_1_semantic_conformance.py" tests/test_phase2_1_semantic_conformance.py
$PY - <<'EOF'
import pathlib
p = pathlib.Path("arpipe/verify.py"); b = bytearray(p.read_bytes()); i = b.index(b"a"); b[i] = ord("b"); p.write_bytes(bytes(b))
EOF
$PY -m pytest -q -p no:cacheprovider --rootdir=. \
  "tests/t0_4/test_t0_4_setup.py::test_frozen_corpus_and_history_are_unchanged" \
  "tests/t0_4/test_t0_4_setup.py::test_fail_closed_setup_audit_passes" \
  "tests/t0_4/test_t0_4_closure_record.py::test_frozen_inputs_are_unchanged_since_the_audited_commit" -rxXf 2>&1 | grep -E 'XFAIL|XPASS|FAILED|passed|failed|xfailed' | cut -c1-200
git checkout -q -- arpipe/verify.py

echo; echo "=== scratch clone final state (candidate worktree must be untouched) ==="
echo "candidate HEAD after negatives: $(git -C "$CAND" rev-parse HEAD)"
echo "candidate status:"; git -C "$CAND" status --porcelain=v1 -uall
