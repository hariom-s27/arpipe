"""Source adapters: turn a company into a list of candidate report URLs.

Four sources, used together because none is complete:

  NSE   /api/annual-reports?index=equities&symbol=SYM
        Cleanest source. Returns one row per FY with fromYr/toYr and a direct
        link on nsearchives.nseindia.com. Coverage starts around FY2009-10
        and is good for anything that has been NSE-listed. Older rows are
        .zip, newer rows are .pdf. Requires a browser-like session: hit
        www.nseindia.com first to get the cookies, then reuse them.

  BSE   api.bseindia.com/BseIndiaAPI/api/AnnualReport_New/w?scripcode=NNNNNN
        The only source for BSE-only issuers, which is most of the small- and
        micro-cap tail (BSE has ~5,900 listings vs NSE's ~2,800). Requires
        Referer/Origin headers or it answers 403. Files sit under
        /bseplus/AnnualReport/<scrip>/... for older years and
        /xml-data/corpfiling/AttachHis/<uuid>.pdf for recent ones.

  screener.in/company/<SYMBOL>/  A convenient union of the two above: the
        Documents section lists annual reports per year with links pointing
        at whichever exchange holds them. Excellent as a reconciliation
        source; scrape politely and cache.

  IR site  The company's own investor-relations page. The only route to
        pre-2010 reports and to the occasional year both exchanges lost.
        Needs a per-company recipe, so keep it for a curated tail.

Discovery writes a manifest of ReportRef rows; nothing is downloaded here.
"""
from __future__ import annotations

import json
import re
import time
from dataclasses import replace

import httpx

from .models import Company, ReportRef

NSE_HOME = "https://www.nseindia.com"
NSE_AR = NSE_HOME + "/api/annual-reports?index=equities&symbol={sym}"
BSE_AR = ("https://api.bseindia.com/BseIndiaAPI/api/AnnualReport_New/w"
          "?scripcode={scrip}")
SCREENER_CO = "https://www.screener.in/company/{sym}/"

UA = ("Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) "
      "Chrome/126.0 Safari/537.36")

NSE_HEADERS = {
    "User-Agent": UA,
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "en-US,en;q=0.9",
    "Referer": NSE_HOME + "/companies-listing/corporate-filings-annual-reports",
}
BSE_HEADERS = {
    "User-Agent": UA,
    "Accept": "application/json, text/plain, */*",
    "Referer": "https://www.bseindia.com/",
    "Origin": "https://www.bseindia.com",
}


def nse_session(timeout: float = 20.0) -> httpx.Client:
    """NSE hands out the cookies only after a normal page load."""
    cl = httpx.Client(headers=NSE_HEADERS, timeout=timeout, follow_redirects=True)
    cl.get(NSE_HOME)
    cl.get(NSE_HOME + "/companies-listing/corporate-filings-annual-reports")
    return cl


def _fy_end_from_pair(from_yr: str | int, to_yr: str | int) -> int | None:
    try:
        a, b = int(from_yr), int(to_yr)
    except (TypeError, ValueError):
        return None
    if b - a == 1:
        return b
    if a == b:                      # a few rows report a single year
        return a
    return None


def discover_nse(company: Company, client: httpx.Client) -> list[ReportRef]:
    if not company.nse_symbol:
        return []
    refs: list[ReportRef] = []
    symbols = [company.nse_symbol, *[a for a in company.aliases if a.isupper()
                                     and " " not in a]]
    seen_fy: set[int] = set()
    for sym in symbols:
        try:
            r = client.get(NSE_AR.format(sym=sym))
            if r.status_code != 200:
                continue
            rows = r.json().get("data", r.json() if isinstance(r.json(), list) else [])
        except Exception:
            continue
        for row in rows:
            fy = _fy_end_from_pair(row.get("fromYr"), row.get("toYr"))
            url = row.get("fileName") or row.get("filename")
            if not fy or not url or fy in seen_fy:
                continue
            seen_fy.add(fy)
            refs.append(ReportRef(
                company_id=company.company_id, fy_end=fy, source="nse",
                url=url.strip(),
                declared_name=row.get("companyName"),
                declared_fy=f"{row.get('fromYr')}-{row.get('toYr')}",
                priority=10))
        time.sleep(0.4)
    return refs


def discover_bse(company: Company, client: httpx.Client) -> list[ReportRef]:
    if not company.bse_scrip:
        return []
    try:
        r = client.get(BSE_AR.format(scrip=company.bse_scrip), headers=BSE_HEADERS)
        if r.status_code != 200:
            return []
        payload = r.json()
    except Exception:
        return []
    rows = payload if isinstance(payload, list) else payload.get("Table", []) or []
    refs: list[ReportRef] = []
    for row in rows:
        yr = str(row.get("Year") or row.get("year") or "").strip()
        m = re.search(r"(20\d{2})\s*[-–]\s*(\d{2,4})", yr) or re.search(r"(20\d{2})", yr)
        if not m:
            continue
        fy = (_fy_end_from_pair(m.group(1), m.group(2)) if m.lastindex == 2
              else int(m.group(1)))
        url = (row.get("PDFFLAG") or row.get("Pdf_Link") or row.get("attachmentname")
               or row.get("PDFDownload") or "")
        if not url:
            continue
        if not url.startswith("http"):
            url = f"https://www.bseindia.com/bseplus/AnnualReport/{company.bse_scrip}/{url}"
        refs.append(ReportRef(company_id=company.company_id, fy_end=int(fy),
                              source="bse", url=url, declared_fy=yr, priority=20))
    return refs


SCREENER_LINK_RE = re.compile(
    r'href="(?P<url>[^"]*(?:annual_reports|AnnualReport|AnnPdfOpen|AttachHis)[^"]*)"'
    r'[^>]*>\s*(?P<label>[^<]{0,80})', re.I)


def discover_screener(company: Company, client: httpx.Client) -> list[ReportRef]:
    if not company.nse_symbol:
        return []
    try:
        r = client.get(SCREENER_CO.format(sym=company.nse_symbol),
                       headers={"User-Agent": UA})
        if r.status_code != 200:
            return []
        html = r.text
    except Exception:
        return []
    refs: list[ReportRef] = []
    for m in SCREENER_LINK_RE.finditer(html):
        url, label = m.group("url"), m.group("label")
        yr = re.search(r"(20\d{2})", label) or re.search(r"_(20\d{2})_(20\d{2})_", url)
        if not yr:
            continue
        fy = int(yr.group(yr.lastindex or 1))
        refs.append(ReportRef(company_id=company.company_id, fy_end=fy,
                              source="screener", url=url, declared_fy=label.strip(),
                              priority=30))
    return refs


def reconcile(refs: list[ReportRef], years: range) -> dict[int, list[ReportRef]]:
    """Group by FY, best source first, so the fetcher can fail over."""
    by_year: dict[int, list[ReportRef]] = {}
    for r in refs:
        if r.fy_end in years:
            by_year.setdefault(r.fy_end, []).append(r)
    for y in by_year:
        by_year[y].sort(key=lambda r: (r.priority, r.url))
    return by_year


def coverage_report(by_year: dict[int, list[ReportRef]],
                    years: range) -> dict[str, object]:
    have = sorted(y for y in years if by_year.get(y))
    missing = [y for y in years if y not in have]
    return {"have": have, "missing": missing,
            "coverage": round(len(have) / max(1, len(list(years))), 3)}
