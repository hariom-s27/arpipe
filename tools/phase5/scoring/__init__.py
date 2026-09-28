"""Pure, standard-library SAP v0.1 scoring functions.

Gold records use schema v0.1 when ``schema_version`` is absent, v0.2 when it is
exactly ``"0.2"``, v0.3 when it is exactly ``"0.3"``, and v0.4 when it is exactly
``"0.4"``. Prediction rows use the SAP §3
fields ``document_id``, ``source_pdf_sha256``, ``disposition``, ``span``,
``reasons``, and ``physical_page_count``. Callers group rows by claimed document
ID; the row's own document ID is still checked for identity.
"""

from __future__ import annotations

from collections import Counter
from math import floor
import re
from typing import Mapping, Sequence

NOT_ESTIMABLE = "NOT_ESTIMABLE"
STATES = ("PRESENT", "ABSENT", "AMBIGUOUS")
STATUSES = (
    "NO_OUTPUT", "DUPLICATE", "IDENTITY_INVALID", "QUARANTINE",
    "NOT_LOCATED", "TYPE_INVALID", "ORDER_INVALID", "RANGE_INVALID", "VALID",
)
GOLD_SCHEMA_V0_1_FILENAME = "gold_schema_v0_1.json"
GOLD_SCHEMA_V0_2_FILENAME = "gold_schema_v0_2.json"
GOLD_SCHEMA_V0_3_FILENAME = "gold_schema_v0_3.json"
GOLD_SCHEMA_V0_4_FILENAME = "gold_schema_v0_4.json"
# Decisions 8.7: the two Gold shared-page answers (boundary_evidence keys) of schema v0.3
# (kept by v0.4), each with the flag that mirrors it.
SHARED_PAGE_KEYS = ("start_page_shared", "end_page_shared")
SHARED_PAGE_FLAGS = {"start_page_shared": "mixed_start_page", "end_page_shared": "mixed_end_page"}
# Schema v0.4: the anchor-text field paired with each shared-page key above.
ANCHOR_TEXT_KEYS = {"start_page_shared": "start_anchor_text", "end_page_shared": "end_anchor_text"}


def gold_schema_filename(record: Mapping) -> str:
    """Select one Gold schema from the record version; never try another."""
    if "schema_version" not in record:
        return GOLD_SCHEMA_V0_1_FILENAME
    if record["schema_version"] == "0.2":
        return GOLD_SCHEMA_V0_2_FILENAME
    if record["schema_version"] == "0.3":
        return GOLD_SCHEMA_V0_3_FILENAME
    if record["schema_version"] == "0.4":
        return GOLD_SCHEMA_V0_4_FILENAME
    raise ValueError("Unsupported Gold schema_version")


def _integer(value: object) -> bool:
    return type(value) is int


def _endpoints(span: object) -> tuple[object, object]:
    if not isinstance(span, Mapping):
        return None, None
    return span.get("start_page"), span.get("end_page")


def is_valid_span(span: object, page_count: object) -> bool:
    """SAP §3: require integer inclusive boundaries inside a positive page count."""
    start, end = _endpoints(span)
    return (
        _integer(page_count) and page_count > 0
        and _integer(start) and _integer(end)
        and 0 <= start <= end < page_count
    )


def classify_prediction(gold: Mapping, rows: Sequence[Mapping]) -> str:
    """SAP §3: apply the nine mutually exclusive statuses in priority order."""
    if not rows:
        return "NO_OUTPUT"
    if len(rows) != 1:
        return "DUPLICATE"
    row = rows[0]
    if (row.get("document_id") != gold["document_id"]
            or row.get("source_pdf_sha256") != gold["source_pdf_sha256"]):
        return "IDENTITY_INVALID"
    if row.get("disposition") == "QUARANTINE":
        return "QUARANTINE"
    span = row.get("span")
    reasons = row.get("reasons")
    if span is None and isinstance(reasons, list) and "mda_not_located" in reasons:
        return "NOT_LOCATED"
    start, end = _endpoints(span)
    if (not isinstance(reasons, list)
            or any(not isinstance(reason, str) for reason in reasons)
            or "mda_not_located" in reasons
            or not _integer(row.get("physical_page_count"))
            or row["physical_page_count"] <= 0
            or not _integer(start) or not _integer(end)):
        return "TYPE_INVALID"
    if start > end:
        return "ORDER_INVALID"
    if start < 0 or end >= row["physical_page_count"]:
        return "RANGE_INVALID"
    return "VALID"


