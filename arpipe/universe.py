"""Build and maintain the company master.

The hard part of a 2010-2025 panel is not downloading PDFs, it is knowing
that BIRLA3M and 3MINDIA are the same issuer, that "Bajaj Finserv Lending"
became "Bajaj Finance", and that a symbol you scrape today did not exist in
2011. Keys, in descending order of stability:

  CIN    issued by MCA, survives name changes, changes only on
         re-incorporation or state transfer. Best long-run key, but not
         printed in exchange master files - it has to be mined from the
         documents themselves or from MCA data.
  ISIN   issued by NSDL/CDSL, survives name and symbol changes; changes on
         face-value splits in some corporate actions. Present in every
         exchange master file. This is what we use as company_id.
  scrip  BSE's numeric code. Stable, but BSE-only.
  symbol NSE's ticker. Changes - the exchange publishes the full history.

Free primary sources:
  NSE equity master   https://nsearchives.nseindia.com/content/equities/EQUITY_L.csv
  NSE symbol changes  https://nsearchives.nseindia.com/content/equities/symbolchange.csv
  BSE scrip master    https://api.bseindia.com/BseIndiaAPI/api/ListofScripData/w?...
                      (or the "List of Scrips" xlsx under bseindia.com/downloads)
  AMFI cap bands      https://www.amfiindia.com/research-information/other-data/
                      categorization-of-stocks  (large/mid/small, revised H1/H2)
"""
from __future__ import annotations

import csv
import io
import re
import sys
from collections import defaultdict
from dataclasses import asdict
from typing import Any

from .models import Company

NSE_EQUITY_L = "https://nsearchives.nseindia.com/content/equities/EQUITY_L.csv"
NSE_SYMBOL_CHANGE = "https://nsearchives.nseindia.com/content/equities/symbolchange.csv"
BSE_SCRIP_MASTER = ("https://api.bseindia.com/BseIndiaAPI/api/ListofScripData/w"
                    "?Group=&Scripcode=&industry=&segment=Equity&status=Active")


def parse_nse_equity_master(csv_text: str) -> dict[str, dict]:
    """EQUITY_L.csv -> {isin: {...}}. Columns: SYMBOL, NAME OF COMPANY,
    SERIES, DATE OF LISTING, PAID UP VALUE, MARKET LOT, ISIN NUMBER, FACE VALUE."""
    out: dict[str, dict] = {}
    for row in csv.DictReader(io.StringIO(csv_text)):
        row = {(k or "").strip().upper(): (v or "").strip() for k, v in row.items()}
        isin = row.get("ISIN NUMBER") or row.get("ISIN")
        if not isin:
            continue
        out[isin] = {
            "nse_symbol": row.get("SYMBOL"),
            "name": row.get("NAME OF COMPANY"),
            "listing_date": row.get("DATE OF LISTING"),
            "series": row.get("SERIES"),
        }
    return out


def parse_symbol_changes(csv_text: str) -> dict[str, list[str]]:
    """symbolchange.csv -> {current_symbol: [older symbols, oldest last]}.

    The file is a flat list of (name, old, new, date) so a symbol that
    changed twice needs chaining: UTIBANK -> AXISBANK is one hop; some
    issuers have three.
    """
    edges: dict[str, str] = {}
    names: dict[str, str] = {}
    rdr = csv.reader(io.StringIO(csv_text))
    rows = [r for r in rdr if len(r) >= 3]
    if rows and not re.match(r"^INE|^[A-Z0-9]+$", rows[0][1].strip()):
        rows = rows[1:]                      # drop header
    for r in rows:
        name, old, new = r[0].strip(), r[1].strip(), r[2].strip()
        if old and new:
            edges[old] = new
            names[new] = name
    chains: dict[str, list[str]] = defaultdict(list)
    for old in edges:
        cur, seen = old, {old}
        while cur in edges and edges[cur] not in seen:
            cur = edges[cur]
            seen.add(cur)
        chains[cur].append(old)
    return dict(chains)


