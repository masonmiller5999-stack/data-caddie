"""Recommendations API endpoint."""

import math
from fastapi import APIRouter, HTTPException
from typing import Optional

from api.schemas import (
    RecommendationRequest, RecommendationResponse, GolferEV,
    SeasonRecommendation, Weights,
    AdvancedRecommendationRequest, AdvancedRecommendationResponse,
    AdvancedGolferEV, AdvancedWeights
)
from data.schedule import get_current_tournament, get_upcoming_tournaments
from data.odds import fetch_tournament_odds, odds_to_skill_bonus
from data.advanced_stats_baseline import get_advanced_stats_dict, normalize_stat
from data.rankings_baseline import OWGR_TOP_200
from model.golfer_skill import get_skill_ratings
from model.course_fit import get_course_fit_scores
from model.field_strength import calculate_field_strength, field_strength_multiplier
from config import PAYOUT_PERCENTAGES


# Tournament tier definitions
TIER_1_EVENTS = {"masters tournament", "pga championship", "u.s. open", "the open championship"}
TIER_2_EVENTS = {"the players championship"}
# Tier 3 = other signature events ($15M+ purse)


def get_tournament_tier(tournament):
    """Get tournament tier: 1 (majors), 2 (Players), 3 (signature), 4 (regular)."""
    name_lower = tournament.get("name", "").lower()
    if any(t in name_lower for t in TIER_1_EVENTS):
        return 1
    if any(t in name_lower for t in TIER_2_EVENTS):
        return 2
    if tournament.get("purse", 0) >= 15_000_000:
        return 3
    return 4


def get_global_elite_pool(used_golfers, top_n=30):
    """Get global elite pool based on OWGR, excluding used golfers.

    Returns list of dicts with rank and name for top N available golfers.
    """
    used_set = set(used_golfers)
    elite = []
    for rank, name in OWGR_TOP_200:
        if name not in used_set:
            elite.append({"rank": rank, "name": name})
        if len(elite) >= top_n:
            break
    return elite


