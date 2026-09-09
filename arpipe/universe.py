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


def parse_bse_master(rows: list[dict]) -> dict[str, dict]:
    """BSE ListofScripData JSON rows -> {isin: {...}}."""
    out: dict[str, dict] = {}
    for r in rows:
        isin = (r.get("ISIN_NUMBER") or r.get("ISIN") or "").strip()
        if not isin:
            continue
        out[isin] = {
            "bse_scrip": str(r.get("SCRIP_CD") or r.get("Scrip_Code") or "").strip(),
            "name": (r.get("Scrip_Name") or r.get("SCRIP_NAME") or "").strip(),
            "group": (r.get("GROUP") or "").strip(),
            "status": (r.get("Status") or "Active").strip(),
            "industry": (r.get("Industry") or "").strip(),
        }
    return out


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
        aliases: list[str] = []
        if b.get("name") and b["name"] != name:
            aliases.append(b["name"])
        if sym and sym in symbol_chains:
            aliases.extend(symbol_chains[sym])
        companies.append(Company(
            company_id=isin,
            canonical_name=name,
            isin=isin,
            nse_symbol=sym,
            bse_scrip=b.get("bse_scrip"),
            aliases=sorted(set(a for a in aliases if a)),
            sector=b.get("industry") or None,
            cap_band=cap_bands.get(isin),
            status=b.get("status", "Active").lower(),
        ))
    return companies


def to_csv(companies: list[Company], path: str) -> None:
    fields = list(asdict(companies[0]).keys()) if companies else []
    with open(path, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=fields)
        w.writeheader()
        for c in companies:
            d = asdict(c)
            d["aliases"] = "|".join(d["aliases"])
            w.writerow(d)


def from_csv(path: str) -> list[Company]:
    out = []
    with open(path, encoding="utf-8") as fh:
        for row in csv.DictReader(fh):
            row["aliases"] = [a for a in (row.get("aliases") or "").split("|") if a]
            out.append(Company(**row))
    return out
