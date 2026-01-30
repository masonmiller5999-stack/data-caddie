"""Weekly pick recommendation engine."""

import json
import os

from config import USED_GOLFERS_FILE, SEASON_RESULTS_FILE


def get_used_golfers():
    """Load set of already-used golfer names."""
    if not os.path.exists(USED_GOLFERS_FILE):
        return set()
    with open(USED_GOLFERS_FILE, "r") as f:
        data = json.load(f)
    return {entry["name"] for entry in data.get("used", [])}


def record_pick(golfer_name, tournament_name, week=None):
    """Record a golfer pick for the season."""
    # Update used golfers
    if os.path.exists(USED_GOLFERS_FILE):
        with open(USED_GOLFERS_FILE, "r") as f:
            data = json.load(f)
    else:
        data = {"used": []}

    data["used"].append({
        "name": golfer_name,
        "tournament": tournament_name,
        "week": week,
        "earnings": None,  # Updated after tournament completes
    })

    with open(USED_GOLFERS_FILE, "w") as f:
        json.dump(data, f, indent=4)

    print(f"  Recorded: {golfer_name} for {tournament_name}")


def record_result(golfer_name, tournament_name, earnings):
    """Record actual earnings for a completed pick."""
    # Update used golfers
    if os.path.exists(USED_GOLFERS_FILE):
        with open(USED_GOLFERS_FILE, "r") as f:
            data = json.load(f)
        for entry in data["used"]:
            if entry["name"] == golfer_name and entry["tournament"] == tournament_name:
                entry["earnings"] = earnings
                break
        with open(USED_GOLFERS_FILE, "w") as f:
            json.dump(data, f, indent=4)

    # Update season results
    if os.path.exists(SEASON_RESULTS_FILE):
        with open(SEASON_RESULTS_FILE, "r") as f:
            results = json.load(f)
    else:
        results = {"season": 2026, "total_earnings": 0, "picks": []}

    results["picks"].append({
        "golfer": golfer_name,
        "tournament": tournament_name,
        "earnings": earnings,
    })
    results["total_earnings"] = sum(p["earnings"] for p in results["picks"]
                                     if p["earnings"] is not None)

    with open(SEASON_RESULTS_FILE, "w") as f:
        json.dump(results, f, indent=4)


def get_season_summary():
    """Get season results summary."""
    if not os.path.exists(SEASON_RESULTS_FILE):
        return {"total_earnings": 0, "picks": [], "completed": 0}

    with open(SEASON_RESULTS_FILE, "r") as f:
        results = json.load(f)

    completed = sum(1 for p in results["picks"] if p["earnings"] is not None)
    return {
        "total_earnings": results["total_earnings"],
        "picks": results["picks"],
        "completed": completed,
    }