def calculate_season_strategy(current_tournament, used_golfers, available_in_field):
    """Calculate season-aware SAVE/USE strategy based on OWGR and tournament tiers.

    Returns:
        dict with elite_pool, tier_assignments, and recommendations
    """
    future = get_upcoming_tournaments()
    current_name = current_tournament.get("name", "")
    current_date = current_tournament.get("start_date", "")
    current_tier = get_tournament_tier(current_tournament)

    # Excluded events (non-competitive or restricted)
    EXCLUDED_EVENTS = {"tour championship", "hero world challenge", "good good championship"}

    # Get future premium events by tier
    premium_events = []
    for t in future:
        if t["start_date"] <= current_date:
            continue
        if t["status"] == "STATUS_FINAL":
            continue
        if any(exc in t["name"].lower() for exc in EXCLUDED_EVENTS):
            continue
        tier = get_tournament_tier(t)
        if tier <= 3:  # Only tiers 1-3 are premium
            premium_events.append({**t, "tier": tier})

    # Sort by tier (best first), then by date
    premium_events.sort(key=lambda x: (x["tier"], x["start_date"]))

    # Count events by tier
    tier_counts = {1: 0, 2: 0, 3: 0}
    for e in premium_events:
        tier_counts[e["tier"]] = tier_counts.get(e["tier"], 0) + 1

    # Get global elite pool (top OWGR players not yet used)
    # We need enough elites to cover all premium events
    total_premium = len(premium_events)
    elite_pool = get_global_elite_pool(used_golfers, top_n=max(30, total_premium + 5))

    # Create OWGR lookup for players in field
    field_names = set(p["player_name"] for p in available_in_field)
    owgr_lookup = {name: rank for rank, name in OWGR_TOP_200}

    # Assign elite golfers to tournament tiers
    # Tier 1 (majors) gets top 4 available elites
    # Tier 2 (Players) gets next best
    # Tier 3 (signature) gets remaining elites
    tier_1_count = tier_counts.get(1, 0)
    tier_2_count = tier_counts.get(2, 0)
    tier_3_count = tier_counts.get(3, 0)

    # Reserve top golfers for majors
    reserved_for_tier1 = set(e["name"] for e in elite_pool[:tier_1_count])
    # Next best for Players
    reserved_for_tier2 = set(e["name"] for e in elite_pool[tier_1_count:tier_1_count + tier_2_count])
    # Next for other signature events
    reserved_for_tier3 = set(e["name"] for e in elite_pool[tier_1_count + tier_2_count:tier_1_count + tier_2_count + tier_3_count])

    all_reserved = reserved_for_tier1 | reserved_for_tier2 | reserved_for_tier3

    # Determine if current tournament qualifies for using reserved golfers
    can_use_tier1 = current_tier == 1
    can_use_tier2 = current_tier <= 2
    can_use_tier3 = current_tier <= 3

    # Build recommendations for each golfer in field
    recommendations = {}
    for p in available_in_field:
        name = p["player_name"]
        owgr = owgr_lookup.get(name, 999)

        if name in reserved_for_tier1:
            if can_use_tier1:
                action = "USE"
                reason = "Top pick for major"
            else:
                action = "SAVE"
                reason = f"Reserve for majors (OWGR #{owgr})"
        elif name in reserved_for_tier2:
            if can_use_tier2:
                action = "USE"
                reason = "Top pick for Players/major"
            else:
                action = "SAVE"
                reason = f"Reserve for Players (OWGR #{owgr})"
        elif name in reserved_for_tier3:
            if can_use_tier3:
                action = "USE"
                reason = "Premium event"
            else:
                action = "SAVE"
                reason = f"Reserve for signature events (OWGR #{owgr})"
        else:
            action = "USE"
            reason = ""

        recommendations[name] = {
            "action": action,
            "reason": reason,
            "owgr": owgr,
            "reserved_tier": 1 if name in reserved_for_tier1 else (2 if name in reserved_for_tier2 else (3 if name in reserved_for_tier3 else None))
        }

    # Calculate surplus (elites in field that can be used)
    elites_in_field = [p for p in available_in_field if p["player_name"] in all_reserved]
    usable_elites = [p for p in elites_in_field if recommendations[p["player_name"]]["action"] == "USE"]

    return {
        "elite_pool": elite_pool,
        "premium_events": premium_events,
        "tier_counts": tier_counts,
        "current_tier": current_tier,
        "reserved_for_tier1": reserved_for_tier1,
        "reserved_for_tier2": reserved_for_tier2,
        "reserved_for_tier3": reserved_for_tier3,
        "recommendations": recommendations,
        "elites_in_field": len(elites_in_field),
        "usable_elites": len(usable_elites),
    }

router = APIRouter()


def calculate_ev_with_weights(
    golfer_name: str,
    tournament_purse: int,
    skill_rating: dict,
    course_fit_score: float,
    field_strength_score: float,
    weights: Weights,
    field_size: int = 156,
    odds_score: Optional[float] = None,
) -> dict:
    """Calculate EV with custom weights."""
    if not skill_rating or tournament_purse <= 0:
        return {
            "ev": 0, "win_prob": 0, "top5_prob": 0, "top10_prob": 0,
            "top25_prob": 0, "make_cut_prob": 0
        }

    skill = skill_rating.get("skill_score", 50)
    form = skill_rating.get("form_score", 50)

    # Composite score with custom weights
    if odds_score is not None:
        composite = (
            skill * weights.skill +
            form * weights.form +
            course_fit_score * weights.course +
            (100 - field_strength_score) * weights.field +
            odds_score * weights.odds
        )
    else:
        # Fallback weights when no odds (redistribute odds weight)
        total_other = weights.skill + weights.form + weights.course + weights.field
        if total_other > 0:
            scale = 1.0 / total_other
            composite = (
                skill * weights.skill * scale +
                form * weights.form * scale +
                course_fit_score * weights.course * scale +
                (100 - field_strength_score) * weights.field * scale
            )
        else:
            composite = skill * 0.5 + form * 0.2 + course_fit_score * 0.2 + (100 - field_strength_score) * 0.1

    fs_mult = field_strength_multiplier(field_strength_score)
    probs = _composite_to_probabilities(composite, fs_mult, field_size)

    ev = 0
    for pos, prob in probs.items():
        if isinstance(pos, int):
            payout_pct = PAYOUT_PERCENTAGES.get(pos, 0)
            prize = tournament_purse * payout_pct
            ev += prob * prize

    residual_prob = probs.get("residual_made_cut", 0)
    ev += residual_prob * tournament_purse * 0.0014

    return {
        "ev": round(ev, 0),
        "win_prob": round(probs.get(1, 0) * 100, 2),
        "top5_prob": round(sum(probs.get(i, 0) for i in range(1, 6)) * 100, 1),
        "top10_prob": round(sum(probs.get(i, 0) for i in range(1, 11)) * 100, 1),
        "top25_prob": round(sum(probs.get(i, 0) for i in range(1, 26)) * 100, 1),
        "make_cut_prob": round(probs.get("make_cut_total", 0) * 100, 1),
    }


