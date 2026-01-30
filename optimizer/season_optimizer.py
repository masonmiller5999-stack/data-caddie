"""Season-long optimization using linear assignment.

Determines the optimal allocation of golfers to tournaments
to maximize total expected prize money across the season.
"""

import numpy as np
from scipy.optimize import linear_sum_assignment

from data.scraper import get_tournament_details
from data.schedule import get_upcoming_tournaments
from model.golfer_skill import get_skill_ratings
from model.course_fit import get_course_fit_scores
from model.field_strength import calculate_field_strength
from model.expected_value import calculate_ev


def optimize_season(used_golfers, top_n_golfers=50, max_tournaments=None):
    """Find optimal golfer-tournament assignments for remaining season.

    Args:
        used_golfers: Set of player names already used
        top_n_golfers: Number of top golfers to consider for optimization
        max_tournaments: Max tournaments to look ahead (None = all remaining)

    Returns:
        dict: {
            assignments: [{tournament, golfer, ev}, ...],
            total_ev: float,
            this_week: {tournament, golfer, ev, alternatives}
        }
    """
    print("  Loading skill ratings...")
    skill_ratings = get_skill_ratings()

    # Get top N available golfers (by skill score, excluding used)
    available = sorted(
        [(name, info) for name, info in skill_ratings.items()
         if name not in used_golfers],
        key=lambda x: x[1]["skill_score"],
        reverse=True,
    )[:top_n_golfers]

    golfer_names = [name for name, _ in available]
    golfer_ratings = {name: info for name, info in available}

    print(f"  Top {len(golfer_names)} available golfers loaded")

    # Get upcoming tournaments
    print("  Loading upcoming tournaments...")
    upcoming = get_upcoming_tournaments(include_current_week=True)

    if max_tournaments:
        upcoming = upcoming[:max_tournaments]

    # Filter to tournaments that haven't completed
    upcoming = [t for t in upcoming if t["status"] != "STATUS_FINAL"]

    if not upcoming:
        return {"assignments": [], "total_ev": 0, "this_week": None}

    print(f"  {len(upcoming)} upcoming tournaments")

    # Build EV matrix: golfers (rows) x tournaments (cols)
    n_golfers = len(golfer_names)
    n_tournaments = len(upcoming)

    # We need the matrix to be square for assignment, pad with zeros
    size = max(n_golfers, n_tournaments)
    cost_matrix = np.zeros((size, size))

    print("  Calculating EV matrix...")
    tournament_data = []

    for j, tourn in enumerate(upcoming):
        # Get field and field strength for this tournament
        details = get_tournament_details(tourn["id"])
        field = details.get("field", []) if details else []
        fs_score = calculate_field_strength(field, skill_ratings)

        # Get course fit scores for our golfer pool
        course_fits = get_course_fit_scores(tourn["name"], golfer_names)

        tournament_data.append({
            "tournament": tourn,
            "field_strength": fs_score,
            "course_fits": course_fits,
        })

        for i, golfer_name in enumerate(golfer_names):
            rating = golfer_ratings[golfer_name]
            course_fit = course_fits.get(golfer_name, {}).get("score", 50)

            ev_result = calculate_ev(
                golfer_name,
                tourn["purse"],
                rating,
                course_fit,
                fs_score,
                tourn.get("field_size", 156),
            )

            # Use negative EV because linear_sum_assignment minimizes cost
            cost_matrix[i][j] = -ev_result["ev"]

    # Solve assignment problem
    print("  Solving optimization...")
    row_indices, col_indices = linear_sum_assignment(cost_matrix)

    # Extract assignments
    assignments = []
    for row, col in zip(row_indices, col_indices):
        if row >= n_golfers or col >= n_tournaments:
            continue  # Skip padding
        ev = -cost_matrix[row][col]
        if ev <= 0:
            continue
        assignments.append({
            "tournament": upcoming[col]["name"],
            "tournament_date": upcoming[col]["start_date"],
            "tournament_purse": upcoming[col]["purse"],
            "golfer": golfer_names[row],
            "ev": ev,
            "skill": golfer_ratings[golfer_names[row]]["skill_score"],
        })

    assignments.sort(key=lambda x: x["tournament_date"])
    total_ev = sum(a["ev"] for a in assignments)

    # This week's recommendation
    this_week = None
    if assignments:
        this_week_assignment = assignments[0]

        # Also get top 5 alternatives for this week
        if tournament_data:
            td = tournament_data[0]
            tourn = upcoming[0]
            alternatives = []
            for i, golfer_name in enumerate(golfer_names[:20]):
                rating = golfer_ratings[golfer_name]
                course_fit = td["course_fits"].get(golfer_name, {}).get("score", 50)
                ev_result = calculate_ev(
                    golfer_name, tourn["purse"], rating, course_fit,
                    td["field_strength"], tourn.get("field_size", 156)
                )
                alternatives.append({
                    "golfer": golfer_name,
                    "ev": ev_result["ev"],
                    "skill": rating["skill_score"],
                    "form": rating.get("form_label", "?"),
                    "course_fit": td["course_fits"].get(golfer_name, {}).get("history_label", "No Data"),
                })
            alternatives.sort(key=lambda x: x["ev"], reverse=True)

            this_week = {
                "tournament": tourn["name"],
                "tournament_date": tourn["start_date"],
                "tournament_purse": tourn["purse"],
                "optimal_pick": this_week_assignment["golfer"],
                "optimal_ev": this_week_assignment["ev"],
                "alternatives": alternatives[:10],
            }

    return {
        "assignments": assignments,
        "total_ev": total_ev,
        "this_week": this_week,
    }