def fetch_bse_master(client=None) -> list[dict]:
    """Fetch active equity listings from BSE ListofScripData endpoint."""
    import httpx
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
        "Accept": "application/json, text/plain, */*",
        "Referer": "https://www.bseindia.com/",
        "Origin": "https://www.bseindia.com",
    }
    if client:
        r = client.get(BSE_SCRIP_MASTER, headers=headers)
        r.raise_for_status()
        return r.json()
    with httpx.Client(headers=headers, timeout=45.0, follow_redirects=True) as cl:
        r = cl.get(BSE_SCRIP_MASTER)
        r.raise_for_status()
        return r.json()


def parse_bse_master(rows: list[dict]) -> dict[str, dict]:
    """BSE ListofScripData JSON rows -> {isin: {...}}."""
    out: dict[str, dict] = {}
    for r in rows:
        isin = (r.get("ISIN_NUMBER") or r.get("ISIN") or "").strip()
        if not isin:
            continue
        issuer = (r.get("Issuer_Name") or "").strip()
        scrip_name = (r.get("Scrip_Name") or r.get("SCRIP_NAME") or "").strip()
        name = issuer or scrip_name
        scrip_id = (r.get("scrip_id") or "").strip()
        aliases = []
        if issuer and scrip_name and issuer != scrip_name:
            aliases.append(scrip_name)
        if scrip_id:
            aliases.append(scrip_id)
        out[isin] = {
            "bse_scrip": str(r.get("SCRIP_CD") or r.get("Scrip_Code") or "").strip(),
            "name": name,
            "group": (r.get("GROUP") or "").strip(),
            "status": (r.get("Status") or "Active").strip(),
            "industry": (r.get("Industry") or r.get("INDUSTRY") or "").strip() or None,
            "aliases": aliases,
        }
    return out


import dataclasses as dc

_LEGAL_SUFFIXES = re.compile(
    r"\b(LIMITED|LTD|PVT|PRIVATE|PUBLIC|PLC|CORP|CORPORATION|CO|COMPANY)\b\.?",
    re.I,
)
_DVR_SUFFIXES = re.compile(
    r"\b(DIFFERENTIAL\s+VOTING\s+RIGHTS|DVR)\b",
    re.I,
)


def normalize_company_name(name: str | None) -> str:
    """Normalise company name for duplicate detection.

    Strips legal suffixes (Limited, Pvt, etc.), DVR terms, punctuation,
    normalises '&' to 'AND', and collapses whitespace.
    """
    if not name:
        return ""
    s = name.upper()
    s = s.replace("&", " AND ")
    s = re.sub(r"[^A-Z0-9\s]", " ", s)
    s = _DVR_SUFFIXES.sub(" ", s)
    s = _LEGAL_SUFFIXES.sub(" ", s)
    return re.sub(r"\s+", " ", s).strip()


def detect_series_type(
    isin: str | None = None,
    nse_symbol: str | None = None,
    series: str | None = None,
    canonical_name: str | None = None,
) -> str:
    """Classify equity line: 'ordinary' | 'dvr' | 'partly_paid' | 'other'."""
    isin_u = (isin or "").strip().upper()
    sym_u = (nse_symbol or "").strip().upper()
    ser_u = (series or "").strip().upper()
    name_u = (canonical_name or "").strip().upper()
    if isin_u.startswith("IN9") or sym_u.endswith("DVR") or sym_u.endswith("DVREQS"):
        return "dvr"
    if ser_u in ("E1", "DVR") or re.search(r"\b(DVR|DIFFERENTIAL\s+VOTING\s+RIGHTS)\b", name_u):
        return "dvr"
    if "-RE" in sym_u or sym_u.endswith("-PP") or re.search(r"\b(PARTLY\s+PAID|PART\s+PAID|RIGHTS\s+ENTITLEMENT)\b", name_u):
        return "partly_paid"
    if isin_u.startswith("INE"):
        return "ordinary"
    return "other"


def _primary_rank(c: Company) -> tuple:
    st = c.series_type or detect_series_type(c.isin, c.nse_symbol, canonical_name=c.canonical_name)
    isin = (c.isin or c.company_id or "").strip().upper()
    series_score = {"ordinary": 0, "dvr": 1, "partly_paid": 2, "other": 3}.get(st, 3)
    if isin.startswith("INE"):
        isin_score = 0
    elif isin.startswith("IN9"):
        isin_score = 1
    elif isin.startswith("INF"):
        isin_score = 2
    else:
        isin_score = 3
    return (series_score, isin_score, 0 if c.cin else 1, 0 if c.nse_symbol else 1, 0 if c.bse_scrip else 1, isin)


