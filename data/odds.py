"""Betting odds fetcher for PGA Tour tournaments.

Scrapes outright winner odds from Action Network articles.
Converts American odds to implied probabilities for the EV model.
"""

import json
import os
import re
import time
from datetime import datetime, timedelta

import requests

from config import CACHE_DIR, CACHE_EXPIRY_HOURS


def _odds_cache_path(tournament_name):
    os.makedirs(CACHE_DIR, exist_ok=True)
    safe = re.sub(r'[^a-z0-9]', '_', tournament_name.lower())
    return os.path.join(CACHE_DIR, f"odds_{safe}.json")


def _get_cached_odds(tournament_name):
    path = _odds_cache_path(tournament_name)
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


def _set_cached_odds(tournament_name, data):
    path = _odds_cache_path(tournament_name)
    with open(path, "w") as f:
        json.dump({"timestamp": datetime.now().isoformat(), "data": data}, f)


def american_to_implied_prob(odds):
    """Convert American odds to implied win probability.

    +1300 → 1/14 ≈ 0.0714
    -150 → 150/250 = 0.60
    """
    if odds > 0:
        return 100.0 / (odds + 100.0)
    elif odds < 0:
        return abs(odds) / (abs(odds) + 100.0)
    return 0.0


def fetch_tournament_odds(tournament_name):
    """Fetch outright winner odds for a tournament.

    First checks cache, then tries manual odds file, then scrapes Action Network.
    Returns dict: {player_name: {"odds": +1300, "implied_prob": 0.071}} or empty dict.
    """
    cached = _get_cached_odds(tournament_name)
    if cached is not None:
        return cached

    # Try manual odds file first (most reliable)
    odds_data = _load_manual_odds(tournament_name)

    # Fall back to scraping
    if not odds_data:
        odds_data = _scrape_action_network(tournament_name)

    if odds_data:
        _set_cached_odds(tournament_name, odds_data)

    return odds_data


def _load_manual_odds(tournament_name):
    """Load odds from manual JSON file in data/odds_manual/.

    File format: data/odds_manual/<tournament_slug>.json
    Content: {"Player Name": +1300, "Player Name": +5000, ...}
    """
    odds_dir = os.path.join(os.path.dirname(__file__), "odds_manual")
    if not os.path.exists(odds_dir):
        return {}

    slug = re.sub(r'[^a-z0-9]', '_', tournament_name.lower()).strip('_')
    path = os.path.join(odds_dir, f"{slug}.json")
    if not os.path.exists(path):
        return {}

    try:
        with open(path, "r") as f:
            raw = json.load(f)
        return {
            name: {"odds": odds_val, "implied_prob": round(american_to_implied_prob(odds_val), 6)}
            for name, odds_val in raw.items()
        }
    except (json.JSONDecodeError, TypeError):
        return {}


def _scrape_action_network(tournament_name):
    """Scrape odds from Action Network full field article."""
    # Build search-friendly tournament name
    search_name = tournament_name.lower().replace("the ", "").strip()
    search_slug = re.sub(r'[^a-z0-9\s]', '', search_name).replace(' ', '-')

    # Try common URL patterns for Action Network golf odds articles
    year = datetime.now().year
    urls_to_try = [
        f"https://www.actionnetwork.com/golf/{year}-{search_slug}-odds-full-field",
        f"https://www.actionnetwork.com/golf/{year}-{search_slug}-odds",
    ]

    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                       "AppleWebKit/537.36 (KHTML, like Gecko) "
                       "Chrome/120.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml",
    }

    for url in urls_to_try:
        try:
            resp = requests.get(url, headers=headers, timeout=15)
            if resp.status_code == 200:
                odds = _parse_odds_from_html(resp.text)
                if odds:
                    return odds
        except requests.RequestException:
            continue
        time.sleep(0.5)

    return {}


def _parse_odds_from_html(html):
    """Parse player names and odds from article HTML.

    Looks for patterns like "Player Name: +1300" or "Player Name (+1300)"
    or table rows with name and odds columns.
    """
    odds_data = {}

    # Pattern 1: "Name: +/-XXXX" or "Name +/-XXXX"
    # Matches lines like "Xander Schauffele: +1300" or "Xander Schauffele +1300"
    patterns = [
        # Name followed by colon and odds
        r'([A-Z][a-zA-Z\.\-\'\s]+?)\s*[:]\s*([+-]\d{3,6})',
        # Name followed by odds in parens
        r'([A-Z][a-zA-Z\.\-\'\s]+?)\s*\(([+-]\d{3,6})\)',
        # Table/list format: Name then odds
        r'>([A-Z][a-zA-Z\.\-\'\s]{3,30}?)</.*?([+-]\d{3,6})',
    ]

    for pattern in patterns:
        matches = re.findall(pattern, html)
        for name, odds_str in matches:
            name = name.strip()
            # Skip common false matches
            if len(name) < 4 or len(name) > 35:
                continue
            if any(word in name.lower() for word in [
                'click', 'view', 'read', 'sign', 'odds', 'field',
                'the ', 'this', 'bet ', 'open', 'pick', 'best'
            ]):
                continue

            try:
                odds_val = int(odds_str)
                if abs(odds_val) < 100 or abs(odds_val) > 200000:
                    continue
                implied = american_to_implied_prob(odds_val)
                odds_data[name] = {
                    "odds": odds_val,
                    "implied_prob": round(implied, 6),
                }
            except ValueError:
                continue

    return odds_data


def odds_to_skill_bonus(odds, field_median_odds=15000):
    """Convert odds to a 0-100 skill adjustment score.

    Shorter odds (favorites) get higher scores.
    +1300 (favorite) → ~90
    +5000 → ~65
    +15000 (median) → ~50
    +50000 (longshot) → ~25
    +100000 → ~15

    Uses log scale since odds range is enormous.
    """
    import math

    if odds <= 0:
        # Negative odds = heavy favorite
        return min(100, 95 + abs(odds) / 100)

    # Log scale: ln(1300) ≈ 7.17, ln(100000) ≈ 11.51
    log_odds = math.log(max(odds, 100))
    log_median = math.log(field_median_odds)

    # Map: low odds (log ~7) → 95, median (log ~9.6) → 50, high odds (log ~11.5) → 10
    # Linear mapping from log scale
    score = 95 - (log_odds - 7.0) * (85.0 / (log_median - 5.5))
    return max(5, min(98, round(score, 1)))
