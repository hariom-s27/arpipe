"""Offline Gold annotation form (P5-T). tkinter view over ``annotator_core``.

Run from the unpacked bundle folder::

    python annotator_app.py

No network, no PDF rendering: open the PDF in the pinned viewer yourself, with page
labels disabled, and type the viewer's page numbers (1-based). The tool stores
0-based indices. All checks live in ``annotator_core``; this file is only the form.
"""

from __future__ import annotations

import sys
import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox, simpledialog, ttk

BUNDLE_ROOT = Path(__file__).resolve().parent
try:  # package import (tests, repository)
    from . import annotator_core as core
except ImportError:  # run as a script from the bundle folder
    sys.path.insert(0, str(BUNDLE_ROOT))
    import annotator_core as core  # noqa: E402

RECORDS_DIR = BUNDLE_ROOT / "records"
ASSIGNMENT_PATH = BUNDLE_ROOT / "ASSIGNMENT.csv"
PLACEHOLDER = BUNDLE_ROOT / "TITLE_LIST_NOT_YET_FROZEN.txt"
BOUNDARY_KEYS = [
    ("heading_start_page", "Heading start page"),
    ("substantive_start_page", "Substantive start page"),
    ("last_content_page", "Last content page"),
    ("next_section_heading_page", "Next section heading page"),
    ("mixed_end_page", "Mixed end page"),
]


def _opt_int(text: str, label: str) -> int | None:
    text = (text or "").strip()
    if not text:
        return None
    if not text.isdigit():
        raise core.AnnotatorError(f"{label}: enter a whole viewer page number")
    return int(text)