def inclusive_iou(prediction_span: Mapping, gold_span: Mapping) -> float:
    """SAP §4: 0-based inclusive intersection over union of two spans."""
    ps, pe = _endpoints(prediction_span)
    gs, ge = _endpoints(gold_span)
    if not all(_integer(x) for x in (ps, pe, gs, ge)) or min(ps, gs) < 0 or ps > pe or gs > ge:
        raise ValueError("IoU requires ordered, non-negative integer spans")
    intersection = max(0, min(pe, ge) - max(ps, gs) + 1)
    union = (pe - ps + 1) + (ge - gs + 1) - intersection
    return intersection / union


def _validate_gold(record: Mapping) -> None:
    """SAP §1; Gold Schema §§2–3: block malformed scoring-relevant Gold."""
    try:
        schema_filename = gold_schema_filename(record)
        is_v0_4 = schema_filename == GOLD_SCHEMA_V0_4_FILENAME
        is_v0_3 = is_v0_4 or schema_filename == GOLD_SCHEMA_V0_3_FILENAME  # v0.4 keeps v0.3's rules
        is_v0_2 = is_v0_3 or schema_filename == GOLD_SCHEMA_V0_2_FILENAME  # v0.3 keeps v0.2's rules
        doc_id = record["document_id"]
        source_hash = record["source_pdf_sha256"]
        state = record["presence_state"]
        count = record["structured_provenance"]["physical_page_count"]
        primary = record["primary_span"]
        alternatives = record["alternative_spans"]
        admissible = record["admissible_spans"]
        reason = record["presence_reason_code"]
        ambiguity_code = record["ambiguity_code"]
        flags = record["flags"]
        gaps = record["gap_pages"]
    except (KeyError, TypeError) as exc:
        raise ValueError("Gold is missing a scoring field") from exc
    if (not isinstance(doc_id, str) or re.fullmatch(r"[A-Za-z0-9._-]{1,256}", doc_id) is None
            or not isinstance(source_hash, str) or re.fullmatch(r"[0-9a-f]{64}", source_hash) is None
            or state not in STATES or not _integer(count) or count <= 0
            or not isinstance(alternatives, list) or not isinstance(admissible, list)
            or not isinstance(flags, list) or not isinstance(gaps, list)):
        raise ValueError("Invalid Gold scoring field")
    if (record.get("record_type") not in ("RAW", "ADJUDICATED")
            or (record["record_type"] == "RAW" and record.get("annotator_role") not in ("ANNOTATOR_A", "ANNOTATOR_B"))
            or (record["record_type"] == "ADJUDICATED" and record.get("annotator_role") != "ADJUDICATED_RECORD")):
        raise ValueError("Invalid Gold record type or role")
    if state == "PRESENT":
        if (not is_valid_span(primary, count) or admissible or ambiguity_code != "NONE"
                or reason not in ("BODY_QUALIFYING_TITLE", "CONDITIONAL_TITLE_CONTEXT_MET")):
            raise ValueError("PRESENT Gold needs one valid primary span")
    elif primary is not None:
        raise ValueError("Non-PRESENT Gold cannot have a primary span")
    if state == "ABSENT":
        absent_reasons = {
            "NO_QUALIFYING_BODY_SECTION", "TOC_ONLY", "POINTER_ONLY",
            "CONFUSABLE_SECTION_ONLY", "NOT_AN_ANNUAL_REPORT",
        }
        if is_v0_2:
            absent_reasons.update({"NO_ENGLISH_MDA", "EXTERNAL_REFERENCE_ONLY"})
        hindi_only = is_v0_2 and reason == "NO_ENGLISH_MDA"
        alternatives_invalid = (
            any(
                not isinstance(span, Mapping) or span.get("type") != "HINDI_COPY"
                for span in alternatives
            )
            if hindi_only else bool(alternatives)
        )
        if (alternatives_invalid or admissible or gaps or ambiguity_code != "NONE"
                or reason not in absent_reasons):
            raise ValueError("Invalid ABSENT Gold spans or reason")
    if state == "AMBIGUOUS" and (not admissible or ambiguity_code == "NONE" or reason not in (
            "PRESENCE_UNRESOLVABLE", "START_UNRESOLVABLE", "END_UNRESOLVABLE",
            "SPAN_UNRESOLVABLE", "TITLE_CONTEXT_UNRESOLVABLE")):
        raise ValueError("AMBIGUOUS Gold needs admissible spans")
    if any(not is_valid_span(span, count) for span in alternatives + admissible):
        raise ValueError("Invalid Gold alternative or admissible span")
    if (not all(_integer(page) for page in gaps) or gaps != sorted(set(gaps))
            or bool(gaps) != ("noncontiguous_hull" in flags)):
        raise ValueError("Invalid Gold gap pages")
    if gaps and (primary is None or any(not primary["start_page"] < page < primary["end_page"] for page in gaps)):
        raise ValueError("Gold gap must be strictly inside the primary hull")
    if not is_v0_2 and (
        "stub_word_count" in record
        or "csr_esg_pages" in record
        or {"stub", "contains_csr_esg"} & set(flags)
    ):
        raise ValueError("v0.1 Gold contains a v0.2-only field or flag")
    if is_v0_2:
        stub_count = record.get("stub_word_count")
        if (stub_count is not None
                and (not _integer(stub_count) or stub_count < 0 or "stub" not in flags)):
            raise ValueError("Invalid Gold stub_word_count")
        if state != "PRESENT" and ({"stub", "contains_csr_esg"} & set(flags)):
            raise ValueError("stub and contains_csr_esg require PRESENT Gold")
        csr_pages = record.get("csr_esg_pages", [])
        if (not isinstance(csr_pages, list)
                or any(not _integer(page) or page < 0 for page in csr_pages)
                or len(csr_pages) != len(set(csr_pages))
                or bool(csr_pages) != ("contains_csr_esg" in flags)):
            raise ValueError("Invalid Gold csr_esg_pages")
        if csr_pages and (
            primary is None
            or any(not primary["start_page"] <= page <= primary["end_page"] for page in csr_pages)
            or any(page in gaps for page in csr_pages)
        ):
            raise ValueError(
                "Gold CSR/ESG page must be inside the primary span and outside gaps"
            )
    if is_v0_3:
        evidence = record.get("boundary_evidence")
        if not isinstance(evidence, Mapping) or any(key not in evidence for key in SHARED_PAGE_KEYS):
            raise ValueError("v0.3 Gold is missing a shared-page answer")
        answers = [evidence[key] for key in SHARED_PAGE_KEYS]
        if (any(type(answer) is not bool for answer in answers) if state == "PRESENT"
                else any(answer is not None for answer in answers)):
            raise ValueError("Invalid Gold shared-page answers")
        if any((SHARED_PAGE_FLAGS[key] in flags) != (evidence[key] is True) for key in SHARED_PAGE_KEYS):
            raise ValueError("Gold shared-page flags disagree with the answers")
        if is_v0_4:
            for shared_key, anchor_key in ANCHOR_TEXT_KEYS.items():
                if anchor_key not in evidence:
                    raise ValueError("v0.4 Gold is missing an anchor-text field")
                anchor = evidence[anchor_key]
                if evidence[shared_key] is True:
                    if not isinstance(anchor, str) or not anchor.strip() or anchor != anchor.strip():
                        raise ValueError("Invalid Gold anchor text for a shared page")
                elif anchor is not None:
                    raise ValueError("Gold anchor text must be null when the page is not shared")


