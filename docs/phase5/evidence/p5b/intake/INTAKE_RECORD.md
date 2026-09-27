# P5-B intake record: v0.2.2 blind title evidence (27 Sep 2026)

Evidence labels: VERIFIED = checked by code in this intake; INFERRED = reasoned, not proven.

## 1. What entered the repo
- **Raw commit** `06261d1` (branch `phase5-b-intake`, parent `e1803fc` = `phase5-a1`) added the v0.2.2 package **as produced**:
  - `v0_2_2/`: 28 files, of which 25 are listed in `HASHES_v0_2_2.txt`;
  - `inputs_ref/`: the manifest, the v0.2 hash list, the v0.2 catalog, and the expected-hash list v2.
- **Merged to `main` as PR #32** (`2fb2718`) before this intake verification. The content is identical; only this `intake/` folder is added on top.
- **Byte-exact storage:** `.gitattributes` (`* -text`) keeps the bytes unchanged.
- **Produced by:** Codex (GPT-5.6 Sol) in the isolated `D:\gold_blind` workspace, prompt v6 (P5-B.2.2 attempt 6). Verdict `P5_B22_PASS_WITH_REVIEW_ITEMS`.

## 2. Independent verification in this intake (VERIFIED)
Run `python docs/phase5/evidence/p5b/intake/build_intake_pack.py`. It was run twice here and gave byte-identical output.

| Check | Result |
|---|---|
| Package files vs `HASHES_v0_2_2.txt` | 25/25 match (the hash list itself is `b7327ee3…b9ca`) |
| Ledger / frame rows | 3,215 / 1 |
| Documents | 60; 0 PDF-hash mismatches against the manifest |
| Unique 5-part key / `obs_id` | 0 / 0 duplicates |
| Pages within the page count | 0 out of range |
| Class counts (EQUIVALENT / CONDITIONAL / CONFUSABLE) | 150 / 66 / 2,999 |
| Evidence index | 259 rows (258 structural + 1 frame), 146 distinct PNGs; all 216 key rows have a PNG |

**This agrees with the producing run's G1–G5.**

## 3. New finding: the ledger's heading fields are not verbatim (VERIFIED)
`heading_text_verbatim` and `heading_text_visual` are usually **the AI reader's notes**, not the printed heading. For example:
`, main section heading: \`MANAGEMENT DISCUSSIONS AND ANALYSIS\``, or a paragraph that *mentions* MD&A.

| Class | Rows | Clean quoted heading only | Heading quoted inside a note | No quoted heading | Mention wording (heuristic) |
|---|---|---|---|---|---|
| EQUIVALENT | 150 | 24 | 108 | 18 | 9 |
| CONDITIONAL | 66 | 0 | 60 | 6 | 32 |
| CONFUSABLE | 2,999 | 786 | 1,713 | 500 | 5 |

**Consequences (INFERRED):**
1. The v0.2 title catalog couldn't be traced to the ledger (29/80 entries with no match): the ledger holds notes, not headings.
2. Some key rows record a *mention* of MD&A in running text (e.g. "Means of Communication … MD&A forms part of the Annual Report"). That is not a title.
3. Several ledger notes contain page references (e.g. "(p5)"). **The ledger must never be shown to annotators.**
4. The pre-declared 5% spot-check rule ("page, text or class wrong") is very likely to trigger on *text* for the key rows. Its declared fallback is: redo the affected scope with TOC + section-opening pages, verified page by page.

## 4. What this intake adds (mechanical, no class decisions)
| File | Purpose |
|---|---|
| `KEY_ROW_CANDIDATES_v0_2_2.csv` | All 216 EQUIVALENT/CONDITIONAL rows. For each: page, location, field format, mention flag, the back-quoted strings pulled from the note, and the evidence PNG |
| `KEY_QUOTED_STRING_INVENTORY_v0_2_2.csv` | The 124 distinct quoted strings in key rows, with row, document and class counts (exact text, no grouping) |
| `DOCUMENT_WORKSHEET_v0_2_2.csv` | One row per FIT DEVELOPMENT document (60). It lists the AI-suggested pages and strings and the evidence PNGs, plus **blank reviewer columns**: MD&A present, TOC title verbatim, body title verbatim, body start page, notes |
| `INTAKE_SUMMARY.json` | All counts above, produced by the script |

**Documents with no key rows** (the reviewer checks these first): `INE004C01028_2017`, `INE004C01028_2025`, `INE00FF01025_2015` (the frame stub: a SEBI letter, not an annual report).

## 5. Recommended use (the rules reviewer / author)
1. **Don't use** `TITLE_EQUIVALENCE_v0_2_2.md` or the v0.2 catalog as the title list. They are a **draft reference** only (reconciliation: L1 = 26, L2 = 25, NONE = 29; AGREES = 40, CONFLICT = 11).
2. **Fill `DOCUMENT_WORKSHEET_v0_2_2.csv` for all 60 documents.** Open the listed PNGs (kept on the author's PC under `D:\gold_blind\output\v0_2\evidence_pages\`, identified by SHA-256 in `EVIDENCE_INDEX_v0_2_2.csv`) and record the printed MD&A title **verbatim**. This is the pre-declared fallback (TOC + section-opening pages, page by page), limited to the MD&A scope.
3. **Build the blind title list from the reviewer's verbatim titles.** Decide EQUIVALENT / CONDITIONAL per rule, including the open items: "Business Environment", apostrophe/plural variants, "CORPORATE GOVERNANCE AND MANAGEMENT DISCUSSIONS & ANALYSIS", and the Hindi title.
4. **Freeze the title list** before any annotator sees anything (governance Q5/Q7). No HOLDOUT material is involved.

## 6. Known issues carried forward
The package's `METHOD_NOTE_v0_2_2.md` lists K-A to K-L. The most important:
- **K-I:** four v0.2 non-data files were rewritten at 13:42 by an unknown session. Data files are unaffected.
- **K-C:** earlier runs read repo-side Claude logs without disclosing it.
- **K-L:** visual coverage is 25.84%, not 22.5%.

## 7. Blindness note
- This intake was done by an agent (Claude, claude.ai session) that has repository access.
- It **made no classification decisions**: it only verified hashes, re-counted, and extracted quoted strings mechanically.
- It didn't read `arpipe/` heading patterns, tests, reports, labels or eval files for this work.
- All title decisions stay with the human reviewer.
