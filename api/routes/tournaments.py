"""Tournament-related API endpoints."""

from fastapi import APIRouter, HTTPException
from typing import List

from api.schemas import Tournament
from data.schedule import get_current_tournament, get_upcoming_tournaments

router = APIRouter()


@router.get("/current", response_model=Tournament)
def get_current():
    """Get the current/next tournament."""
    tournament = get_current_tournament()
    if not tournament:
        raise HTTPException(status_code=404, detail="No current tournament found")

    return Tournament(
        id=tournament.get("id", ""),
        name=tournament.get("name", ""),
        start_date=tournament.get("start_date", ""),
        purse=tournament.get("purse"),
        major=tournament.get("major", False),
        status=tournament.get("status", ""),
        field_size=len(tournament.get("field", [])),
    )


@router.get("/upcoming", response_model=List[Tournament])
def get_upcoming():
    """Get list of upcoming tournaments."""
    tournaments = get_upcoming_tournaments()

    return [
        Tournament(
            id=t.get("id", ""),
            name=t.get("name", ""),
            start_date=t.get("start_date", ""),
            purse=t.get("purse"),
            major=t.get("major", False),
            status=t.get("status", ""),
            field_size=t.get("field_size", 156),
        )
        for t in tournaments
        if t.get("status") != "STATUS_FINAL"
    ]
