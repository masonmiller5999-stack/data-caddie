"""Tournament schedule utilities."""

from datetime import datetime

from data.scraper import get_schedule, get_tournament_details

# Known 2026 PGA Tour purses for major events and signature events
# Source: PGA Tour announcements and estimates based on 2025 actuals
KNOWN_PURSES_2026 = {
    "The Sentry": 20_000_000,
    "AT&T Pebble Beach Pro-Am": 20_000_000,
    "The Genesis Invitational": 20_000_000,
    "Arnold Palmer Invitational pres. by Mastercard": 20_000_000,
    "THE PLAYERS Championship": 25_000_000,
    "RBC Heritage": 20_000_000,
    "Wells Fargo Championship": 20_000_000,
    "the Memorial Tournament pres. by Workday": 20_000_000,
    "Travelers Championship": 20_000_000,
    "Masters Tournament": 20_000_000,
    "PGA Championship": 18_500_000,
    "U.S. Open": 21_500_000,
    "The Open Championship": 17_500_000,
    "FedEx St. Jude Championship": 20_000_000,
    "BMW Championship": 20_000_000,
    "TOUR Championship": 100_000_000,
    "Sony Open in Hawaii": 8_700_000,
    "The American Express": 8_400_000,
    "Farmers Insurance Open": 9_600_000,
    "WM Phoenix Open": 9_200_000,
    "Mexico Open at Vidanta": 8_700_000,
    "Cognizant Classic in The Palm Beaches": 8_000_000,
    "Houston Open": 9_200_000,
    "Valero Texas Open": 9_100_000,
    "Zurich Classic of New Orleans": 8_800_000,
    "Charles Schwab Challenge": 9_100_000,
    "the Memorial Tournament": 20_000_000,
    "Rocket Mortgage Classic": 9_200_000,
    "John Deere Classic": 8_000_000,
    "Genesis Scottish Open": 9_000_000,
    "3M Open": 8_400_000,
    "Wyndham Championship": 8_400_000,
}

# Known majors
MAJOR_NAMES = {
    "Masters Tournament", "PGA Championship", "U.S. Open",
    "The Open Championship", "The Open",
}

DEFAULT_PURSE = 8_500_000  # Default for unknown events


def _lookup_purse(tournament_name):
    """Look up purse from known data, with fuzzy matching."""
    if tournament_name in KNOWN_PURSES_2026:
        return KNOWN_PURSES_2026[tournament_name]
    # Fuzzy: check if any known name is contained in the tournament name
    name_lower = tournament_name.lower()
    for known, purse in KNOWN_PURSES_2026.items():
        if known.lower() in name_lower or name_lower in known.lower():
            return purse
    return DEFAULT_PURSE


def _is_major(tournament_name):
    """Check if tournament is a major."""
    name_lower = tournament_name.lower()
    return any(m.lower() in name_lower for m in MAJOR_NAMES)


def get_upcoming_tournaments(include_current_week=True):
    """Get list of upcoming tournaments with purse data.

    Uses known purse lookup first, only fetches from API if needed.
    Returns list of dicts: {id, name, start_date, purse, major, status}
    """
    schedule = get_schedule()
    today = datetime.now().strftime("%Y-%m-%d")
    upcoming = []

    for tourn in schedule:
        start = tourn["start_date"]
        end = tourn.get("end_date", start)

        if end < today and not include_current_week:
            continue
        if start < today and end >= today and not include_current_week:
            continue

        # Use known purse data (fast) — only fetch from API for current/near events
        purse = _lookup_purse(tourn["name"])
        major = _is_major(tourn["name"])
        status = "STATUS_SCHEDULED" if start > today else "STATUS_IN_PROGRESS"

        # For events in the past, check if they're completed
        if end < today:
            status = "STATUS_FINAL"

        upcoming.append({
            "id": tourn["id"],
            "name": tourn["name"],
            "start_date": start,
            "purse": purse,
            "major": major,
            "status": status,
            "field_size": 156,  # Default; actual field fetched separately when needed
        })

    return upcoming


def get_upcoming_tournaments_full(include_current_week=True):
    """Get upcoming tournaments with full API data (slower).

    Only use when full field/status data is needed (e.g., season optimizer).
    """
    schedule = get_schedule()
    today = datetime.now().strftime("%Y-%m-%d")
    upcoming = []

    for tourn in schedule:
        start = tourn["start_date"]
        end = tourn.get("end_date", start)

        if end < today and not include_current_week:
            continue

        details = get_tournament_details(tourn["id"])
        if details:
            upcoming.append({
                "id": tourn["id"],
                "name": tourn["name"],
                "start_date": start,
                "purse": details["purse"] or _lookup_purse(tourn["name"]),
                "major": details["major"] or _is_major(tourn["name"]),
                "status": details["status"],
                "field_size": len(details.get("field", [])),
            })

    return upcoming


def get_current_tournament():
    """Get the current or next upcoming tournament."""
    schedule = get_schedule()
    today = datetime.now().strftime("%Y-%m-%d")

    for tourn in schedule:
        start = tourn["start_date"]
        end = tourn.get("end_date", start)

        # Current week or next upcoming
        if end >= today:
            details = get_tournament_details(tourn["id"])
            if details:
                return {
                    "id": tourn["id"],
                    "name": tourn["name"],
                    "start_date": start,
                    "purse": details["purse"],
                    "major": details["major"],
                    "status": details["status"],
                    "field": details["field"],
                }
    return None


def get_completed_tournaments():
    """Get list of completed tournaments this season with results."""
    schedule = get_schedule()
    completed = []

    for tourn in schedule:
        details = get_tournament_details(tourn["id"])
        if details and details["status"] == "STATUS_FINAL":
            completed.append({
                "id": tourn["id"],
                "name": tourn["name"],
                "start_date": tourn["start_date"],
                "purse": details["purse"],
                "major": details["major"],
                "field": details["field"],
            })

    return completed
