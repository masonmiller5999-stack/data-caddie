"""Golfer skill rating model.

Combines world ranking, strokes gained, and recent form into a 0-100 skill score.

Skill score breakdown:
  - 50% base skill = average of OWGR ranking score and SG Total score
  - 50% base skill allocated as: 50% ranking + 50% strokes gained
  - Then blended with recent form (65/35 split)
"""

from data.scraper import get_world_rankings, get_schedule, get_tournament_details
from data.sg_baseline import get_sg_total_dict, sg_to_score


def get_skill_ratings():
    """Calculate skill ratings for all known golfers.

    Returns dict: player_name -> {skill_score, rank, rank_score, sg_score, form_score, form_label}
    """
    rankings = get_world_rankings()
    recent_form = _calculate_recent_form()
    sg_data = get_sg_total_dict()

    ratings = {}
    for entry in rankings:
        name = entry["player_name"]
        rank = entry.get("rank", 999)

        # Ranking score (rank 1 = 100, rank 200 = 10)
        rank_score = max(10, 100 - (rank - 1) * 0.45)

        # Strokes Gained score (SG Total per round → 0-100)
        sg_total = sg_data.get(name)
        if sg_total is not None:
            sg_score = sg_to_score(sg_total)
        else:
            # No SG data — estimate from ranking
            sg_score = rank_score * 0.8

        # Base skill: 50% ranking + 50% strokes gained
        base_skill = (rank_score * 0.50) + (sg_score * 0.50)

        # Recent form bonus/penalty
        form = recent_form.get(name, {})
        if form:
            form_score = form.get("score", 50)
        else:
            # No recent form data — estimate from base skill
            form_score = max(40, base_skill * 0.7)
        form_label = _form_label(form_score)

        # Final skill: 65% base skill + 35% recent form
        skill = (base_skill * 0.65) + (form_score * 0.35)
        skill = min(100, max(0, skill))

        ratings[name] = {
            "skill_score": round(skill, 1),
            "rank": rank,
            "rank_score": round(rank_score, 1),
            "sg_score": round(sg_score, 1),
            "sg_total": round(sg_total, 3) if sg_total is not None else None,
            "form_score": round(form_score, 1),
            "form_label": form_label,
        }

    return ratings


def _calculate_recent_form():
    """Calculate recent form based on last 3 completed tournaments.

    Form score: 0-100 based on recent earnings vs field average.
    Limits API calls to avoid slow performance early in the season.
    """
    try:
        schedule = get_schedule()
    except Exception:
        return {}

    player_results = {}  # name -> list of (position, field_size)

    completed_count = 0
    attempts = 0
    max_attempts = 8  # Don't try more than 8 events

    # Find recent events by iterating forward to current date, then backwards
    # This avoids checking future events that can't be completed
    from datetime import date
    today = date.today().isoformat()
    past_events = [t for t in schedule if t["start_date"] <= today]

    for tourn in reversed(past_events):  # Start from most recent past event
        attempts += 1
        if attempts > max_attempts:
            break

        try:
            details = get_tournament_details(tourn["id"])
        except Exception:
            continue

        if not details or details["status"] != "STATUS_FINAL":
            continue

        field = details.get("field", [])
        field_size = len(field) or 156
        purse = details.get("purse", 0)

        for player in field:
            name = player["player_name"]
            pos = player.get("position", 999)
            earnings = player.get("earnings", 0) or 0

            if name not in player_results:
                player_results[name] = []

            player_results[name].append({
                "position": pos,
                "field_size": field_size,
                "earnings": earnings,
                "purse": purse,
            })

        completed_count += 1
        if completed_count >= 3:
            break

    # Score each player's form
    form_scores = {}
    for name, results in player_results.items():
        if not results:
            continue

        # Weighted average of percentile finishes (recent events weighted higher)
        total_weight = 0
        weighted_pct = 0
        for i, result in enumerate(results):  # Most recent first
            weight = 1.0 + (0.2 * (len(results) - i - 1))  # Recent = higher weight
            pct = 1.0 - (result["position"] / result["field_size"])
            pct = max(0, min(1, pct))
            weighted_pct += pct * weight
            total_weight += weight

        avg_pct = weighted_pct / total_weight if total_weight > 0 else 0.5

        # Convert to 0-100 score
        form_score = avg_pct * 100

        form_scores[name] = {
            "score": round(form_score, 1),
            "events": len(results),
        }

    return form_scores


def _form_label(score):
    """Convert form score to human-readable label."""
    if score >= 80:
        return "Hot"
    elif score >= 60:
        return "Good"
    elif score >= 40:
        return "Average"
    elif score >= 20:
        return "Cold"
    else:
        return "Poor"