def collapse_universe(companies: list[Company]) -> tuple[list[Company], int]:
    """Collapse duplicate company rows and return rows removed."""
    if not companies:
        return [], 0
    for c in companies:
        if not c.series_type:
            c.series_type = detect_series_type(c.isin, c.nse_symbol, canonical_name=c.canonical_name)
    n = len(companies)
    parent = list(range(n))

    def find(i: int) -> int:
        path = []
        while parent[i] != i:
            path.append(i)
            i = parent[i]
        for node in path:
            parent[node] = i
        return i

    def union(i: int, j: int) -> None:
        ri, rj = find(i), find(j)
        if ri != rj:
            parent[ri] = rj

    cin_index: dict[str, int] = {}
    name_index: dict[str, int] = {}
    isin_index: dict[str, int] = {}
    for i, c in enumerate(companies):
        if c.cin:
            key = c.cin.strip().upper()
            if key in cin_index:
                union(i, cin_index[key])
            else:
                cin_index[key] = i
        norm_name = normalize_company_name(c.canonical_name)
        if norm_name:
            if norm_name in name_index:
                union(i, name_index[norm_name])
            else:
                name_index[norm_name] = i
        for is_val in [c.isin, c.company_id, *c.alternate_isins]:
            if is_val:
                key = is_val.strip().upper()
                if key in isin_index:
                    union(i, isin_index[key])
                else:
                    isin_index[key] = i

    groups: dict[int, list[Company]] = defaultdict(list)
    for i, c in enumerate(companies):
        groups[find(i)].append(c)
    collapsed: list[Company] = []
    for group in groups.values():
        if len(group) == 1:
            collapsed.append(group[0])
            continue
        primary = min(group, key=_primary_rank)
        pri_isin = (primary.isin or primary.company_id or "").strip().upper()
        all_isins: set[str] = set()
        for member in group:
            all_isins.update(x.strip().upper() for x in [member.isin, member.company_id, *member.alternate_isins] if x)
        aliases: set[str] = set()
        for member in group:
            aliases.update(member.aliases)
            if member.canonical_name and member.canonical_name != primary.canonical_name:
                aliases.add(member.canonical_name)
            if member.nse_symbol and member.nse_symbol != primary.nse_symbol:
                aliases.add(member.nse_symbol)
        cin = primary.cin or next((m.cin for m in group if m.cin), None)
        nse_symbol = primary.nse_symbol or next((m.nse_symbol for m in group if m.nse_symbol), None)
        bse_scrip = primary.bse_scrip or next((m.bse_scrip for m in group if m.bse_scrip), None)
        sector = primary.sector or next((m.sector for m in group if m.sector), None)
        cap_band = primary.cap_band or next((m.cap_band for m in group if m.cap_band), None)
        cap_band_current = primary.cap_band_current or next((m.cap_band_current for m in group if m.cap_band_current), None) or cap_band
        exchange = "both" if (nse_symbol and bse_scrip) or any(m.exchange == "both" for m in group) else ("nse" if nse_symbol or any(m.exchange == "nse" for m in group) else "bse")
        collapsed.append(Company(company_id=primary.company_id, canonical_name=primary.canonical_name, cin=cin, isin=primary.isin, bse_scrip=bse_scrip, nse_symbol=nse_symbol, aliases=sorted(a for a in aliases if a and a != primary.canonical_name), sector=sector, cap_band=cap_band, status=primary.status, alternate_isins=sorted(x for x in all_isins if x and x != pri_isin), series_type=primary.series_type, exchange=exchange, cap_band_current=cap_band_current))
    collapsed.sort(key=lambda c: c.company_id)
    return collapsed, len(companies) - len(collapsed)


NSE_INDEX_URLS: dict[str, str] = {
    "large": "https://archives.nseindia.com/content/indices/ind_nifty100list.csv",
    "mid": "https://archives.nseindia.com/content/indices/ind_niftymidcap150list.csv",
    "small": "https://archives.nseindia.com/content/indices/ind_niftysmallcap250list.csv",
}


