"""Select a balanced cohort of companies across all 4 market cap bands
(Large, Mid, Small, Micro) for stratified discovery and sampling.
"""
from __future__ import annotations

import csv
import os
import sys

from arpipe import universe
from arpipe.models import Company


def select_cohort(companies_path: str, out_path: str) -> list[Company]:
    companies = universe.from_csv(companies_path)
    by_band: dict[str, list[Company]] = {
        "large": [],
        "mid": [],
        "small": [],
        "micro": [],
    }

    for c in companies:
        band = getattr(c, "cap_band_current", None) or c.cap_band or "micro"
        band = band.strip().lower()
        if band in by_band:
            by_band[band].append(c)

    selected: list[Company] = []

    # 1. Large: 6 companies
    large_picked: list[Company] = []
    preferred_large = {"RELIANCE", "INFY", "TATASTEEL", "ITC", "NTPC", "SUNPHARMA", "TCS", "HDFCBANK"}
    for c in by_band["large"]:
        if c.nse_symbol in preferred_large and len(large_picked) < 6:
            large_picked.append(c)
    if len(large_picked) < 6:
        for c in by_band["large"]:
            if c not in large_picked and len(large_picked) < 6:
                large_picked.append(c)
    selected.extend(large_picked)

    # 2. Mid: 8 companies
    mid_picked: list[Company] = []
    preferred_mid = {"ASTRAL", "CRISIL", "VOLTAS", "FEDERALBNK", "TRENT", "TATACOMM", "MRF", "JUBLFOOD", "SJVN", "PAGEIND"}
    for c in by_band["mid"]:
        if c.nse_symbol in preferred_mid and len(mid_picked) < 8:
            mid_picked.append(c)
    if len(mid_picked) < 8:
        for c in by_band["mid"]:
            if c not in mid_picked and len(mid_picked) < 8:
                mid_picked.append(c)
    selected.extend(mid_picked)

    # 3. Small: 10 companies
    small_picked: list[Company] = []
    preferred_small = {"CENTURYPLY", "BLUESTARCO", "VIPIND", "CEATLTD", "BALRAMCHIN", "GREAVESCOT", "WELSPUNLIV", "ORIENTELEC", "PVRINOX", "STLTECH", "MGL", "IDBI"}
    for c in by_band["small"]:
        if c.nse_symbol in preferred_small and len(small_picked) < 10:
            small_picked.append(c)
    if len(small_picked) < 10:
        for c in by_band["small"]:
            if c not in small_picked and len(small_picked) < 10:
                small_picked.append(c)
    selected.extend(small_picked)

    # 4. Micro: 12 companies (including BSE-only to get scanned historical filings)
    micro_picked: list[Company] = []
    preferred_micro_isins = {
        "INE001B01026", # KRBL
        "INE003B01014", # Inter State Oil
        "INE001F01019", # Modern Steels
        "INE004C01028", # Gujarat Cotex
        "INE005E01013", # Ekansh Concepts
        "INE006C01015", # K.Z. Leasing
        "INE004E01016", # Span Divergent
        "INE003F01015", # Muller & Phipps
    }
    for c in by_band["micro"]:
        if c.isin in preferred_micro_isins and len(micro_picked) < 8:
            micro_picked.append(c)
    for c in by_band["micro"]:
        if c.exchange == "bse" and c not in micro_picked and len(micro_picked) < 12:
            micro_picked.append(c)
    if len(micro_picked) < 12:
        for c in by_band["micro"]:
            if c not in micro_picked and len(micro_picked) < 12:
                micro_picked.append(c)
    selected.extend(micro_picked)

    universe.to_csv(selected, out_path)
    print(f"Selected {len(selected)} companies into {out_path}:")
    print(f"  Large: {len(large_picked)}")
    print(f"  Mid:   {len(mid_picked)}")
    print(f"  Small: {len(small_picked)}")
    print(f"  Micro: {len(micro_picked)}")
    for c in selected:
        b = getattr(c, "cap_band_current", None) or c.cap_band
        print(f"    [{b:5}] {c.canonical_name:<35} | {c.exchange:<4} | NSE:{c.nse_symbol or '-':<12} | BSE:{c.bse_scrip or '-'}")
    return selected


if __name__ == "__main__":
    in_file = sys.argv[1] if len(sys.argv) > 1 else "companies.csv"
    out_file = sys.argv[2] if len(sys.argv) > 2 else "cohort_companies.csv"
    select_cohort(in_file, out_file)
