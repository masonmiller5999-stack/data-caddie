"""ESPN API client and data scraping for PGA Tour data."""

import json
import os
import time
from datetime import datetime, timedelta

import requests

from config import (
    ESPN_SCOREBOARD,
    ESPN_LEADERBOARD,
    CACHE_DIR,
    CACHE_EXPIRY_HOURS,
    MAJOR_PURSES,
    SEASON_YEAR,
)


def _cache_path(key):
    os.makedirs(CACHE_DIR, exist_ok=True)
    safe_key = key.replace("/", "_").replace("?", "_").replace("&", "_")
    return os.path.join(CACHE_DIR, f"{safe_key}.json")


def _get_cached(key):
    path = _cache_path(key)
    if not os.path.exists(path):
        return None
    try:
        with open(path, "r") as f:
            cached = json.load(f)
        ts = datetime.fromisoformat(cached["timestamp"])
        if datetime.now() - ts > timedelta(hours=CACHE_EXPIRY_HOURS):
            return None
        return cached["data"]
    except (json.JSONDecodeError, KeyError):
        return None


def _set_cache(key, data):
    path = _cache_path(key)
    with open(path, "w") as f:
        json.dump({"timestamp": datetime.now().isoformat(), "data": data}, f)


def _fetch_json(url, cache_key=None):
    if cache_key:
        cached = _get_cached(cache_key)
        if cached is not None:
            return cached

    resp = requests.get(url, timeout=15)
    resp.raise_for_status()
    data = resp.json()

    if cache_key:
        _set_cache(cache_key, data)
    return data


# -----------------------------------------------------------
# Schedule
# -----------------------------------------------------------

def get_schedule(year=SEASON_YEAR):
    """Get full PGA Tour schedule for a season.

    Returns list of dicts: {id, name, start_date, end_date}
    """
    cache_key = f"schedule_{year}"
    url = ESPN_SCOREBOARD if year == SEASON_YEAR else f"{ESPN_SCOREBOARD}?dates={year}"
    data = _fetch_json(url, cache_key)

    leagues = data.get("leagues", [])
    if not leagues:
        return []

    calendar = leagues[0].get("calendar", [])
    tournaments = []
    for entry in calendar:
        tournaments.append({
            "id": entry["id"],
            "name": entry["label"],
            "start_date": entry["startDate"][:10],
            "end_date": entry["endDate"][:10],
        })
    return tournaments


# -----------------------------------------------------------
# Tournament Details (purse, field, results)
# -----------------------------------------------------------

def get_tournament_details(event_id):
    """Get tournament details: purse, field, results.

    Returns dict with keys: name, purse, major, status, field
    field is a list of {player_id, player_name, position, earnings}
    """
    cache_key = f"event_{event_id}"
    url = f"{ESPN_LEADERBOARD}?event={event_id}"

    try:
        data = _fetch_json(url, cache_key)
    except requests.HTTPError:
        return None

    events = data.get("events", [])
    if not events:
        return None

    event = events[0]
    name = event.get("name", "")
    purse = event.get("purse", 0)
    is_major = event.get("tournament", {}).get("major", False)

    # Use known major purses if ESPN doesn't have it
    if (not purse or purse == 0) and name in MAJOR_PURSES:
        purse = MAJOR_PURSES[name]

    competitions = event.get("competitions", [])
    status = "unknown"
    field = []

    if competitions:
        comp = competitions[0]
        if not isinstance(comp, dict):
            # Some API responses nest competitions differently
            return {"id": event_id, "name": name, "purse": purse, "major": is_major,
                    "status": "unknown", "field": []}

        try:
            comp_status = comp.get("status", {})
            if isinstance(comp_status, dict):
                status = comp_status.get("type", {}).get("name", "unknown")
            elif isinstance(comp_status, list) and comp_status:
                status = comp_status[0].get("type", {}).get("name", "unknown")
        except (AttributeError, IndexError, TypeError):
            status = "unknown"

        for player in comp.get("competitors", []):
            if not isinstance(player, dict):
                continue
            athlete = player.get("athlete", {}) or {}
            try:
                player_status = player.get("status", {}) or {}
                if isinstance(player_status, dict):
                    pos_info = player_status.get("position", {}) or {}
                else:
                    pos_info = {}
            except (AttributeError, TypeError):
                pos_info = {}
            field.append({
                "player_id": athlete.get("id", ""),
                "player_name": athlete.get("displayName", "Unknown"),
                "position": int(pos_info.get("id", 0)) if pos_info.get("id", "").isdigit() else 999,
                "position_display": pos_info.get("displayName", ""),
                "earnings": player.get("earnings", 0),
                "amateur": player.get("amateur", False),
            })

    return {
        "id": event_id,
        "name": name,
        "purse": purse,
        "major": is_major,
        "status": status,
        "field": field,
    }


