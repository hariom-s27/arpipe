# P-C0 — Coverage Diagnosis

**Mode:** READ-ONLY DIAGNOSIS. No production code, manifest, or P-M5 stage membership was changed. No acquisition or extraction was rerun.
**Machine-readable companion:** `reports/coverage_diagnosis.json`. Frozen sample: `reports/pc0_sample_manifest.json`.

---

## 0. Setup and provenance

| Item | Value |
|---|---|
| Target HEAD SHA | `0fb8cbf6d932f4190bdfe3b2a1fecf62170cca14` ("P33: audit post-P25 patterns for false positives, fix is-given-below rejection") |
| Diagnostic worktree (created this task) | `D:\sem_iitk\sem9\thesis\sep_week1\arpipe-pc0-coverage-diag`, via `git worktree add --detach <path> 0fb8cbf...` from `arpipe-0.1.0`. Detached HEAD, clean, one untracked file added at a time (`reports/pc0_sample_manifest.json`, then the two report files). |
| Original worktree `arpipe-0.1.0` | READ-ONLY forensic evidence. Not read from or written to by this task. |
| P-M5 evidence source | `arpipe-pm5-coverage`, branch `pm5-coverage-funnel` @ `7292111149ab1cf9fc8d638d1f08023e3fcb13d5`. Read-only: opened and hashed, never edited. |
| P-C0 diagnostic-base evidence | `arpipe-pc0-diagnostic-base`, same HEAD `0fb8cbf`. Read-only: `reports/pc0_diagnostic_base_check.md` / `.json` used as input, reused where explicitly noted, corrected where its "ZERO" grouping conflated `accepted=0` with `downloaded=0`. |
| Other worktrees | Not touched. |

SHA-256 of frozen evidence used (independently recomputed, matches values embedded in `coverage.json` / `pm5_source_snapshot_manifest.json` / the diagnostic-base files — no drift):

| File | SHA-256 |
|---|---|
| `pm5-coverage/reports/coverage.json` | `c84166741d36a9774b7c9f29d71ea9583934d98c2ab153e651ec66ec4d371bcf` |
| `pm5-coverage/reports/pm5_stage_table.csv` | `30e93b59ac689f00fab182583fb25883322e429be42b4ba14e13a1011b916dc9` |
| `pm5-coverage/reports/pm5_expected_universe_snapshot.csv` | `b287a82d0fa2b15098882c328be6afc2c1672c9255f64103e4aaeabd94ccebe5` |
| `pm5-coverage/reports/pm5_source_snapshot_manifest.json` | `827406a1d2fce8a084e65583c5adea172a330c2233c025c0e02b858c0ce1adfb` |
| `pm5-coverage/reports/pm5_reason_code_completeness.csv` | `0adb7410a857435e8a859d30c7ede67e7fa4beb4a4f8c7abda76eb43a246684c` |
| `pc0-diagnostic-base/reports/pc0_diagnostic_base_check.md` | `53968bf73621bc08ed754336437f12e39723ab7a01b47f887b2596fb9a9d46c7` |
| `pc0-diagnostic-base/reports/pc0_diagnostic_base_check.json` | `7d7ed536b8dc696f36dce10128eb462779de59904819d94bc28628924d697885` |

---

## Part 1 — Full FY/stage table (reconstructed from `pm5_stage_table.csv`)