def fetch_cap_bands(client: Any = None) -> dict[str, str]:
    """Fetch official SEBI/AMFI market-cap categorisation from index constituents."""
    import httpx
    cl = client or httpx.Client(headers={"User-Agent": "Mozilla/5.0"}, timeout=15)
    cap_map: dict[str, str] = {}
    should_close = client is None
    try:
        for band, url in NSE_INDEX_URLS.items():
            try:
                r = cl.get(url)
                if r.status_code == 200:
                    for row in csv.DictReader(io.StringIO(r.text)):
                        isin = (row.get("ISIN Code") or row.get("ISIN") or "").strip().upper()
                        if isin:
                            cap_map[isin] = band
            except Exception as exc:
                print(f"Warning: Failed to fetch {band} cap band list from {url}: {exc}", file=sys.stderr)
    finally:
        if should_close:
            cl.close()
    return cap_map


def build_master(nse: dict[str, dict], bse: dict[str, dict], symbol_chains: dict[str, list[str]], cap_bands: dict[str, str] | None = None) -> list[Company]:
    cap_bands = cap_bands or {}
    isins = set(nse) | set(bse)
    companies: list[Company] = []
    for isin in sorted(isins):
        n, b = nse.get(isin, {}), bse.get(isin, {})
        name = n.get("name") or b.get("name") or ""
        sym = n.get("nse_symbol")
        aliases: list[str] = []
        if b.get("name") and b["name"] != name:
            aliases.append(b["name"])
        aliases.extend(b.get("aliases") or [])
        if sym and sym in symbol_chains:
            aliases.extend(symbol_chains[sym])
        band = cap_bands.get(isin, "micro") if cap_bands else None
        companies.append(Company(company_id=isin, canonical_name=name, isin=isin, nse_symbol=sym, bse_scrip=b.get("bse_scrip"), aliases=sorted(set(a for a in aliases if a)), sector=b.get("industry") or None, cap_band=band, status=b.get("status", "Active").lower(), series_type=detect_series_type(isin, sym, n.get("series"), canonical_name=name), exchange="both" if isin in nse and isin in bse else ("nse" if isin in nse else "bse"), cap_band_current=band))
    collapsed, _ = collapse_universe(companies)
    return collapsed


def to_csv(companies: list[Company], path: str) -> None:
    fields = list(asdict(companies[0]).keys()) if companies else []
    with open(path, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=fields)
        w.writeheader()
        for c in companies:
            d = asdict(c)
            d["aliases"] = "|".join(d["aliases"])
            d["alternate_isins"] = "|".join(d.get("alternate_isins") or [])
            w.writerow(d)


def from_csv(path: str) -> list[Company]:
    out = []
    company_fields = {f.name for f in dc.fields(Company)}
    with open(path, encoding="utf-8") as fh:
        for row in csv.DictReader(fh):
            row["aliases"] = [a for a in (row.get("aliases") or "").split("|") if a]
            row["alternate_isins"] = [a for a in (row.get("alternate_isins") or "").split("|") if a]
            if not row.get("series_type"):
                row["series_type"] = detect_series_type(row.get("isin"), row.get("nse_symbol"), canonical_name=row.get("canonical_name"))
            if not row.get("exchange"):
                has_nse = bool(row.get("nse_symbol"))
                has_bse = bool(row.get("bse_scrip"))
                row["exchange"] = "both" if (has_nse and has_bse) else ("nse" if has_nse else "bse")
            if not row.get("cap_band_current") and row.get("cap_band"):
                row["cap_band_current"] = row.get("cap_band")
            if not row.get("cap_band") and row.get("cap_band_current"):
                row["cap_band"] = row.get("cap_band_current")
            for k in ("cin", "isin", "bse_scrip", "nse_symbol", "sector", "cap_band", "cap_band_current"):
                if row.get(k) == "":
                    row[k] = None
            out.append(Company(**{k: v for k, v in row.items() if k in company_fields}))
    return out


def collapse_companies_file(in_path: str, out_path: str | None = None, cap_bands: dict[str, str] | None = None) -> tuple[list[Company], int]:
    out_path = out_path or in_path
    companies = from_csv(in_path)
    if cap_bands:
        for c in companies:
            if not c.cap_band:
                c.cap_band = cap_bands.get(c.isin or "", "micro")
            if not c.cap_band_current:
                c.cap_band_current = c.cap_band
    collapsed, removed = collapse_universe(companies)
    to_csv(collapsed, out_path)
    return collapsed, removed
