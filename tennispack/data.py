
import json
import re

import pandas as pd
import requests


# Player information
# Additional players can be added here.
PLAYERS = {
    "serenawilliams": ("SerenaWilliams", "1981-09-26"),
    "rafaelnadal": ("RafaelNadal", "1986-06-03"),
}


def _normalize_name(player_name):
    """Normalize capitalization and spacing."""
    if not isinstance(player_name, str):
        raise ValueError("Player name must be a string.")
    return re.sub(r"\s+", "", player_name).lower()


def _download_player_data(player_id):
    """Download career match data from Tennis Abstract."""
    url = (
        "https://www.tennisabstract.com/jsmatches/"
        f"{player_id}Career.js"
    )
    headers = {
        "User-Agent": "Mozilla/5.0",
        "Referer": "https://www.tennisabstract.com/"
    }
    try:
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()
    except requests.RequestException as error:
        raise ValueError(
            f"Could not retrieve data for {player_id}: {error}"
        ) from error
    return response.text


def _parse_matches(raw_data):
    """Convert Tennis Abstract JavaScript into a DataFrame."""
    match = re.search(
        r"var\s+morematchmx\s*=\s*(\[.*?\]);",
        raw_data,
        re.DOTALL
    )

    if match is None:
        raise ValueError("Could not find career match data.")

    try:
        matches = json.loads(match.group(1))
    except json.JSONDecodeError as error:
        raise ValueError("Invalid match data format.") from error

    return pd.DataFrame(matches)


def _calculate_age(dates, birth_date):
    """Calculate age in years from dates."""
    return (dates - birth_date).dt.days / 365.25


def _clean_female_matches(df):
    """Process matches containing opponent birth dates."""
    cleaned = df[[0, 4, 11, 16]].copy()
    cleaned.columns = [
        "date", "result", "opponent", "opponent_dob"
    ]
    cleaned["opponent_dob"] = pd.to_datetime(
        cleaned["opponent_dob"],
        format="%Y%m%d",
        errors="coerce"
    )
    cleaned["opponent_age"] = _calculate_age(
        cleaned["date"], cleaned["opponent_dob"]
    )
    return cleaned.drop(columns="opponent_dob")


def _clean_male_matches(df):
    """Process matches containing opponent ages."""
    cleaned = df[[0, 4, 11, 16]].copy()
    cleaned.columns = [
        "date", "result", "opponent", "opponent_age"
    ]
    cleaned["opponent_age"] = pd.to_numeric(
        cleaned["opponent_age"], errors="coerce"
    )
    return cleaned


def _clean_matches(df, player_dob, female):
    """Produce a DataFrame ready for plotting."""
    df = df.copy()
    df[0] = pd.to_datetime(
        df[0], format="%Y%m%d", errors="coerce"
    )
    if female:
        cleaned = _clean_female_matches(df)
    else:
        cleaned = _clean_male_matches(df)
    cleaned["player_age"] = _calculate_age(
        cleaned["date"], pd.Timestamp(player_dob)
    )
    cleaned["age_difference"] = (
        cleaned["player_age"] - cleaned["opponent_age"]
    )
    return cleaned.dropna(
        subset=["player_age", "opponent_age"]
    ).reset_index(drop=True)


def get_player_data(player_name):
    """Retrieve and clean a tennis player's career matches."""
    name = _normalize_name(player_name)

    if name not in PLAYERS:
        raise ValueError(
            f"Player '{player_name}' is not supported."
        )

    player_id, player_dob = PLAYERS[name]
    raw_data = _download_player_data(player_id)
    df = _parse_matches(raw_data)

    if df.empty or df.shape[1] <= 16:
        raise ValueError("No valid career match data found.")

    female = player_id == "SerenaWilliams"
    return _clean_matches(df, player_dob, female)
