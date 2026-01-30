"""Field strength estimation.

Weaker fields mean better expected finishes for top players.
"""


def calculate_field_strength(field, skill_ratings):
    """Calculate field strength score (0-100, higher = stronger field).

    Args:
        field: List of player dicts from tournament details
        skill_ratings: Dict of player_name -> {skill_score, ...}

    Returns:
        float: Field strength score 0-100
    """
    if not field:
        return 50.0  # Default neutral

    # Get skill scores for field players
    skills = []
    for player in field:
        name = player.get("player_name", "")
        rating = skill_ratings.get(name)
        if rating:
            skills.append(rating["skill_score"])

    if not skills:
        return 50.0

    # Field strength = weighted average emphasizing top players
    skills.sort(reverse=True)

    # Top 30 players define the field strength
    top_n = min(30, len(skills))
    top_skills = skills[:top_n]

    return round(sum(top_skills) / len(top_skills), 1)


def field_strength_multiplier(field_strength):
    """Convert field strength to a multiplier for expected finish.

    Weaker field = higher multiplier (better expected finish).
    Stronger field = lower multiplier (worse expected finish).

    Returns multiplier centered around 1.0:
        - 50 (average) -> 1.0
        - 30 (weak) -> 1.3 (30% better expected finish)
        - 70 (strong) -> 0.8 (20% worse expected finish)
    """
    # Linear scaling: each point away from 50 = 1.5% adjustment
    adjustment = (50 - field_strength) * 0.015
    return max(0.5, min(1.5, 1.0 + adjustment))