| FY | expected | discovered | downloaded | identity_verified | mda_located | accepted | acc/exp% | down/exp% | mda/exp% | disc→down loss | down→id loss | id→mda loss | mda→acc loss |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 2010 | 36 | 28 | 0 | 0 | 0 | 0 | 0.0 | 0.0 | 0.0 | 28 | 0 | 0 | 0 |
| 2011 | 36 | 29 | 1 | 1 | 1 | 0 | 0.0 | 2.78 | 2.78 | 28 | 0 | 0 | 1 |
| 2012 | 36 | 28 | 28 | 23 | 26 | 17 | 47.22 | 77.78 | 72.22 | 0 | 5 | −3 | 9 |
| 2013 | 36 | 29 | 29 | 23 | 28 | 17 | 47.22 | 80.56 | 77.78 | 0 | 6 | −5 | 11 |
| 2014 | 36 | 30 | 0 | 0 | 0 | 0 | 0.0 | 0.0 | 0.0 | 30 | 0 | 0 | 0 |
| 2015 | 36 | 33 | 2 | 0 | 0 | 0 | 0.0 | 5.56 | 0.0 | 31 | 2 | 0 | 0 |
| 2016 | 36 | 31 | 0 | 0 | 0 | 0 | 0.0 | 0.0 | 0.0 | 31 | 0 | 0 | 0 |
| 2017 | 36 | 31 | 31 | 28 | 29 | 22 | 61.11 | 86.11 | 80.56 | 0 | 3 | −1 | 7 |
| 2018 | 36 | 31 | 31 | 26 | 28 | 18 | 50.00 | 86.11 | 77.78 | 0 | 5 | −2 | 10 |
| 2019 | 36 | 32 | 0 | 0 | 0 | 0 | 0.0 | 0.0 | 0.0 | 32 | 0 | 0 | 0 |
| 2020 | 36 | 33 | 0 | 0 | 0 | 0 | 0.0 | 0.0 | 0.0 | 33 | 0 | 0 | 0 |
| 2021 | 36 | 34 | 0 | 0 | 0 | 0 | 0.0 | 0.0 | 0.0 | 34 | 0 | 0 | 0 |
| 2022 | 36 | 35 | 0 | 0 | 0 | 0 | 0.0 | 0.0 | 0.0 | 35 | 0 | 0 | 0 |
| 2023 | 36 | 36 | 0 | 0 | 0 | 0 | 0.0 | 0.0 | 0.0 | 36 | 0 | 0 | 0 |
| 2024 | 36 | 36 | 36 | 35 | 35 | 26 | 72.22 | 100.0 | 97.22 | 0 | 1 | 0 | 9 |
| 2025 | 36 | 36 | 36 | 34 | 35 | 27 | 75.00 | 100.0 | 97.22 | 0 | 2 | −1 | 8 |

`loss_X_to_Y = count(X) − count(Y)` for the same FY. **Negative values are real, not bugs**: `coverage.json`'s own `monotonicity_checks` report `mda_located<=identity_verified: false`, with 12 violations (e.g. `INE007A01025::FY2012` "mda_located_without_identity_verified"). MDA-location and identity-verification are independent checks in this pipeline, not a strict nested waterfall — a company-year can have `mda_located=True` while `identity_verified=False`.

### The three lists — kept explicitly separate

| List | FYs | n |
|---|---|---|
| **`downloaded = 0`** | 2010, 2014, 2016, 2019, 2020, 2021, 2022, 2023 | **8** |
| **`mda_located = 0`** | 2010, 2014, 2015, 2016, 2019, 2020, 2021, 2022, 2023 | **9** |
| **`accepted = 0`** | 2010, 2011, 2014, 2015, 2016, 2019, 2020, 2021, 2022, 2023 | **10** |

These are nested but **not equal**: `downloaded=0` ⊂ `mda_located=0` ⊂ `accepted=0`.

- **FY2011** is in `accepted=0` but **not** in `downloaded=0` or `mda_located=0` — it had 1 download, 1 identity-verify, 1 MDA-locate, and 0 accepts.
- **FY2015** is in `accepted=0` and `mda_located=0` but **not** in `downloaded=0` — it had 2 downloads, 0 identity-verifies, 0 MDA-locates, 0 accepts.

**This resolves the task's own framing question directly**: the earlier informal summary "8 of 16 fiscal years at zero" is *exactly* the `downloaded=0` count (8), and is only true for that specific stage. Read as `accepted=0` it would be wrong (10, not 8); read as `mda_located=0` it would also be wrong (9, not 8). The three failure mechanisms are not interchangeable, and this diagnosis uses `downloaded=0` as the strict definition of "the acquisition/coverage problem" wherever "zero" is used below.

---

## Part 2 — FY pattern, reported per stage

| Stage | Non-zero FYs | Zero FYs |
|---|---|---|
| **downloaded** | 2011, 2012, 2013, 2015, 2017, 2018, 2024, 2025 | 2010 · 2014 · 2016 · **2019–2023 (5y run)** |
| **mda_located** | 2011, 2012, 2013, 2017, 2018, 2024, 2025 | 2010 · **2014–2016 (3y run)** · **2019–2023 (5y run)** |
| **accepted** | 2012, 2013, 2017, 2018, 2024, 2025 | **2010–2011 (2y run)** · **2014–2016 (3y run)** · **2019–2023 (5y run)** |

**Classification: clustered.** Not contiguous overall, not alternating, not a single pre/post-date split. Three tight non-zero clusters — roughly `{2011–13}`, `{2017–18}`, `{2024–25}` — separated by multi-year zero runs, the largest being the 5-year `2019–2023` gap that no prior diagnostic had sampled.

