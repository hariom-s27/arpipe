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
from collections import defaultdict
from dataclasses import asdict

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
        row = { (k or "").strip().upper(): (v or "").strip() for k, v in row.items() }
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
    """Classify equity line: 'ordinary' | 'dvr' | 'partly_paid' | 'other'.

    Signals for DVR (differential voting rights):
      - ISIN prefix IN9 (NSDL designation for DVR shares)
      - NSE symbol ending in 'DVR' or 'DVREQS'
      - NSE series 'E1' or 'DVR'
      - Name containing 'DVR' or 'DIFFERENTIAL VOTING RIGHTS'

    Signals for partly paid / rights entitlement:
      - NSE symbol containing '-RE' or ending in 'PP'
      - Name containing 'PARTLY PAID' or 'RIGHTS ENTITLEMENT'

    Signals for ordinary:
      - ISIN prefix INE (standard Indian equity)
      - NSE series EQ

    Signals for other:
      - ISIN prefix INF (mutual funds / ETFs) or any non-INE/IN9 prefix
    """
    isin_u = (isin or "").strip().upper()
    sym_u = (nse_symbol or "").strip().upper()
    ser_u = (series or "").strip().upper()
    name_u = (canonical_name or "").strip().upper()

    # DVR signals (highest precedence among specialized types)
    if isin_u.startswith("IN9"):
        return "dvr"
    if sym_u.endswith("DVR") or sym_u.endswith("DVREQS"):
        return "dvr"
    if ser_u in ("E1", "DVR"):
        return "dvr"
    if re.search(r"\b(DVR|DIFFERENTIAL\s+VOTING\s+RIGHTS)\b", name_u):
        return "dvr"

    # Partly paid / Rights Entitlement signals
    if "-RE" in sym_u or sym_u.endswith("-PP") or re.search(r"\b(PARTLY\s+PAID|PART\s+PAID|RIGHTS\s+ENTITLEMENT)\b", name_u):
        return "partly_paid"

    # Ordinary equity
    if isin_u.startswith("INE"):
        return "ordinary"

    # Other (e.g. INF, INC, IND, or unclassified)
    return "other"


def _primary_rank(c: Company) -> tuple:
    """Sorting key to choose the primary Company row when collapsing.

    Lower tuple values are preferred:
      1. series_type: ordinary (0) > dvr (1) > partly_paid (2) > other (3)
      2. isin prefix: INE (0) > IN9 (1) > INF (2) > other (3)
      3. has CIN: 0 if present else 1
      4. has NSE symbol: 0 if present else 1
      5. has BSE scrip: 0 if present else 1
      6. isin string (deterministic tie-breaker)
    """
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

    has_cin = 0 if c.cin else 1
    has_symbol = 0 if c.nse_symbol else 1
    has_scrip = 0 if c.bse_scrip else 1

    return (series_score, isin_score, has_cin, has_symbol, has_scrip, isin)


def collapse_universe(companies: list[Company]) -> tuple[list[Company], int]:
    """Collapse duplicate lines (e.g., ordinary vs DVR) into a single Company row.

    When several ISINs share a CIN or normalised company name, collapse them into
    ONE row. The primary row is chosen according to _primary_rank (preferring
    ordinary equity INE... over DVR IN9... over INF...).
    Secondary ISINs are recorded in `alternate_isins` on the primary row.

    Returns:
        (collapsed_companies, n_rows_removed)
    """
    if not companies:
        return [], 0

    # Ensure series_type is populated
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
        # 1. Match on CIN if present
        if c.cin:
            cin_clean = c.cin.strip().upper()
            if cin_clean in cin_index:
                union(i, cin_index[cin_clean])
            else:
                cin_index[cin_clean] = i

        # 2. Match on normalised company name
        norm_name = normalize_company_name(c.canonical_name)
        if norm_name:
            if norm_name in name_index:
                union(i, name_index[norm_name])
            else:
                name_index[norm_name] = i

        # 3. Match on ISIN / alternate_isins if already linked
        all_candidate_isins = [c.isin, c.company_id, *c.alternate_isins]
        for is_val in all_candidate_isins:
            if is_val:
                is_u = is_val.strip().upper()
                if is_u in isin_index:
                    union(i, isin_index[is_u])
                else:
                    isin_index[is_u] = i

    groups: dict[int, list[Company]] = defaultdict(list)
    for i, c in enumerate(companies):
        groups[find(i)].append(c)

    collapsed: list[Company] = []
    for group in groups.values():
        if len(group) == 1:
            collapsed.append(group[0])
            continue

        primary = min(group, key=_primary_rank)

        # Collect alternate ISINs (all ISINs across group except primary's isin/company_id)
        pri_isin = (primary.isin or primary.company_id or "").strip().upper()
        all_isins: set[str] = set()
        for member in group:
            if member.isin:
                all_isins.add(member.isin.strip().upper())
            if member.company_id:
                all_isins.add(member.company_id.strip().upper())
            for alt in member.alternate_isins:
                if alt:
                    all_isins.add(alt.strip().upper())
        alt_isins = sorted(alt for alt in all_isins if alt and alt != pri_isin)

        # Merge aliases
        all_aliases: set[str] = set()
        for member in group:
            all_aliases.update(member.aliases)
            if member.canonical_name and member.canonical_name != primary.canonical_name:
                all_aliases.add(member.canonical_name)
            if member.nse_symbol and member.nse_symbol != primary.nse_symbol:
                all_aliases.add(member.nse_symbol)
        merged_aliases = sorted(a for a in all_aliases if a and a != primary.canonical_name)

        # Fill missing fields on primary from secondary members
        cin = primary.cin or next((m.cin for m in group if m.cin), None)
        nse_symbol = primary.nse_symbol or next((m.nse_symbol for m in group if m.nse_symbol), None)
        bse_scrip = primary.bse_scrip or next((m.bse_scrip for m in group if m.bse_scrip), None)
        sector = primary.sector or next((m.sector for m in group if m.sector), None)
        cap_band = primary.cap_band or next((m.cap_band for m in group if m.cap_band), None)
        cap_band_current = (primary.cap_band_current
                            or next((m.cap_band_current for m in group if m.cap_band_current), None)
                            or cap_band)

        # Determine exchange on merged company:
        if (nse_symbol and bse_scrip) or any(m.exchange == "both" for m in group) or (
            any(m.exchange == "nse" for m in group) and any(m.exchange == "bse" for m in group)
        ):
            exchange = "both"
        elif nse_symbol or any(m.exchange == "nse" for m in group):
            exchange = "nse"
        else:
            exchange = "bse"

        merged = Company(
            company_id=primary.company_id,
            canonical_name=primary.canonical_name,
            cin=cin,
            isin=primary.isin,
            bse_scrip=bse_scrip,
            nse_symbol=nse_symbol,
            aliases=merged_aliases,
            sector=sector,
            cap_band=cap_band,
            status=primary.status,
            alternate_isins=alt_isins,
            series_type=primary.series_type,
            exchange=exchange,
            cap_band_current=cap_band_current,
        )
        collapsed.append(merged)

    collapsed.sort(key=lambda c: c.company_id)
    return collapsed, len(companies) - len(collapsed)


