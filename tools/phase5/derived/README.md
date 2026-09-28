# Post-seal text-layer audit

`text_layer_audit.py` derives the D1–D7 §7.2–§7.3 text-layer fields from a sealed
span CSV and the corresponding PDFs. It uses the PDF text layer only: it never runs
OCR, changes Gold, or imports `arpipe`.

Run it with the project interpreter:

```text
python tools/phase5/derived/text_layer_audit.py --input INPUT.csv --pdf-dir PDF_DIR --out NEW_OUT_DIR [--max-bad-char-share 0.05] [--min-latin-word-share 0.50] [--wordlist WORDLIST] [--i-have-author-approval]
```

The input header must be exactly:

```text
document_id,start_page_0based,end_page_0based,body_title,gap_pages,csr_esg_pages,split
```

Page lists are sorted, unique, semicolon-separated 0-based integers and may be
empty. Splits are `FIT`, `VALIDATION`, or `HOLDOUT`. A HOLDOUT row is refused unless
the explicit author-approval switch is present. Document IDs follow
`[A-Za-z0-9._-]+`, and the PDF is `<pdf-dir>/<document_id>.pdf`.

The program refuses an existing output path, an output path beneath any `.git`
marker, duplicate document IDs, invalid spans or pages, gap pages outside the strict
span interior, CSR/ESG pages outside the span or also listed as gaps, missing PDFs,
and malformed input. It validates and computes every document before creating the
output directory.

## Heading normalization

Both the Gold `body_title` and extracted start-page text undergo the same ordered
normalization: Unicode NFKC; casefold; replace `&` with `and`; remove possessive
`'s`, the words `report` and `annexure`, and the phrase `to the directors'`; remove
year ranges such as `2023-24` and `2011-12`; remove a leading item/annexure label
such as `b.`, `4.`, `annexure 1 –`, or `annexure - ii`; then delete every Unicode
whitespace and punctuation character. `heading_in_text_layer` is true when the
normalized title is a substring of normalized start-page text. An empty title emits
`NA`.

## Broken-text fields

`bad_char_share` is the number of extracted start-page characters that are U+FFFD,
U+E000–U+F8FF, or Unicode control characters other than newline, carriage return,
and tab, divided by all extracted characters. It is `0.0` for an empty text layer.

For `latin_word_share`, the start-page text is split on whitespace and Unicode
punctuation is stripped only at token edges. Tokens containing any digit are dropped.
Tokens consisting only of non-Latin-script letters and their combining marks are
dropped. Remaining tokens shorter than three characters are dropped. A kept token is
a real Latin word only when it consists of ASCII letters with optional internal
straight apostrophes or hyphens. `kept_token_count` is the denominator and
`latin_word_share` is the matching-word share.

`text_layer_broken` is true when `bad_char_share` is strictly greater than
`max_bad_char_share` or `latin_word_share` is strictly less than
`min_latin_word_share`. If no token is kept, it is `NO_TEXT` and
`latin_word_share` is JSON `null` / an empty CSV cell.

## Word counts and artifacts

A word-count word is a whitespace token which, after stripping leading/trailing
Unicode punctuation, contains at least one ASCII letter. `mdna_word_count` sums the
inclusive `start..end` pages except `gap_pages`. `csr_esg_word_count` sums exactly
`csr_esg_pages`; those pages remain part of the MD&A count unless they are excluded by
the span rules. Counts always come from the existing text layer.

`TEXT_LAYER_AUDIT.json` is UTF-8 canonical JSON with sorted keys, compact separators,
and one final LF. Its top-level `header` contains the script SHA-256, PyMuPDF version,
thresholds, and raw input SHA-256; `documents` is sorted by ID. The CSV is UTF-8 with
LF line endings, begins with a `header_key,header_value` metadata block, then a blank
row and the document table. Booleans are lowercase in CSV; `NA` and `NO_TEXT` remain
literal states. Neither artifact contains timestamps or machine-specific paths, so
identical inputs, script, thresholds, and PyMuPDF version produce identical bytes.

The 0.05 and 0.50 defaults are calibration values, not tunable analysis choices.
Thresholds must be calibrated on FIT only, then frozen after FIT calibration and
before any HOLDOUT use. The production calibration result is outside this synthetic
test implementation and must be recorded separately before author-approved HOLDOUT
processing.

## v0.2

Version 0.2 introduces two-page evaluation (evaluating heading presence on the start
page and body quality on a representative quality page), unified broken indicators,
page-sharing indicators, and optional dictionary token coverage.

### Input schema and CLI additions