def get_save_vs_use_analysis(golfer_name, current_tournament, used_golfers,
                              skill_ratings, current_ev=None):
    """Check if a golfer should be saved for a higher-value future tournament.

    Uses purse-based EV estimation for future events (fast — no API calls).
    Since future fields aren't known, EV scales roughly linearly with purse
    for a given golfer skill level.

    Returns dict with recommendation and reasoning.
    """
    upcoming = get_upcoming_tournaments()
    upcoming = [t for t in upcoming if t["status"] != "STATUS_FINAL"]

    if not upcoming:
        return {"recommendation": "USE", "reason": "No future tournaments"}

    rating = skill_ratings.get(golfer_name)
    if not rating:
        return {"recommendation": "USE", "reason": "Unknown golfer"}

    current_purse = current_tournament.get("purse", 0) or 0
    if current_purse <= 0:
        return {"recommendation": "USE", "reason": "Purse unknown"}

    # For current tournament, use the already-calculated EV if provided
    if current_ev is None:
        current_ev = 0

    # Estimate future EVs using purse ratio (EV scales ~linearly with purse)
    # For future events, we don't know fields, so use purse as the primary signal
    # Also flag majors which have higher prestige/opportunity
    # Exclude invite-only/special events with unusual purse structures
    EXCLUDED_EVENTS = {"TOUR Championship", "Hero World Challenge", "Good Good Championship"}

    future_evs = []
    for tourn in upcoming[1:]:  # Skip current
        # Skip invite-only or non-standard events
        if any(exc.lower() in tourn["name"].lower() for exc in EXCLUDED_EVENTS):
            continue

        future_purse = tourn.get("purse", 0) or 0
        if future_purse <= 0:
            continue

        # Estimated EV = current EV * (future_purse / current_purse)
        # With a course fit bonus for majors (elite players do well at majors)
        purse_ratio = future_purse / current_purse
        is_major = tourn.get("major", False)
        major_boost = 1.15 if is_major and rating["skill_score"] > 70 else 1.0

        estimated_ev = current_ev * purse_ratio * major_boost

        future_evs.append({
            "tournament": tourn["name"],
            "date": tourn["start_date"],
            "purse": future_purse,
            "ev": estimated_ev,
            "major": is_major,
        })

    if not future_evs:
        return {"recommendation": "USE", "reason": "No future tournaments with known purses"}

    # Find the best future tournament for this golfer
    best_future = max(future_evs, key=lambda x: x["ev"])

    # If future EV is significantly higher (>25%), recommend saving
    if best_future["ev"] > current_ev * 1.25:
        major_note = " [MAJOR]" if best_future.get("major") else ""
        return {
            "recommendation": "SAVE",
            "reason": f"Higher EV at {best_future['tournament']}{major_note} "
                     f"({best_future['date']}, ${best_future['purse']:,.0f} purse): "
                     f"~${best_future['ev']:,.0f} vs ${current_ev:,.0f} this week",
            "best_future": best_future,
            "current_ev": current_ev,
        }
    else:
        return {
            "recommendation": "USE",
            "reason": f"This week (${current_ev:,.0f}) is close to best future "
                     f"({best_future['tournament']}: ~${best_future['ev']:,.0f})",
            "best_future": best_future,
            "current_ev": current_ev,
        }
