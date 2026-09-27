"""Minimal offline tkinter entry form for independent RAW A/B annotation."""

from __future__ import annotations

import tkinter as tk
from datetime import datetime, timezone
from pathlib import Path
from tkinter import filedialog, messagebox, simpledialog, ttk

from core import (AnnotationError, PAGE_CONVENTION, PROTOCOL_FILE, ROLES,
                  check_workspace, create_supersede, load_assignments, load_schema, sha256_file,
                  submit_raw, verify_source, viewer_to_index, workspace_id)


def now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


class SpanRows:
    def __init__(self, parent: ttk.Frame, title: str, types: list[str] | None = None):
        self.types = types
        self.rows: list[tuple[ttk.Frame, ttk.Entry, ttk.Entry, ttk.Combobox | None]] = []
        self.box = ttk.LabelFrame(parent, text=title)
        self.box.pack(fill="x", padx=6, pady=4)
        ttk.Button(self.box, text="Add span", command=self.add).pack(anchor="w")

    def add(self) -> None:
        row = ttk.Frame(self.box)
        row.pack(fill="x", pady=2)
        ttk.Label(row, text="Start viewer page").pack(side="left")
        start = ttk.Entry(row, width=8)
        start.pack(side="left", padx=3)
        ttk.Label(row, text="End viewer page").pack(side="left")
        end = ttk.Entry(row, width=8)
        end.pack(side="left", padx=3)
        kind = None
        if self.types:
            kind = ttk.Combobox(row, values=self.types, state="readonly", width=36)
            kind.current(0)
            kind.pack(side="left", padx=3)
        self.rows.append((row, start, end, kind))
        ttk.Button(row, text="Remove", command=lambda: self.remove(row)).pack(side="left")

    def remove(self, row: ttk.Frame) -> None:
        self.rows = [item for item in self.rows if item[0] is not row]
        row.destroy()

    def values(self, count: int) -> list[dict]:
        result = []
        for _, start, end, kind in self.rows:
            value = {"start_page": viewer_to_index(start.get(), count),
                     "end_page": viewer_to_index(end.get(), count)}
            if kind is not None:
                value["type"] = kind.get()
            result.append(value)
        return result


