# Post-seal text-layer audit

`text_layer_audit.py` derives the D1–D7 §7.2–§7.3 text-layer fields from a sealed
span CSV and the corresponding PDFs. It uses the PDF text layer only: it never runs
OCR, changes Gold, or imports `arpipe`.

Run it with the project interpreter:

```text
python tools/phase5/derived/text_layer_audit.py --input INPUT.csv --pdf-dir PDF_DIR --out NEW_OUT_DIR [--max-bad-char-share 0.05] [--min-latin-word-share 0.50] [--i-have-author-approval]
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
