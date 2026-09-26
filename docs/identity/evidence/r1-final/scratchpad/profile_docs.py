"""Step 3: triage profiling only. No pipeline, no OCR.

usage: profile_docs.py <checkout> <universe.json> <out.json> [split ...]

Imports arpipe from <checkout> and asserts it resolved there (R5). Loads the checkout's own
arpipe/configs/default.yaml through config.set_active_config, which applies the triage
thresholds exactly as the pipeline does, then profiles each document with
triage.profile_document and records, per page: PageKind, OCR-set membership, and (as
supplementary evidence) every other PageProfile field except script_meta.
"""
import dataclasses
import json
import os
import pathlib
import sys
import time

checkout = pathlib.Path(sys.argv[1]).resolve()
universe = json.loads(pathlib.Path(sys.argv[2]).read_text(encoding="utf-8"))["documents"]
out_path = pathlib.Path(sys.argv[3])
splits = set(sys.argv[4:]) or {"FIT", "VALIDATION"}
assert splits <= {"FIT", "VALIDATION"}, "HOLDOUT is forbidden"

os.chdir(checkout)
sys.path.insert(0, str(checkout))
import arpipe  # noqa: E402
from arpipe import config, models, triage  # noqa: E402

for mod in (arpipe, triage, models, config):
    assert pathlib.Path(mod.__file__).resolve().is_relative_to(checkout), (mod.__name__, mod.__file__)
print("python:", sys.executable, flush=True)
print("arpipe:", arpipe.__file__, flush=True)
print("sys.path[:4]:", sys.path[:4], flush=True)

cfg = config.load_config(config_path=str(checkout / "arpipe/configs/default.yaml"))
config.set_active_config(cfg)
thresholds = {n: getattr(triage, n) for n in (
    "MIN_CHARS_PER_PAGE", "MIN_CHARS_DENSE", "MAX_MOJIBAKE_RATIO", "BIG_IMAGE_AREA_FRAC",
    "HYBRID_IMAGE_AREA_FRAC", "BLANK_CHARS", "VECTOR_PATH_TEXT_THRESHOLD", "COLUMN_HIST_BINS",
    "GUTTER_MIN_RUN_FRAC", "GUTTER_PEAK_THRESHOLD", "GUTTER_SEARCH_LO", "GUTTER_SEARCH_HI",
    "DOC_SCANNED_FRAC", "DOC_DIGITAL_FRAC")}
needs_ocr = sorted(k.value for k in triage.NEEDS_OCR)


def plain(value):
    if hasattr(value, "value") and not isinstance(value, (int, float, str)):
        return value.value
    return value


results, started = {}, time.monotonic()
docs = [d for d in universe if d["split"] in splits]
for n, doc in enumerate(docs, 1):
    entry = {"split": doc["split"], "pdf_sha256": doc["pdf_sha256"]}
    try:
        profile = triage.profile_document(doc["pdf"])
        pages = []
        for p in profile.pages:
            fields = {k: plain(v) for k, v in dataclasses.asdict(p).items() if k != "script_meta"}
            fields["kind"] = p.kind.value
            fields["needs_ocr"] = p.kind in triage.NEEDS_OCR
            pages.append(fields)
        entry.update({
            "n_pages": profile.n_pages, "pages": pages,
            "ocr_pages": triage.ocr_page_numbers(profile),
            "doc_kind": plain(profile.doc_kind), "frac_needing_ocr": profile.frac_needing_ocr,
        })
    except Exception as exc:  # recorded, never swallowed silently
        entry["error"] = f"{type(exc).__name__}: {exc}"
    results[doc["document_id"]] = entry
    print(f"[{n}/{len(docs)}] {doc['document_id']} {doc['split']} "
          f"pages={len(entry.get('pages', []))} error={entry.get('error')} t={time.monotonic() - started:.0f}s", flush=True)

out_path.write_text(json.dumps({
    "checkout": str(checkout), "arpipe_file": arpipe.__file__, "python": sys.executable,
    "thresholds_after_configure": thresholds, "needs_ocr_kinds": needs_ocr,
    "seconds": time.monotonic() - started, "documents": results,
}, indent=1), encoding="utf-8")
print("done", out_path, flush=True)
