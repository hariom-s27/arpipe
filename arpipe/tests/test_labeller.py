import os
import tempfile
import pytest

from arpipe import labeller
from arpipe.models import Company


def test_era_classification():
    assert labeller.era_for_year(2010) == "2010-2013"
    assert labeller.era_for_year(2013) == "2010-2013"
    assert labeller.era_for_year(2014) == "2014-2018"
    assert labeller.era_for_year(2018) == "2014-2018"
    assert labeller.era_for_year(2019) == "2019-2025"
    assert labeller.era_for_year(2025) == "2019-2025"


def test_cap_band_classification():
    # Explicit company cap_band
    c1 = Company(company_id="C1", canonical_name="Co 1", cap_band="Large")
    assert labeller.cap_band_for_company(c1) == "large"

    # BSE-only fallback -> micro
    c2 = Company(company_id="C2", canonical_name="Co 2", exchange="bse")
    assert labeller.cap_band_for_company(c2) == "micro"

    # Dual listed Nifty symbol -> large
    c3 = Company(company_id="C3", canonical_name="Co 3", exchange="both", nse_symbol="RELIANCE")
    assert labeller.cap_band_for_company(c3) == "large"

    # Dual listed other symbol -> mid
    c4 = Company(company_id="C4", canonical_name="Co 4", exchange="both", nse_symbol="SOMEOTHER")
    assert labeller.cap_band_for_company(c4) == "mid"


def test_reason_codes():
    expected = {"OK", "WRONG_START", "WRONG_END", "BOTH", "NOT_FOUND", "NO_MDA_IN_DOC", "ORDER_SCRAMBLED"}
    assert set(labeller.REASON_CODES) == expected


def test_prompt_user_defaults():
    # 1. Matching proposed -> OK
    inputs = iter(["\n", "\n", "\n"])
    s, e, r = labeller.prompt_user_for_label(5, 10, input_fn=lambda _: next(inputs).strip())
    assert s == 5
    assert e == 10
    assert r == "OK"

    # 2. Start changed -> WRONG_START
    inputs = iter(["6\n", "\n", "\n"])
    s, e, r = labeller.prompt_user_for_label(5, 10, input_fn=lambda _: next(inputs).strip())
    assert s == 6
    assert e == 10
    assert r == "WRONG_START"

    # 3. End changed -> WRONG_END
    inputs = iter(["\n", "12\n", "\n"])
    s, e, r = labeller.prompt_user_for_label(5, 10, input_fn=lambda _: next(inputs).strip())
    assert s == 5
    assert e == 12
    assert r == "WRONG_END"

    # 4. Both changed -> BOTH
    inputs = iter(["6\n", "12\n", "\n"])
    s, e, r = labeller.prompt_user_for_label(5, 10, input_fn=lambda _: next(inputs).strip())
    assert s == 6
    assert e == 12
    assert r == "BOTH"

    # 5. None -> NO_MDA_IN_DOC
    inputs = iter(["none\n", "none\n", "\n"])
    s, e, r = labeller.prompt_user_for_label(None, None, input_fn=lambda _: next(inputs).strip())
    assert s is None
    assert e is None
    assert r == "NO_MDA_IN_DOC"


def test_sample_for_labelling():
    with tempfile.TemporaryDirectory() as td:
        out_csv = os.path.join(td, "to_label.csv")
        stores = []
        for s in ["arpipe/p11_store", "arpipe/live_store"]:
            if os.path.exists(s):
                stores.append(s)
        if not stores:
            pytest.skip("Stores not available for sampling test")

        res = labeller.sample_for_labelling(
            store_roots=stores,
            companies_path="arpipe/companies.csv",
            n_samples=50,
            out_csv=out_csv,
        )
        assert os.path.exists(out_csv)
        assert res["total_selected"] > 0
        assert len(res["cells"]) == 36