def _composite_to_probabilities(composite, fs_mult, field_size=156):
    """Convert composite score to probability distribution."""
    pct_from_bottom = (1.0 - composite / 100) ** 2
    expected_pos = max(1, pct_from_bottom * field_size)
    std_dev = 10 + (pct_from_bottom * 35)
    expected_pos *= (1.5 - 0.5 * fs_mult)
    expected_pos = max(1, min(field_size, expected_pos))

    probs = {}
    total_prob = 0

    for pos in range(1, 66):
        z = (pos - expected_pos) / std_dev
        prob = math.exp(-0.5 * z * z) / (std_dev * math.sqrt(2 * math.pi))
        if pos <= 3 and composite > 65:
            prob *= 1.0 + (composite - 65) * 0.08
        probs[pos] = max(0, prob)
        total_prob += probs[pos]

    min_make_cut = (composite / 100) ** 1.5
    make_cut_prob = max(min(0.98, total_prob), min(0.95, min_make_cut))

    if total_prob > 0:
        normalize = make_cut_prob / total_prob
        for pos in probs:
            probs[pos] *= normalize

    top65_prob = sum(probs.get(i, 0) for i in range(1, 66))
    probs["residual_made_cut"] = max(0, make_cut_prob - top65_prob)
    probs["make_cut_total"] = make_cut_prob
    probs["miss_cut"] = 1.0 - make_cut_prob

    return probs


def _find_odds_for_player(player_name: str, odds_data: dict) -> Optional[dict]:
    """Find odds for a player with fuzzy matching."""
    if player_name in odds_data:
        return odds_data[player_name]

    name_lower = player_name.lower()
    for odds_name, odds_info in odds_data.items():
        if odds_name.lower() == name_lower:
            return odds_info

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


