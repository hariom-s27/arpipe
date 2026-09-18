"""ARPipe T0.1 Corpus Gap Audit Tool.

Implements the three-pass audit architecture:
  PASS 1 — CHEAP CENSUS across all 194 frozen PDFs.
  PASS 2 — TARGETED FORENSICS on candidate pages/documents.
  PASS 3 — REVIEW MANIFEST deterministic candidate generation.

Strict boundaries:
  - Cryptographically verifies the 194 frozen PDFs against corpus_inventory.csv.
  - Verifies total physical page count equals 37,917.
  - Hashes and protects all 12 frozen T0 input artifacts.
  - Reuses frozen T0 page_profile.csv indicators alongside new T0.1 measurements.
  - All detectors are audit-only and produce EVIDENCE, not ground truth.
  - Separates detector_status (CANDIDATE / NOT_OBSERVED) from verification_status.
  - Outputs to an explicitly specified --out-dir.
"""
from __future__ import annotations

import argparse
import csv
import datetime
import hashlib
import json
import math
import os
import platform
import re
import subprocess
import sys
from collections import Counter, defaultdict
from dataclasses import asdict, dataclass, field
from typing import Any

import pymupdf

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
T0_DIR = os.path.join(REPO_ROOT, "dataset", "corpus_freeze")
DEFAULT_LIVE_STORE = os.path.abspath(os.path.join(REPO_ROOT, "..", "arpipe-0.1.0", "live_store"))
DEFAULT_CONFIG = os.path.join(REPO_ROOT, "configs", "audit_config.json")

PROTECTED_T0_FILES = [
    "corpus_inventory.csv",
    "page_profile.csv",
    "issuer_split.csv",
    "development_manifest.csv",
    "validation_manifest.csv",
    "holdout_manifest.csv",
    "challenge_coverage_manifest.csv",
    "annotation_roster.csv",
    "diversity_matrix.csv",
    "interaction_matrix.csv",
    "rare_condition_register.csv",
    "freeze_summary.json",
]

DEVANAGARI_RE = re.compile(r"[\u0900-\u097f]")
LATIN_RE = re.compile(r"[a-zA-Z]")
NUMERIC_RE = re.compile(r"^[₹$€£]?[+-]?\d+([.,]\d+)*%?$")


