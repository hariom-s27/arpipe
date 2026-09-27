# Phase 5 blocker research R1: title-rule questions and viewer pin

**Status:** `RESEARCH_INPUT_PENDING_AUTHOR`. **Date:** 2026-09-27.
**Branch:** `phase5-research-r1` (from `phase5-b-intake` `a286de6`).

This memo gathers evidence and sets out options for the title-rule and viewer
questions that block freezing the blind title list and the method. **It decides
nothing.** Every choice below is for the author (rules reviewer) to make and record.
Labels follow R3: VERIFIED / SOURCED / DERIVED / INFERRED / PROPOSED.

**Blindness and scope.**
- Written by an agent (Claude) with repository access. It did not open
  `arpipe/patterns.py`, `arpipe/tests/`, `reports/`, `labels*.csv`, eval files, any
  PDF, or any HOLDOUT row.
- Corpus evidence comes only from the committed intake worksheet
  `DOCUMENT_WORKSHEET_v0_2_2.csv` (SHA-256 `0d05c6d7…66b4`). Its `ai_quoted_strings`
  are **AI notes from P5-B, not verified titles** (see `INTAKE_RECORD.md` §3).
- All counts are **DEVELOPMENT-subset counts** (60 FIT documents), never FIT prevalence
  (`PILOT_PLAN_v0_1.md` §3).

## 1. Regulatory basis (SOURCED)

| Period | Source | Relevant text |
|---|---|---|
| FY2005–FY2015 reports | Clause 49 of the Listing Agreement, IV(F)(i); SEBI circular SEBI/CFD/DIL/CG/1/2004/12/10, 29 Oct 2004 | "As part of the directors' report or as an addition thereto, a Management Discussion and Analysis report should form part of the Annual Report to the shareholders." Items: industry structure and developments; opportunities and threats; segment-wise or product-wise performance; outlook; risks and concerns; internal control systems; financial vs operational performance; HR/IR developments |
| FY2016 onward | SEBI (LODR) Regulations 2015, Reg. 34(2)(e) (as originally notified), with Schedule V Part B | "management discussion and analysis report – either as a part of directors report or addition thereto". Schedule V Part B repeats the same content items; later amendments added key financial ratios |
| Both | Schedule V Part C (LODR) / Clause 49 | The Corporate Governance report is a **separate** required report |

**INFERRED.** Three consequences for the title rules:
1. The statutory name of the section is "Management Discussion and Analysis (report)".
   Spelling variants refer to the same thing.
2. Placing MD&A inside the Directors' Report is expressly allowed. This matches
   Rule 5 (embedded).
3. MD&A and the Corporate Governance report are distinct statutory reports, so a
   heading that joins them names two reports, not one.

**Caveat (PROPOSED check).** Later LODR amendments renumbered parts of Reg. 34(2). The
clause letter "(e)" is as originally notified. GOLD_PROTOCOL Rule 6 already cites it
that way, so nothing needs to change. Confirm against the official consolidated SEBI
text before publication.

## 2. Open title questions

The worksheet counts below are documents whose AI-quoted strings match the pattern.
They show how many documents a decision touches; they are not title facts.

### T1. Spelling variants: apostrophe, plural, "&", "Report", numbering

**DERIVED (worksheet).** Variant forms appear in the DEVELOPMENT subset:
- "Management's": 7 documents;
- "Discussions": 7;
- "Discussion & Analysis": 15;
- plus leading enumerators ("19.", "5.", "J.") and TOC page numbers appended
  ("… Analysis 86").

**Options.**
- **(A) Declared normalisation rule.** Treat as the same title after these steps:
  1. case-fold;
  2. treat straight and curly apostrophes alike and drop the possessive `'s`;
  3. `Discussions` → `Discussion`;
  4. `&` → `and`;
  5. optional trailing "Report";
  6. strip a leading enumerator and a trailing TOC page number.

  The list shows one EQUIVALENT entry plus the rule and some verbatim examples.
- **(B) Enumerate every verbatim string** as its own EQUIVALENT entry.

**PROPOSED.** A is simpler for annotators and follows from §1(1). B is the more
literal reading of Q7 ("title-equivalence list"). Either way, the annotator-facing list
must contain no document IDs, pages or issuer names (GOLD_PROTOCOL §6).

### T2. Combined heading: "Corporate Governance and Management Discussions & Analysis"

**DERIVED (worksheet).**
- 5 documents, all from one issuer (`INE001F01019`).
- The same documents also carry a separate "MANAGEMENT DISCUSSIONS AND ANALYSIS"
  string, which suggests an MD&A sub-heading. This is **unverified**.

**Options.**
- **(A) CONDITIONAL.** Qualifies only when an MD&A sub-heading is visible under the
  combined heading. The span is that subsection alone, ending before the next
  same-level or higher heading (the Rule 5 sibling logic).
- **(B) EQUIVALENT.** The span is the whole combined section. By §1(3) this would
  include Corporate Governance report pages.
- **(C) CONFUSABLE.** Only a separate MD&A heading counts.

**Schema gap (VERIFIED).**
- `embedded_in_directors_report` is the only "embedded" flag, and it names the
  Directors' Report.
- Under option A, an MD&A embedded in a combined CG+MD&A section has no matching flag.
- Deciding whether to add a flag (for example `embedded_in_other_section`) or to reuse
  `parent_section` without the flag is a schema change. It belongs in the method
  revision, not in this memo.

### T3. "Directors' Report and Management's Discussion and Analysis"

**DERIVED (worksheet).** 1 document (`INE002A01018_2013`).

**Options.**
- **(A)** If an MD&A sub-heading exists, apply Rule 5: record the subsection, set
  `embedded_in_directors_report`, and record the parent.