@router.post("/calculate", response_model=RecommendationResponse)
def calculate_recommendations(request: RecommendationRequest):
    """Calculate EV recommendations with custom weights."""
    # Get current tournament
    current = get_current_tournament()
    if not current:
        raise HTTPException(status_code=404, detail="No current tournament found")

    if not current.get("purse"):
        raise HTTPException(status_code=400, detail="Tournament purse not available yet")

    # Get data
    skill_ratings = get_skill_ratings()
    field = current.get("field", [])
    fs_score = calculate_field_strength(field, skill_ratings)

    used_set = set(request.used_golfers)
    player_names = [p["player_name"] for p in field if p["player_name"] not in used_set]
    course_fits = get_course_fit_scores(current["name"], player_names)
    odds_data = fetch_tournament_odds(current["name"]) or {}

    # Calculate EV for each player
    results = []
    for player in field:
        name = player.get("player_name", "")
        if not name:
            continue

        rating = skill_ratings.get(name)
        if not rating:
            rating = {"skill_score": 25, "form_score": 50, "form_label": "Unknown"}

        course_fit = course_fits.get(name, {}).get("score", 50)

        player_odds = _find_odds_for_player(name, odds_data)
        odds_score = None
        odds_display = ""
        if player_odds:
            odds_score = odds_to_skill_bonus(player_odds["odds"])
            odds_display = f"+{player_odds['odds']}" if player_odds["odds"] > 0 else str(player_odds["odds"])

        ev_data = calculate_ev_with_weights(
            name, current["purse"], rating, course_fit,
            fs_score, request.weights, len(field), odds_score=odds_score
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
            "sg_total": rating.get("sg_total"),
            "owgr_rank": rating.get("rank"),
            "form_label": rating.get("form_label", "?"),
            "course_fit": course_fit,
            "course_label": course_fits.get(name, {}).get("history_label", "No Data"),
            "odds": odds_display,
            "odds_score": odds_score,
        })

    results.sort(key=lambda x: x["ev"], reverse=True)

    # Filter available (not used)
    available = [r for r in results if r["player_name"] not in used_set]

    # Calculate season strategy using OWGR-based elite pool
    strategy = calculate_season_strategy(current, request.used_golfers, available)

    # Extract strategy results
    premium_events = strategy["premium_events"]
    n_premium = len(premium_events)
    major_events = [e for e in premium_events if e["tier"] == 1]
    current_tier = strategy["current_tier"]
    is_premium_week = current_tier <= 3

    # Elite tracking based on global OWGR pool
    elite_pool = strategy["elite_pool"]
    elite_count = len(elite_pool)
    elite_threshold = elite_pool[-1]["rank"] if elite_pool else 50

    # Count usable elites (those in field that can be used this week)
    surplus = strategy["usable_elites"]

    # Determine season action and pick rank using OWGR-based strategy
    pick_rank = 0
    golfers = []
    for i, p in enumerate(available):
        name = p["player_name"]
        rec = strategy["recommendations"].get(name, {"action": "USE", "reason": ""})
        action = rec["action"]
        reason = rec["reason"]

        if action == "USE":
            pick_rank += 1
            current_pick_rank = pick_rank
        else:
            current_pick_rank = None

        golfers.append(GolferEV(
            rank=i + 1,
            player_name=name,
            player_id=p.get("player_id"),
            ev=p["ev"],
            skill_score=p["skill_score"],
            sg_total=p.get("sg_total"),
            owgr_rank=p.get("owgr_rank"),
            form_label=p["form_label"],
            course_label=p["course_label"],
            odds=p["odds"] or None,
            win_prob=p["win_prob"],
            top5_prob=p["top5_prob"],
            top10_prob=p["top10_prob"],
            make_cut_prob=p["make_cut_prob"],
            season_action=action,
            pick_rank=current_pick_rank,
            reason=reason,
        ))

    # Recommended pick (highest EV among USE picks)
    use_picks = [g for g in golfers if g.season_action == "USE"]
    recommended = use_picks[0] if use_picks else golfers[0]

    season_rec = SeasonRecommendation(
        premium_events=n_premium,
        major_events=len(major_events),
        elite_count=elite_count,
        elite_threshold=round(elite_threshold, 1),
        surplus=surplus,
        is_premium_week=is_premium_week,
        recommended_pick=recommended.player_name,
        recommended_ev=recommended.ev,
    )

    return RecommendationResponse(
        tournament_name=current["name"],
        tournament_date=current["start_date"],
        purse=current["purse"],
        field_size=len(field),
        field_strength=round(fs_score, 1),
        golfers=golfers,
        season_recommendation=season_rec,
    )


