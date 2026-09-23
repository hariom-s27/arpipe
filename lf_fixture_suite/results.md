# LF synthetic fixture results

PyMuPDF 1.28.2; ARPipe `arpipe/triage.py` imported unmodified from main @ 52ff2fe. Synthetic PDFs only — no ARPipe corpus PDF was used.

CER = normalised Levenshtein distance vs ground truth of what a reader sees on the page (lower is better). R1 = ignore /ToUnicode, map glyph IDs back through the embedded font's own `cmap`. R3 = apply the fixture's ASCII-slot table blindly to all text. Font-level flag = per-font junk ratio >2% or English-lexicon hit rate <0.3.

| Fixture | Mechanism | ARPipe kind → route | mojibake ratio | Native CER | Tesseract CER | R1 cmap CER | R3 blind table CER | Font-level flag |
|---|---|---|---|---|---|---|---|---|
| F00_clean | healthy control (subset font) | digital → NATIVE_READ | 0.0 | 0.0 | 0.0 (eng) | n/a (subset font has no cmap) | 0.517 | False |
| F00b_clean_fullfont | healthy control (full font) | digital → NATIVE_READ | 0.0 | 0.0 | 0.0 (eng) | 0.0 | 0.517 | False |
| F01_missing_tounicode_subset | /ToUnicode missing, Identity-H, subset | broken_text → OCR | 0.15629 | 0.989 | 0.0 (eng) | n/a (subset font has no cmap) | 0.989 | True |
| F02_missing_tounicode_fullfont | /ToUnicode missing, Identity-H, full font | broken_text → OCR | 0.15629 | 0.989 | 0.0 (eng) | 0.0 | 0.989 | True |
| F03_wrong_tounicode_shift | /ToUnicode present but wrong (substitution) | digital → NATIVE_READ | 0.0 | 0.828 | 0.0 (eng) | n/a (subset font has no cmap) | 0.831 | True |
| F03b_wrong_tounicode_fullfont | same, full font (cmap retained) | digital → NATIVE_READ | 0.0 | 0.828 | 0.0 (eng) | 0.0 | 0.831 | True |
| F04_pua_tounicode | /ToUnicode maps to Private Use Area | digital → NATIVE_READ | 0.0 | 0.989 | 0.0 (eng) | n/a (subset font has no cmap) | 0.989 | True |
| F05_ascii_slot_legacy_deva | ASCII-slot 'legacy' Devanagari font (Kruti-Dev-type mechanism) | digital → NATIVE_READ | 0.0 | 0.716 | 0.093 (hin+eng) | n/a (subset font has no cmap) | 0.0 | True |
| F06_mixed_heading_missing_tu | clean body + heading font with missing /ToUnicode | digital → NATIVE_READ | 0.00465 | 0.048 | 0.0 (eng) | n/a (subset font has no cmap) | 0.54 | True |
| F07_mixed_heading_wrong_tu | clean body + heading font with wrong /ToUnicode | digital → NATIVE_READ | 0.0 | 0.043 | 0.0 (eng) | n/a (subset font has no cmap) | 0.535 | True |
| F08_mixed_heading_legacy_slot | clean body + ASCII-slot Devanagari heading | digital → NATIVE_READ | 0.0 | 0.016 | 0.004 (hin+eng) | n/a (subset font has no cmap) | 0.506 | True |
| F09_bilingual_half_legacy | bilingual page: ½ English, ½ ASCII-slot Hindi | digital → NATIVE_READ | 0.0 | 0.271 | 0.036 (hin+eng) | n/a (subset font has no cmap) | 0.319 | True |
| F10_image_plus_wrong_invisible_layer | page image + invisible (Tr 3) wrong text layer | digital → NATIVE_READ | 0.0 | 0.828 | 0.0 (eng) | n/a (subset font has no cmap) | 0.831 | True |
| F11_unicode_deva_shaped | valid Unicode Devanagari font, HarfBuzz-shaped (conjuncts, reph, pre-base matra) — no legacy font | digital → NATIVE_READ (script = mixed, mojibake 0.0) | 0.0 | 0.298 | 0.0 (hin) | not run | not run | not run |

Notes
- F01/F02 are caught by ARPipe only because the space glyph has glyph ID 3, so each raw-CID space becomes control character U+0003. Detection of missing /ToUnicode therefore depends on incidental glyph numbering, not on a mapping check.
- Subset fonts written by MuPDF carry no `cmap` and no glyph names (`post` dropped), so R1 and glyph-name checks are impossible on them; on full fonts R1 restores the text exactly (F02, F03b) and the /ToUnicode-vs-cmap agreement falls from 1.0 (F00b) to 0.186 (F03b).
- R3 (a legacy table) gives 0.0 on F05 only because the table is the fixture's own; applied blindly to a clean page it corrupts it (CER 0.517).
- The MD&A heading regex (`patterns.MDA_HEADING_RE`) matches the clean page but not F06/F07, both routed NATIVE_READ.
- pypdf 3.17.4 raised an exception on MuPDF's /ToUnicode (it writes 5-hex-digit destinations for astral code points, not UTF-16 pairs); pypdf CERs in results.json are harness errors, not measurements. pdfminer.six raised on the full-font F02.
- Font-level flag: 0/2 false positives on clean fixtures — a sample of two, not an FP-rate estimate.