**Structural alignment checks (not causal claims):**
- **Era boundaries** — not aligned. `E1(2010-12)`, `E4(2016-19)`, `E6(2023-25)` are each internally mixed zero/non-zero at the `downloaded` stage.
- **Source/issuer** — not aligned. The same companies (Reliance, HDFC Bank, Tata Steel, Infosys, Sun Pharma) appear in *both* the zero and non-zero groups, just in different FYs — the split tracks *when*, not *which issuer or source*.
- **Exchange/cap-band** — structurally incapable of explaining an FY-level pattern: they are per-company attributes, not per-FY ones.

No cause is inferred from shape alone here — see Parts 9–13.

---

## Part 3 — Frozen 10-observation sample

Full detail: `reports/pc0_sample_manifest.json`. **Frozen before any current-network test was run; no substitution afterward.**

8 of 10 observations are reused **verbatim** from `pc0_diagnostic_base_check.json`. **2 were deliberately replaced**, and this replacement is itself a finding: the diagnostic-base check's "ZERO" group was actually `accepted=0` (its own selection included FY2011 Infosys and FY2015 SunPharma), which — per Part 1 above — is *not* the same set as `downloaded=0`. Those two were swapped for two new observations drawn from the untouched 2019–2023 zero-download run:

| # | Group | Observation | Basis |
|---|---|---|---|
| 1 | `DOWNLOAD_ZERO_FY` | Reliance / FY2010 | reused |
| 2 | `DOWNLOAD_ZERO_FY` | HDFC Bank / FY2014 | reused |
| 3 | `DOWNLOAD_ZERO_FY` | Tata Steel / FY2016 | reused |
| 4 | `DOWNLOAD_ZERO_FY` | **Federal Bank / FY2021 (new)** | replaces Infosys/FY2011 — FY2011 has `downloaded=1`, disqualified |
| 5 | `DOWNLOAD_ZERO_FY` | **Voltas / FY2022 (new)** | replaces SunPharma/FY2015 — FY2015 has `downloaded=2`, disqualified |
| 6 | `DOWNLOAD_NONZERO_FY_CONTROL` | Reliance / FY2012 (ACCEPTED) | reused |
| 7 | `DOWNLOAD_NONZERO_FY_CONTROL` | Infosys / FY2013 (ACCEPTED) | reused |
| 8 | `DOWNLOAD_NONZERO_FY_CONTROL` | HDFC Bank / FY2017 (downloaded, later rejected: `source_shredded` at ACCEPTANCE) | reused |
| 9 | `DOWNLOAD_NONZERO_FY_CONTROL` | Sun Pharma / FY2018 (ACCEPTED) | reused |
| 10 | `DOWNLOAD_NONZERO_FY_CONTROL` | Tata Steel / FY2024 (ACCEPTED) | reused |

All 10 exact URLs, source ids, and full `M5_stage_state` are in the JSON manifest.

---

## Part 4 — Current HTTP diagnostic (single deterministic configuration)

**Deterministic request configuration (recorded once, used for every URL):**