def calculate_ev_with_advanced_weights(
    golfer_name: str,
    tournament_purse: int,
    advanced_stats: dict,
    course_fit_score: float,
    weights: AdvancedWeights,
    field_size: int = 156,
    odds_score: Optional[float] = None,
) -> dict:
    """Calculate EV with advanced granular weights."""
    if not advanced_stats or tournament_purse <= 0:
        return {
            "ev": 0, "composite_score": 0,
            "win_prob": 0, "top5_prob": 0, "top10_prob": 0,
            "top25_prob": 0, "make_cut_prob": 0,
            "stat_scores": {}
        }

    # Normalize each stat to 0-100 scale
    stat_scores = {}
    stat_types = [
        "sg_ott", "sg_app", "sg_arg", "sg_putt",
        "driving_dist", "fairways_pct", "gir_pct",
        "scrambling_pct", "putting_avg",
        "birdie_pct", "par5_scoring", "bogey_avoid_pct"
    ]

    for stat_type in stat_types:
        if stat_type in advanced_stats:
            stat_scores[stat_type] = normalize_stat(advanced_stats[stat_type], stat_type)
        else:
            stat_scores[stat_type] = 50.0  # Default middle value

    # Course fit score
    stat_scores["course_fit"] = course_fit_score

    # Odds score
    stat_scores["odds"] = odds_score if odds_score is not None else 50.0

    # Calculate composite using weights
    composite = (
        stat_scores["sg_ott"] * weights.sg_ott +
        stat_scores["sg_app"] * weights.sg_app +
        stat_scores["sg_arg"] * weights.sg_arg +
        stat_scores["sg_putt"] * weights.sg_putt +
        stat_scores["driving_dist"] * weights.driving_dist +
        stat_scores["fairways_pct"] * weights.fairways_pct +
        stat_scores["gir_pct"] * weights.gir_pct +
        stat_scores["scrambling_pct"] * weights.scrambling_pct +
        stat_scores["putting_avg"] * weights.putting_avg +
        stat_scores["birdie_pct"] * weights.birdie_pct +
        stat_scores["par5_scoring"] * weights.par5_scoring +
        stat_scores["bogey_avoid_pct"] * weights.bogey_avoid_pct +
        stat_scores["course_fit"] * weights.course_fit +
        stat_scores["odds"] * weights.odds
    )

    # Use field strength multiplier of 1.0 for advanced model (simpler)
    fs_mult = 1.0
    probs = _composite_to_probabilities(composite, fs_mult, field_size)

    ev = 0
    for pos, prob in probs.items():
        if isinstance(pos, int):
            payout_pct = PAYOUT_PERCENTAGES.get(pos, 0)
            prize = tournament_purse * payout_pct
            ev += prob * prize

    residual_prob = probs.get("residual_made_cut", 0)
    ev += residual_prob * tournament_purse * 0.0014

    return {
        "ev": round(ev, 0),
        "composite_score": round(composite, 1),
        "win_prob": round(probs.get(1, 0) * 100, 2),
        "top5_prob": round(sum(probs.get(i, 0) for i in range(1, 6)) * 100, 1),
        "top10_prob": round(sum(probs.get(i, 0) for i in range(1, 11)) * 100, 1),
        "top25_prob": round(sum(probs.get(i, 0) for i in range(1, 26)) * 100, 1),
        "make_cut_prob": round(probs.get("make_cut_total", 0) * 100, 1),
        "stat_scores": stat_scores,
    }