# -----------------------------------------------------------
# World Rankings (from ESPN or OWGR)
# -----------------------------------------------------------

def get_world_rankings():
    """Get current world golf rankings.

    Uses hardcoded OWGR baseline (fast, accurate).
    Returns list of {rank, player_id, player_name}
    """
    from data.rankings_baseline import get_owgr_rankings
    return get_owgr_rankings()


def _build_rankings_from_results():
    """Build skill rankings from recent tournament earnings.

    Uses the prior season (full year) + current season results,
    weighted toward recency.
    """
    player_earnings = {}  # player_name -> {total_weighted, events, player_id}

    # Load prior season (2025) for baseline + current season
    for year, weight in [(SEASON_YEAR - 1, 0.6), (SEASON_YEAR, 1.0)]:
        try:
            schedule = get_schedule(year)
        except Exception:
            continue

        completed = 0
        # For prior year, use cached data aggressively
        for tourn in schedule:
            details = get_tournament_details(tourn["id"])
            if not details or details["status"] != "STATUS_FINAL":
                continue
            completed += 1

            for player in details.get("field", []):
                name = player["player_name"]
                earnings = player.get("earnings", 0) or 0
                if name not in player_earnings:
                    player_earnings[name] = {
                        "player_id": player["player_id"],
                        "total_weighted": 0,
                        "events": 0,
                    }
                player_earnings[name]["total_weighted"] += earnings * weight
                player_earnings[name]["events"] += 1

            # Limit: 8 events from prior year, all completed from current
            max_events = 8 if year < SEASON_YEAR else 50
            if completed >= max_events:
                break
            time.sleep(0.1)

    # Sort by weighted earnings
    sorted_players = sorted(
        player_earnings.items(),
        key=lambda x: x[1]["total_weighted"],
        reverse=True,
    )

    rankings = []
    for i, (name, info) in enumerate(sorted_players):
        rankings.append({
            "rank": i + 1,
            "player_id": info["player_id"],
            "player_name": name,
            "total_earnings": info["total_weighted"],
            "events_played": info["events"],
        })

    return rankings


# -----------------------------------------------------------
# Historical Results (for course fit)
# -----------------------------------------------------------

def get_historical_results(event_name, years_back=3):
    """Get historical results for a tournament across prior seasons.

    Returns list of tournament detail dicts from past years.
    """
    results = []
    current_year = SEASON_YEAR

    for year in range(current_year - 1, current_year - years_back - 1, -1):
        try:
            schedule = get_schedule(year)
        except Exception:
            continue

        for tourn in schedule:
            # Fuzzy match tournament name
            if _tournament_name_match(event_name, tourn["name"]):
                details = get_tournament_details(tourn["id"])
                if details and details["status"] == "STATUS_FINAL":
                    details["year"] = year
                    results.append(details)
                break
        time.sleep(0.3)

    return results


def _tournament_name_match(name1, name2):
    """Check if two tournament names refer to the same event."""
    def normalize(s):
        s = s.lower()
        for word in ["the ", "pres. by ", "presented by ", "pres by "]:
            s = s.replace(word, "")
        # Keep core name words
        return s.strip()

    n1 = normalize(name1)
    n2 = normalize(name2)
    # Check if one contains the other or significant overlap
    return n1 in n2 or n2 in n1 or _word_overlap(n1, n2) > 0.5


def _word_overlap(s1, s2):
    """Calculate word overlap ratio between two strings."""
    w1 = set(s1.split())
    w2 = set(s2.split())
    if not w1 or not w2:
        return 0
    overlap = len(w1 & w2)
    return overlap / min(len(w1), len(w2))