def _shared_answer(record: Mapping, key: str) -> bool | None:
    """The Yes/No a v0.3/v0.4 PRESENT record gives for ``key``; None where it carries none."""
    if record.get("schema_version") not in ("0.3", "0.4") or record["presence_state"] != "PRESENT":
        return None
    return record["boundary_evidence"][key]


def _ratio(numerator: int | float, denominator: int) -> float | str:
    return numerator / denominator if denominator else NOT_ESTIMABLE


def _quantiles(values: Sequence[int]) -> dict[str, float | str]:
    """SAP §6: type-7 quantiles, with an empty-sample sentinel."""
    ordered = sorted(values)
    result = {}
    for label, p in (("0", 0), ("0.25", .25), ("0.5", .5), ("0.75", .75), ("1", 1)):
        if not ordered:
            result[label] = NOT_ESTIMABLE
            continue
        h = 1 + (len(ordered) - 1) * p
        j = floor(h)
        lower = ordered[j - 1]
        upper = ordered[min(j, len(ordered) - 1)]
        result[label] = float(lower + (h - j) * (upper - lower))
    return result


def _indicators(p: Mapping, g: Mapping) -> dict[str, int]:
    ps, pe = _endpoints(p)
    gs, ge = _endpoints(g)
    return {
        "exact_start": int(ps == gs),
        "exact_end": int(pe == ge),
        "within_one_start": int(abs(ps - gs) <= 1),
        "within_one_end": int(abs(pe - ge) <= 1),
        "exact_full_span": int(ps == gs and pe == ge),
    }


