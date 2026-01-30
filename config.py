"""Configuration for Fantasy Golf Optimizer."""

import os

# Season
SEASON_YEAR = 2026

# ESPN API endpoints
ESPN_BASE = "https://site.api.espn.com/apis/site/v2/sports/golf"
ESPN_SCOREBOARD = f"{ESPN_BASE}/pga/scoreboard"
ESPN_LEADERBOARD = f"{ESPN_BASE}/leaderboard"

# Cache settings
CACHE_DIR = os.path.join(os.path.dirname(__file__), "data", "cache")
CACHE_EXPIRY_HOURS = 12  # Re-fetch data after 12 hours

# Tracker files
TRACKER_DIR = os.path.join(os.path.dirname(__file__), "tracker")
USED_GOLFERS_FILE = os.path.join(TRACKER_DIR, "used_golfers.json")
SEASON_RESULTS_FILE = os.path.join(TRACKER_DIR, "season_results.json")

# Model weights for EV calculation
# When odds are available, they replace form weight (market is smarter)
WEIGHT_SKILL = 0.35
WEIGHT_FORM = 0.10
WEIGHT_COURSE = 0.15
WEIGHT_FIELD = 0.10
WEIGHT_ODDS = 0.30  # Betting market implied probability

# Fallback weights when odds are NOT available (future tournaments)
WEIGHT_SKILL_NO_ODDS = 0.50
WEIGHT_FORM_NO_ODDS = 0.20
WEIGHT_COURSE_NO_ODDS = 0.20
WEIGHT_FIELD_NO_ODDS = 0.10

# Known major purses (estimated for 2026 based on recent trends)
MAJOR_PURSES = {
    "Masters Tournament": 20_000_000,
    "PGA Championship": 18_500_000,
    "U.S. Open": 21_500_000,
    "The Open": 17_500_000,
}

# PGA Tour standard payout percentages (top positions)
# Based on standard 156-player field with 65+ties making cut
PAYOUT_PERCENTAGES = {
    1: 0.180,
    2: 0.109,
    3: 0.069,
    4: 0.049,
    5: 0.041,
    6: 0.036,
    7: 0.0335,
    8: 0.031,
    9: 0.029,
    10: 0.027,
    11: 0.025,
    12: 0.023,
    13: 0.0215,
    14: 0.020,
    15: 0.019,
    16: 0.018,
    17: 0.017,
    18: 0.016,
    19: 0.015,
    20: 0.014,
    21: 0.013,
    22: 0.012,
    23: 0.0111,
    24: 0.0103,
    25: 0.0095,
    26: 0.0087,
    27: 0.0081,
    28: 0.0076,
    29: 0.0071,
    30: 0.0066,
    31: 0.0062,
    32: 0.0058,
    33: 0.0054,
    34: 0.00505,
    35: 0.0047,
    36: 0.0044,
    37: 0.00415,
    38: 0.0039,
    39: 0.00365,
    40: 0.0034,
    41: 0.0032,
    42: 0.003,
    43: 0.0028,
    44: 0.0026,
    45: 0.0024,
    46: 0.00224,
    47: 0.0021,
    48: 0.00198,
    49: 0.00188,
    50: 0.0018,
    51: 0.00176,
    52: 0.00172,
    53: 0.00168,
    54: 0.00164,
    55: 0.00162,
    56: 0.0016,
    57: 0.00158,
    58: 0.00156,
    59: 0.00154,
    60: 0.00152,
    61: 0.0015,
    62: 0.00148,
    63: 0.00146,
    64: 0.00144,
    65: 0.00142,
}