| Field | Value |
|---|---|
| Tool / version | `curl 8.19.0 (x86_64-w64-mingw32) libcurl/8.19.0 Schannel zlib/1.3.2 brotli/1.2.0 zstd/1.5.7` |
| Method | GET |
| User-Agent | `Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36` (verbatim copy of `discover.UA`) |
| Timeout | 120s (`--max-time 120`, matches `fetch_one`'s per-request timeout) |
| Redirects | follow, max 20 (`-L --max-redirs 20`, matches httpx's default) |
| Headers | **User-Agent only** — no Accept, no Accept-Language, no Referer (matches `cmd_fetch`'s actual client exactly) |
| Cookies/session | none — fresh, unseeded |
| Proxy | none (system default) |
| Retries added by this diagnostic | **none** (single attempt per URL) |
| Timestamp | 2026-09-17T13:59:08Z – 13:59:49Z (IST session, sequential, one host) |

**Result: 10 of 10 succeeded with clean HTTP 200s.**

| # | Group | Status | Content-Type | Bytes | Magic | Time (s) |
|---|---|---|---|---|---|---|
| 1 | ZERO | 200 | application/zip | 8,795,366 | `PK\x03\x04` (ZIP) | 8.30 |
| 2 | ZERO | 200 | application/zip | 5,591,336 | ZIP | 1.21 |
| 3 | ZERO | 200 | application/zip | 5,455,878 | ZIP | 2.94 |
| 4 | ZERO | 200 | application/zip | 9,448,336 | ZIP | 1.68 |
| 5 | ZERO | 200 | application/zip | 7,482,626 | ZIP | 1.77 |
| 6 | CONTROL | 200 | application/zip | 5,111,665 | ZIP | 0.95 |
| 7 | CONTROL | 200 | application/zip | 8,608,682 | ZIP | 2.16 |
| 8 | CONTROL | 200 | application/zip | 7,230,114 | ZIP | 0.99 |
| 9 | CONTROL | 200 | application/zip | 3,050,947 | ZIP | 0.79 |
| 10 | CONTROL | 200 | application/pdf | 26,006,738 | `%PDF` | 2.59 |

Every body has a valid magic number matching its declared extension — none is an HTML block/error page disguised behind a 200. Notably, observation #10's downloaded bytes hash to `870be0ca867c1c…` — an **exact match** to the `authoritative_artifact_sha256` already on record for that company-year in the frozen P-M5 evidence, confirming this specific source has been byte-stable since the original crawl.

**This is a complete reversal from the immediately preceding diagnostic.** `pc0_diagnostic_base_check.md` Step 3 tested 9 of these same 10 URLs from the same network roughly 40–50 minutes earlier the same day and got **0 of 9** successes (`CURLE_RECV_ERROR` resets and 45s timeouts across the board). The identical URL set flipped from total failure to total success inside under an hour, with no code change in between, and the flip was **uniform across both groups both times** — it never once tracked zero vs. non-zero membership. That single fact is the strongest current-observation evidence in this diagnosis: whatever governs `nsearchives.nseindia.com`'s availability right now, it operates on a sub-hour timescale and is not company- or FY-specific.

**Caveat (repeated deliberately): this is current-endpoint behavior only. It does not by itself prove what happened on 2026-09-11.**

---

## Part 5 — Redaction

Config A's cookie-seeding step (Part 9) received real Akamai bot-management cookies from `www.nseindia.com` (names `nsit`, `_abck`). **Values are redacted in this report and in the JSON companion**; only names are retained. No `Authorization` header, API key, or signed query parameter was present anywhere in this diagnosis — every tested URL is a public, unauthenticated regulatory-archive endpoint. The archive host's own responses (`nsearchives.nseindia.com`) never sent a `Set-Cookie` header in any config, so no redaction was needed on those specific response headers.

---

## Part 6 — Historical evidence vs. current network observation

| | **Historical evidence** | **Current network observation** |
|---|---|---|
| What it is | `fetched_at` timestamps for the 194 successes; discovered-candidate rows for 512 company-years; `pm5_stage_table.csv`'s derived flags | Live GETs issued 2026-09-17 by this task and its predecessor |
| Proves | 194/512 discovered pairs have a persisted success record dated 2026-09-11, 10:28:44–10:33:08 UTC. 0/318 have *any* record. | What the endpoint returns *right now*, under two documented configs; that it changed from 0/9 to 10/10 success within ~40–50 min |
| Does **not** prove | Whether `cmd_fetch` was ever invoked against the 318; what error (if any) occurred; whether the 2026-09-11 run(s) used code byte-identical to HEAD (the live `arpipe-0.1.0` tree is confirmed dirty *today*, so it cannot stand in for 2026-09-11) | What the endpoint returned on 2026-09-11; that today's mechanism (whatever it is) is the *same* mechanism as whatever occurred then |

These two classes are kept separate everywhere in this report and are never merged into a single "this is what happened" statement.

---

## Part 7 — Committed fetch control-flow inspection

Files read: `arpipe/discover.py`, `arpipe/fetch.py`, `arpipe/cli.py` (`cmd_discover`, `cmd_fetch`, `cmd_universe`). Nothing was modified.

**Why separate clients exist:** `discover` and `fetch` are deliberately separate CLI subcommands ("Stages are separate commands on purpose... `fetch` runs once" — `cli.py`'s own module docstring), so that `extract` can be re-run without re-fetching. `discover.nse_session()` is opened once inside `cmd_discover` and closed when that command ends. `cmd_fetch` is a later, separate invocation that only ever reads the discovery manifest **file** from disk — a JSONL of `ReportRef` rows (url/source/priority/company_id/fy_end/…, **no header or cookie field in the schema**) — and builds its own `httpx.Client` from scratch at `cli.py:176-177`.

| Question | Answer |
|---|---|
| 1. Why separate clients | Architectural decoupling of CLI stages; no shared in-memory client by design |
| 2. Cookies differ? | **Yes.** `nse_session()` seeds a cookie jar with 2 GETs to `NSE_HOME` first. `cmd_fetch`'s client starts and stays empty. |
| 3. Headers differ? | **Yes.** Discovery: `User-Agent, Accept, Accept-Language, Referer`. Fetch: `User-Agent` only. |
| 4. User-Agent differs? | **No** — identical string (`discover.UA`) in both. |
| 5. Redirects differ? | **No** — both `follow_redirects=True`, neither overrides httpx's default `max_redirects=20`. |
| 6. Timeout differs? | Nominally yes (`nse_session` default 20s vs. fetch client's 120s), but `fetch_one` explicitly overrides its own per-request timeout to 120.0 regardless of the client default, so this only matters for calls made directly on the (production-unused-for-archives) discovery client. |
| 7. TLS/proxy differs? | No evidence of difference — both use httpx defaults, no custom SSL context or proxy configured anywhere. |
| 8. Connection/session reuse differs? | **Yes** — two entirely separate client objects with no shared history, one per CLI invocation. |
| 9. Is discovery state transferred to fetch? | **No, structurally impossible as written.** The on-disk manifest schema has no cookie/header field, and no line of code copies client state between the two commands even conceptually. |
| 10. What formats are accepted? | `fetch_one` never checks `Content-Type`. It sniffs the first 2 bytes (`b"PK"` ⇒ zip, else assumed PDF), tries `pymupdf.open`, falls back to a `qpdf` repair pass, and returns `None` **silently** if both fail — no exception, no print at that point. |
| 11. What happens on network exceptions? | Broad `except Exception`, stored as `last_err`, linear backoff, re-raised after 3 attempts. **Separately confirmed gap:** HTTP 403/429/503 triggers quadratic backoff via `continue` **without** setting `last_err`. If all 3 attempts return 403/429/503 (never a generic exception), the loop exits with `last_err` still `None` and `fetch_one` falls through to `return None` — **zero exception, zero output, on any channel.** |
| 12. Persisted or only printed? | **Only ever printed.** `_fetch_pair` → stderr `WARN`; the `ThreadPoolExecutor` completion loop → stderr `ERR`/`FAILED`; `fetch_one` itself → informational stdout `[FETCH]` lines. None reach `documents.jsonl` or any file. Independently corroborated by `tools/pm5_coverage.py`'s own source comment, which hard-codes `DOWNLOAD`/`DISCOVERY` failures to `REASON_CODE_MISSING` because — in the tool's own words — those stages have no persisted artifact to derive a reason from. |
| 13. Can fetch be skipped before invocation? | **Tested directly, ruled out for the one candidate mechanism found.** See below. |

### The `cohort_fetch_manifest.jsonl` check (a hypothesis formed, tested, and rejected)

`cohort_fetch_manifest.jsonl` is the *only* committed, fetch-manifest-shaped file at this HEAD. It has 460 rows / **194 distinct `(company_id, fy_end)` pairs** — which is *exactly* the `downloaded=True` set in `pm5_stage_table.csv`, matching its FY distribution digit for digit (`{2011:1, 2012:28, 2013:29, 2015:2, 2017:31, 2018:31, 2024:36, 2025:36}` → 194). At first glance this looks like direct evidence that the 318 losses were *filtered out before `cmd_fetch` ever ran* — a control-flow/skipping bug, not an HTTP problem.

This was checked and **rejected**: the file was committed at `1d7dc05` ("P13b evaluate post-P30 pipeline against historical ground truth"), alongside `tools/seed_historical_labels.py`, which reads `arpipe/p11_store/documents.jsonl` — the **post-fetch success store** — for an unrelated evaluation/labelling task. No committed script reads or writes `cohort_fetch_manifest.jsonl` at all (`git grep` finds zero references), so its generator isn't available to inspect directly — but a pre-fetch filter would have had to *predict* which 194 of 512 candidates would later succeed, which nothing in this codebase does. The far more consistent explanation is that it is a **post-hoc export built from the successful `documents.jsonl`/store contents**, for the same evaluation task, not an input that ever constrained `cmd_fetch`. Inside `cmd_fetch` itself, the only skip logic is the `done` set read from any pre-existing `documents.jsonl`, which can only ever contain *already-succeeded* pairs — it structurally cannot skip a pair that only ever failed. **No skip-before-invocation mechanism was found for the 318 losses.**

---

## Part 8 — Fetch invocation evidence hierarchy

**Strong (persisted) evidence available:** `fetched_at` timestamps for the 194 successes; discovered-candidate rows for 512 company-years; `pm5_reason_code_completeness.csv` (0/318 DOWNLOAD reasons, 0/64 DISCOVERY reasons, vs. 24/24 IDENTITY and 39/43 ACCEPTANCE).

**Strong evidence absent, for all 318 losses:** no persisted fetch-attempt record, no persisted exception, no persisted HTTP telemetry, no download log of any kind.

**Indirect evidence only:** a discovered candidate exists; no downloaded artifact exists; later stages are absent by construction of the funnel.

Per this task's fixed rule — *absence of a downloaded artifact is not proof fetch was attempted; absence of a persisted reason is not proof no reason existed* — **historical fetch invocation for the 318 discover→download losses is classified UNKNOWN.** This diagnosis does not upgrade that.

---

## Part 9 — Controlled client differential test

**Hypothesis under test:** the fetch-client's missing NSE cookies/Referer causes `nsearchives.nseindia.com` to block/reset archive downloads.

Tested on 3 representative URLs (2 from `DOWNLOAD_ZERO_FY` — Reliance/FY2010 and the newly-sampled Federal Bank/FY2021 — plus 1 control, Infosys/FY2013), each under both configs, 2026-09-17 13:59:51Z–14:00:25Z:

- **Config A** (discovery-client-equivalent): 2 seed GETs to `NSE_HOME` (first returned **403**, second **200** — cookies were still set on the 403), then the target GET with the resulting cookie jar + `NSE_HEADERS`.
- **Config B** (fetch-client-equivalent, i.e. what `cmd_fetch` actually sends): fresh client, `User-Agent` only, no cookies, no Referer.

**Result for all 3 URLs: A and B both succeed.** Target response headers were byte-for-byte identical between configs (aside from `Date` and the per-request `Akamai-GRN` id), and the archive host sent no `Set-Cookie` in either case.

**Interpretation (current observation only):** today, a completely cookie-less, Referer-less client succeeds against this host exactly as well as one carrying NSE session cookies. This **weakens** the cookie/session-asymmetry hypothesis as a general or currently-necessary explanation — it does not eliminate the possibility that cookies mattered under whatever specific (unobserved) conditions applied on 2026-09-11. A current differential result shows a reproducible current mechanism; it does not by itself prove what caused the historical losses.

---

## Part 10 — Zero-download vs. non-zero-download comparison

Compared across URL pattern, hostname, path, extension, redirects, content-type, cookie/session requirement, UA requirement, fetch-client behavior, invocation state, exception behavior, acceptance logic, source id, year encoding, and exchange. **No structural difference was found on any dimension**, historical or current: identical `AR_<id>_<SYMBOL>_<FY0>_<FY1>_<ts>.<ext>` naming, same host, same source priority (`nse`), same `exchange='both'`, same zip/pdf split-by-calendar-year (not by group), 0 redirects in both groups both times, and — per Part 9 — no cookie/session requirement in either group today.

Invocation state and exception behavior *cannot* be compared historically between the groups, because per Part 8 the `DOWNLOAD_ZERO_FY` group's historical invocation is UNKNOWN — there is nothing to structurally contrast against the control group's known-successful records.

**The only measurable difference anywhere in this diagnosis is temporal** — the `fetched_at` clustering (Part 11) and today's demonstrated ~40–50 minute flip from 0/9 to 10/10 (Part 4). This is consistent with, but does not prove, a time-varying access condition rather than a company- or file-specific one.

---

## Part 11 — Historical timestamp evidence, read carefully

`fetched_at` is generated **client-side**, by `arpipe/models.py`'s `StoredDoc` dataclass (`default_factory=dt.datetime.now(dt.UTC).isoformat()`), stamped the instant `fetch_one()` successfully builds a `StoredDoc` — i.e., *after* the GET succeeded and the file was verified/stored. It exists **only on success**; nothing equivalent is stamped on failure.

**What it proves:** all 194 successes completed inside one continuous window, 2026-09-11T10:28:44.38Z–10:33:08.08Z (~4.5 min), in three tight FY-ordered sub-bursts — `{2012,2013}` (10:28:44–10:29:58), `{2017,2018}` (10:30:04–10:31:26), `{2024,2025}` (10:31:29–10:33:08) — with FY2011's lone success (10:29:04) landing inside the first burst and FY2015's 2 successes (10:31:21–22) landing inside the second.

**What it does not prove:**
- That any of the 318 failures were attempted before, during, or after this window — no timestamp exists for them at all.
- How many retries (of `fetch_one`'s built-in up-to-3) preceded any given success — attempt count isn't persisted.
- That there was only **one** invocation of `arpipe fetch` ever run — `cmd_fetch` supports incremental resume via a `done` set read from any pre-existing `documents.jsonl`, so multiple invocations over time are structurally possible, and any invocation that produced zero successes would leave no trace whatsoever.
- Attempt-start ordering — `ThreadPoolExecutor` runs pairs concurrently, so completion order (what `fetched_at` shows) is not necessarily attempt-start order.

This diagnosis does **not** infer "not downloaded ⇒ attempted and failed" from this evidence. Per Part 8, the 318 losses remain UNKNOWN for invocation.

---

## Part 12 — Observability gap vs. acquisition failure

| Stage | Reason-code coverage |
|---|---|
| DISCOVERY | 0.0% (0/64) |
| **DOWNLOAD** | **0.0% (0/318)** |
| IDENTITY | 100.0% (24/24) |
| ACCEPTANCE | 90.7% (39/43) |

Where the code actually goes on a DOWNLOAD failure: `_fetch_pair` prints a `WARN` to **stderr**; the `ThreadPoolExecutor` loop prints `ERR`/`FAILED` to **stderr**; `fetch_one` itself prints `[FETCH]` notices to **stdout**; and — confirmed in Part 7 q11 — the exhausted-403/429/503 path prints **nothing at all**. None of these three channels write to any file.

This is not merely "stderr instead of a log file." A DOWNLOAD failure produces **no artifact** — the content-addressed store only ever writes an entry on success — so even a deliberately post-hoc reconciliation tool has nothing on disk to inspect. `tools/pm5_coverage.py`'s own source comment confirms this design tension directly: DISCOVERY/DOWNLOAD failures are unconditionally coded `REASON_CODE_MISSING` because those stages have no persisted artifact to derive a reason from. Both readings — the CLI code and the reconciliation tool's own comment — independently corroborate each other.

**Kept separate, per this task's instruction:**
- **Observability failure: confirmed**, directly, by code reading. DOWNLOAD/DISCOVERY reasons are never persisted, only printed (or, on one path, not even that).
- **Acquisition failure mechanism: not established by this fact alone.** "Reason was not persisted" proves the pipeline cannot currently tell you *why* a company-year failed; it does not tell you *what* that reason was. Observability failure is treated below as a contributing factor, not automatically promoted to primary cause.

---

## Part 13 — Root-cause structure

### Primary cause

**C. HTTP/access problem — time-varying availability on the NSE archive host.** Confidence: **MEDIUM**.

Supporting evidence:
1. All 194 historical successes fall inside one ~4.5 min window with nothing before or after (Part 11).
2. The identical 10-URL sample flipped from **0/10** success (predecessor diagnostic, same day) to **10/10** success (this task, ~40–50 min later, same network, no code change) (Part 4).
3. No structural difference between the zero-download and control groups on any dimension, historical or current (Part 10) — ruling out a company- or file-specific cause and leaving a time-dependent access condition as the best-supported remaining explanation.
4. The controlled differential test found **no current requirement** for discovery-session cookies/Referer against this host (Part 9) — this rules out client-configuration asymmetry as a sole, currently-active explanation, though it does not rule it out for 2026-09-11's specific, unobserved conditions.

**Why this is MEDIUM, not HIGH:** historical per-attempt execution evidence for the 318 losses does not exist (Part 8: UNKNOWN). No specific 403/429/503/timeout/reset was directly observed for any of the 318 pairs on 2026-09-11. The conclusion rests on convergent circumstantial evidence, which this task's own definitions place at MEDIUM.

### Contributing factors

- **Observability/reason-code persistence failure** (Part 12) — doesn't cause the loss, but makes the primary-cause hypothesis unconfirmable from historical records and would silently reabsorb the same failure on any future re-run.
- **`fetch_one`'s silent-return-`None` path on exhausted 403/429/503** (Part 7 q11) — a confirmed code gap whose failure signature (repeated 403/429/503, total silence) is directly compatible with an HTTP/access-problem cause.
- **Discovery-client vs. fetch-client configuration asymmetry** (Part 7 q1–q9, Part 9) — a real, confirmed code difference, tested directly and found *not* to matter under today's conditions. Downgraded from a primary-cause candidate to a documented, unconfirmed contributing hypothesis.

### Causes considered and ruled out

| Hypothesis | Status |
|---|---|
| D. File-format/validation problem | **Ruled out** for the sample — all 10 URLs returned valid, correctly-typed bodies today; `fetch_one` would accept every one. |
| E. Control-flow/skipping problem (`cohort_fetch_manifest.jsonl` pre-filtering) | **Ruled out** — shown to be a post-hoc derivative of successful downloads, not a pre-fetch filter (Part 7). |
| A. Discovery/source problem | **Not applicable** to this loss by definition (`discovered=True` for all 318); a separate, already-quantified 64-company-year DISCOVERY loss exists but is out of scope here. |

Only one primary cause is named; **B** (fetch invocation/client-state) is retained strictly as an unconfirmed contributing factor, not promoted to a second primary cause, given Part 9's result.

---

## Part 14 — Confidence, as applied here

| Level | Definition | Applied to |
|---|---|---|
| **HIGH** | Direct evidence from committed control flow or persisted historical records | The discovery/fetch client asymmetry exists; DOWNLOAD/DISCOVERY reason coverage is 0%; `fetch_one`'s silent 403/429/503-exhaustion path; `cohort_fetch_manifest.jsonl`'s pair-set exactly equals `downloaded=True` (ruling out the pre-filter hypothesis) |
| **MEDIUM** | Independent evidence converges, but historical execution can't be directly observed | The primary-cause conclusion itself (time-varying HTTP/access condition) |
| **LOW** | Plausible but incomplete | Any claim about which *specific* failure mode hit any *specific* one of the 318 pairs on 2026-09-11 |

---

## Unresolved questions

- Whether the 2026-09-11 crawl(s) ran on code byte-identical to HEAD `0fb8cbf` — not establishable from committed history alone.
- Whether there was one `arpipe fetch` invocation that day or several — `documents.jsonl`'s append + resume-skip design can't distinguish these.
- Which specific failure mode (timeout / reset / 403 / 429 / 503 / other) hit any specific one of the 318 losses — no per-attempt evidence exists at all.
- Whether the archive host's volatility is NSE-side (time-of-day/session/rate-limit state) or reflects conditions specific to the IIT Kanpur campus network used for every live probe in this diagnosis and its predecessor — both remain open.
- Whether concurrency (the `ThreadPoolExecutor` worker count) interacted with `HostLimiter`'s 1.5s-per-host minimum interval and any Akamai bot-mitigation threshold at the moment a "good" window opened — `HostLimiter` would not prevent a burst of near-simultaneous connections from multiple worker threads at that instant.

---

## Minimal next repair test (defined, not implemented)

Add **purely additive, structured** failure-reason logging to `_fetch_pair`/`fetch_one` — one JSONL row per failed attempt: `company_id, fy_end, source, url, exception_type_or_status, timestamp_utc`. No retry, backoff, timeout, or client change. Then re-run `arpipe fetch` against a small, already-frozen subset — e.g. this task's 5 `DOWNLOAD_ZERO_FY` sample observations — in isolation, and read the new persisted reasons directly. This converts "historical invocation = UNKNOWN" into a directly observable, persisted, per-attempt record going forward, and would immediately confirm or refute whether repeated 403/429/503 (the silent path found in Part 7 q11), timeouts, or resets are what these pairs actually hit.

This is deliberately the *smallest* change that turns an unknown into evidence — not implemented in this task, per scope.

---

## Scope compliance

Did **not**: modify production code (diff against HEAD is empty), rerun the 576-observation acquisition, rerun the 194-document extraction, add retries/backoff, change any timeout, alter any HTTP client, change URL handling/acceptance logic, modify any manifest, create Universe V2, change P-M5 stage membership, or touch `arpipe-0.1.0` / `arpipe-pm5-coverage` / `arpipe-pc0-diagnostic-base`. Network requests made by this task: 22 GETs total (10 for Part 4 + 12 for Part 9's seeding/target requests across 3 URLs × 2 configs), all single-attempt, to public regulatory-archive endpoints already sampled by the predecessor diagnostic.

---

## Final verdict

# COVERAGE MECHANISM PARTIALLY IDENTIFIED — FURTHER EVIDENCE REQUIRED
