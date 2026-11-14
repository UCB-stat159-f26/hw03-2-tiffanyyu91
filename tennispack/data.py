
import json
import re
from functools import lru_cache
from io import StringIO

import pandas as pd
import requests


def _normalize_name(player_name):
    """Convert a player name to Tennis Abstract's URL format."""
    if not isinstance(player_name, str) or not player_name.strip():
        raise ValueError("Player name must be a nonempty string.")
    parts = player_name.split()
    if len(parts) > 1:
        return "".join(word.capitalize() for word in parts)
    return parts[0]


def _download_player_data(player_id):
    """Download a player's career match JavaScript."""
    url = f"https://www.tennisabstract.com/jsmatches/{player_id}Career.js"
    headers = {
        "User-Agent": "Mozilla/5.0",
        "Referer": "https://www.tennisabstract.com/"
    }
    try:
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()
    except requests.RequestException as error:
        raise ValueError(
            f"Could not retrieve matches for {player_id}: {error}"
        ) from error
    return response.text


def _parse_matches(raw_data):
    """Convert a JavaScript match array into a DataFrame."""
    match = re.search(
        r"var\s+morematchmx\s*=\s*(\[.*?\])\s*;",
        raw_data,
        re.DOTALL
    )
    if not match:
        raise ValueError("Could not find match records in JavaScript.")
    try:
        records = json.loads(match.group(1))
    except json.JSONDecodeError as error:
        raise ValueError("Could not parse match records.") from error
    return pd.DataFrame(records)


def _get_male_dob(player_id):
    """Read a birthday from a men's Tennis Abstract profile."""
    url = (
        "https://www.tennisabstract.com/cgi-bin/"
        f"player-classic.cgi?p={player_id}"
    )
    try:
        response = requests.get(url, timeout=30)
        response.raise_for_status()
    except requests.RequestException:
        return None

    match = re.search(
        r"var\s+dob\s*=\s*['\"]?(\d{8})",
        response.text
    )
    if not match:
        return None
    dob = match.group(1)
    return dob if pd.notna(
        pd.to_datetime(dob, format="%Y%m%d", errors="coerce")
    ) else None


@lru_cache(maxsize=1)
def _load_wta_players():
    """Download and cache the WTA player directory."""
    url = (
        "https://raw.githubusercontent.com/ivanxieau/"
        "WTA_TennisAbstract/master/wta_players.csv"
    )
    try:
        response = requests.get(url, timeout=30)
        response.raise_for_status()
    except requests.RequestException as error:
        raise ValueError(
            "Could not download the WTA player directory."
        ) from error

    return pd.read_csv(
        StringIO(response.text),
        usecols=["name_first", "name_last", "dob"],
        dtype={"dob": "string"}
    )


def _get_female_dob(player_id):
    """Look up a player's birthday in the WTA directory."""
    players = _load_wta_players()
    names = (
        players["name_first"].fillna("")
        + players["name_last"].fillna("")
    ).str.replace(r"\s+", "", regex=True).str.casefold()

    dates = players.loc[
        names == player_id.casefold(), "dob"
    ].dropna()

    if dates.empty:
        raise ValueError(f"Could not find birthday for {player_id}.")
    dob = str(dates.iloc[0])
    if pd.isna(pd.to_datetime(dob, format="%Y%m%d", errors="coerce")):
        raise ValueError(f"Invalid birthday for {player_id}.")
    return dob


def _get_player_dob(player_id):
    """Look up a player's birthday, checking WTA first."""
    try:
        return _get_female_dob(player_id)
    except ValueError as error:
        if "Could not find birthday" not in str(error):
            raise

    dob = _get_male_dob(player_id)
    if dob is None:
        raise ValueError(f"Could not find birthday for {player_id}.")
    return dob

def _prepare_matches(df):
    """Select and format the match columns."""
    cleaned = df[[0, 4, 11, 16]].copy()
    cleaned.columns = [
        "date", "result", "opponent", "raw_opponent_age"
    ]
    cleaned["date"] = pd.to_datetime(
        cleaned["date"], format="%Y%m%d", errors="coerce"
    )
    return cleaned


def _opponent_ages(cleaned):
    """Convert opponent birth dates or ages into years."""
    raw = cleaned["raw_opponent_age"].astype("string").str.strip()
    has_dob = raw.str.fullmatch(r"\d{8}").fillna(False)
    opponent_dob = pd.to_datetime(
        raw.where(has_dob), format="%Y%m%d", errors="coerce"
    )
    ages = pd.to_numeric(raw.where(~has_dob), errors="coerce")
    ages.loc[has_dob] = (
        cleaned.loc[has_dob, "date"] - opponent_dob.loc[has_dob]
    ).dt.days / 365.25
    return ages


def _clean_matches(df, player_dob):
    """Calculate ages and prepare match data for plotting."""
    cleaned = _prepare_matches(df)
    cleaned["opponent_age"] = _opponent_ages(cleaned)
    cleaned["player_age"] = (
        cleaned["date"] - pd.Timestamp(player_dob)
    ).dt.days / 365.25
    cleaned["age_difference"] = (
        cleaned["player_age"] - cleaned["opponent_age"]
    )
    cleaned = cleaned[cleaned["result"].isin(["W", "L"])]
    cleaned = cleaned.dropna(
        subset=["date", "player_age", "opponent_age"]
    )
    return cleaned.drop(
        columns="raw_opponent_age"
    ).reset_index(drop=True)
    
def get_player_data(player_name):
    """Download and clean a player's career match data for plotting."""
    player_id = _normalize_name(player_name)
    raw = _download_player_data(player_id)
    matches = _parse_matches(raw)

    if matches.empty or matches.shape[1] <= 16:
        raise ValueError(f"No usable match data for {player_name}.")

    dob = _get_player_dob(player_id)
    return _clean_matches(matches, dob)
