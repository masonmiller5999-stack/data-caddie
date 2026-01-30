"""Golfer management API endpoints."""

import json
import os
from fastapi import APIRouter, HTTPException
from typing import List

from api.schemas import UsedGolfer, AddGolferRequest, GolferSearchResult, SeasonSummary
from config import USED_GOLFERS_FILE, SEASON_RESULTS_FILE
from model.golfer_skill import get_skill_ratings

router = APIRouter()


def _load_used_golfers_data():
    """Load the full used golfers data structure."""
    if not os.path.exists(USED_GOLFERS_FILE):
        return {"used": []}
    with open(USED_GOLFERS_FILE, "r") as f:
        return json.load(f)


def _save_used_golfers_data(data):
    """Save the used golfers data structure."""
    os.makedirs(os.path.dirname(USED_GOLFERS_FILE), exist_ok=True)
    with open(USED_GOLFERS_FILE, "w") as f:
        json.dump(data, f, indent=4)


@router.get("/used", response_model=List[UsedGolfer])
def get_used():
    """Get list of used golfers."""
    data = _load_used_golfers_data()
    return [
        UsedGolfer(
            name=entry["name"],
            tournament=entry.get("tournament"),
            earnings=entry.get("earnings"),
        )
        for entry in data.get("used", [])
    ]


@router.post("/used", response_model=UsedGolfer)
def add_used(request: AddGolferRequest):
    """Add a golfer to the used list."""
    data = _load_used_golfers_data()

    # Check if already used
    existing_names = {entry["name"].lower() for entry in data.get("used", [])}
    if request.name.lower() in existing_names:
        raise HTTPException(status_code=400, detail=f"{request.name} is already used")

    new_entry = {
        "name": request.name,
        "tournament": request.tournament,
        "week": None,
        "earnings": None,
    }
    data["used"].append(new_entry)
    _save_used_golfers_data(data)

    return UsedGolfer(
        name=request.name,
        tournament=request.tournament,
        earnings=None,
    )


@router.delete("/used/{name}")
def remove_used(name: str):
    """Remove a golfer from the used list."""
    data = _load_used_golfers_data()

    # Find and remove
    original_len = len(data.get("used", []))
    data["used"] = [
        entry for entry in data.get("used", [])
        if entry["name"].lower() != name.lower()
    ]

    if len(data["used"]) == original_len:
        raise HTTPException(status_code=404, detail=f"Golfer '{name}' not found in used list")

    _save_used_golfers_data(data)
    return {"status": "ok", "message": f"Removed {name} from used list"}


@router.get("/search", response_model=List[GolferSearchResult])
def search_golfers(q: str = "", limit: int = 10):
    """Search for golfers by name (for autocomplete)."""
    if not q or len(q) < 2:
        return []

    skill_ratings = get_skill_ratings()
    q_lower = q.lower()

    matches = []
    for name, rating in skill_ratings.items():
        if q_lower in name.lower():
            matches.append(GolferSearchResult(
                name=name,
                rank=rating.get("rank"),
                skill_score=rating.get("skill_score"),
            ))

    # Sort by skill score descending
    matches.sort(key=lambda x: x.skill_score or 0, reverse=True)
    return matches[:limit]


@router.get("/season/summary", response_model=SeasonSummary)
def get_season_summary():
    """Get season summary with earnings and picks."""
    used_data = _load_used_golfers_data()

    # Load season results if exists
    if os.path.exists(SEASON_RESULTS_FILE):
        with open(SEASON_RESULTS_FILE, "r") as f:
            results = json.load(f)
    else:
        results = {"total_earnings": 0, "picks": []}

    picks = [
        UsedGolfer(
            name=entry["name"],
            tournament=entry.get("tournament"),
            earnings=entry.get("earnings"),
        )
        for entry in used_data.get("used", [])
    ]

    completed = sum(1 for p in picks if p.earnings is not None)

    return SeasonSummary(
        total_earnings=results.get("total_earnings", 0),
        picks_made=len(picks),
        completed=completed,
        picks=picks,
    )