def presence_endpoint(documents: Sequence[Mapping]) -> dict:
    """SAP §5: full 2×3 table and error-penalized 2×2 collapse."""
    table = {
        state: {column: 0 for column in ("PRESENT", "NOT_LOCATED", "FAILED_OR_ABSTAINED")}
        for state in ("PRESENT", "ABSENT")
    }
    for doc in documents:
        state = doc["gold_state"]
        if state not in table:
            continue
        status = doc["prediction_status"]
        column = "PRESENT" if status == "VALID" else (
            "NOT_LOCATED" if status == "NOT_LOCATED" else "FAILED_OR_ABSTAINED"
        )
        table[state][column] += 1
    tp = table["PRESENT"]["PRESENT"]
    fn = table["PRESENT"]["NOT_LOCATED"] + table["PRESENT"]["FAILED_OR_ABSTAINED"]
    tn = table["ABSENT"]["NOT_LOCATED"]
    fp = table["ABSENT"]["PRESENT"] + table["ABSENT"]["FAILED_OR_ABSTAINED"]
    collapsed = {"TP": tp, "FN": fn, "FP": fp, "TN": tn}
    return {
        "table_2x3": table,
        "ambiguous_count": sum(d["gold_state"] == "AMBIGUOUS" for d in documents),
        "collapsed_2x2": collapsed,
        "accuracy": {"value": _ratio(tp + tn, tp + fn + fp + tn), "denominator": tp + fn + fp + tn},
        "sensitivity": {"value": _ratio(tp, tp + fn), "denominator": tp + fn},
        "specificity": {"value": _ratio(tn, tn + fp), "denominator": tn + fp},
    }


