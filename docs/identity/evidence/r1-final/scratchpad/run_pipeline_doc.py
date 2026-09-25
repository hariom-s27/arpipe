"""Step 4: run the candidate pipeline once on the single FIT document INE00LO01017_2025.

usage: run_pipeline_doc.py <clean candidate checkout> <output dir> [document_id]

The document must be FIT (checked against the frozen development manifest before any of its
files is opened). Imports arpipe from <checkout> and asserts it resolved there (R5).
Tesseract-only escalator, unmodified candidate config, one process, no retries.
"""
import csv
import glob
import hashlib
import json
import os
import pathlib
import sys
import time

checkout = pathlib.Path(sys.argv[1]).resolve()
out = pathlib.Path(sys.argv[2]).resolve()
docid = sys.argv[3] if len(sys.argv) > 3 else "INE00LO01017_2025"
SEP = pathlib.Path(r"D:\sem_iitk\sem9\thesis\sep_week1")

with (checkout / "dataset/corpus_freeze/development_manifest.csv").open(newline="", encoding="utf-8-sig") as fh:
    fit = {r["document_id"]: r for r in csv.DictReader(fh)}
assert docid in fit, f"{docid} is not FIT"

os.chdir(checkout)
sys.path.insert(0, str(checkout))
import arpipe  # noqa: E402
from arpipe import config, models, ocr, pipeline, universe  # noqa: E402

for mod in (arpipe, models, ocr, pipeline, config):
    assert pathlib.Path(mod.__file__).resolve().is_relative_to(checkout), (mod.__name__, mod.__file__)
print("python:", sys.executable)
print("arpipe:", arpipe.__file__)

company_id, year = docid.rsplit("_", 1)
hist_dir = pathlib.Path(glob.glob(str(SEP / "arpipe-0.1.0/pm1_baseline_run/companies" / f"*__{company_id}" / year))[0])
data = json.loads((hist_dir / "document.json").read_text(encoding="utf-8"))
data.pop("script_map", None)  # historical telemetry is never seeded into the candidate
pdf = hist_dir / "annual_report.pdf"
digest = hashlib.sha256(pdf.read_bytes()).hexdigest()
assert digest == fit[docid]["pdf_sha256"] == data["sha256"], "PDF hash mismatch"
data["path"] = str(pdf)
doc = models.StoredDoc(**data)

out.mkdir(parents=True, exist_ok=False)
cfg = config.load_config(config_path=str(checkout / "arpipe/configs/default.yaml"))
config.set_active_config(cfg)
companies = {}
for company in universe.from_csv(str(checkout / "arpipe/companies.csv")):
    companies[company.company_id] = company
    if company.isin:
        companies[company.isin] = company
    for alt in company.alternate_isins:
        companies[alt] = company

started = time.monotonic()
result = pipeline.process_document(doc, companies[doc.company_id], str(out),
                                   escalator=ocr.Escalator([ocr.TesseractBackend()]),
                                   keep_pages=False, store_root=str(pdf.parent))
payload = json.loads(models.to_json(result))
(out / "result.json").write_text(json.dumps(payload, indent=2), encoding="utf-8")
summary = {
    "document_id": docid, "checkout": str(checkout), "arpipe_file": arpipe.__file__,
    "confidence": payload["confidence"], "start_page": payload["span"]["start_page"],
    "end_page": payload["span"]["end_page"], "method": payload["span"]["method"],
    "score": payload["span"]["score"], "ocr_pages": payload.get("ocr_pages"), "ocr_engine": payload.get("ocr_engine"),
    "method_candidates": payload.get("method_candidates"), "reasons": payload.get("reasons"),
    "errors": payload.get("errors"), "seconds": round(time.monotonic() - started, 1),
}
(out / "summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
print(json.dumps(summary))