@router.post("/calculate-advanced", response_model=AdvancedRecommendationResponse)
def calculate_advanced_recommendations(request: AdvancedRecommendationRequest):
    """Calculate EV recommendations with advanced granular weights."""
    # Get current tournament
    current = get_current_tournament()
    if not current:
        raise HTTPException(status_code=404, detail="No current tournament found")

    if not current.get("purse"):
        raise HTTPException(status_code=400, detail="Tournament purse not available yet")

    # Get data
    skill_ratings = get_skill_ratings()
    advanced_stats = get_advanced_stats_dict()
    field = current.get("field", [])
    fs_score = calculate_field_strength(field, skill_ratings)

    used_set = set(request.used_golfers)
    player_names = [p["player_name"] for p in field if p["player_name"] not in used_set]
    course_fits = get_course_fit_scores(current["name"], player_names)
    odds_data = fetch_tournament_odds(current["name"]) or {}

    # Calculate EV for each player
    results = []
    for player in field:
        name = player.get("player_name", "")
        if not name:
            continue

        # Get advanced stats for player
        player_advanced = advanced_stats.get(name, {})
        if not player_advanced:
            # Fall back to basic skill rating if no advanced stats
            rating = skill_ratings.get(name, {})
            player_advanced = {
                "sg_ott": 0, "sg_app": 0, "sg_arg": 0, "sg_putt": 0,
                "driving_dist": 295, "fairways_pct": 60, "gir_pct": 65,
                "scrambling_pct": 58, "putting_avg": 29,
                "birdie_pct": 16, "par5_scoring": 4.65, "bogey_avoid_pct": 75,
            }

        course_fit = course_fits.get(name, {}).get("score", 50)

        player_odds = _find_odds_for_player(name, odds_data)
        odds_score = None
        odds_display = ""
        if player_odds:
            odds_score = odds_to_skill_bonus(player_odds["odds"])
            odds_display = f"+{player_odds['odds']}" if player_odds["odds"] > 0 else str(player_odds["odds"])

        ev_data = calculate_ev_with_advanced_weights(
            name, current["purse"], player_advanced, course_fit,
            request.weights, len(field), odds_score=odds_score
        )

        results.append({
            "player_name": name,
            "player_id": player.get("player_id", ""),
            "ev": ev_data["ev"],
            "composite_score": ev_data["composite_score"],
            "stat_scores": ev_data["stat_scores"],
            "win_prob": ev_data["win_prob"],
            "top5_prob": ev_data["top5_prob"],
            "top10_prob": ev_data["top10_prob"],
            "make_cut_prob": ev_data["make_cut_prob"],
            "odds": odds_display,
            "odds_score": odds_score,
            "has_advanced_stats": name in advanced_stats,
        })

    results.sort(key=lambda x: x["ev"], reverse=True)

    # Filter available (not used)
    available = [r for r in results if r["player_name"] not in used_set]

    # Calculate season strategy using OWGR-based elite pool
    strategy = calculate_season_strategy(current, request.used_golfers, available)

    # Extract strategy results
    premium_events = strategy["premium_events"]
    n_premium = len(premium_events)
    major_events = [e for e in premium_events if e["tier"] == 1]
    current_tier = strategy["current_tier"]
    is_premium_week = current_tier <= 3

    # Elite tracking based on global OWGR pool
    elite_pool = strategy["elite_pool"]
    elite_count = len(elite_pool)
    elite_threshold = elite_pool[-1]["rank"] if elite_pool else 50

    # Count usable elites (those in field that can be used this week)
    surplus = strategy["usable_elites"]

    # Determine season action and pick rank using OWGR-based strategy
    pick_rank = 0
    golfers = []
    for i, p in enumerate(available):
        name = p["player_name"]
        rec = strategy["recommendations"].get(name, {"action": "USE", "reason": ""})
        action = rec["action"]
        reason = rec["reason"]

        if action == "USE":
            pick_rank += 1
            current_pick_rank = pick_rank
        else:
            current_pick_rank = None

        stat_scores = p.get("stat_scores", {})
        golfers.append(AdvancedGolferEV(
            rank=i + 1,
            player_name=name,
            player_id=p.get("player_id"),
            ev=p["ev"],
            composite_score=p["composite_score"],
            sg_ott_score=stat_scores.get("sg_ott"),
            sg_app_score=stat_scores.get("sg_app"),
            sg_arg_score=stat_scores.get("sg_arg"),
            sg_putt_score=stat_scores.get("sg_putt"),
            driving_dist_score=stat_scores.get("driving_dist"),
            fairways_pct_score=stat_scores.get("fairways_pct"),
            gir_pct_score=stat_scores.get("gir_pct"),
            scrambling_pct_score=stat_scores.get("scrambling_pct"),
            putting_avg_score=stat_scores.get("putting_avg"),
            birdie_pct_score=stat_scores.get("birdie_pct"),
            par5_scoring_score=stat_scores.get("par5_scoring"),
            bogey_avoid_pct_score=stat_scores.get("bogey_avoid_pct"),
            course_fit_score=stat_scores.get("course_fit"),
            odds_score=stat_scores.get("odds"),
            odds=p["odds"] or None,
            win_prob=p["win_prob"],
            top5_prob=p["top5_prob"],
            top10_prob=p["top10_prob"],
            make_cut_prob=p["make_cut_prob"],
            season_action=action,
            pick_rank=current_pick_rank,
            reason=reason,
        ))

    # Recommended pick
    use_picks = [g for g in golfers if g.season_action == "USE"]
    recommended = use_picks[0] if use_picks else golfers[0]

    season_rec = SeasonRecommendation(
        premium_events=n_premium,
        major_events=len(major_events),
        elite_count=elite_count,
        elite_threshold=round(elite_threshold, 1),
        surplus=surplus,
        is_premium_week=is_premium_week,
        recommended_pick=recommended.player_name,
        recommended_ev=recommended.ev,
    )

    return AdvancedRecommendationResponse(
        tournament_name=current["name"],
        tournament_date=current["start_date"],
        purse=current["purse"],
        field_size=len(field),
        field_strength=round(fs_score, 1),
        golfers=golfers,
        season_recommendation=season_rec,
    )