def compute_file_sha256(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest()


def load_protected_t0_hashes(t0_dir: str) -> dict[str, str]:
    hashes = {}
    for filename in PROTECTED_T0_FILES:
        path = os.path.join(t0_dir, filename)
        if not os.path.isfile(path):
            raise FileNotFoundError(f"Protected T0 input artifact missing: {path}")
        hashes[filename] = compute_file_sha256(path)
    return hashes


def load_t0_page_profiles(t0_dir: str) -> dict[tuple[str, int], dict[str, str]]:
    """Loads frozen page_profile.csv to reuse authoritative T0 measurements."""
    path = os.path.join(t0_dir, "page_profile.csv")
    profiles = {}
    with open(path, "r", encoding="utf-8", newline="") as f:
        for r in csv.DictReader(f):
            profiles[(r["document_id"], int(r["physical_page"]))] = r
    return profiles


@dataclass
class PageCensus:
    document_id: str
    physical_page: int  # 0-indexed
    page_count: int
    char_count: int
    word_count: int
    page_width: float
    page_height: float
    rotation: int
    image_count: int
    image_area_frac: float
    devanagari_count: int
    latin_count: int
    replacement_char_count: int
    pua_count: int
    is_scanned: bool
    is_native: bool
    is_hybrid: bool
    is_t0_ocr: bool
    is_t0_broken: bool
    is_devanagari_page: bool
    is_hindi_page: bool
    is_bilingual_page: bool
    estimated_columns: int
    has_top_furniture: bool
    has_bottom_furniture: bool
    top_furniture_text: str
    bottom_furniture_text: str
    top_furniture_y1: float
    bottom_furniture_y0: float
    has_toc_keyword: bool
    has_mda_keyword: bool
    has_annexure_keyword: bool
    drawings_rect_count: int
    drawings_line_count: int
    font_names: list[str] = field(default_factory=list)


def calculate_long_report_distribution(executable_rows: list[dict[str, str]]) -> dict[str, Any]:
    page_counts = sorted(int(r["page_count"]) for r in executable_rows)
    n = len(page_counts)

    def percentile(data: list[int], p: float) -> float:
        k = (len(data) - 1) * p
        f = math.floor(k)
        c = math.ceil(k)
        if f == c:
            return float(data[int(k)])
        return data[f] * (c - k) + data[c] * (k - f)

    return {
        "min": page_counts[0],
        "max": page_counts[-1],
        "mean": round(sum(page_counts) / n, 2),
        "median": percentile(page_counts, 0.50),
        "q1": percentile(page_counts, 0.25),
        "q3": percentile(page_counts, 0.75),
        "p75": percentile(page_counts, 0.75),
        "p90": percentile(page_counts, 0.90),
        "p95": percentile(page_counts, 0.95),
    }


def execute_pass1_and_pass2(
    executable_rows: list[dict[str, str]],
    live_store: str,
    t0_profiles: dict[tuple[str, int], dict[str, str]],
    cfg: dict[str, Any],
) -> tuple[dict[str, list[PageCensus]], dict[str, Any], int]:
    """Execute Pass 1 Cheap Census and Pass 2 Targeted Forensics while each PDF is open."""
    census_by_doc: dict[str, list[PageCensus]] = {}
    total_pages_sum = 0

    forensics: dict[str, Any] = {
        "table_candidates": [],
        "header_footer_candidates": [],
        "toc_offset_candidates": [],
        "duplicate_text_candidates": [],
        "language_candidates": [],
        "structure_candidates": [],
        "mdna_complexity": [],
        "doc_page_counts": {},
    }

    top_frac = cfg["layout_and_reading_order"]["margin_top_frac"]
    bot_frac = 1.0 - cfg["layout_and_reading_order"]["margin_bottom_frac"]
    min_align_cols = cfg["table_candidate_heuristics"]["table_min_aligned_columns"]
    min_align_rows = cfg["table_candidate_heuristics"]["table_min_aligned_rows"]
    num_ratio_thresh = cfg["table_candidate_heuristics"]["table_numeric_token_min_ratio"]

    for row in executable_rows:
        doc_id = row["document_id"]
        sha = row["pdf_sha256"]
        expected_pages = int(row["page_count"])

        pdf_path = os.path.join(live_store, "blobs", sha[:2], sha[2:4], f"{sha}.pdf")
        if not os.path.isfile(pdf_path):
            raise FileNotFoundError(f"Missing PDF file for {doc_id}: {pdf_path}")

        # Compute and verify SHA-256
        actual_sha = compute_file_sha256(pdf_path)
        if actual_sha != sha:
            raise ValueError(f"SHA-256 mismatch for {doc_id}: actual {actual_sha} != expected {sha}")

        doc = pymupdf.open(pdf_path)
        actual_pages = len(doc)
        if actual_pages != expected_pages:
            raise ValueError(
                f"Page count mismatch for {doc_id}: actual {actual_pages} != expected {expected_pages}"
            )
        total_pages_sum += actual_pages

        pages_list: list[PageCensus] = []
        table_cand_pages = set()
        header_cand_pages = set()
        footer_cand_pages = set()
        duplicate_cand_pages = set()
        hidden_cand_pages = set()
        legacy_cand_pages = set()

        for pno in range(actual_pages):
            page = doc[pno]
            rect = page.rect
            width, height = rect.width, rect.height
            text = page.get_text()
            char_count = len(text)
            words = text.split()
            word_count = len(words)

            # Images
            imgs = page.get_images()
            img_count = len(imgs)
            total_img_area = 0.0
            page_area = max(1.0, width * height)
            if img_count > 0:
                for img_info in imgs:
                    xref = img_info[0]
                    try:
                        for img_rect in page.get_image_rects(xref):
                            total_img_area += img_rect.width * img_rect.height
                    except Exception:
                        pass
            image_area_frac = min(1.0, total_img_area / page_area)

            # Script counts
            dev_matches = len(DEVANAGARI_RE.findall(text))
            lat_matches = len(LATIN_RE.findall(text))
            repl_count = text.count("\ufffd")
            pua_count = sum(1 for c in text if 0xE000 <= ord(c) <= 0xF8FF)

            is_dev = dev_matches >= cfg["language_and_script"]["devanagari_page_min_chars"]
            is_hindi = dev_matches >= cfg["language_and_script"]["hindi_page_min_devanagari_chars"]
            is_bilingual = (
                lat_matches >= cfg["language_and_script"]["bilingual_page_min_latin_chars"]
                and dev_matches >= cfg["language_and_script"]["bilingual_page_min_devanagari_chars"]
            )

            # Check frozen T0 page profile
            t0_prof = t0_profiles.get((doc_id, pno), {})
            is_t0_ocr = t0_prof.get("render_mode_ocr_layer_indicator") == "True"
            is_t0_broken = t0_prof.get("cid_or_broken_text_indicator") == "True"

            # Page classification
            is_scanned = (
                char_count <= cfg["text_and_pdf_representation"]["scanned_page_max_chars"]
                and image_area_frac >= cfg["text_and_pdf_representation"]["scanned_page_min_image_frac"]
            )
            is_native = char_count > 50 and not is_scanned
            is_hybrid = (
                char_count > 50
                and image_area_frac >= cfg["text_and_pdf_representation"]["hybrid_page_min_image_frac"]
            )

            if is_t0_broken or repl_count > 0 or pua_count > 5:
                legacy_cand_pages.add(pno)

            # Fonts
            font_list = []
            try:
                for f_info in page.get_fonts():
                    if f_info and len(f_info) > 3 and f_info[3]:
                        font_list.append(str(f_info[3]))
            except Exception:
                pass

            # Blocks & furniture extraction
            blocks = page.get_text("blocks")
            top_furn = False
            top_furn_text = ""
            top_furn_y1 = 0.0
            bot_furn = False
            bot_furn_text = ""
            bot_furn_y0 = height
            body_block_x_spans = []

            for b in blocks:
                bx0, by0, bx1, by1, btext, bno, btype = b
                bstr = btext.strip()
                if not bstr:
                    continue
                if by1 <= height * top_frac:
                    top_furn = True
                    top_furn_text = bstr
                    top_furn_y1 = by1
                elif by0 >= height * bot_frac:
                    bot_furn = True
                    bot_furn_text = bstr
                    bot_furn_y0 = by0
                else:
                    body_block_x_spans.append((bx0, bx1))

            # Column estimation
            est_cols = 1
            if body_block_x_spans:
                x_mid = width / 2.0
                left_count = sum(1 for (x0, x1) in body_block_x_spans if x1 <= x_mid + 20 and (x1 - x0) < width * 0.55)
                right_count = sum(1 for (x0, x1) in body_block_x_spans if x0 >= x_mid - 20 and (x1 - x0) < width * 0.55)
                wide_count = sum(1 for (x0, x1) in body_block_x_spans if (x1 - x0) >= width * 0.65)
                if left_count >= 2 and right_count >= 2 and wide_count <= 2:
                    est_cols = 2
                elif left_count >= 3 or right_count >= 3:
                    est_cols = 3
                elif wide_count >= 2:
                    est_cols = 1

            # Drawings inspection for vector tables
            rect_count = 0
            line_count = 0
            try:
                drawings = page.get_drawings()
                for d in drawings:
                    for item in d.get("items", []):
                        if item[0] == "re":
                            rect_count += 1
                        elif item[0] == "l":
                            line_count += 1
            except Exception:
                pass

            # Table Candidate Detection
            has_vector_grid = (rect_count >= 4 or (line_count >= 6 and rect_count >= 1))
            page_lines = text.splitlines()
            numeric_lines_count = 0
            for pline in page_lines:
                tokens = pline.strip().split()
                if len(tokens) >= min_align_cols:
                    n_tokens = sum(1 for t in tokens if NUMERIC_RE.match(t))
                    if n_tokens / len(tokens) >= num_ratio_thresh:
                        numeric_lines_count += 1

            has_numeric_table = numeric_lines_count >= min_align_rows
            if has_vector_grid or has_numeric_table:
                table_cand_pages.add(pno)
                forensics["table_candidates"].append({
                    "document_id": doc_id,
                    "page_index": pno,
                    "vector_grid_detected": has_vector_grid,
                    "aligned_numeric_rows": numeric_lines_count,
                    "detector_status": "CANDIDATE",
                    "verification_status": "NOT_REVIEWED",
                    "notes": f"grid={has_vector_grid}, numeric_rows={numeric_lines_count}",
                })

            # Keywords
            lower_text = text.lower()
            has_toc_kw = any(k in lower_text for k in cfg["toc_candidate_heuristics"]["toc_title_patterns"])
            has_mda_kw = any(k in lower_text for k in cfg["structure_and_mda_heuristics"]["mda_heading_patterns"])
            has_annex_kw = any(k in lower_text for k in cfg["structure_and_mda_heuristics"]["annexure_patterns"])

            pc = PageCensus(
                document_id=doc_id,
                physical_page=pno,
                page_count=actual_pages,
                char_count=char_count,
                word_count=word_count,
                page_width=round(width, 2),
                page_height=round(height, 2),
                rotation=page.rotation,
                image_count=img_count,
                image_area_frac=round(image_area_frac, 4),
                devanagari_count=dev_matches,
                latin_count=lat_matches,
                replacement_char_count=repl_count,
                pua_count=pua_count,
                is_scanned=is_scanned,
                is_native=is_native,
                is_hybrid=is_hybrid,
                is_t0_ocr=is_t0_ocr,
                is_t0_broken=is_t0_broken,
                is_devanagari_page=is_dev,
                is_hindi_page=is_hindi,
                is_bilingual_page=is_bilingual,
                estimated_columns=est_cols,
                has_top_furniture=top_furn,
                has_bottom_furniture=bot_furn,
                top_furniture_text=top_furn_text[:100],
                bottom_furniture_text=bot_furn_text[:100],
                top_furniture_y1=round(top_furn_y1, 2),
                bottom_furniture_y0=round(bot_furn_y0, 2),
                has_toc_keyword=has_toc_kw,
                has_mda_keyword=has_mda_kw,
                has_annexure_keyword=has_annex_kw,
                drawings_rect_count=rect_count,
                drawings_line_count=line_count,
                font_names=font_list,
            )
            pages_list.append(pc)

        # -------------------------------------------------------------
        # PASS 2: Multi-page Forensics for this Document
        # -------------------------------------------------------------
        # Running Furniture Forensics
        for pno in range(len(pages_list) - 1):
            cp = pages_list[pno]
            np_ = pages_list[pno + 1]
            if cp.has_top_furniture and np_.has_top_furniture:
                t1 = re.sub(r"\d+", "", cp.top_furniture_text).strip().lower()
                t2 = re.sub(r"\d+", "", np_.top_furniture_text).strip().lower()
                if t1 and t2 and (t1 in t2 or t2 in t1 or (len(t1) >= 6 and t1[:10] == t2[:10])):
                    header_cand_pages.add(cp.physical_page)
                    header_cand_pages.add(np_.physical_page)
                    forensics["header_footer_candidates"].append({
                        "document_id": doc_id,
                        "page_index": cp.physical_page,
                        "furniture_type": "running_header",
                        "text_snippet": cp.top_furniture_text[:100],
                        "vertical_coord": cp.top_furniture_y1,
                        "detector_status": "CANDIDATE",
                        "verification_status": "NOT_REVIEWED",
                    })
            if cp.has_bottom_furniture and np_.has_bottom_furniture:
                b1 = re.sub(r"\d+", "", cp.bottom_furniture_text).strip().lower()
                b2 = re.sub(r"\d+", "", np_.bottom_furniture_text).strip().lower()
                if b1 and b2 and (b1 in b2 or b2 in b1 or (len(b1) >= 6 and b1[:10] == b2[:10])):
                    footer_cand_pages.add(cp.physical_page)
                    footer_cand_pages.add(np_.physical_page)
                    forensics["header_footer_candidates"].append({
                        "document_id": doc_id,
                        "page_index": cp.physical_page,
                        "furniture_type": "running_footer",
                        "text_snippet": cp.bottom_furniture_text[:100],
                        "vertical_coord": cp.bottom_furniture_y0,
                        "detector_status": "CANDIDATE",
                        "verification_status": "NOT_REVIEWED",
                    })

        # Overlap & Duplicate Text Forensics (targeted sample)
        cand_sample = [p for p in pages_list if p.char_count > 500][:25]
        for pc in cand_sample:
            pno = pc.physical_page
            try:
                p_dict = doc[pno].get_text("dict")
                spans = []
                for blk in p_dict.get("blocks", []):
                    if blk.get("type") == 0:
                        for line in blk.get("lines", []):
                            for sp in line.get("spans", []):
                                stext = sp.get("text", "").strip()
                                if stext:
                                    spans.append((stext, sp.get("bbox"), sp.get("flags", 0), sp.get("size", 0.0)))

                for stext, sbbox, sflags, ssize in spans:
                    if ssize < cfg["text_and_pdf_representation"]["hidden_text_max_font_size"]:
                        hidden_cand_pages.add(pno)
                        forensics["duplicate_text_candidates"].append({
                            "document_id": doc_id,
                            "page_index": pno,
                            "condition_class": "HIDDEN_TEXT_CANDIDATE",
                            "text_snippet": stext[:100],
                            "detector_status": "CANDIDATE",
                            "verification_status": "NOT_REVIEWED",
                            "notes": f"font_size={ssize}",
                        })
                        break

                for i in range(min(len(spans), 60)):
                    t1, b1, f1, s1 = spans[i]
                    if len(t1) < 5:
                        continue
                    for j in range(i + 1, min(len(spans), 60)):
                        t2, b2, f2, s2 = spans[j]
                        if len(t2) < 5:
                            continue
                        ix0 = max(b1[0], b2[0])
                        iy0 = max(b1[1], b2[1])
                        ix1 = min(b1[2], b2[2])
                        iy1 = min(b1[3], b2[3])
                        if ix1 > ix0 and iy1 > iy0:
                            inter = (ix1 - ix0) * (iy1 - iy0)
                            a1 = max(1.0, (b1[2] - b1[0]) * (b1[3] - b1[1]))
                            a2 = max(1.0, (b2[2] - b2[0]) * (b2[3] - b2[1]))
                            iou = inter / (a1 + a2 - inter)
                            if iou >= cfg["text_and_pdf_representation"]["overlap_iou_threshold"] and t1 == t2:
                                duplicate_cand_pages.add(pno)
                                forensics["duplicate_text_candidates"].append({
                                    "document_id": doc_id,
                                    "page_index": pno,
                                    "condition_class": "EXACT_TEXT_OVERLAP",
                                    "text_snippet": t1[:100],
                                    "detector_status": "CANDIDATE",
                                    "verification_status": "NOT_REVIEWED",
                                    "notes": f"iou={round(iou, 2)}",
                                })
                                break
                            elif iou >= cfg["text_and_pdf_representation"]["near_overlap_iou_threshold"]:
                                duplicate_cand_pages.add(pno)
                                forensics["duplicate_text_candidates"].append({
                                    "document_id": doc_id,
                                    "page_index": pno,
                                    "condition_class": "NEAR_TEXT_OVERLAP",
                                    "text_snippet": t1[:100],
                                    "detector_status": "CANDIDATE",
                                    "verification_status": "NOT_REVIEWED",
                                    "notes": f"iou={round(iou, 2)}",
                                })
                                break
                    if pno in duplicate_cand_pages:
                        break
            except Exception:
                pass

        # TOC Offset Forensics
        toc_candidate_pages = [
            p.physical_page
            for p in pages_list
            if p.has_toc_keyword and p.physical_page < cfg["toc_candidate_heuristics"]["toc_max_start_page_search"]
        ]
        if toc_candidate_pages:
            toc_entries = []
            for toc_pno in toc_candidate_pages[:3]:
                ttext = doc[toc_pno].get_text("text")
                for line in ttext.splitlines():
                    line = line.strip()
                    m = re.search(r"^(.*?)(?:\.{2,}|\s{2,}|\t+)(\d{1,4})$", line)
                    if m:
                        title = m.group(1).strip(" .-_")
                        folio = int(m.group(2))
                        if len(title) >= 4 and 1 <= folio <= len(pages_list):
                            toc_entries.append((toc_pno, title, folio))

            if toc_entries:
                offsets_found = []
                for toc_pno, title, folio in toc_entries[:15]:
                    title_lower = title.lower()
                    if len(title_lower) < 6:
                        continue
                    search_range = range(max(0, folio - 15), min(len(pages_list), folio + 30))
                    for bpno in search_range:
                        btext = doc[bpno].get_text("text").lower()
                        if title_lower in btext:
                            offset = bpno - folio
                            offsets_found.append((toc_pno, title, folio, bpno, offset))
                            break

                if offsets_found:
                    offset_counts = Counter(o[4] for o in offsets_found)
                    best_offset, count = offset_counts.most_common(1)[0]
                    consistency = count / len(offsets_found)
                    status = (
                        "STRONG_CANDIDATE"
                        if count >= cfg["toc_candidate_heuristics"]["toc_offset_high_confidence_min_matches"]
                        else "CANDIDATE"
                    )
                    entries_str = "; ".join(f"{o[1]} (folio {o[2]} -> page {o[3]})" for o in offsets_found if o[4] == best_offset)[:200]
                    forensics["toc_offset_candidates"].append({
                        "document_id": doc_id,
                        "toc_page": offsets_found[0][0],
                        "candidate_offset": best_offset,
                        "support_count": count,
                        "total_matches": len(offsets_found),
                        "offset_consistency": round(consistency, 2),
                        "support_entries": entries_str,
                        "detector_status": status,
                        "verification_status": "NOT_REVIEWED",
                    })
                else:
                    forensics["toc_offset_candidates"].append({
                        "document_id": doc_id,
                        "toc_page": toc_candidate_pages[0],
                        "candidate_offset": "UNRESOLVED",
                        "support_count": 0,
                        "total_matches": 0,
                        "offset_consistency": 0.0,
                        "support_entries": "",
                        "detector_status": "UNRESOLVED",
                        "verification_status": "NOT_REVIEWED",
                    })
        else:
            forensics["toc_offset_candidates"].append({
                "document_id": doc_id,
                "toc_page": "",
                "candidate_offset": "NO_TOC",
                "support_count": 0,
                "total_matches": 0,
                "offset_consistency": 0.0,
                "support_entries": "",
                "detector_status": "NOT_OBSERVED",
                "verification_status": "NOT_REVIEWED",
            })

        # Structure & MD&A Complexity Forensics
        mda_pages = [p.physical_page for p in pages_list if p.has_mda_keyword]
        annex_pages = [p.physical_page for p in pages_list if p.has_annexure_keyword]
        toc_outline = doc.get_toc()
        deep_hierarchy = any(len(item) >= 3 and item[0] >= 3 for item in toc_outline) if toc_outline else False
        combined_mda = False

        for item in toc_outline:
            title = item[1].lower()
            if "management" in title and "discussion" in title:
                if any(comb in title for comb in ["governance", "directors' report", "annexure", "board"]):
                    combined_mda = True

        for pno in mda_pages:
            p_text = doc[pno].get_text("text")
            for line in p_text.splitlines():
                llower = line.strip().lower()
                for mda_pat in cfg["structure_and_mda_heuristics"]["mda_heading_patterns"]:
                    if mda_pat in llower:
                        forensics["structure_candidates"].append({
                            "document_id": doc_id,
                            "page_index": pno,
                            "heading_text": line.strip()[:100],
                            "condition": "mda_heading_candidate",
                            "detector_status": "CANDIDATE",
                            "verification_status": "NOT_REVIEWED",
                        })
                        if any(comb in llower for comb in ["governance", "directors' report", "annexure", "board"]):
                            combined_mda = True
                        break

        forensics["mdna_complexity"].append({
            "document_id": doc_id,
            "mda_candidate_pages": len(mda_pages),
            "annexure_candidate_pages": len(annex_pages),
            "combined_mda_candidate": combined_mda,
            "deep_hierarchy_candidate": deep_hierarchy,
            "outline_entries_count": len(toc_outline),
            "detector_status": "CANDIDATE" if mda_pages else "NOT_OBSERVED",
            "verification_status": "NOT_REVIEWED",
        })

        # Language Candidates
        dev_pages = [p for p in pages_list if p.is_devanagari_page]
        for pc in dev_pages:
            forensics["language_candidates"].append({
                "document_id": doc_id,
                "page_index": pc.physical_page,
                "devanagari_chars": pc.devanagari_count,
                "latin_chars": pc.latin_count,
                "is_hindi_page": pc.is_hindi_page,
                "is_bilingual_page": pc.is_bilingual_page,
                "detector_status": "CANDIDATE",
                "verification_status": "NOT_REVIEWED",
            })

        ocr_pages_count = sum(1 for p in pages_list if p.is_t0_ocr)

        forensics["doc_page_counts"][doc_id] = {
            "native_page_count": sum(1 for p in pages_list if p.is_native),
            "ocr_page_count": ocr_pages_count,
            "scanned_page_count": sum(1 for p in pages_list if p.is_scanned),
            "legacy_candidate_page_count": len(legacy_cand_pages),
            "hidden_text_candidate_page_count": len(hidden_cand_pages),
            "duplicate_text_candidate_page_count": len(duplicate_cand_pages),
            "devanagari_page_count": len(dev_pages),
            "bilingual_candidate_page_count": sum(1 for p in pages_list if p.is_bilingual_page),
            "one_column_page_count": sum(1 for p in pages_list if p.estimated_columns == 1),
            "two_column_page_count": sum(1 for p in pages_list if p.estimated_columns == 2),
            "multi_column_page_count": sum(1 for p in pages_list if p.estimated_columns >= 3),
            "table_candidate_page_count": len(table_cand_pages),
            "header_candidate_page_count": len(header_cand_pages),
            "footer_candidate_page_count": len(footer_cand_pages),
            "toc_candidate": len(toc_candidate_pages) > 0,
            "deep_hierarchy_candidate": deep_hierarchy,
            "annexure_candidate": len(annex_pages) > 0,
            "combined_mdna_candidate": combined_mda,
        }

        doc.close()
        census_by_doc[doc_id] = pages_list

    return census_by_doc, forensics, total_pages_sum


def pass3_review_manifest(
    forensics: dict[str, Any],
    executable_rows: list[dict[str, str]],
    cfg: dict[str, Any],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    """Pass 3: Generate deterministic stratified review manifest."""
    manifest_rows = []
    results_rows = []

    doc_meta = {r["document_id"]: r for r in executable_rows}
    review_conditions = cfg["review_manifest_sampling"]["conditions_for_review"]

    for cond in review_conditions:
        candidates = []
        if cond == "table_candidate":
            candidates = forensics["table_candidates"]
        elif cond == "full_width_header":
            candidates = [c for c in forensics["header_footer_candidates"] if c["furniture_type"] == "running_header"]
        elif cond == "full_width_footer":
            candidates = [c for c in forensics["header_footer_candidates"] if c["furniture_type"] == "running_footer"]
        elif cond == "toc_offset":
            candidates = [c for c in forensics["toc_offset_candidates"] if c["detector_status"] in ("STRONG_CANDIDATE", "CANDIDATE")]
        elif cond == "duplicate_text":
            candidates = forensics["duplicate_text_candidates"]
        elif cond == "bilingual_candidate":
            candidates = [c for c in forensics["language_candidates"] if c["is_bilingual_page"]]
        elif cond == "annexure_candidate":
            candidates = [c for c in forensics["structure_candidates"] if "annexure" in c.get("heading_text", "").lower()]
        elif cond == "combined_mda_candidate":
            candidates = [c for c in forensics["mdna_complexity"] if c["combined_mda_candidate"]]

        sampled = []
        seen_issuers = set()
        for c in candidates:
            did = c["document_id"]
            meta = doc_meta[did]
            issuer = meta["issuer"]
            if issuer not in seen_issuers or len(sampled) < 5:
                sampled.append(c)
                seen_issuers.add(issuer)
                if len(sampled) >= cfg["review_manifest_sampling"]["target_candidates_per_family"]:
                    break

        for item in sampled:
            did = item["document_id"]
            meta = doc_meta[did]
            page_idx = item.get("page_index", item.get("toc_page", 0))
            record = {
                "document_id": did,
                "issuer": meta["issuer"],
                "fiscal_year": meta["fiscal_year"],
                "split": meta["split"],
                "page_index": page_idx,
                "condition": cond,
                "detector_status": "CANDIDATE",
                "evidence_details": json.dumps(item),
                "verification_status": "NOT_REVIEWED",
                "reviewer_type": "",
                "reviewer_notes": "",
            }
            manifest_rows.append(record)
            results_rows.append(dict(record))

    return manifest_rows, results_rows


def run_audit(
    out_dir: str,
    live_store: str,
    config_path: str,
    seed: int = 20260918,
) -> None:
    os.makedirs(out_dir, exist_ok=True)

    with open(config_path, "r", encoding="utf-8") as f:
        cfg = json.load(f)

    # 1. Hashing protected T0 input artifacts
    input_hashes = load_protected_t0_hashes(T0_DIR)
    with open(os.path.join(out_dir, "input_hashes.json"), "w", encoding="utf-8") as f:
        json.dump(input_hashes, f, indent=2)

    # Copy config and its sha256 to out_dir
    with open(os.path.join(out_dir, "audit_config.json"), "w", encoding="utf-8") as f:
        json.dump(cfg, f, indent=2)
    cfg_sha = compute_file_sha256(os.path.join(out_dir, "audit_config.json"))
    with open(os.path.join(out_dir, "audit_config.sha256"), "w", encoding="utf-8") as f:
        f.write(f"{cfg_sha}  audit_config.json\n")

    # 2. Load inventory
    inv_path = os.path.join(T0_DIR, "corpus_inventory.csv")
    with open(inv_path, "r", encoding="utf-8", newline="") as f:
        inv_rows = list(csv.DictReader(f))

    executable_rows = [r for r in inv_rows if r["openable"] == "True"]
    if len(executable_rows) != cfg["expected_corpus_size"]:
        raise ValueError(f"Expected {cfg['expected_corpus_size']} executable PDFs, found {len(executable_rows)}")

    # Load splits mapping from issuer_split.csv
    with open(os.path.join(T0_DIR, "issuer_split.csv"), "r", encoding="utf-8") as f:
        split_rows = list(csv.DictReader(f))
        split_map_id = {r["issuer_id"]: r["split"] for r in split_rows}
        split_map_name = {r["issuer_name"]: r["split"] for r in split_rows}

    # Attach split to rows
    for r in executable_rows:
        cid = r.get("company_id", "")
        iss_name = r.get("issuer", "")
        r["split"] = split_map_id.get(cid, split_map_name.get(iss_name, "UNKNOWN"))

    # Load dev, challenge, holdout sets
    def load_set_ids(fname: str) -> set[str]:
        with open(os.path.join(T0_DIR, fname), "r", encoding="utf-8") as f:
            return {r["document_id"] for r in csv.DictReader(f)}

    dev_ids = load_set_ids("development_manifest.csv")
    chal_ids = load_set_ids("challenge_coverage_manifest.csv")
    hold_ids = load_set_ids("holdout_manifest.csv")

    # Load frozen T0 page profile
    t0_profiles = load_t0_page_profiles(T0_DIR)

    # 3. Pass 1 & Pass 2
    census_by_doc, forensics, total_pages_sum = execute_pass1_and_pass2(
        executable_rows, live_store, t0_profiles, cfg
    )
    if total_pages_sum != cfg["expected_total_pages"]:
        raise ValueError(
            f"Physical page count integrity check failed: computed {total_pages_sum} != {cfg['expected_total_pages']}"
        )

    # 4. Long report distribution
    dist = calculate_long_report_distribution(executable_rows)

    # 5. Pass 3: Review Manifest
    manifest_rows, results_rows = pass3_review_manifest(forensics, executable_rows, cfg)

    # -------------------------------------------------------------
    # Write Specialized Candidate CSVs
    # -------------------------------------------------------------
    def write_csv(filename: str, rows: list[dict[str, Any]], fieldnames: list[str]) -> None:
        path = os.path.join(out_dir, filename)
        with open(path, "w", encoding="utf-8", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            for r in rows:
                filtered_r = {k: r.get(k, "") for k in fieldnames}
                writer.writerow(filtered_r)

    write_csv(
        "table_candidates.csv",
        forensics["table_candidates"],
        ["document_id", "page_index", "vector_grid_detected", "aligned_numeric_rows", "detector_status", "verification_status", "notes"],
    )

    write_csv(
        "header_footer_candidates.csv",
        forensics["header_footer_candidates"],
        ["document_id", "page_index", "furniture_type", "text_snippet", "vertical_coord", "detector_status", "verification_status"],
    )

    write_csv(
        "toc_offset_candidates.csv",
        forensics["toc_offset_candidates"],
        ["document_id", "toc_page", "candidate_offset", "support_count", "total_matches", "offset_consistency", "support_entries", "detector_status", "verification_status"],
    )

    write_csv(
        "duplicate_text_candidates.csv",
        forensics["duplicate_text_candidates"],
        ["document_id", "page_index", "condition_class", "text_snippet", "detector_status", "verification_status", "notes"],
    )

    write_csv(
        "language_candidates.csv",
        forensics["language_candidates"],
        ["document_id", "page_index", "devanagari_chars", "latin_chars", "is_hindi_page", "is_bilingual_page", "detector_status", "verification_status"],
    )

    write_csv(
        "structure_candidates.csv",
        forensics["structure_candidates"],
        ["document_id", "page_index", "heading_text", "condition", "detector_status", "verification_status"],
    )

    write_csv(
        "mdna_candidate_complexity.csv",
        forensics["mdna_complexity"],
        ["document_id", "mda_candidate_pages", "annexure_candidate_pages", "combined_mda_candidate", "deep_hierarchy_candidate", "outline_entries_count", "detector_status", "verification_status"],
    )

    write_csv(
        "manual_review_manifest.csv",
        manifest_rows,
        ["document_id", "issuer", "fiscal_year", "split", "page_index", "condition", "detector_status", "evidence_details", "verification_status", "reviewer_type", "reviewer_notes"],
    )

    write_csv(
        "manual_review_results.csv",
        results_rows,
        ["document_id", "issuer", "fiscal_year", "split", "page_index", "condition", "detector_status", "evidence_details", "verification_status", "reviewer_type", "reviewer_notes"],
    )

    # -------------------------------------------------------------
    # Write Document-Level CSV: gap_audit_document.csv
    # -------------------------------------------------------------
    doc_rows = []
    toc_cand_docs = {c["document_id"]: c for c in forensics["toc_offset_candidates"]}

    for r in executable_rows:
        did = r["document_id"]
        sha = r["pdf_sha256"]
        pgs = int(r["page_count"])
        counts = forensics["doc_page_counts"][did]

        if pgs < dist["q1"]:
            l_cat = "SHORT"
        elif pgs <= dist["q3"]:
            l_cat = "MEDIUM"
        elif pgs <= dist["p90"]:
            l_cat = "LONG"
        elif pgs <= dist["p95"]:
            l_cat = "VERY_LONG"
        else:
            l_cat = "EXTREME"

        scanned_c = counts["scanned_page_count"]
        ocr_c = counts["ocr_page_count"]
        native_c = counts["native_page_count"]

        if scanned_c == pgs:
            doc_rep = "SCANNED"
        elif scanned_c == 0 and ocr_c == 0:
            doc_rep = "NATIVE"
        elif scanned_c > 0 or ocr_c > 0:
            doc_rep = "MIXED"
        else:
            doc_rep = "UNKNOWN"

        toc_offset_info = toc_cand_docs.get(did, {})
        toc_offset_val = toc_offset_info.get("candidate_offset", "UNKNOWN")

        doc_rows.append({
            "document_id": did,
            "pdf_path": os.path.join(live_store, "blobs", sha[:2], sha[2:4], f"{sha}.pdf"),
            "sha256": sha,
            "issuer": r["issuer"],
            "fiscal_year": r["fiscal_year"],
            "total_pages": pgs,
            "split": r["split"],
            "development_flag": did in dev_ids,
            "challenge_flag": did in chal_ids,
            "holdout_flag": did in hold_ids,
            "native_page_count": counts["native_page_count"],
            "ocr_page_count": counts["ocr_page_count"],
            "scanned_page_count": counts["scanned_page_count"],
            "legacy_candidate_page_count": counts["legacy_candidate_page_count"],
            "hidden_text_candidate_page_count": counts["hidden_text_candidate_page_count"],
            "duplicate_text_candidate_page_count": counts["duplicate_text_candidate_page_count"],
            "devanagari_page_count": counts["devanagari_page_count"],
            "bilingual_candidate_page_count": counts["bilingual_candidate_page_count"],
            "one_column_page_count": counts["one_column_page_count"],
            "two_column_page_count": counts["two_column_page_count"],
            "multi_column_page_count": counts["multi_column_page_count"],
            "table_candidate_page_count": counts["table_candidate_page_count"],
            "header_candidate_page_count": counts["header_candidate_page_count"],
            "footer_candidate_page_count": counts["footer_candidate_page_count"],
            "toc_candidate": counts["toc_candidate"],
            "toc_offset_candidate": toc_offset_val,
            "deep_hierarchy_candidate": counts["deep_hierarchy_candidate"],
            "annexure_candidate": counts["annexure_candidate"],
            "combined_mdna_candidate": counts["combined_mdna_candidate"],
            "long_report_category": l_cat,
            "document_representation": doc_rep,
            "evidence_status": "OBSERVED",
            "notes": f"Q1={dist['q1']}, Median={dist['median']}, Q3={dist['q3']}",
        })

    doc_fields = [
        "document_id", "pdf_path", "sha256", "issuer", "fiscal_year", "total_pages",
        "split", "development_flag", "challenge_flag", "holdout_flag",
        "native_page_count", "ocr_page_count", "scanned_page_count",
        "legacy_candidate_page_count", "hidden_text_candidate_page_count", "duplicate_text_candidate_page_count",
        "devanagari_page_count", "bilingual_candidate_page_count",
        "one_column_page_count", "two_column_page_count", "multi_column_page_count",
        "table_candidate_page_count", "header_candidate_page_count", "footer_candidate_page_count",
        "toc_candidate", "toc_offset_candidate",
        "deep_hierarchy_candidate", "annexure_candidate", "combined_mdna_candidate",
        "long_report_category", "document_representation", "evidence_status", "notes",
    ]
    write_csv("gap_audit_document.csv", doc_rows, doc_fields)

    # -------------------------------------------------------------
    # Condition-Document Map (condition_document_map.csv)
    # -------------------------------------------------------------
    cond_doc_rows = []
    tracked_conditions = [
        ("native", "native_page_count"),
        ("scanned", "scanned_page_count"),
        ("ocr_layer_candidate", "ocr_page_count"),
        ("legacy_font_candidate", "legacy_candidate_page_count"),
        ("hidden_text_candidate", "hidden_text_candidate_page_count"),
        ("duplicate_text_candidate", "duplicate_text_candidate_page_count"),
        ("devanagari_candidate", "devanagari_page_count"),
        ("bilingual_candidate", "bilingual_candidate_page_count"),
        ("two_column", "two_column_page_count"),
        ("multi_column", "multi_column_page_count"),
        ("table_candidate", "table_candidate_page_count"),
        ("header_candidate", "header_candidate_page_count"),
        ("footer_candidate", "footer_candidate_page_count"),
        ("toc_candidate", "toc_candidate"),
        ("deep_hierarchy_candidate", "deep_hierarchy_candidate"),
        ("annexure_candidate", "annexure_candidate"),
        ("combined_mdna_candidate", "combined_mdna_candidate"),
    ]

    for d in doc_rows:
        did = d["document_id"]
        for cond_name, prop in tracked_conditions:
            val = d[prop]
            is_cand = (val > 0) if isinstance(val, int) else bool(val)
            pg_count = val if isinstance(val, int) else (1 if val else 0)
            cond_doc_rows.append({
                "document_id": did,
                "issuer": d["issuer"],
                "fiscal_year": d["fiscal_year"],
                "split": d["split"],
                "condition": cond_name,
                "status": "CANDIDATE" if is_cand else "NOT_OBSERVED",
                "evidence_source": "t0.1_audit_detector",
                "document_count_basis": 1 if is_cand else 0,
                "page_count": pg_count,
                "issuer_count_basis": 1 if is_cand else 0,
                "detector_name": f"audit_detector_{cond_name}",
                "detector_version": "1.0.0",
                "verification_status": "NOT_REVIEWED",
                "reviewer_type": "",
                "notes": f"raw_prop={prop}",
            })

    cond_doc_fields = [
        "document_id", "issuer", "fiscal_year", "split", "condition",
        "status", "evidence_source", "document_count_basis", "page_count",
        "issuer_count_basis", "detector_name", "detector_version",
        "verification_status", "reviewer_type", "notes",
    ]
    write_csv("condition_document_map.csv", cond_doc_rows, cond_doc_fields)

    # -------------------------------------------------------------
    # Condition-Page Map (condition_page_map.csv)
    # -------------------------------------------------------------
    cond_page_rows = []
    for doc_id, pages in census_by_doc.items():
        for pc in pages:
            pno = pc.physical_page
            if pc.is_scanned:
                cond_page_rows.append({
                    "document_id": doc_id,
                    "page_index": pno,
                    "condition": "scanned_page",
                    "detector": "census_scanned_detector",
                    "detector_version": "1.0.0",
                    "score_or_evidence": f"chars={pc.char_count}, img_area={pc.image_area_frac}",
                    "candidate_status": "CANDIDATE",
                    "verification_status": "NOT_REVIEWED",
                    "notes": "",
                })
            elif pc.is_native:
                cond_page_rows.append({
                    "document_id": doc_id,
                    "page_index": pno,
                    "condition": "native_page",
                    "detector": "census_native_detector",
                    "detector_version": "1.0.0",
                    "score_or_evidence": f"chars={pc.char_count}",
                    "candidate_status": "CANDIDATE",
                    "verification_status": "NOT_REVIEWED",
                    "notes": "",
                })

            if pc.is_t0_ocr:
                cond_page_rows.append({
                    "document_id": doc_id,
                    "page_index": pno,
                    "condition": "ocr_layer_page",
                    "detector": "t0_profile_ocr_indicator",
                    "detector_version": "1.0.0",
                    "score_or_evidence": "render_mode_ocr_layer_indicator=True",
                    "candidate_status": "CANDIDATE",
                    "verification_status": "NOT_REVIEWED",
                    "notes": "",
                })

            if pc.is_devanagari_page:
                cond_page_rows.append({
                    "document_id": doc_id,
                    "page_index": pno,
                    "condition": "devanagari_page",
                    "detector": "census_devanagari_detector",
                    "detector_version": "1.0.0",
                    "score_or_evidence": f"dev_chars={pc.devanagari_count}",
                    "candidate_status": "CANDIDATE",
                    "verification_status": "NOT_REVIEWED",
                    "notes": "",
                })

            if pc.estimated_columns == 2:
                cond_page_rows.append({
                    "document_id": doc_id,
                    "page_index": pno,
                    "condition": "two_column_page",
                    "detector": "census_layout_detector",
                    "detector_version": "1.0.0",
                    "score_or_evidence": "est_cols=2",
                    "candidate_status": "CANDIDATE",
                    "verification_status": "NOT_REVIEWED",
                    "notes": "",
                })

    cond_page_fields = [
        "document_id", "page_index", "condition", "detector", "detector_version",
        "score_or_evidence", "candidate_status", "verification_status", "notes",
    ]
    write_csv("condition_page_map.csv", cond_page_rows, cond_page_fields)

    # -------------------------------------------------------------
    # Interaction Gap Matrix (interaction_gap_matrix.csv)
    # -------------------------------------------------------------
    interaction_pairs = [
        ("ocr_layer_candidate", "scanned_or_mixed"),
        ("legacy_font_candidate", "scanned_or_mixed"),
        ("hidden_text_candidate", "ocr_layer_candidate"),
        ("duplicate_text_candidate", "ocr_layer_candidate"),
        ("two_column", "table_candidate"),
        ("two_column", "header_candidate"),
        ("two_column", "footer_candidate"),
        ("two_column", "devanagari_candidate"),
        ("toc_candidate", "deep_hierarchy_candidate"),
        ("toc_candidate", "toc_offset_candidate"),
        ("annexure_candidate", "combined_mdna_candidate"),
        ("bilingual_candidate", "legacy_font_candidate"),
        ("bilingual_candidate", "scanned_or_mixed"),
        ("long_report", "deep_hierarchy_candidate"),
        ("long_report", "scanned_or_mixed"),
    ]

    cond_col_map = {
        "ocr_layer_candidate": "ocr_page_count",
        "legacy_font_candidate": "legacy_candidate_page_count",
        "hidden_text_candidate": "hidden_text_candidate_page_count",
        "duplicate_text_candidate": "duplicate_text_candidate_page_count",
        "devanagari_candidate": "devanagari_page_count",
        "bilingual_candidate": "bilingual_candidate_page_count",
        "two_column": "two_column_page_count",
        "multi_column": "multi_column_page_count",
        "table_candidate": "table_candidate_page_count",
        "header_candidate": "header_candidate_page_count",
        "footer_candidate": "footer_candidate_page_count",
        "toc_candidate": "toc_candidate",
        "deep_hierarchy_candidate": "deep_hierarchy_candidate",
        "annexure_candidate": "annexure_candidate",
        "combined_mdna_candidate": "combined_mdna_candidate",
    }

    inter_rows = []
    for cond_a, cond_b in interaction_pairs:
        matched_docs = []
        for d in doc_rows:
            def check_cond(c_name: str) -> bool:
                if c_name == "scanned_or_mixed":
                    return d["document_representation"] in ("SCANNED", "MIXED")
                if c_name == "long_report":
                    return d["long_report_category"] in ("LONG", "VERY_LONG", "EXTREME")
                if c_name == "toc_offset_candidate":
                    return d["toc_offset_candidate"] not in ("UNKNOWN", "NO_TOC")
                col = cond_col_map.get(c_name, c_name)
                val = d.get(col, False)
                return (val > 0) if isinstance(val, int) else bool(val)

            if check_cond(cond_a) and check_cond(cond_b):
                matched_docs.append(d)

        doc_count = len(matched_docs)
        iss_count = len({d["issuer"] for d in matched_docs})
        page_sum = sum(d["total_pages"] for d in matched_docs)
        dev_c = sum(1 for d in matched_docs if d["development_flag"])
        chal_c = sum(1 for d in matched_docs if d["challenge_flag"])
        val_c = sum(1 for d in matched_docs if d["split"] == "VALIDATION")
        hold_c = sum(1 for d in matched_docs if d["split"] == "HOLDOUT")

        inter_rows.append({
            "condition_a": cond_a,
            "condition_b": cond_b,
            "document_count": doc_count,
            "issuer_count": iss_count,
            "page_count": page_sum,
            "development_count": dev_c,
            "challenge_count": chal_c,
            "validation_count": val_c,
            "holdout_count": hold_c,
            "status": "OBSERVED" if doc_count > 0 else "NOT_OBSERVED",
            "notes": f"issuers={iss_count}",
        })

    inter_fields = [
        "condition_a", "condition_b", "document_count", "issuer_count", "page_count",
        "development_count", "challenge_count", "validation_count", "holdout_count", "status", "notes",
    ]
    write_csv("interaction_gap_matrix.csv", inter_rows, inter_fields)

    # -------------------------------------------------------------
    # Summary JSON (gap_audit_summary.json)
    # -------------------------------------------------------------
    summary_data = {
        "audit_name": "T0.1 Corpus Gap Audit",
        "seed": seed,
        "corpus_inventory": {
            "total_records": len(inv_rows),
            "executable_pdfs": len(executable_rows),
            "missing_historical_records": len(inv_rows) - len(executable_rows),
            "total_physical_pages": total_pages_sum,
            "distinct_issuers": len({r["issuer"] for r in executable_rows}),
            "page_count_distribution": dist,
        },
        "splits": {
            "fit_docs": sum(1 for r in executable_rows if r["split"] == "FIT"),
            "val_docs": sum(1 for r in executable_rows if r["split"] == "VALIDATION"),
            "hold_docs": sum(1 for r in executable_rows if r["split"] == "HOLDOUT"),
            "dev_docs": len(dev_ids),
            "challenge_docs": len(chal_ids),
        },
        "conditions_summary": {
            cond: {
                "document_count": sum(1 for r in cond_doc_rows if r["condition"] == cond and r["status"] == "CANDIDATE"),
                "issuer_count": len({r["issuer"] for r in cond_doc_rows if r["condition"] == cond and r["status"] == "CANDIDATE"}),
            }
            for cond, _ in tracked_conditions
        },
    }
    with open(os.path.join(out_dir, "gap_audit_summary.json"), "w", encoding="utf-8") as f:
        json.dump(summary_data, f, indent=2)

    # -------------------------------------------------------------
    # Gap Summary CSV (gap_summary.csv)
    # -------------------------------------------------------------
    gap_summary_rows = []
    for cond, _ in tracked_conditions:
        c_docs = [r for r in cond_doc_rows if r["condition"] == cond and r["status"] == "CANDIDATE"]
        n_docs = len(c_docs)
        n_iss = len({r["issuer"] for r in c_docs})
        p_count = sum(r["page_count"] for r in c_docs)
        fit_c = sum(1 for r in c_docs if r["split"] == "FIT")
        val_c = sum(1 for r in c_docs if r["split"] == "VALIDATION")
        hold_c = sum(1 for r in c_docs if r["split"] == "HOLDOUT")

        if n_docs >= 50 and n_iss >= 20:
            classification = "WELL_REPRESENTED"
        elif n_docs >= 15 and n_iss >= 10:
            classification = "REPRESENTED"
        elif 1 <= n_docs < 10 or n_iss <= 2:
            classification = "RARE"
        elif n_docs == 0:
            classification = "UNKNOWN"
        else:
            classification = "NOT_SUFFICIENTLY_REPRESENTED"

        gap_summary_rows.append({
            "condition": cond,
            "document_count": n_docs,
            "issuer_count": n_iss,
            "page_count": p_count,
            "fit_count": fit_c,
            "validation_count": val_c,
            "holdout_count": hold_c,
            "classification": classification,
            "concentration": round(n_docs / max(1, n_iss), 2),
        })

    gap_summary_fields = [
        "condition", "document_count", "issuer_count", "page_count",
        "fit_count", "validation_count", "holdout_count", "classification", "concentration",
    ]
    write_csv("gap_summary.csv", gap_summary_rows, gap_summary_fields)

    # -------------------------------------------------------------
    # Environment Provenance JSON (environment.json)
    # -------------------------------------------------------------
    pip_res = subprocess.run([sys.executable, "-m", "pip", "freeze"], capture_output=True, text=True)
    pip_hash = hashlib.sha256(pip_res.stdout.encode("utf-8")).hexdigest()

    env_data = {
        "python_version": sys.version,
        "platform": platform.platform(),
        "pymupdf_version": pymupdf.__version__,
        "pip_freeze_sha256": pip_hash,
        "t0_base_commit": "23d62286c4b807607b29a4dc14940179f90e3c0d",
        "audit_config_sha256": cfg_sha,
        "input_manifest_hash": input_hashes["corpus_inventory.csv"],
        "run_timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "notes": "run_timestamp is for execution provenance only; substantive results are fully deterministic.",
    }
    with open(os.path.join(out_dir, "environment.json"), "w", encoding="utf-8") as f:
        json.dump(env_data, f, indent=2)


def main() -> int:
    parser = argparse.ArgumentParser(description="ARPipe T0.1 Corpus Gap Audit")
    parser.add_argument("--out-dir", required=True, help="Directory to store audit output artifacts")
    parser.add_argument("--live-store-root", default=DEFAULT_LIVE_STORE, help="Path to live_store root")
    parser.add_argument("--config", default=DEFAULT_CONFIG, help="Path to audit_config.json")
    parser.add_argument("--seed", type=int, default=20260918, help="Random seed")
    args = parser.parse_args()

    run_audit(
        out_dir=args.out_dir,
        live_store=args.live_store_root,
        config_path=args.config,
        seed=args.seed,
    )
    print(f"PASS: Audit completed successfully. Artifacts written to {args.out_dir}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

