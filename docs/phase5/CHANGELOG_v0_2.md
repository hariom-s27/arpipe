# ARPipe Gold method v0.2 changelog

**Document status:** `DRAFT_PENDING_PILOT`

**Execution date:** 2026-09-28

## 1. Scope and predecessor preservation

This revision implements F5 from
`docs/phase5/decisions/D1_D7_DECISIONS_v0_1.md` §4, using the author decisions in
§§1–2 and §§5–7. It adds `GOLD_PROTOCOL_v0_2.md`, `SAP_v0_2.md`, and this changelog;
updates the two annotator bundle filename references; and updates only the matching
bundle-content test assertions.

The v0.1 files are unchanged. Their SHA-256 values are:

| v0.1 path | SHA-256 |
|---|---|
| `docs/phase5/GOLD_PROTOCOL_v0_1.md` | `6775a87453412ef25d5485c551bb31facfc8deaf0c92667b0dcc9a3c350b607d` |
| `docs/phase5/SAP_v0_1.md` | `2a945bc92e1b256ce0ca9fc14e91902f2a4b3424e91253e3dec058929e1f5dcf` |
| `docs/phase5/CHANGELOG_v0_1.md` | `944a5a9ec6d82ff12532af865f06344a6c3b8064557ffeca72a83a77b3aada19` |

## 2. Gold protocol v0.2

- Changed the title/version line and added a top change box
  (`D1_D7_DECISIONS_v0_1.md` §4 F5).
- Added the three-level boundary hierarchy: own heading means heading-bounded; MD&A
  embedded in a Directors'/Board's Report uses the legal-content test; TOC grouping
  never overrides report identity (`D1_D7_DECISIONS_v0_1.md` §2, D5).
- Added ABSENT reasons `NO_ENGLISH_MDA` and `EXTERNAL_REFERENCE_ONLY`, and specified that
  a pointer sentence is not a stub and must be followed
  (`D1_D7_DECISIONS_v0_1.md` §§1 D1–D2, 6 F4, and 7.1).
- Replaced the untested/unknown bilingual text with the three IDBI FIT findings from the
  2026-09-28 title review; made English primary regardless of copy order; retained Hindi
  as `HINDI_COPY`; and specified Hindi-only handling without permitting post-HOLDOUT rule
  revision (`D1_D7_DECISIONS_v0_1.md` §§1 D1, 3, and 7.1).
- Defined the D4 embedded end as immediately before the first statutory item after MD&A
  begins, reproduced the closed items 1–16, and added the three-topic tie-break list
  (`D1_D7_DECISIONS_v0_1.md` §§1 D4, 5, and 6 A1–A3).
- Limited the D7 exclusion to the Board's-report “Subsidiary Companies” section while
  retaining subsidiary discussion in standalone MD&A
  (`D1_D7_DECISIONS_v0_1.md` §§1 D7 and 2).
- Added the D3 single-purpose divider/own-contents start rule and the no-body-heading
  first-TOC-sub-entry fallback documented for IDBI 2012
  (`D1_D7_DECISIONS_v0_1.md` §§1 D3, 3, and 5).
- Added Rule 10 for the visible one-page-or-less `stub` judgment and hand-entered
  `stub_word_count` only when the text layer is broken
  (`D1_D7_DECISIONS_v0_1.md` §7.2).
- Added Rule 11 for `contains_csr_esg` and viewer-page capture, including zero-based tool
  storage, in-span validation, and gap exclusion
  (`D1_D7_DECISIONS_v0_1.md` §§6 and 7.2).
- Added Rule 12 requiring `BOUNDARY_ALTERNATIVE` for D3/D4/D7 boundary decisions
  (`D1_D7_DECISIONS_v0_1.md` §7.5).
- Assigned `BROKEN_TEXT`, `HEADING_NOT_IN_TEXT_LAYER`, `mdna_word_count`, and
  `csr_esg_word_count` to the post-seal script while retaining
  `legacy_or_corrupted_boundary_heading` as an annotator observation
  (`D1_D7_DECISIONS_v0_1.md` §7.3).

## 3. SAP v0.2

- Changed the title/version line and added a top change box
  (`D1_D7_DECISIONS_v0_1.md` §4 F5).
- Made `NO_ENGLISH_MDA` and `EXTERNAL_REFERENCE_ONLY` ABSENT for the presence endpoint
  and excluded `HINDI_COPY` spans from scoring
  (`D1_D7_DECISIONS_v0_1.md` §§6 and 7.1).
- Required both exact and ±1-page start accuracy reporting
  (`D1_D7_DECISIONS_v0_1.md` §1 D3).
- Added descriptive strata for computed `BROKEN_TEXT`, computed
  `HEADING_NOT_IN_TEXT_LAYER`, `stub`, `embedded_in_directors_report`, and `bilingual`
  (`D1_D7_DECISIONS_v0_1.md` §§7.2–7.3).
- Added labelled primary-metric recomputations without D3 divider/own-contents start
  pages and without `contains_csr_esg` pages
  (`D1_D7_DECISIONS_v0_1.md` §§1 D3, 6, and 7.2).
- Directed text-measure users to the derived `mdna_word_count` and
  `csr_esg_word_count`, with no Gold word cut-off
  (`D1_D7_DECISIONS_v0_1.md` §7.3).
- Added the rule-change policy: before HOLDOUT scoring, D3/D4/D7 changes switch to the
  recorded `BOUNDARY_ALTERNATIVE`; after scoring, they are sensitivity results only
  (`D1_D7_DECISIONS_v0_1.md` §7.5).

## 4. Annotator bundle and synthetic test

- Changed `annotator_core.PROTOCOL_FILENAME` to `GOLD_PROTOCOL_v0_2.md`, so protocol
  hashing follows F5 (`D1_D7_DECISIONS_v0_1.md` §4 F5).
- Changed the bundle source to ship `GOLD_PROTOCOL_v0_2.md` instead of v0.1
  (`D1_D7_DECISIONS_v0_1.md` §4 F5).
- Updated only the bundle-content assertions that follow the filename change: v0.2 must
  be present and v0.1 must be absent. The test remains synthetic-only
  (`D1_D7_DECISIONS_v0_1.md` §4 F5).