- **(B)** If there is no MD&A sub-heading (one merged narrative), treat the whole
  combined section as the MD&A span, as a CONDITIONAL title whose condition is "no
  separate MD&A sub-heading exists".

**PROPOSED.** §1(2) supports treating this combined title as legitimate. Choosing
between A and B depends on what the page shows, and the reviewer records that.

### T4. "Business Environment"

**DERIVED (worksheet).**
- 1 document (`INE008A01015_2012`).
- The same document also lists "Management Discussion & Analysis" and a Hindi MD&A
  string.

**Analysis (INFERRED).**
- "Business Environment" is not a statutory title. It matches the *content* items in
  Schedule V ("industry structure and developments", "outlook").
- If the document has an explicit MD&A heading, "Business Environment" is just its
  first sub-heading. It then bears on `substantive_start_page`, not on the title list.

**PROPOSED default.** CONFUSABLE. Reopen only if the reviewer finds a report whose MD&A
has **no** MD&A heading and begins with "Business Environment". Under Rule 9 that
would be an unusual title needing an explicit list entry.

### T5. Hindi title "प्रबंध विवेचना एवं विश्लेषण"

**DERIVED (worksheet).**
- 2 documents (`INE008A01015_2012`, `_2017`).
- Includes the bilingual TOC form "प्रबंध विवेचना एवं विश्लेषण / Management
  Discussion and Analysis".

**Analysis.**
- **INFERRED.** Word for word, the Hindi reads "management (प्रबंध) discussion/
  interpretation (विवेचना) and (एवं) analysis (विश्लेषण)".
- **SOURCED (Rule 3).** The English full MD&A is primary; the Hindi copy is listed
  as an alternative span of type `HINDI_COPY` with the `bilingual` flag.

**Options.**
- **(A)** List the Hindi string as CONDITIONAL, with the observable condition "used
  only to identify the Hindi copy (alternative span `HINDI_COPY`); never qualifies the
  primary span".
- **(B)** Leave it off the list and rely on Rule 3's wording alone.

**Caution (SOURCED, master context §6).** An earlier P5-B "verbatim" IDBI 2012 Hindi
heading was text-layer garbage (a legacy font). Any Hindi list entry must be copied
from the **rendered page**, never from extracted text.

### T6. Pointers and mentions (no decision needed)

**DERIVED (worksheet).** 6 documents have "Means of Communication"-type strings among
their AI-quoted strings.

**SOURCED.** Rule 1 and the `POINTER_ONLY` reason code already say a "forms part of"
pointer is not presence and not a title. The reviewer should simply reject these as
titles.

### T7. Annexure-prefixed titles (no decision needed)

**DERIVED (worksheet).** 10 documents have "Annexure" strings.

**SOURCED.** Rule 6 covers them. The title is the MD&A string; the annexure label goes
in `annexure_identity`.

## 3. Viewer pin (open decision (d) in `CHANGELOG_v0_1.md` §6)

**Requirement (SOURCED, GOLD_PROTOCOL §2).** The page box shows the physical 1-based
page with page labels disabled. Viewer, version and setting are pinned at method
freeze.

| Viewer | Evidence | Fit |
|---|---|---|
| Adobe Acrobat / Reader | **SOURCED.** Preference "Use logical page numbers" under Preferences → Page Display. When it is off, the page box shows physical numbers | Meets the requirement directly. The setting is checkable and can be recorded |
| SumatraPDF | **SOURCED.** There is no setting to hide page labels. When a PDF has labels, it shows the label **and** the physical number as "(x / Total)". A developer reply on the forum declined a switch | Usable only with an explicit instruction to type the "x" in "(x / Total)". The risk of typing the label is higher |

**PROPOSED.** Pin Adobe Acrobat Reader (the exact version at freeze) with "Use logical
page numbers" **off**. Add one pre-annotation check per workspace: open a PDF whose
first sheet is a cover, confirm the page box shows 1 on the cover, and have the
setting check signed ("SETTING VERIFIED BY"). The P5-T tool's page-count check
catches a wrong viewer count, but **not** a single mistyped label. The pilot should
therefore measure how often that happens.

## 4. Not researched here (still on hold, with reasons)

| Item | Why on hold |
|---|---|
| Interval method | Author choice before HOLDOUT scoring; not a pilot blocker (`CHANGELOG_v0_1.md` §6(a)). The earlier recommendation (issuer-cluster percentile bootstrap, 10k reps, sensitivity only) stands |
| Q10 climate recipe (C4, B7) | Deferred by governance until C4 |
| INE00LO01017_2015 (2-page stub candidate) | Needs its PDF, which is on the author's PC only |
| K1 (repo-side Claude logs read during P5-B) | Only the author knows |
| A1–A5, C1-D1 signatures | Author signatures at method freeze |

## 5. Sources

- Clause 49, SEBI circular of 29 Oct 2004 (NSE archive): https://nsearchives.nseindia.com/content/equities/clause_49_sebi_circ.pdf
- LODR Regulation 34 (CAIRR ready reckoner): https://ca2013.com/lodr-regulation-34/
- LODR Schedule V (CAIRR): https://ca2013.com/schedule/lodr-schedule-v-2/
- ICSI deck on MD&A, June 2023: https://www.icsi.edu/media/filer_public/21/a7/21a72c94-c540-4b07-9b1b-fcec707eedda/icsi_deck_on_mda_june23_.pdf
- Acrobat "Use logical page numbers" steps (Enfocus manual): https://cdn.enfocus.com/manuals/Extra/PreflightReportHelp/18/en-us/common/pr/task/t_aa1014034.html
- SumatraPDF forum, "Option to display Real Page Number": https://forum.sumatrapdfreader.org/t/option-to-display-real-page-number/1020
- SumatraPDF settings reference: https://www.sumatrapdfreader.org/settings.html
