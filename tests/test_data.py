
import json

import pandas as pd
import pytest

from tennispack.data import (
    _normalize_name,
    _parse_matches,
    _clean_matches,
)


def sample_match(opponent_info):
    """Create a simulated tennis match record."""
    row = [""] * 17
    row[0] = "19951030"
    row[4] = "L"
    row[11] = "Anne Miller"
    row[16] = opponent_info
    return row


def test_normalize_name():
    assert _normalize_name("serena williams") == "SerenaWilliams"
    assert _normalize_name("Rafael Nadal") == "RafaelNadal"
    assert _normalize_name("SerenaWilliams") == "SerenaWilliams"


def test_invalid_name():
    with pytest.raises(ValueError):
        _normalize_name("")


def test_parse_matches():
    records = [sample_match("19770119")]
    raw = f"var morematchmx = {json.dumps(records)};"
    df = _parse_matches(raw)

    assert df.shape == (1, 17)
    assert df.iloc[0, 11] == "Anne Miller"


def test_female_match_cleaning():
    df = pd.DataFrame([sample_match("19770119")])
    cleaned = _clean_matches(df, "19810926")

    assert len(cleaned) == 1
    assert abs(cleaned.loc[0, "player_age"] - 14.09) < 0.02
    assert abs(cleaned.loc[0, "opponent_age"] - 18.78) < 0.02
    assert cleaned.loc[0, "result"] == "L"


def test_male_match_cleaning():
    row = sample_match("22.264202601")
    row[0] = "20010910"
    df = pd.DataFrame([row])
    cleaned = _clean_matches(df, "19860603")

    assert abs(cleaned.loc[0, "player_age"] - 15.27) < 0.02
    assert abs(cleaned.loc[0, "opponent_age"] - 22.26) < 0.02
    assert cleaned.loc[0, "age_difference"] < 0
