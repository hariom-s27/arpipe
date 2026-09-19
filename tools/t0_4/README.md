# T0.4 setup harness

This package is deliberately setup-only. It builds and audits the preregistered dual-track manifest; it has no OCR runner.

From the repository root:

```powershell
python tools/build_t0_4_manifest.py
python -m pytest tests/t0_4 -q
python tools/audit_t0_4_setup.py
```

Run the builder and audit a second time and compare the printed manifest SHA-256. The generated files are:

- `artifacts/t0_4/benchmark_manifest.json`
- `artifacts/t0_4/config_hashes.json`
- `artifacts/t0_4/setup_audit.json`

The manifest's `input_image_hash` remains `NOT_YET_RENDERED` by design. Do not replace it in this worktree. A later execution worktree must render every selected page once with `tools.t0_4.renderer`, freeze the resulting hash, construct exactly four primary-engine request rows with that same hash, and pass them through `validate_primary_engine_inputs` before invocation.

Runtime output must validate against the common, raw-output, efficiency, and future-results schemas. Preserve raw engine output separately. Never put timestamps, hostnames, UUIDs, absolute paths, model output, or telemetry into deterministic setup/gold artifacts.

The following are prohibited here: opening/rendering corpus PDFs, probing or installing engines, OCR execution, cloud/API calls, external acquisition, benchmark-result creation, HOLDOUT tuning, and production-pipeline edits.
