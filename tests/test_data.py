
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


def test_get_player_data_female(monkeypatch):
    """Test the full data function without downloading data."""
    import tennispack.data as data

    row = sample_match("19770119")
    raw = f"var morematchmx = {json.dumps([row])};"

    def fake_download(player_id):
        assert player_id == "SerenaWilliams"
        return raw

    monkeypatch.setattr(data, "_download_player_data", fake_download)
    monkeypatch.setattr(data, "_get_player_dob", lambda name: "19810926")

    result = data.get_player_data("serena williams")

    assert len(result) == 1
    assert abs(result.loc[0, "player_age"] - 14.09) < 0.02
    assert abs(result.loc[0, "opponent_age"] - 18.78) < 0.02
    assert result.loc[0, "result"] == "L"


def test_get_player_data_male(monkeypatch):
    """Test male player data without downloading data."""
    import tennispack.data as data

    row = sample_match("22.264202601")
    row[0] = "20010910"
    raw = f"var morematchmx = {json.dumps([row])};"

    monkeypatch.setattr(data, "_download_player_data", lambda name: raw)
    monkeypatch.setattr(data, "_get_player_dob", lambda name: "19860603")

    result = data.get_player_data("Rafael Nadal")

    assert len(result) == 1
    assert abs(result.loc[0, "player_age"] - 15.27) < 0.02
    assert abs(result.loc[0, "opponent_age"] - 22.26) < 0.02


def test_unknown_player(monkeypatch):
    """Check that unavailable players produce meaningful errors."""
    import tennispack.data as data

    def fake_download(player_id):
        raise ValueError(f"Could not retrieve matches for {player_id}")

    monkeypatch.setattr(data, "_download_player_data", fake_download)

    with pytest.raises(ValueError, match="Could not retrieve matches"):
        data.get_player_data("Gaston Sanchez")


def test_empty_match_data(monkeypatch):
    """Check that empty match records are rejected."""
    import tennispack.data as data

    monkeypatch.setattr(
        data, "_download_player_data",
        lambda name: "var morematchmx = [];"
    )

    with pytest.raises(ValueError, match="No usable match data"):
        data.get_player_data("Serena Williams")


def test_plot_player_matches():
    """Check that the plotting function generates the expected plot."""
    import matplotlib.pyplot as plt
    from tennispack import plot_player_matches

    df = pd.DataFrame({
        "player_age": [14.1, 15.5],
        "age_difference": [-4.7, 2.0],
        "result": ["L", "W"]
    })

    ax = plot_player_matches(df)

    assert ax.get_xlabel() == "Player Age"
    assert ax.get_ylabel() == "Player Age - Opponent Age"

    labels = [text.get_text() for text in ax.get_legend().get_texts()]
    assert set(labels) == {"Win", "Loss"}

    plt.close(ax.figure)