NSE_INDEX_URLS: dict[str, str] = {
    "large": "https://archives.nseindia.com/content/indices/ind_nifty100list.csv",
    "mid": "https://archives.nseindia.com/content/indices/ind_niftymidcap150list.csv",
    "small": "https://archives.nseindia.com/content/indices/ind_niftysmallcap250list.csv",
}


def fetch_cap_bands(client: Any = None) -> dict[str, str]:
    """Fetch official SEBI/AMFI market-cap categorisation from index constituents.

    Top 100: Large cap (Nifty 100)
    101-250: Mid cap (Nifty Midcap 150)
    251-500: Small cap (Nifty Smallcap 250)
    501+: Micro cap (default for remaining companies)
    """
    import io
    import httpx

    cl = client or httpx.Client(headers={"User-Agent": "Mozilla/5.0"}, timeout=15)
    cap_map: dict[str, str] = {}
    should_close = client is None
    try:
        for band, url in NSE_INDEX_URLS.items():
            try:
                r = cl.get(url)
                if r.status_code == 200:
                    reader = csv.DictReader(io.StringIO(r.text))
                    for row in reader:
                        isin = (row.get("ISIN Code") or row.get("ISIN") or "").strip().upper()
                        if isin:
                            cap_map[isin] = band
            except Exception as exc:
                print(f"Warning: Failed to fetch {band} cap band list from {url}: {exc}", file=sys.stderr)
    finally:
        if should_close:
            cl.close()
    return cap_map


def build_master(nse: dict[str, dict], bse: dict[str, dict],
                 symbol_chains: dict[str, list[str]],
                 cap_bands: dict[str, str] | None = None) -> list[Company]:
    cap_bands = cap_bands or {}
    isins = set(nse) | set(bse)
    companies: list[Company] = []
    for isin in sorted(isins):
        n, b = nse.get(isin, {}), bse.get(isin, {})
        name = n.get("name") or b.get("name") or ""
        sym = n.get("nse_symbol")
        series = n.get("series")
        aliases: list[str] = []
        if b.get("name") and b["name"] != name:
            aliases.append(b["name"])
        if b.get("aliases"):
            aliases.extend(b["aliases"])
        if sym and sym in symbol_chains:
            aliases.extend(symbol_chains[sym])
        st = detect_series_type(isin, sym, series, canonical_name=name)
        ex = "both" if (isin in nse and isin in bse) else ("nse" if isin in nse else "bse")
        band = cap_bands.get(isin, "micro") if cap_bands else None
        companies.append(Company(
            company_id=isin,
            canonical_name=name,
            isin=isin,
            nse_symbol=sym,
            bse_scrip=b.get("bse_scrip"),
            aliases=sorted(set(a for a in aliases if a)),
            sector=b.get("industry") or None,
            cap_band=band,
            status=b.get("status", "Active").lower(),
            series_type=st,
            exchange=ex,
            cap_band_current=band,
        ))
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
                row["series_type"] = detect_series_type(
                    row.get("isin"),
                    row.get("nse_symbol"),
                    canonical_name=row.get("canonical_name"),
                )
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
            clean_row = {k: v for k, v in row.items() if k in company_fields}
            out.append(Company(**clean_row))
    return out


def collapse_companies_file(in_path: str, out_path: str | None = None,
                            cap_bands: dict[str, str] | None = None) -> tuple[list[Company], int]:
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