- **`end_page_shared` (optional input column):** The input CSV accepts an optional
  eighth column `end_page_shared` with values `Y`, `N`, or empty. Input files without
  this column remain valid and are treated as empty.
- **`--wordlist <path>` (CLI option):** Accepts either a plain file with one word per
  line or a CSV file whose first line contains a comma and a header cell equal to
  `Word` (case-insensitive). Strip whitespace and casefold words when loading.
- **Header block metadata:** `audit_version` is set to `"0.2"`. `wordlist_sha256`
  records the SHA-256 hex digest of the wordlist file, or `null` in JSON and empty in
  CSV if no wordlist was provided.

### New output columns and exact rules

Output columns are appended in this order after the existing v0.1 columns:

1. **`quality_page_0based` (integer):** The 0-based page index chosen for evaluating
   body text quality. It is the first page `p` in the range `start_page_0based..end_page_0based`
   (excluding any pages listed in `gap_pages`) where `count_raw_tokens(page_text) >= 50`.
   `count_raw_tokens(text)` counts whitespace-separated tokens that have length >= 3
   after stripping edge punctuation using `_strip_edge_punctuation`. Digit tokens,
   non-Latin tokens, and corrupted/garbage characters are not dropped and count toward
   the 50-token threshold. If no page in `start..end` reaches 50 tokens, the start page
   is used as fallback.
2. **`quality_page_fallback` (boolean):** `true` if no page reached 50 raw tokens and
   the start page was selected as fallback; `false` otherwise.
3. **`broken_text_group` (boolean or `"NO_TEXT"`):** Unified indicator combining
   `text_layer_broken` (evaluated on the quality page) and `heading_in_text_layer`
   (evaluated on the start page):
   - `true` if `text_layer_broken` is `true` OR `heading_in_text_layer` is `false`.
   - `false` if `text_layer_broken` is `false` AND `heading_in_text_layer` is `true` or `"NA"`.
   - `"NO_TEXT"` if `text_layer_broken` is `"NO_TEXT"` and `heading_in_text_layer` is not `false`.
4. **`dictionary_word_share` (float or `"NA"`):** Share of the quality page's kept tokens
   (casefolded) present in the dictionary supplied via `--wordlist`. Evaluated on the
   exact same kept tokens as `latin_word_share`. Emits `"NA"` if no kept tokens exist or
   if no `--wordlist` was provided. This measure is purely descriptive and does not alter
   `text_layer_broken` or `broken_text_group`.
5. **`start_page_shared` (boolean or `"NA"`):** Evaluated strictly on the start page.
   If `body_title` is empty, emits `"NA"`. Otherwise, extracts text lines and their
   vertical bounding-box positions (`page.get_text("dict")` blocks and lines, line top =
   `line["bbox"][1]`, line text = join of span text). Locates the first line `i` such
   that `normalize_heading(line i)`, `normalize_heading(line i + line i+1)`, or
   `normalize_heading(line i + line i+1 + line i+2)` (joined with a space) contains
   `normalize_heading(body_title)`. If found, returns `true` if `line top > 0.20 * page.rect.height`
   (indicating a shared start page where the section begins lower down), or `false`
   otherwise. If the heading is not found on the start page, emits `"NA"`.
6. **`end_page_shared` (boolean or `"NA"`):** Derived from the input `end_page_shared`
   column: `"Y"` -> `true`, `"N"` -> `false`, empty or omitted -> `"NA"`.
7. **`word_count_scope` (string):** Always the constant string `"PAGE_LEVEL"`.

Body quality metrics (`bad_char_share`, `latin_word_share`, `kept_token_count`, and
`text_layer_broken`) are computed on the quality page. `heading_in_text_layer` is
computed strictly on the start page.

### Threshold calibration rule (Decisions §8.4 and §8.5)

On the FIT recalibration rerun, evaluated over documents expected CLEAN or PARTIAL (all
FIT documents except the three expected BROKEN):
- `max_bad_char_share` = `max(0.05, 2 × highest clean value)`
- `min_latin_word_share` = `min(0.50, 0.5 × lowest clean value)`

Clean sets as defined in §8.5:
- **Body check:** Clean comprises every FIT document whose body text layer is not broken,
  i.e. all FIT documents except Span 2018 (`INE004E01016_2018`). Jubilant 2013 and
  Gujarat Cotex 2017 have clean bodies and count as clean for this threshold.
- **Heading check:** The expected positives are the three listed documents: Span 2018,
  Jubilant 2013, and Gujarat Cotex 2017.

The resulting threshold values must be recorded and frozen before any VALIDATION or
HOLDOUT documents are scored.
