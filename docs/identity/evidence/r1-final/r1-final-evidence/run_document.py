import csv, dataclasses, hashlib, json, os, pathlib, subprocess, sys, time
checkout = pathlib.Path.cwd().resolve()
scratch = checkout.parent
phase, docid = sys.argv[1:3]
assert phase in {"smoke-a", "primary", "smoke-b"}
registration = json.loads((scratch/"preregistration.json").read_text())
with (checkout/"dataset/corpus_freeze/development_manifest.csv").open(newline="",encoding="utf-8-sig") as f:
    fit = {r["document_id"] for r in csv.DictReader(f) if r["split"] == "FIT"}
assert docid in fit, ("NOT FIT",docid)
allowed = registration["primary_documents"] if phase == "primary" else registration["eligible_smoke"]
assert docid in allowed
assert subprocess.check_output(["git","rev-parse","HEAD"]).decode().strip() == registration["candidate_commit"]
assert not subprocess.check_output(["git","status","--porcelain"]).strip()
import arpipe
from arpipe import config, models, ocr, pipeline, universe
assert pathlib.Path(arpipe.__file__).resolve().is_relative_to(checkout)
assert pathlib.Path(models.__file__).resolve().is_relative_to(checkout)
info = json.loads((scratch/"fit-inputs.json").read_text())[docid]
# The FIT assertion above precedes opening this document's historical PDF.
pdf = pathlib.Path(info["pdf"])
digest = hashlib.file_digest(pdf.open("rb"),"sha256").hexdigest()
assert digest == info["document"]["sha256"], ("PDF hash mismatch",docid)
out = scratch / phase / docid
out.mkdir(parents=True, exist_ok=False)  # A second attempt is forbidden.
cfg = config.load_config(config_path=str(checkout/"arpipe/configs/default.yaml"))
config.set_active_config(cfg)
companies = {}
for company in universe.from_csv(str(checkout/"arpipe/companies.csv")):
    companies[company.company_id] = company
    if company.isin: companies[company.isin] = company
    for alt in company.alternate_isins: companies[alt] = company
data = dict(info["document"])
data.pop("script_map",None)  # Historical telemetry is never seeded into the candidate.
data["path"] = str(pdf)
doc = models.StoredDoc(**data)
started = time.monotonic()
result = pipeline.process_document(doc, companies[doc.company_id], str(out),
                                  escalator=ocr.Escalator([ocr.TesseractBackend()]),
                                  keep_pages=False, store_root=str(pdf.parent))
payload = json.loads(models.to_json(result))
(out/"result.json").write_text(json.dumps(payload,indent=2),encoding="utf-8")
metadata = {"document_id":docid,"phase":phase,"pdf_sha256":digest,"completed":True,
            "confidence":payload["confidence"],"span_path":payload.get("path"),
            "reasons":payload.get("reasons"),"errors":payload.get("errors"),
            "duration_seconds":time.monotonic()-started,"candidate_import":arpipe.__file__}
(out/"execution.json").write_text(json.dumps(metadata,indent=2),encoding="utf-8")
print(json.dumps(metadata),flush=True)
assert "crash" not in payload.get("reasons",[]), metadata
assert not payload.get("errors"), metadata
if phase.startswith("smoke") and docid == "INE008A01015_2024":
    assert payload["confidence"] == "quarantine" and payload.get("path") is None, metadata
