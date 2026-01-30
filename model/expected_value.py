"""Expected Value engine.

Calculates expected prize money for each golfer-tournament pair.
EV = sum of P(finish_position) * prize_money(position, purse)
"""

import math

from config import (
    PAYOUT_PERCENTAGES,
    WEIGHT_SKILL, WEIGHT_FORM, WEIGHT_COURSE, WEIGHT_FIELD, WEIGHT_ODDS,
    WEIGHT_SKILL_NO_ODDS, WEIGHT_FORM_NO_ODDS, WEIGHT_COURSE_NO_ODDS, WEIGHT_FIELD_NO_ODDS,
)
from model.field_strength import field_strength_multiplier


def calculate_ev(golfer_name, tournament_purse, skill_rating, course_fit_score,
                 field_strength_score, field_size=156, odds_score=None):
    """Calculate expected prize money for a golfer in a tournament.

    Args:
        golfer_name: Player name
        tournament_purse: Total tournament purse in dollars
        skill_rating: Dict with skill_score, form_score, etc.
        course_fit_score: 0-100 course fit score
        field_strength_score: 0-100 field strength score
        field_size: Number of players in the field
        odds_score: 0-100 score derived from betting odds (None if unavailable)

    Returns:
        dict: {ev, win_prob, top5_prob, top10_prob, top25_prob, make_cut_prob, details}
    """
    if not skill_rating or tournament_purse <= 0:
        return {"ev": 0, "win_prob": 0, "top5_prob": 0, "top10_prob": 0,
                "top25_prob": 0, "make_cut_prob": 0, "details": {}}

    skill = skill_rating.get("skill_score", 50)
    form = skill_rating.get("form_score", 50)

    # Composite strength score (0-100)
    # Use odds-weighted formula when odds are available
    if odds_score is not None:
        composite = (
            skill * WEIGHT_SKILL +
            form * WEIGHT_FORM +
            course_fit_score * WEIGHT_COURSE +
            (100 - field_strength_score) * WEIGHT_FIELD +
            odds_score * WEIGHT_ODDS
        )
    else:
        composite = (
            skill * WEIGHT_SKILL_NO_ODDS +
            form * WEIGHT_FORM_NO_ODDS +
            course_fit_score * WEIGHT_COURSE_NO_ODDS +
            (100 - field_strength_score) * WEIGHT_FIELD_NO_ODDS
        )

    # Apply field strength multiplier
    fs_mult = field_strength_multiplier(field_strength_score)

    # Convert composite to probability distribution
    # Higher composite = better expected finish position
    probs = _composite_to_probabilities(composite, fs_mult, field_size)

    # Calculate EV
    ev = 0
    for pos, prob in probs.items():
        payout_pct = PAYOUT_PERCENTAGES.get(pos, 0)
        prize = tournament_purse * payout_pct
        ev += prob * prize

    # Also add residual probability for positions 66+ (minimal payout)
    # These players roughly get 0.14% of purse each
    residual_prob = probs.get("residual_made_cut", 0)
    ev += residual_prob * tournament_purse * 0.0014

    return {
        "ev": round(ev, 0),
        "win_prob": round(probs.get(1, 0) * 100, 2),
        "top5_prob": round(sum(probs.get(i, 0) for i in range(1, 6)) * 100, 1),
        "top10_prob": round(sum(probs.get(i, 0) for i in range(1, 11)) * 100, 1),
        "top25_prob": round(sum(probs.get(i, 0) for i in range(1, 26)) * 100, 1),
        "make_cut_prob": round(probs.get("make_cut_total", 0) * 100, 1),
        "details": {
            "composite": round(composite, 1),
            "field_multiplier": round(fs_mult, 2),
        },
    }