def score_documents(gold_records: Sequence[Mapping], predictions: Mapping[str, Sequence[Mapping]]) -> dict:
    """SAP §§1–6: failure-inclusive document scoring and presence/secondary displays."""
    by_id = {}
    for gold in gold_records:
        _validate_gold(gold)
        doc_id = gold["document_id"]
        if doc_id in by_id:
            raise ValueError(f"Duplicate Gold document: {doc_id}")
        by_id[doc_id] = gold
    if set(predictions) - set(by_id):
        raise ValueError("Prediction claims an unknown Gold document")
    documents = []
    indicator_counts = Counter({name: 0 for name in _indicators(
        {"start_page": 0, "end_page": 0}, {"start_page": 0, "end_page": 0}
    )})
    start_errors, end_errors = [], []
    ambiguous_values = []
    special_not_located = 0
    alternative_only = 0
    for doc_id, gold in sorted(by_id.items()):
        rows = predictions.get(doc_id, ())
        status = classify_prediction(gold, rows)
        state = gold["presence_state"]
        pred_span = rows[0]["span"] if status == "VALID" else None
        score = inclusive_iou(pred_span, gold["primary_span"]) if state == "PRESENT" and status == "VALID" else (
            0.0 if state == "PRESENT" else None
        )
        documents.append({"document_id": doc_id, "gold_state": state, "prediction_status": status, "iou": score})
        if state == "PRESENT" and status == "VALID":
            indicator_counts.update(_indicators(pred_span, gold["primary_span"]))
            ps, pe = _endpoints(pred_span)
            gs, ge = _endpoints(gold["primary_span"])
            start_errors.append(ps - gs)
            end_errors.append(pe - ge)
            if (inclusive_iou(pred_span, gold["primary_span"]) == 0
                    and any(
                        alt.get("type") != "HINDI_COPY"
                        and inclusive_iou(pred_span, alt) > 0
                        for alt in gold["alternative_spans"]
                    )):
                alternative_only += 1
        if state == "AMBIGUOUS":
            if status == "VALID":
                ambiguous_values.append(max(inclusive_iou(pred_span, span) for span in gold["admissible_spans"]))
            elif status == "NOT_LOCATED" and gold["presence_reason_code"] == "PRESENCE_UNRESOLVABLE":
                ambiguous_values.append(1.0)
                special_not_located += 1
            else:
                ambiguous_values.append(0.0)
    present = [d for d in documents if d["gold_state"] == "PRESENT"]
    valid_count = len(start_errors)
    secondary = {
        name: {"count": indicator_counts[name], "denominator": len(present),
               "value": _ratio(indicator_counts[name], len(present))}
        for name in indicator_counts
    }
    secondary["signed_start_error"] = {"coverage": valid_count, "eligible": len(present), "quantiles": _quantiles(start_errors)}
    secondary["signed_end_error"] = {"coverage": valid_count, "eligible": len(present), "quantiles": _quantiles(end_errors)}
    secondary["alternative_overlap_without_primary"] = {"count": alternative_only, "eligible": len(present)}
    return {
        "documents": documents,
        "gold_counts": {state: sum(d["gold_state"] == state for d in documents) for state in STATES},
        "prediction_status_counts": {status: sum(d["prediction_status"] == status for d in documents) for status in STATUSES},
        "primary": {"value": _ratio(sum(d["iou"] for d in present), len(present)), "denominator": len(present)},
        "presence": presence_endpoint(documents),
        "secondary": secondary,
        "ambiguous_optimistic": {
            "value": _ratio(sum(ambiguous_values), len(ambiguous_values)),
            "denominator": len(ambiguous_values),
            "presence_unresolvable_not_located_count": special_not_located,
        },
    }


def census_summary(scored: Mapping, issuer_by_document: Mapping[str, str]) -> dict:
    """SAP §7: exact census and issuer-weighted/leave-one-out sensitivities."""
    documents = scored["documents"]
    if set(issuer_by_document) != {d["document_id"] for d in documents}:
        raise ValueError("Issuer map must cover exactly the scored documents")
    if any(not isinstance(name, str) or not name for name in issuer_by_document.values()):
        raise ValueError("Issuer names must be non-empty strings")
    by_issuer = {}
    for issuer in sorted(set(issuer_by_document.values())):
        present = [d["iou"] for d in documents
                   if issuer_by_document[d["document_id"]] == issuer and d["gold_state"] == "PRESENT"]
        by_issuer[issuer] = {"value": _ratio(sum(present), len(present)), "denominator": len(present)}
    eligible = [item["value"] for item in by_issuer.values() if item["denominator"]]
    left_out = {}
    for issuer in by_issuer:
        retained = [d["iou"] for d in documents
                    if d["gold_state"] == "PRESENT" and issuer_by_document[d["document_id"]] != issuer]
        left_out[issuer] = {"value": _ratio(sum(retained), len(retained)), "denominator": len(retained)}
    excluded = [issuer for issuer, item in by_issuer.items() if not item["denominator"]]
    return {
        "overall": scored["primary"], "per_issuer": by_issuer,
        "issuer_weighted": {"value": _ratio(sum(eligible), len(eligible)), "denominator": len(eligible)},
        "excluded_zero_present_issuers": {"count": len(excluded), "issuers": excluded},
        "leave_one_issuer_out": left_out,
    }