class AnnotatorApp:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        root.title(f"ARPipe Gold annotation ({core.TOOL_VERSION}) - offline")
        core.assert_workspace_isolated(BUNDLE_ROOT, Path.cwd())
        self.workspace_id = core.load_or_create_workspace_id(RECORDS_DIR)
        self.schema = core.load_schema(BUNDLE_ROOT)
        self.enums = core.schema_enums(self.schema)
        self.protocol_hash = core.protocol_version_hash(BUNDLE_ROOT)
        if not ASSIGNMENT_PATH.exists():
            raise core.AnnotatorError("ASSIGNMENT.csv is missing from the bundle folder.")
        self.assignment = core.load_assignment(ASSIGNMENT_PATH)
        self.role = self._ask_role()
        self.doc: dict | None = None
        self.started_at: str | None = None
        self._build()

    # -- set-up ---------------------------------------------------------------
    def _ask_role(self) -> str:
        role = simpledialog.askstring(
            "Role", "Type your role exactly: ANNOTATOR_A or ANNOTATOR_B", parent=self.root
        )
        if role not in core.RAW_ROLES:
            raise core.AnnotatorError("Role must be ANNOTATOR_A or ANNOTATOR_B.")
        return role

    def _build(self) -> None:
        outer = ttk.Frame(self.root)
        outer.pack(fill="both", expand=True)
        canvas = tk.Canvas(outer, width=900, height=760)
        bar = ttk.Scrollbar(outer, orient="vertical", command=canvas.yview)
        self.form = ttk.Frame(canvas)
        self.form.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=self.form, anchor="nw")
        canvas.configure(yscrollcommand=bar.set)
        canvas.pack(side="left", fill="both", expand=True)
        bar.pack(side="right", fill="y")
        f = self.form
        r = 0

        def row(label: str, widget: tk.Widget) -> None:
            nonlocal r
            ttk.Label(f, text=label).grid(row=r, column=0, sticky="nw", padx=6, pady=3)
            widget.grid(row=r, column=1, sticky="we", padx=6, pady=3)
            r += 1

        if PLACEHOLDER.exists():
            ttk.Label(
                f, foreground="red",
                text="Title list NOT frozen yet: you may explore the form but cannot submit.",
            ).grid(row=r, column=0, columnspan=2, sticky="w", padx=6)
            r += 1
        ttk.Label(f, text=f"Role: {self.role}    Workspace: {self.workspace_id}").grid(
            row=r, column=0, columnspan=2, sticky="w", padx=6)
        r += 1

        self.doc_var = tk.StringVar()
        row("Document", ttk.Combobox(f, textvariable=self.doc_var, state="readonly",
                                     values=sorted(self.assignment)))
        self.pdf_status = tk.StringVar(value="No PDF verified yet.")
        pick = ttk.Frame(f)
        ttk.Button(pick, text="Choose assigned PDF and verify hash",
                   command=self.choose_pdf).pack(side="left")
        ttk.Label(pick, textvariable=self.pdf_status).pack(side="left", padx=8)
        row("PDF", pick)

        self.viewer_name = tk.StringVar()
        self.viewer_version = tk.StringVar()
        self.viewer_count = tk.StringVar()
        row("Viewer name", ttk.Entry(f, textvariable=self.viewer_name))
        row("Viewer version", ttk.Entry(f, textvariable=self.viewer_version))
        row("Page count shown by viewer", ttk.Entry(f, textvariable=self.viewer_count))
        self.page_hint = tk.StringVar(value="viewer page X = stored index X-1")
        ttk.Label(f, textvariable=self.page_hint, foreground="blue").grid(
            row=r, column=1, sticky="w", padx=6)
        r += 1

        self.presence = tk.StringVar()
        row("Presence state", ttk.Combobox(f, textvariable=self.presence, state="readonly",
                                           values=self.enums["presence_state"]))
        self.reason = tk.StringVar()
        row("Reason code", ttk.Combobox(f, textvariable=self.reason, state="readonly",
                                        values=self.enums["presence_reason_code"]))
        self.p_start, self.p_end = tk.StringVar(), tk.StringVar()
        span = ttk.Frame(f)
        ttk.Entry(span, width=8, textvariable=self.p_start).pack(side="left")
        ttk.Label(span, text=" to ").pack(side="left")
        ttk.Entry(span, width=8, textvariable=self.p_end).pack(side="left")
        ttk.Label(span, text="  (viewer pages; blank if not PRESENT)").pack(side="left")
        row("Primary span", span)
        for var in (self.p_start, self.p_end):
            var.trace_add("write", lambda *_: self._update_hint())

        self.alt_text = tk.Text(f, height=3, width=60)
        row("Alternative spans\n(one per line: start-end TYPE)\nTYPE in: "
            + ", ".join(self.enums["alternative_span_type"]), self.alt_text)
        self.gaps = tk.StringVar()
        row("Gap pages (e.g. 14, 16-17)", ttk.Entry(f, textvariable=self.gaps))

        flag_box = ttk.Frame(f)
        self.flag_vars = {}
        for i, flag in enumerate(self.enums["flags"]):
            var = tk.BooleanVar()
            self.flag_vars[flag] = var
            ttk.Checkbutton(flag_box, text=flag, variable=var).grid(
                row=i // 3, column=i % 3, sticky="w")
        row("Flags", flag_box)
        self.flag_pages_text = tk.Text(f, height=3, width=60)
        row("Flag pages\n(one per line: flag: 12, 14-15)", self.flag_pages_text)

        self.ambiguity = tk.StringVar(value="NONE")
        row("Ambiguity code", ttk.Combobox(f, textvariable=self.ambiguity, state="readonly",
                                           values=self.enums["ambiguity_code"]))
        self.adm_text = tk.Text(f, height=3, width=60)
        row("Admissible spans\n(AMBIGUOUS only; one per line: start-end)", self.adm_text)
        self.parent_section = tk.StringVar()
        row("Parent section (if embedded)", ttk.Entry(f, textvariable=self.parent_section))
        self.annexure_identity = tk.StringVar()
        row("Annexure identity (if annexure)", ttk.Entry(f, textvariable=self.annexure_identity))
        self.visible_parent = tk.StringVar()
        row("Visible parent heading", ttk.Entry(f, textvariable=self.visible_parent))
        self.cond_context = tk.StringVar()
        row("Conditional title context", ttk.Entry(f, textvariable=self.cond_context))

        self.boundary_vars = {}
        for key, label in BOUNDARY_KEYS:
            var = tk.StringVar()
            self.boundary_vars[key] = var
            row(f"{label} (viewer page, optional)", ttk.Entry(f, textvariable=var))

        aid_box = ttk.Frame(f)
        self.aid_vars = {}
        for i, aid in enumerate(self.enums["aids_used"]):
            var = tk.BooleanVar()
            self.aid_vars[aid] = var
            ttk.Checkbutton(aid_box, text=aid, variable=var).grid(
                row=i // 3, column=i % 3, sticky="w")
        row("Aids used", aid_box)
        self.search_text = tk.Text(f, height=3, width=60)
        row("Search queries (one per line)", self.search_text)
        self.search_usable = tk.BooleanVar()
        row("Viewer search usable", ttk.Checkbutton(f, variable=self.search_usable))
        self.bookmarks = tk.StringVar()
        row("Bookmark pages (viewer)", ttk.Entry(f, textvariable=self.bookmarks))
        self.att_repo = tk.BooleanVar()
        self.att_output = tk.BooleanVar()
        row("I had no repository access", ttk.Checkbutton(f, variable=self.att_repo))
        row("I saw no system output", ttk.Checkbutton(f, variable=self.att_output))

        buttons = ttk.Frame(f)
        ttk.Button(buttons, text="Check", command=self.check).pack(side="left", padx=4)
        ttk.Button(buttons, text="Submit and seal", command=self.submit).pack(side="left", padx=4)
        ttk.Button(buttons, text="Supersede my earlier record",
                   command=self.supersede).pack(side="left", padx=4)
        row("", buttons)
        f.columnconfigure(1, weight=1)

    # -- helpers ----------------------------------------------------------------
    def _update_hint(self) -> None:
        text = self.p_start.get().strip()
        if text.isdigit():
            self.page_hint.set(f"viewer page {text} = stored index {int(text) - 1}")
        else:
            self.page_hint.set("viewer page X = stored index X-1")

    def choose_pdf(self) -> None:
        doc_id = self.doc_var.get()
        if not doc_id:
            messagebox.showerror("PDF", "Choose the document first.")
            return
        path = filedialog.askopenfilename(filetypes=[("PDF", "*.pdf"), ("All", "*")])
        if not path:
            return
        try:
            core.verify_pdf(Path(path), self.assignment[doc_id]["source_pdf_sha256"])
        except core.AnnotatorError as exc:
            self.doc = None
            self.pdf_status.set("NOT verified")
            messagebox.showerror("PDF", str(exc))
            return
        self.doc = self.assignment[doc_id]
        self.started_at = core.now_rfc3339()
        self.pdf_status.set(
            f"Verified. {self.doc['physical_page_count']} physical pages. Started {self.started_at}"
        )

    @staticmethod
    def _lines(widget: tk.Text) -> list[str]:
        return [ln.strip() for ln in widget.get("1.0", "end").splitlines() if ln.strip()]

    def _span_lines(self, widget: tk.Text, typed: bool) -> list:
        out = []
        for line in self._lines(widget):
            parts = line.split()
            rng = parts[0]
            if "-" not in rng:
                raise core.AnnotatorError(f"span {line!r}: write start-end")
            a, b = rng.split("-", 1)
            if not (a.isdigit() and b.isdigit()):
                raise core.AnnotatorError(f"span {line!r}: pages must be numbers")
            if typed:
                if len(parts) != 2:
                    raise core.AnnotatorError(f"span {line!r}: write start-end TYPE")
                out.append((int(a), int(b), parts[1]))
            else:
                out.append((int(a), int(b)))
        return out

    def _form(self) -> dict:
        if self.doc is None or self.doc["document_id"] != self.doc_var.get():
            raise core.AnnotatorError("Choose the document and verify its PDF first.")
        start, end = _opt_int(self.p_start.get(), "start"), _opt_int(self.p_end.get(), "end")
        if (start is None) != (end is None):
            raise core.AnnotatorError("Primary span needs both start and end, or neither.")
        flag_pages = {}
        for line in self._lines(self.flag_pages_text):
            flag, _, pages = line.partition(":")
            flag_pages[flag.strip()] = core.parse_page_list(pages)
        count = self.viewer_count.get().strip()
        return {
            "viewer_page_count": int(count) if count.isdigit() else None,
            "viewer_name": self.viewer_name.get().strip(),
            "viewer_version": self.viewer_version.get().strip(),
            "presence_state": self.presence.get(),
            "presence_reason_code": self.reason.get(),
            "primary_span_viewer": None if start is None else (start, end),
            "alternative_spans_viewer": self._span_lines(self.alt_text, typed=True),
            "gap_pages_viewer": core.parse_page_list(self.gaps.get()),
            "flags": [k for k, v in self.flag_vars.items() if v.get()],
            "flag_pages_viewer": flag_pages,
            "ambiguity_code": self.ambiguity.get(),
            "admissible_spans_viewer": self._span_lines(self.adm_text, typed=False),
            "parent_section": self.parent_section.get().strip(),
            "annexure_identity": self.annexure_identity.get().strip(),
            "visible_parent_heading": self.visible_parent.get().strip(),
            "conditional_title_context": self.cond_context.get().strip(),
            "boundary_evidence_viewer": {
                key: _opt_int(var.get(), key) for key, var in self.boundary_vars.items()
            },
            "aids_used": [k for k, v in self.aid_vars.items() if v.get()],
            "search_queries": self._lines(self.search_text),
            "search_usable": self.search_usable.get(),
            "bookmark_pages_viewer": core.parse_page_list(self.bookmarks.get()),
            "no_repository_access_attested": self.att_repo.get(),
            "no_system_output_access_attested": self.att_output.get(),
        }

    def _record(self) -> dict:
        ctx = {
            **self.doc,
            "annotator_role": self.role,
            "workspace_id": self.workspace_id,
            "protocol_version_hash": self.protocol_hash,
            "started_at": self.started_at,
        }
        return core.build_raw_record(self._form(), ctx)

    # -- actions ----------------------------------------------------------------
    def check(self) -> None:
        try:
            errors = core.validate_record(self._record(), self.schema)
        except core.AnnotatorError as exc:
            messagebox.showerror("Check", str(exc))
            return
        if errors:
            messagebox.showerror("Check", "\n".join(errors[:25]))
        else:
            messagebox.showinfo("Check", "Record is valid. Nothing was saved.")

    def _refuse_if_placeholder(self) -> bool:
        if PLACEHOLDER.exists():
            messagebox.showerror(
                "Submit", "The title list is not frozen yet, so records cannot be sealed.")
            return True
        return False

    def submit(self) -> None:
        if self._refuse_if_placeholder():
            return
        try:
            path, digest = core.seal_raw_record(RECORDS_DIR, self._record(), self.schema)
        except core.AnnotatorError as exc:
            messagebox.showerror("Submit", str(exc))
            return
        messagebox.showinfo("Sealed", f"Saved read-only:\n{path.name}\nSHA-256 {digest}")

    def supersede(self) -> None:
        if self._refuse_if_placeholder():
            return
        old = simpledialog.askstring("Supersede", "Full SHA-256 of your earlier record:")
        reason = simpledialog.askstring("Supersede", "Reason (required):")
        if not old or not reason:
            return
        try:
            new_path, new_sha, note_path, _ = core.supersede(
                RECORDS_DIR, old.strip(), self._record(), reason, self.schema, self.workspace_id)
        except core.AnnotatorError as exc:
            messagebox.showerror("Supersede", str(exc))
            return
        messagebox.showinfo(
            "Superseded",
            f"New record {new_path.name}\nSHA-256 {new_sha}\nNote {note_path.name}")


def main() -> int:
    root = tk.Tk()
    try:
        AnnotatorApp(root)
    except core.AnnotatorError as exc:
        root.withdraw()
        messagebox.showerror("ARPipe annotation tool", str(exc))
        root.destroy()
        return 2
    root.mainloop()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
