"""Generate docs/identity/RUNNABLE_IDENTITY_v1.md from recorded command output."""
import hashlib
import json
import pathlib
import re
import sys

S = pathlib.Path(sys.argv[1])
dst = pathlib.Path(sys.argv[2])
uni = json.loads((S / "identity_universe.json").read_text(encoding="utf-8"))
env = (S / "environment_final.txt").read_text(encoding="utf-8", errors="replace").replace("\r\n", "\n")
cmp_ = json.loads((S / "comparison.json").read_text(encoding="utf-8"))
evi = json.loads((S / "evidence_compact.json").read_text(encoding="utf-8"))


def sha(name):
    return hashlib.sha256((S / name).read_bytes()).hexdigest()


def section(title, nxt):
    i = env.index(title)
    j = env.index(nxt, i + len(title)) if nxt else len(env)
    return env[i + len(title):j].strip("\n")


tess_version = section("### tesseract --version\n", "### tesseract --list-langs").strip()
tess_langs = section("### tesseract --list-langs\n", "### pip freeze (venv, PYTHONPATH unset)").strip()
freeze_a = section("### pip freeze (venv, PYTHONPATH unset)\n", "### pip freeze (venv + PYTHONPATH=test-deps)").strip().splitlines()
freeze_b = section("### pip freeze (venv + PYTHONPATH=test-deps)\n", "### arpipe/requirements.txt").strip().splitlines()
test_only = sorted(set(freeze_b) - set(freeze_a))

table = "\n".join(f"| {i} | `{r['path']}` | `{r['sha256']}` |" for i, r in enumerate(uni["files"], 1))
g = cmp_["governing"]
sec = cmp_["secondary_page_profile"]

doc = (S / "identity_template.md").read_text(encoding="utf-8")
subs = {
    "@@TIP@@": uni["tip"], "@@PARENT@@": uni["parent"], "@@COUNT@@": str(uni["count"]), "@@DIGEST@@": uni["manifest_digest"],
    "@@ARPIPE_TREE@@": uni["trees"]["arpipe"], "@@CONFIGS_TREE@@": uni["trees"]["configs"], "@@TABLE@@": table,
    "@@TESS_VERSION@@": tess_version, "@@TESS_LANGS@@": tess_langs, "@@FREEZE@@": "\n".join(freeze_a),
    "@@TEST_ONLY@@": "\n".join(test_only),
    "@@FIT_DOCS@@": str(g["FIT"]["documents"]), "@@FIT_PAGES@@": str(g["FIT"]["pages"]),
    "@@VAL_DOCS@@": str(g["VALIDATION"]["documents"]), "@@VAL_PAGES@@": str(g["VALIDATION"]["pages"]),
    "@@TOT_DOCS@@": str(g["total_documents"]), "@@TOT_PAGES@@": str(g["total_pages"]),
    "@@KIND_MATCH@@": str(g["pagekind_matches"]), "@@KIND_MISMATCH@@": str(g["pagekind_mismatches"]),
    "@@OCR_MATCH@@": str(g["ocr_page_matches"]), "@@OCR_MISMATCH@@": str(g["ocr_page_mismatches"]),
    "@@OCR_DOC_MATCH@@": str(g["ocr_set_document_matches"]), "@@OCR_DOC_MISMATCH@@": str(g["ocr_set_document_mismatches"]),
    "@@SUPP_IDENT@@": str(g["supplementary_all_fields_except_script_meta_identical_pages"]),
    "@@PP_CAND_MATCH@@": str(sec["candidate"]["matches"]), "@@PP_CAND_MISMATCH@@": str(sec["candidate"]["mismatches"]),
    "@@PP_BASE_MATCH@@": str(sec["base"]["matches"]), "@@PP_BASE_MISMATCH@@": str(sec["base"]["mismatches"]),
    "@@PP_FIT@@": str(sec["candidate"]["FIT"]["matches"]), "@@PP_VAL@@": str(sec["candidate"]["VALIDATION"]["matches"]),
    "@@OCR_ROUTED_TOTAL@@": str(sum(evi["ocr_routed_pages_by_split"].values())),
    "@@OCR_ROUTED_FIT@@": str(evi["ocr_routed_pages_by_split"]["FIT"]), "@@OCR_ROUTED_VAL@@": str(evi["ocr_routed_pages_by_split"]["VALIDATION"]),
    "@@KINDS@@": ", ".join(f"{k} {v}" for k, v in sorted(evi["candidate_page_kind_totals"].items(), key=lambda kv: -kv[1])),
    "@@H_UNIVERSE@@": sha("universe.json"), "@@H_PROFILE_BASE@@": sha("profile_base.json"), "@@H_PROFILE_CAND@@": sha("profile_cand.json"),
    "@@H_COMPARISON@@": sha("comparison.json"), "@@H_COMPACT@@": sha("evidence_compact.json"), "@@H_SUITE_TXT@@": sha("suite_pin.txt"),
    "@@H_SUITE_XML@@": sha("suite_pin.xml"), "@@H_NEG@@": sha("negative_tests.out"), "@@H_HIST@@": hashlib.sha256(
        pathlib.Path(r"D:\sem_iitk\sem9\thesis\sep_week1\r1-final-evidence\historical-comparison.json").read_bytes()).hexdigest(),
}
for k, v in subs.items():
    assert k in doc, k
    doc = doc.replace(k, v)
left = re.findall(r"@@[A-Z_]+@@", doc)
assert not left, left
assert "\r" not in doc
dst.write_text(doc, encoding="utf-8", newline="\n")
print("wrote", dst, len(doc.splitlines()), "lines")
