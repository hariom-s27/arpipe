# ARPipe Gold annotation bundle (offline)

**Start: open your folder and double-click `annotator_app.exe` (do not start it from a
terminal that is inside another project). Your role is set by this folder.**

Status: DRAFT_PENDING_PILOT. Tool version p5t-0.2.0.

## Before you start
- Work on a computer folder that is **not** inside any code repository and has no
  internet use during annotation. The tool refuses to start if it finds `.git`, or
  folders named `arpipe/`, `reports/`, `docs/identity/`, or any `labels*.csv` file.
- You need Python 3 with tkinter, and the `jsonschema` package. Without `jsonschema`
  the form opens but you cannot submit.
- The custodian gives you `ASSIGNMENT.csv` (your documents) and the frozen title
  list. While `TITLE_LIST_NOT_YET_FROZEN.txt` is in this folder, nothing can be sealed.
- Read `GOLD_PROTOCOL_v0_4.md`. It is the rulebook.
- Pilot viewer: Adobe Acrobat Reader (record the version). In Edit > Preferences >
  Page Display, switch "Use logical page numbers" OFF.

## Pages: always the viewer's physical page, 1-based
1. In your PDF viewer, **turn page labels off** so the page box shows 1, 2, 3 ...
   from the very first sheet of the file (not printed page numbers, not Roman numerals).
2. Type exactly the number in the viewer's page box. The form shows
   "viewer page X = stored index X-1"; the file stores X-1.
3. Type the viewer's total page count. If it differs from the verified PDF, stop:
   page labels are probably still on.

## Run
Start: double-click `annotator_app.exe` if you were given one, otherwise run
`python annotator_app.py`.
```
python annotator_app.py
```
1. Type your role (`ANNOTATOR_A` or `ANNOTATOR_B`).
2. Pick a document, then choose its PDF. The tool checks the SHA-256; a wrong file
   cannot be used.
3. Fill the form. **Check** validates without saving. **Submit and seal** saves a
   read-only record in `records/<role>/` and appends its SHA-256 to
   `records/HASH_LOG.txt`.
4. A record is never overwritten. To correct one **before** the custodian exports your
   records, use **Supersede** with the old SHA-256 and a reason. Both files are kept.

## Anchor text on shared start/end pages
When you answer **Yes** to *Start page shared with another section?* or *End page
shared with another section?*, the matching anchor-text box below it turns on: copy that
page's heading line into it (the MD&A heading for a shared start page, the heading of the
section that follows MD&A for a shared end page), from the text layer if you can, typed
from the page image otherwise. Answer **No** and the box stays off and must stay blank.

## Permitted aids
Only the pinned PDF viewer, its thumbnails, search, bookmarks, zoom/rotate and page
count. No AI assistant, OCR, web search, repository tool, regex or earlier record.
