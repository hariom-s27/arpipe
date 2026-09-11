import json
import pytest
from arpipe.models import Company, ReportRef, to_json
from arpipe import discover


def test_parse_nse_url_filename():
    cases = [
        ("https://nsearchives.nseindia.com/annual_reports/AR_27875_KRBL_2024_2025_A_34429015_29082025160935.pdf", ("KRBL", "2024_2025")),
        ("https://nsearchives.nseindia.com/annual_reports/AR_BHEL_2011_2012_18092012091256.zip", ("BHEL", "2011_2012")),
        ("https://nsearchives.nseindia.com/annual_reports/AR_1345_ONGC_2012_2013_02092013172104.zip", ("ONGC", "2012_2013")),
        ("https://nsearchives.nseindia.com/annual_reports/AR_COALINDIA_2011_2012_18092012081806.zip", ("COALINDIA", "2011_2012")),
        ("https://nsearchives.nseindia.com/annual_reports/AR_19_RELIANCE_2012_2013_08052013171218.zip", ("RELIANCE", "2012_2013")),
        ("https://nsearchives.nseindia.com/annual_reports/AR_JISLJALEQS_2010_2011_13092011044949.zip", ("JISLJALEQS", "2010_2011")),
        ("https://nsearchives.nseindia.com/annual_reports/AR_100_M&M_2021_2022_file.pdf", ("M&M", "2021_2022")),
        ("https://www.bseindia.com/bseplus/AnnualReport/500113/5001130311.pdf", (None, None)),
    ]
    for url, expected in cases:
        assert discover.parse_nse_url_filename(url) == expected


def test_report_ref_serialization():
    ref = ReportRef(
        company_id="INE001B01026",
        fy_end=2025,
        source="nse",
        url="https://nsearchives.nseindia.com/annual_reports/AR_27875_KRBL_2024_2025_A_34429015_29082025160935.pdf",
        declared_name="KRBL Limited",
        declared_fy="2024-2025",
        priority=10,
        filename_symbol="KRBL",
        filename_years="2024_2025",
    )
    s = to_json(ref)
    data = json.loads(s)
    assert data["filename_symbol"] == "KRBL"
    assert data["filename_years"] == "2024_2025"
    restored = ReportRef(**data)
    assert restored.filename_symbol == "KRBL"
    assert restored.filename_years == "2024_2025"


class MockNSEClient:
    def __init__(self, rows):
        self.rows = rows

    def get(self, url, **kwargs):
        class Resp:
            status_code = 200
            def json(self_inner):
                return {"data": self.rows}
        return Resp()


def test_discover_nse_valid_and_mismatch_filtering():
    co = Company(
        company_id="INE001B01026",
        canonical_name="KRBL Limited",
        nse_symbol="KRBL",
        aliases=["KRBL_OLD"],
    )

    rows = [
        # 1. Perfectly valid row
        {
            "companyName": "KRBL Limited",
            "fromYr": "2024",
            "toYr": "2025",
            "fileName": "https://nsearchives.nseindia.com/annual_reports/AR_27875_KRBL_2024_2025_A_1.pdf",
        },
        # 2. Valid with alias
        {
            "companyName": "KRBL Limited",
            "fromYr": "2023",
            "toYr": "2024",
            "fileName": "https://nsearchives.nseindia.com/annual_reports/AR_KRBL_OLD_2023_2024_2.pdf",
        },
        # 3. Mis-filed attachment: wrong company (symbol mismatch)
        {
            "companyName": "KRBL Limited",
            "fromYr": "2022",
            "toYr": "2023",
            "fileName": "https://nsearchives.nseindia.com/annual_reports/AR_INFY_2022_2023_3.pdf",
        },
        # 4. Mis-filed attachment: wrong year (declared 2021-2022, but file is 2018_2019)
        {
            "companyName": "KRBL Limited",
            "fromYr": "2021",
            "toYr": "2022",
            "fileName": "https://nsearchives.nseindia.com/annual_reports/AR_KRBL_2018_2019_4.pdf",
        },
    ]

    client = MockNSEClient(rows)
    refs = discover.discover_nse(co, client, rate=0)

    # Only rows 1 and 2 should pass; rows 3 and 4 must be dropped
    assert len(refs) == 2
    by_fy = {r.fy_end: r for r in refs}
    assert 2025 in by_fy
    assert by_fy[2025].filename_symbol == "KRBL"
    assert by_fy[2025].filename_years == "2024_2025"

    assert 2024 in by_fy
    assert by_fy[2024].filename_symbol == "KRBL_OLD"
    assert by_fy[2024].filename_years == "2023_2024"

    assert 2023 not in by_fy
    assert 2022 not in by_fy