class AnnotatorApp:
    def __init__(self, window: tk.Tk, bundle_root: Path):
        self.window = window
        self.root = bundle_root
        self.schema = load_schema(bundle_root)
        self.workspace = workspace_id(bundle_root)
        self.assignments: dict[str, dict] = {}
        self.assignment: dict | None = None
        self.source: Path | None = None
        self.entries: dict[str, ttk.Entry] = {}
        self.checks: dict[str, tk.BooleanVar] = {}
        self.flag_pages: dict[str, ttk.Entry] = {}
        self.started = now()
        window.title("Offline Gold RAW annotation v0.1")
        window.geometry("960x760")
        top = ttk.Frame(window)
        top.pack(fill="x", padx=8, pady=8)
        ttk.Button(top, text="Open assignment CSV", command=self.open_assignments).pack(side="left")
        self.document = ttk.Combobox(top, state="readonly", width=34)
        self.document.pack(side="left", padx=5)
        ttk.Button(top, text="Select file and verify", command=self.select_source).pack(side="left")
        ttk.Label(top, text="Viewer page count:").pack(side="left", padx=5)
        self.viewer_count = ttk.Entry(top, width=6)
        self.viewer_count.pack(side="left")
        self.status = ttk.Label(window, text="Choose the assigned CSV, then select its file by SHA-256.")
        self.status.pack(anchor="w", padx=8)
        self.canvas = tk.Canvas(window, highlightthickness=0)
        scrollbar = ttk.Scrollbar(window, orient="vertical", command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        self.canvas.pack(fill="both", expand=True)
        self.form = ttk.Frame(self.canvas)
        self.canvas.create_window((0, 0), window=self.form, anchor="nw")
        self.form.bind("<Configure>", lambda _event: self.canvas.configure(scrollregion=self.canvas.bbox("all")))

    def open_assignments(self) -> None:
        path = filedialog.askopenfilename(title="Assignment CSV", filetypes=[("CSV", "*.csv")])
        if not path:
            return
        try:
            self.assignments = load_assignments(Path(path))
            self.document.configure(values=list(self.assignments))
            if self.assignments:
                self.document.current(0)
            self.status.configure(text=f"{len(self.assignments)} assignments loaded")
        except (OSError, AnnotationError) as exc:
            messagebox.showerror("Assignment refused", str(exc))

    def select_source(self) -> None:
        try:
            assignment = self.assignments[self.document.get()]
            count = int(self.viewer_count.get())
            path = filedialog.askopenfilename(title="Select the assigned PDF in your own viewer")
            if not path:
                return
            verify_source(Path(path), assignment, count)
            self.assignment, self.source = assignment, Path(path)
            self.started = now()
            self.build_form()
            self.status.configure(text=f"SHA-256 verified for {assignment['document_id']}; viewer pages 1–{count}")
        except (KeyError, ValueError, OSError, AnnotationError) as exc:
            messagebox.showerror("File refused", str(exc))

    def entry(self, parent: ttk.Frame, name: str, label: str, value: str = "", readonly: bool = False) -> ttk.Entry:
        row = ttk.Frame(parent)
        row.pack(fill="x", padx=6, pady=2)
        ttk.Label(row, text=label, width=37).pack(side="left")
        item = ttk.Entry(row, width=76)
        item.insert(0, value)
        if readonly:
            item.configure(state="readonly")
        item.pack(side="left", fill="x", expand=True)
        self.entries[name] = item
        return item

    def combo(self, parent: ttk.Frame, name: str, label: str, values: list[str], default: str | None = None) -> None:
        row = ttk.Frame(parent)
        row.pack(fill="x", padx=6, pady=2)
        ttk.Label(row, text=label, width=37).pack(side="left")
        item = ttk.Combobox(row, values=values, state="readonly", width=70)
        item.set(default or values[0])
        item.pack(side="left")
        self.entries[name] = item

    def checkbox(self, parent: ttk.Frame, name: str, label: str, default: bool = False) -> None:
        variable = tk.BooleanVar(value=default)
        self.checks[name] = variable
        ttk.Checkbutton(parent, text=label, variable=variable).pack(anchor="w", padx=8)

    def build_form(self) -> None:
        for child in self.form.winfo_children():
            child.destroy()
        self.entries.clear()
        self.checks.clear()
        self.flag_pages.clear()
        common = self.schema["$defs"]["commonRecord"]["properties"]
        self.entry(self.form, "document_id", "Document ID", self.assignment["document_id"], True)
        self.entry(self.form, "source_pdf_sha256", "Selected file SHA-256", self.assignment["source_pdf_sha256"], True)
        self.entry(self.form, "record_type", "Record type", "RAW", True)
        self.combo(self.form, "annotator_role", "Annotator role", list(ROLES))
        self.combo(self.form, "presence_state", "Presence state", common["presence_state"]["enum"])
        self.combo(self.form, "presence_reason_code", "Presence reason", common["presence_reason_code"]["enum"])
        self.entry(self.form, "primary_start", "Primary start (viewer page)")
        self.entry(self.form, "primary_end", "Primary end (viewer page)")
        hint = ttk.Label(self.form, text="Viewer page X = stored index X-1. Use physical page numbers, with page labels disabled.")
        hint.pack(anchor="w", padx=8, pady=4)
        self.alternatives = SpanRows(self.form, "Alternative spans (viewer pages)",
                                     common["alternative_spans"]["items"]["properties"]["type"]["enum"])
        self.entry(self.form, "gap_pages", "Gap viewer pages (comma-separated)")
        flag_box = ttk.LabelFrame(self.form, text="Structural flags and optional flag pages (viewer pages)")
        flag_box.pack(fill="x", padx=6, pady=4)
        for flag in common["flags"]["items"]["enum"]:
            row = ttk.Frame(flag_box)
            row.pack(fill="x")
            variable = tk.BooleanVar(value=False)
            self.checks[f"flag:{flag}"] = variable
            ttk.Checkbutton(row, text=flag, variable=variable, width=38).pack(side="left")
            page_entry = ttk.Entry(row, width=36)
            page_entry.pack(side="left")
            self.flag_pages[flag] = page_entry
        self.combo(self.form, "ambiguity_code", "Ambiguity code", common["ambiguity_code"]["enum"])
        self.admissible = SpanRows(self.form, "Admissible spans (viewer pages)")
        self.entry(self.form, "parent_section", "Parent section, if embedded")
        self.entry(self.form, "annexure_identity", "Printed annexure identity")
        for key in ("heading_start_page", "substantive_start_page", "last_content_page",
                    "next_section_heading_page", "mixed_end_page"):
            self.entry(self.form, key, f"{key} (viewer page)")
        ttk.Label(self.form, text="Primary viewer start/end audit copies are taken from the two primary entries above.").pack(anchor="w", padx=8)
        self.entry(self.form, "started_at", "Started at (RFC 3339)", self.started)
        self.entry(self.form, "completed_at", "Completed at (RFC 3339)", now())
        ttk.Button(self.form, text="Set completion to now", command=self.set_completion_now).pack(anchor="w", padx=8)
        aids_box = ttk.LabelFrame(self.form, text="Aids used")
        aids_box.pack(fill="x", padx=6, pady=4)
        for aid in common["aids_used"]["items"]["enum"]:
            self.checkbox(aids_box, f"aid:{aid}", aid, aid == "PDF_VIEWER")
        self.entry(self.form, "annotation_workspace_id", "Random workspace ID", self.workspace, True)
        self.entry(self.form, "viewer_name", "Viewer name")
        self.entry(self.form, "viewer_version", "Viewer version")
        self.entry(self.form, "viewer_page_convention", "Viewer page convention", PAGE_CONVENTION, True)
        self.entry(self.form, "physical_page_count", "Verified physical page count", str(self.assignment["physical_page_count"]), True)
        self.checkbox(self.form, "search_usable", "Viewer search was usable")
        ttk.Label(self.form, text="Search queries (one per line; leave blank if none)").pack(anchor="w", padx=8)
        self.queries = tk.Text(self.form, height=3, width=80)
        self.queries.pack(fill="x", padx=8)
        self.entry(self.form, "bookmark_pages", "Bookmark viewer pages (comma-separated)")
        self.entry(self.form, "visible_parent_heading", "Visible parent heading (optional)")
        self.entry(self.form, "conditional_title_context", "Conditional title context (optional)")
        self.checkbox(self.form, "no_repository_access_attested", "I had no repository access in this annotation workspace")
        self.checkbox(self.form, "no_system_output_access_attested", "I had no system output access for this document")
        self.entry(self.form, "protocol_version_hash", "Protocol SHA-256", sha256_file(self.root / PROTOCOL_FILE), True)
        ttk.Button(self.form, text="Validate and seal RAW record", command=self.submit).pack(anchor="w", padx=8, pady=12)
        ttk.Button(self.form, text="Create explicit supersede record", command=self.supersede).pack(anchor="w", padx=8, pady=4)

    def set_completion_now(self) -> None:
        entry = self.entries["completed_at"]
        entry.delete(0, "end")
        entry.insert(0, now())

    def supersede(self) -> None:
        old_hash = simpledialog.askstring("Supersede RAW record", "Old RAW record SHA-256:", parent=self.window)
        if old_hash is None:
            return
        reason = simpledialog.askstring("Supersede RAW record", "Reason for supersession:", parent=self.window)
        if reason is None:
            return
        try:
            path, digest = create_supersede(self.root, self.assignment["document_id"],
                                            self.entries["annotator_role"].get(), old_hash, reason)
            messagebox.showinfo("Supersede recorded", f"{path.name}\nSHA-256: {digest}\nNow submit the replacement RAW record.")
        except (AnnotationError, OSError) as exc:
            messagebox.showerror("Supersede refused", str(exc))

    def _page(self, field: str, count: int) -> int | None:
        value = self.entries[field].get().strip()
        return viewer_to_index(value, count) if value else None

    def _pages(self, text: str, count: int) -> list[int]:
        return [viewer_to_index(value.strip(), count) for value in text.split(",") if value.strip()]

    def make_record(self) -> dict:
        count = self.assignment["physical_page_count"]
        start = self._page("primary_start", count)
        end = self._page("primary_end", count)
        if (start is None) != (end is None):
            raise AnnotationError("Enter both primary boundaries or neither")
        primary = {"start_page": start, "end_page": end} if start is not None else None
        flags = [flag for flag in self.flag_pages if self.checks[f"flag:{flag}"].get()]
        flag_pages = {flag: self._pages(self.flag_pages[flag].get(), count)
                      for flag in flags if self.flag_pages[flag].get().strip()}
        evidence = {key: self._page(key, count) for key in
                    ("heading_start_page", "substantive_start_page", "last_content_page",
                     "next_section_heading_page", "mixed_end_page")}
        evidence.update(viewer_start_page_1based=start + 1 if start is not None else None,
                        viewer_end_page_1based=end + 1 if end is not None else None)
        def optional(name: str) -> str | None:
            return self.entries[name].get().strip() or None
        return {
            "record_type": "RAW", "document_id": self.assignment["document_id"],
            "source_pdf_sha256": self.assignment["source_pdf_sha256"],
            "annotator_role": self.entries["annotator_role"].get(),
            "presence_state": self.entries["presence_state"].get(),
            "presence_reason_code": self.entries["presence_reason_code"].get(),
            "primary_span": primary, "alternative_spans": self.alternatives.values(count),
            "gap_pages": self._pages(self.entries["gap_pages"].get(), count),
            "flags": flags, "ambiguity_code": self.entries["ambiguity_code"].get(),
            "admissible_spans": self.admissible.values(count),
            "parent_section": optional("parent_section"), "annexure_identity": optional("annexure_identity"),
            "boundary_evidence": evidence,
            "timestamps": {"started_at": self.entries["started_at"].get().strip(),
                           "completed_at": self.entries["completed_at"].get().strip()},
            "aids_used": [aid for aid in self.schema["$defs"]["commonRecord"]["properties"]["aids_used"]["items"]["enum"]
                          if self.checks[f"aid:{aid}"].get()],
            "structured_provenance": {
                "annotation_workspace_id": self.workspace,
                "viewer_name": self.entries["viewer_name"].get().strip(),
                "viewer_version": self.entries["viewer_version"].get().strip(),
                "viewer_page_convention": PAGE_CONVENTION,
                "physical_page_count": count,
                "search_queries": [line.strip() for line in self.queries.get("1.0", "end").splitlines() if line.strip()],
                "search_usable": self.checks["search_usable"].get(),
                "bookmark_pages": self._pages(self.entries["bookmark_pages"].get(), count),
                "flag_pages": flag_pages,
                "visible_parent_heading": optional("visible_parent_heading"),
                "conditional_title_context": optional("conditional_title_context"),
                "source_pdf_hash_verified": True,
                "no_repository_access_attested": self.checks["no_repository_access_attested"].get(),
                "no_system_output_access_attested": self.checks["no_system_output_access_attested"].get(),
            },
            "protocol_version_hash": self.entries["protocol_version_hash"].get(),
        }

    def submit(self) -> None:
        try:
            record = self.make_record()
            path, digest = submit_raw(self.root, record, self.assignment, self.source,
                                      int(self.viewer_count.get()), self.schema)
            messagebox.showinfo("Sealed", f"{path.name}\nSHA-256: {digest}")
        except (AnnotationError, ValueError, OSError) as exc:
            messagebox.showerror("Submission refused", str(exc))


def main() -> None:
    root = Path(__file__).resolve().parent
    check_workspace(root)
    window = tk.Tk()
    AnnotatorApp(window, root)
    window.mainloop()


if __name__ == "__main__":
    main()
