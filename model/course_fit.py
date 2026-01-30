"""Course fit model.

Looks at a golfer's historical performance at a specific tournament/course
to estimate course-specific advantage.
"""

from data.scraper import get_historical_results


def get_course_fit_scores(tournament_name, player_names):
    """Calculate course fit scores for players at a given tournament.

    Returns dict: player_name -> {score (0-100), history_label, past_results}
    """
    history = get_historical_results(tournament_name, years_back=3)

    # Build player history at this course
    player_history = {}
    for past_event in history:
        field = past_event.get("field", [])
        field_size = len(field) or 156
        year = past_event.get("year", "?")

        for player in field:
            name = player["player_name"]
            if name not in player_history:
                player_history[name] = []
            player_history[name].append({
                "year": year,
                "position": player.get("position", 999),
                "earnings": player.get("earnings", 0) or 0,
                "field_size": field_size,
            })

    # Score each requested player
    scores = {}
    for name in player_names:
        past = player_history.get(name, [])
        if not past:
            scores[name] = {
                "score": 50.0,  # Neutral - no history
                "history_label": "No Data",
                "past_results": [],
            }
            continue

        # Average percentile finish at this course
        percentiles = []
        for result in past:
            pct = 1.0 - (result["position"] / result["field_size"])
            pct = max(0, min(1, pct))
            percentiles.append(pct)

        avg_pct = sum(percentiles) / len(percentiles)
        score = avg_pct * 100

        scores[name] = {
            "score": round(score, 1),
            "history_label": _history_label(score),
            "past_results": past,
        }

    return scores


def _history_label(score):
    """Convert course fit score to label."""
    if score >= 75:
        return "Strong"
    elif score >= 55:
        return "Good"
    elif score >= 40:
        return "Average"
    elif score >= 20:
        return "Weak"
    else:
        return "Poor"
