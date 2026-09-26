"""Step 3: derive the eligible FIT + VALIDATION document universe from the frozen split manifests.

Reads only the R4a-whitelisted manifests. HOLDOUT is used solely to prove disjointness by
document_id and issuer; no HOLDOUT row is followed to a PDF or output, and no directory is
opened unless its issuer_year is a FIT or VALIDATION document_id.
"""
import csv
import hashlib
import json
import pathlib
import sys

candidate = pathlib.Path(sys.argv[1]).resolve()
base = pathlib.Path(sys.argv[2]).resolve()
baseline_companies = pathlib.Path(sys.argv[3]).resolve()
out_path = pathlib.Path(sys.argv[4])

FREEZE = "dataset/corpus_freeze/"
manifests = {"FIT": "development_manifest.csv", "VALIDATION": "validation_manifest.csv", "HOLDOUT": "holdout_manifest.csv"}


def rows(root, name):
    with (root / FREEZE / name).open(newline="", encoding="utf-8-sig") as fh:
        return list(csv.DictReader(fh))


# The frozen manifests must be identical in the base and the candidate checkouts.
for split, name in manifests.items():
    assert (candidate / FREEZE / name).read_bytes() == (base / FREEZE / name).read_bytes(), name
assert (candidate / FREEZE / "page_profile.csv").read_bytes() == (base / FREEZE / "page_profile.csv").read_bytes()

data = {split: rows(candidate, name) for split, name in manifests.items()}
ids = {split: {r["document_id"] for r in rs} for split, rs in data.items()}
issuers = {split: {r["issuer"] for r in rs} for split, rs in data.items()}
company_ids = {split: {r["company_id"] for r in rs} for split, rs in data.items()}
for split, rs in data.items():
    assert len(ids[split]) == len(rs), f"duplicate document_id in {split}"
    assert all(r["split"] == split for r in rs), split
pairs = [("FIT", "VALIDATION"), ("FIT", "HOLDOUT"), ("VALIDATION", "HOLDOUT")]
disjoint = {f"{a}&{b}": {"documents": len(ids[a] & ids[b]), "issuer_names": len(issuers[a] & issuers[b]), "company_ids": len(company_ids[a] & company_ids[b])} for a, b in pairs}

eligible = {"FIT": data["FIT"], "VALIDATION": data["VALIDATION"]}
# Every FIT/VALIDATION PDF is located by its frozen manifest SHA-256 in the content-addressed
# store (blobs/<aa>/<bb>/<sha>.pdf) and its content hash is re-verified. No directory is listed.
blob_root = baseline_companies  # argv[3]: the store root that holds blobs/

universe, missing = [], []
for split, rs in eligible.items():
    for r in rs:
        docid, company = r["document_id"], r["company_id"]
        assert docid == f"{company}_{r['fiscal_year']}", docid
        sha = r["pdf_sha256"]
        pdf = blob_root / "blobs" / sha[:2] / sha[2:4] / f"{sha}.pdf"
        if not pdf.is_file():
            missing.append({"document_id": docid, "split": split, "reason": "no blob for the frozen sha256"})
            continue
        digest = hashlib.sha256(pdf.read_bytes()).hexdigest()
        if digest != sha:
            missing.append({"document_id": docid, "split": split, "reason": "blob content sha256 differs from frozen manifest", "actual": digest})
            continue
        universe.append({"document_id": docid, "split": split, "company_id": company, "issuer": r["issuer"], "pdf": str(pdf), "pdf_sha256": digest})

result = {
    "manifest_rows": {s: len(rs) for s, rs in data.items()},
    "disjointness": disjoint,
    "eligible_by_manifest": {"FIT": len(eligible["FIT"]), "VALIDATION": len(eligible["VALIDATION"])},
    "runnable": {s: sum(1 for u in universe if u["split"] == s) for s in eligible},
    "not_runnable": missing,
    "documents": universe,
}
out_path.write_text(json.dumps(result, indent=2), encoding="utf-8")
print(json.dumps({k: v for k, v in result.items() if k != "documents"}, indent=2))
