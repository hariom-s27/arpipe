# Offline Gold RAW annotator v0.1

Extract this ZIP into a fresh directory **outside any Git repository**. Keep that
directory offline. Do not copy repository files, reports, identity files, or
`labels*.csv` into it. The tool refuses those paths at startup.

Install Python 3 with tkinter and `jsonschema` in the offline environment. From
the extracted directory run `python app.py`. The window can open without
`jsonschema`, but submission requires it. No internet connection is used.

The custodian supplies an assignment CSV with exactly these columns:
`document_id,source_pdf_sha256,physical_page_count`. Choose a row and the assigned
PDF. The tool only hashes the selected file; it does not read or render its
pages. Inspect it in your own pinned offline PDF viewer, with **physical page
numbers and page labels disabled**. Enter its displayed 1-based physical page
count and use viewer page numbers in every page field. Viewer page X is stored
as zero-based index X-1. A file hash or page-count mismatch blocks entry.

Complete the protocol's independent RAW fields. The title-equivalence list is
not frozen yet; the included placeholder is not an accepted list and must not
be used for annotation. A record is sealed read-only under `records/ANNOTATOR_A`
or `records/ANNOTATOR_B`; its SHA-256 is appended to `records/HASH_LOG.txt`.
Repeat submission for a document and role is refused. Before A/B comparison,
the same annotator may explicitly supersede a RAW record with its old hash and
reason in the form. The old record remains sealed. Once comparison begins, the
custodian creates `records/COMPARISON_LOCKED` to close supersession.

Custodian export: `python export_role.py . ANNOTATOR_A role_a.zip` (or
`ANNOTATOR_B`). The ZIP contains only that role's sealed records and its matching
hash-log entries. The command prints each member's size and SHA-256.