def _composite_to_probabilities(composite, fs_mult, field_size=156):
    """Convert a composite skill score to position probability distribution.

    Uses a log-normal inspired model:
    - Higher composite → more probability mass on better finishes
    - The distribution shifts based on skill level

    Returns dict: position -> probability, plus 'make_cut_total' and 'residual_made_cut'
    """
    # Map composite score to expected finish position
    # Uses quadratic mapping: better players get much better positions
    # Score 100 → position ~1 (expected winner)
    # Score 80 → position ~6 (top 5)
    # Score 60 → position ~24 (top 25)
    # Score 40 → position ~53 (borderline cut)
    # Score 20 → position ~94 (miss cut territory)
    # Score 0  → position = field_size (last)
    pct_from_bottom = (1.0 - composite / 100) ** 2
    expected_pos = max(1, pct_from_bottom * field_size)

    # Standard deviation of finish (better players are more consistent)
    # Top players: std ~12 positions; weak players: std ~40 positions
    std_dev = 10 + (pct_from_bottom * 35)

    # Mild field strength adjustment (don't over-distort positions)
    # fs_mult > 1 means weak field → slight position improvement
    # fs_mult < 1 means strong field → slight position worsening
    expected_pos *= (1.5 - 0.5 * fs_mult)
    expected_pos = max(1, min(field_size, expected_pos))

    probs = {}
    total_prob = 0

    # Calculate probability for each finish position 1-65
    for pos in range(1, 66):
        # Normal distribution around expected position
        z = (pos - expected_pos) / std_dev
        prob = math.exp(-0.5 * z * z) / (std_dev * math.sqrt(2 * math.pi))

        # Boost win/top finish probability for elite players
        if pos <= 3 and composite > 65:
            prob *= 1.0 + (composite - 65) * 0.08

        probs[pos] = max(0, prob)
        total_prob += probs[pos]

    # Determine make-cut probability
    # Use total_prob as base (what the bell curve says), with a skill-based floor
    min_make_cut = (composite / 100) ** 1.5  # Score 100 → 100%, Score 80 → 72%, Score 50 → 35%
    make_cut_prob = max(min(0.98, total_prob), min(0.95, min_make_cut))
    miss_cut_prob = 1.0 - make_cut_prob

    # Normalize position probabilities to sum to make_cut_prob
    # Single normalization pass — no double-scaling
    if total_prob > 0:
        normalize = make_cut_prob / total_prob
        for pos in probs:
            probs[pos] *= normalize

    # Residual: made cut but finished 66+ (minimal earnings)
    top65_prob = sum(probs.get(i, 0) for i in range(1, 66))
    probs["residual_made_cut"] = max(0, make_cut_prob - top65_prob)
    probs["make_cut_total"] = make_cut_prob
    probs["miss_cut"] = miss_cut_prob

    return probs


def calculate_ev_for_field(tournament_name, tournament_purse, field, skill_ratings,
                           course_fit_scores, field_strength_score, field_size=156,
                           odds_data=None):
    """Calculate EV for all players in a tournament field.

    Args:
        odds_data: Dict from fetch_tournament_odds() — {name: {odds, implied_prob}}

    Returns list of {player_name, ev, win_prob, ...} sorted by EV descending.
    """
    from data.odds import odds_to_skill_bonus

    results = []
    odds_data = odds_data or {}

    for player in field:
        name = player.get("player_name", "")
        if not name:
            continue

        rating = skill_ratings.get(name)
        if not rating:
            # Unknown player - assign low default
            rating = {"skill_score": 25, "form_score": 50, "form_label": "Unknown"}

        course_fit = course_fit_scores.get(name, {}).get("score", 50)

        # Look up odds for this player (try exact match, then fuzzy)
        player_odds = _find_odds_for_player(name, odds_data)
        odds_score = None
        odds_display = ""
        if player_odds:
            odds_score = odds_to_skill_bonus(player_odds["odds"])
            odds_display = f"+{player_odds['odds']}" if player_odds["odds"] > 0 else str(player_odds["odds"])

        ev_data = calculate_ev(
            name, tournament_purse, rating, course_fit,
            field_strength_score, field_size, odds_score=odds_score,
        )

        results.append({
            "player_name": name,
            "player_id": player.get("player_id", ""),
            "ev": ev_data["ev"],
            "win_prob": ev_data["win_prob"],
            "top5_prob": ev_data["top5_prob"],
            "top10_prob": ev_data["top10_prob"],
            "make_cut_prob": ev_data["make_cut_prob"],
            "skill_score": rating["skill_score"],
            "form_label": rating.get("form_label", "?"),
            "course_fit": course_fit,
            "course_label": course_fit_scores.get(name, {}).get("history_label", "No Data"),
            "odds": odds_display,
            "odds_score": odds_score,
        })

    results.sort(key=lambda x: x["ev"], reverse=True)
    return results


def _find_odds_for_player(player_name, odds_data):
    """Find odds for a player, handling name mismatches.

    ESPN uses full names like "Xander Schauffele"
    Odds sources may use slightly different formatting.
    """
    # Exact match
    if player_name in odds_data:
        return odds_data[player_name]

    # Case-insensitive match
    name_lower = player_name.lower()
    for odds_name, odds_info in odds_data.items():
        if odds_name.lower() == name_lower:
            return odds_info

    # Fuzzy: check if last name matches and first initial matches
    parts = player_name.split()
    if len(parts) >= 2:
        last_name = parts[-1].lower()
        first_initial = parts[0][0].lower()
        for odds_name, odds_info in odds_data.items():
            o_parts = odds_name.split()
            if len(o_parts) >= 2:
                if (o_parts[-1].lower() == last_name and
                        o_parts[0][0].lower() == first_initial):
                    return odds_info

    return None