def raw_ab_agreement(raw_a: Sequence[Mapping], raw_b: Sequence[Mapping]) -> dict:
    """SAP §8: agreement on paired immutable raw records, before adjudication.

    ``shared_page_agreement`` is descriptive (decisions 8.7): for each shared-page answer,
    the PRESENT/PRESENT pairs in which both records carry it (schema v0.3), how many agree,
    and the percent agreement (0-100).
    """
    def index(records: Sequence[Mapping], role: str) -> dict:
        result = {}
        for record in records:
            _validate_gold(record)
            if record.get("record_type") != "RAW" or record.get("annotator_role") != role:
                raise ValueError("Agreement requires raw records with the requested role")
            doc_id = record["document_id"]
            if doc_id in result:
                raise ValueError("Duplicate raw record")
            result[doc_id] = record
        return result
    a, b = index(raw_a, "ANNOTATOR_A"), index(raw_b, "ANNOTATOR_B")
    if set(a) != set(b):
        raise ValueError("A/B document sets differ")
    table = {sa: {sb: 0 for sb in STATES} for sa in STATES}
    pp_iou = []
    pp_indicators = Counter({name: 0 for name in _indicators(
        {"start_page": 0, "end_page": 0}, {"start_page": 0, "end_page": 0}
    )})
    reason_matches = flag_matches = 0
    shared_pairs, shared_matches = Counter(), Counter()
    for doc_id in sorted(a):
        ar, br = a[doc_id], b[doc_id]
        if (ar["source_pdf_sha256"] != br["source_pdf_sha256"]
                or ar.get("protocol_version_hash") != br.get("protocol_version_hash")):
            raise ValueError("A/B source or protocol identity differs")
        sa, sb = ar["presence_state"], br["presence_state"]
        table[sa][sb] += 1
        reason_matches += ar["presence_reason_code"] == br["presence_reason_code"]
        flag_matches += set(ar["flags"]) == set(br["flags"])
        if sa == sb == "PRESENT":
            pp_iou.append(inclusive_iou(ar["primary_span"], br["primary_span"]))
            pp_indicators.update(_indicators(ar["primary_span"], br["primary_span"]))
            for key in SHARED_PAGE_KEYS:
                answer_a, answer_b = _shared_answer(ar, key), _shared_answer(br, key)
                if answer_a is not None and answer_b is not None:
                    shared_pairs[key] += 1
                    shared_matches[key] += answer_a == answer_b
    n = len(a)
    exact = sum(table[state][state] for state in STATES)
    observed = _ratio(exact, n)
    if n:
        expected = sum(
            sum(table[state].values()) * sum(table[row][state] for row in STATES) / (n * n)
            for state in STATES
        )
        kappa = (observed - expected) / (1 - expected) if expected != 1 else NOT_ESTIMABLE
        pabak = 2 * observed - 1
    else:
        kappa = pabak = NOT_ESTIMABLE
    pp_count = len(pp_iou)
    return {
        "state_table_3x3": table, "pair_count": n,
        "exact_state_agreement": {"count": exact, "denominator": n, "value": observed},
        "cohens_kappa": kappa, "pabak": pabak,
        "present_present": {
            "count": pp_count,
            "mean_iou": _ratio(sum(pp_iou), pp_count),
            **{name: {"count": pp_indicators[name], "denominator": pp_count,
                      "value": _ratio(pp_indicators[name], pp_count)} for name in pp_indicators},
        },
        "exact_reason_agreement": {"count": reason_matches, "denominator": n, "value": _ratio(reason_matches, n)},
        "exact_flag_agreement": {"count": flag_matches, "denominator": n, "value": _ratio(flag_matches, n)},
        "shared_page_agreement": {
            key: {
                "comparable_pairs": shared_pairs[key],
                "agreements": shared_matches[key],
                "percent_agreement": _ratio(100 * shared_matches[key], shared_pairs[key]),
            }
            for key in SHARED_PAGE_KEYS
        },
    }


def annotator_b_sensitivity(raw_b: Sequence[Mapping], predictions: Mapping[str, Sequence[Mapping]]) -> dict:
    """SAP §8: rescore prediction IoU over B's raw PRESENT primary spans."""
    for record in raw_b:
        _validate_gold(record)
        if record.get("record_type") != "RAW" or record.get("annotator_role") != "ANNOTATOR_B":
            raise ValueError("B-only sensitivity requires Annotator B raw records")
    present_b = [record for record in raw_b if record["presence_state"] == "PRESENT"]
    selected = {record["document_id"]: predictions.get(record["document_id"], ()) for record in present_b}
    return score_documents(present_b, selected)["primary"]
