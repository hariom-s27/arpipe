import csv, json, pathlib, subprocess
checkout = pathlib.Path.cwd().resolve()
scratch = checkout.parent
source = scratch.parent / "arpipe-0.1.0" / "pm1_baseline_run" / "companies"
with (checkout / "dataset/corpus_freeze/development_manifest.csv").open(newline="", encoding="utf-8-sig") as f:
    fit = {r["document_id"] for r in csv.DictReader(f) if r["split"] == "FIT"}
companies = {p.name.rsplit("__", 1)[-1]: p for p in source.iterdir() if p.is_dir()}
population, missing = {}, []
for docid in sorted(fit):
    issuer, year = docid.rsplit("_", 1)
    if issuer not in companies or not (companies[issuer] / year).is_dir():
        missing.append(docid)
        continue
    assert docid in fit
    directory = companies[issuer] / year
    data = json.loads((directory / "document.json").read_text(encoding="utf-8"))
    assert data["company_id"] + "_" + str(data["fy_end"]) == docid
    pdf = directory / "annual_report.pdf"
    assert pdf.is_file(), ("Missing FIT input PDF", docid)
    population[docid] = {"directory": str(directory), "pdf": str(pdf), "document": data}
candidates = ["INE001F01019_2012", "INE001F01019_2013", "INE001F01019_2017", "INE008A01015_2024", "INE008A01015_2025"]
registration = {
    "candidate_commit": subprocess.check_output(["git", "rev-parse", "HEAD"]).decode().strip(),
    "fit_count": len(fit), "fit_source": "dataset/corpus_freeze/development_manifest.csv",
    "smoke_candidates": candidates, "eligible_smoke": [d for d in candidates if d in fit],
    "excluded_smoke": {d: "NOT_FIT; no output opened; no replacement" for d in candidates if d not in fit},
    "primary_documents": sorted(population), "missing_baseline_directory": missing,
    "fields": ["located", "start_page", "end_page", "grade", "span_path_nullness", "per_page_kind", "script_map"],
    "located_definition": "DERIVED: span is present and non-null; independent of acceptance/grade",
    "per_page_kind": "Read explicit page-kind serialization only; absent fields remain absent.",
    "comparison": "Recursive type-exact equality; object order ignored; list order preserved; script_map indexed by typed page_no.",
    "procedure": "Unmodified candidate config arpipe/configs/default.yaml; committed companies.csv; Tesseract-only CLI-default ladder; no external engines; one subprocess per document; no retries.",
}
assert len(population) == 58 and len(registration["eligible_smoke"]) == 4
for path, obj in [(scratch/"preregistration.json", registration), (scratch/"fit-inputs.json", population)]:
    assert not path.exists(), path
    path.write_text(json.dumps(obj, indent=2), encoding="utf-8")
print(json.dumps(registration, indent=2))
