"""CLI transport for the SAP v0.1 pure scoring functions.

Each Gold JSON file contains one v0.1 record. The prediction CSV columns are
``claim_document_id,document_id,source_pdf_sha256,disposition,physical_page_count,span,reasons``.
The last three columns are JSON cells (for example ``12``,
``{"start_page":2,"end_page":4}``, and ``[]``); a missing span is ``null``.
The claim column identifies which Gold document a row claims, so §3 can detect
an identity mismatch in the row itself. An optional ``--issuer-map`` JSON object
maps every document ID to an issuer for the SAP §7 issuer summaries.
"""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path

from . import census_summary, score_documents


def _guard_paths(paths: list[Path], approved: bool) -> None:
    """Refuse HOLDOUT-named input/output paths without explicit author approval."""
    if not approved and any("holdout" in str(path).casefold() for path in paths):
        raise ValueError("HOLDOUT path refused; --i-have-author-approval is required")


def _load_predictions(path: Path) -> dict[str, list[dict]]:
    required = {
        "claim_document_id", "document_id", "source_pdf_sha256", "disposition",
        "physical_page_count", "span", "reasons",
    }
    grouped: dict[str, list[dict]] = {}
    with path.open(newline="", encoding="utf-8-sig") as handle:
        reader = csv.DictReader(handle)
        if reader.fieldnames is None or not required.issubset(reader.fieldnames):
            raise ValueError("Prediction CSV is missing required columns")
        for row in reader:
            if None in row or not row["claim_document_id"]:
                raise ValueError("Malformed prediction CSV row")
            parsed = {
                "document_id": row["document_id"],
                "source_pdf_sha256": row["source_pdf_sha256"],
                "disposition": row["disposition"],
            }
            try:
                for key in ("physical_page_count", "span", "reasons"):
                    parsed[key] = json.loads(row[key])
            except (TypeError, json.JSONDecodeError) as exc:
                raise ValueError("Prediction JSON cell is malformed") from exc
            grouped.setdefault(row["claim_document_id"], []).append(parsed)
    return grouped


def main(argv: list[str] | None = None) -> int:
    """SAP §§2–7: score JSON Gold and CSV predictions to canonical JSON."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--gold", required=True, type=Path)
    parser.add_argument("--pred", required=True, type=Path)
    parser.add_argument("--out", required=True, type=Path)
    parser.add_argument("--issuer-map", type=Path)
    parser.add_argument("--i-have-author-approval", action="store_true")
    args = parser.parse_args(argv)
    paths = [args.gold, args.pred, args.out]
    if args.issuer_map is not None:
        paths.append(args.issuer_map)
    try:
        _guard_paths(paths, args.i_have_author_approval)
        if not args.gold.is_dir():
            raise ValueError("--gold must be a directory")
        gold_files = sorted(args.gold.glob("*.json"))
        if not gold_files:
            raise ValueError("Gold directory has no JSON files")
        _guard_paths(gold_files, args.i_have_author_approval)
        gold = [json.loads(path.read_text(encoding="utf-8")) for path in gold_files]
        result = score_documents(gold, _load_predictions(args.pred))
        if args.issuer_map is not None:
            issuer_map = json.loads(args.issuer_map.read_text(encoding="utf-8"))
            result["census"] = census_summary(result, issuer_map)
        else:
            result["census"] = {"overall": result["primary"], "issuer_values": "NOT_ESTIMABLE"}
        with args.out.open("w", encoding="utf-8", newline="\n") as handle:
            handle.write(
                json.dumps(result, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False) + "\n"
            )
    except (OSError, ValueError, TypeError, KeyError, json.JSONDecodeError) as exc:
        parser.exit(2, f"scoring refused: {exc}\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
