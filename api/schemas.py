"""Pydantic models for API request/response validation."""

from pydantic import BaseModel
from typing import Optional


class Weights(BaseModel):
    """Model weights for EV calculation."""
    skill: float = 0.35
    form: float = 0.10
    course: float = 0.15
    field: float = 0.10
    odds: float = 0.30


class AdvancedWeights(BaseModel):
    """Advanced model weights with granular golf metrics."""
    # Strokes Gained breakdown (40% default)
    sg_ott: float = 0.10        # SG Off-the-Tee
    sg_app: float = 0.12        # SG Approach
    sg_arg: float = 0.08        # SG Around Green
    sg_putt: float = 0.10       # SG Putting
    # Ball Striking (20% default)
    driving_dist: float = 0.05  # Driving Distance
    fairways_pct: float = 0.07  # Fairways Hit %
    gir_pct: float = 0.08       # Greens in Regulation
    # Short Game (15% default)
    scrambling_pct: float = 0.10  # Scrambling %
    putting_avg: float = 0.05     # Putting Average
    # Scoring (10% default)
    birdie_pct: float = 0.04      # Birdie %
    par5_scoring: float = 0.03    # Par 5 Scoring
    bogey_avoid_pct: float = 0.03 # Bogey Avoidance
    # Context (15% default)
    course_fit: float = 0.08    # Course Fit
    odds: float = 0.07          # Betting Odds


class RecommendationRequest(BaseModel):
    """Request body for /recommendations/calculate."""
    weights: Weights
    used_golfers: list[str] = []


class AdvancedRecommendationRequest(BaseModel):
    """Request body for /recommendations/calculate-advanced."""
    weights: AdvancedWeights
    used_golfers: list[str] = []


class GolferEV(BaseModel):
    """EV result for a single golfer."""
    rank: int
    player_name: str
    player_id: Optional[str] = None
    ev: float
    skill_score: float
    sg_total: Optional[float] = None
    owgr_rank: Optional[int] = None
    form_label: str
    course_label: str
    odds: Optional[str] = None
    win_prob: float
    top5_prob: float
    top10_prob: float
    make_cut_prob: float
    season_action: str
    pick_rank: Optional[int] = None
    reason: str


class AdvancedGolferEV(BaseModel):
    """EV result with advanced stats breakdown."""
    rank: int
    player_name: str
    player_id: Optional[str] = None
    ev: float
    composite_score: float
    # Strokes Gained scores (normalized 0-100)
    sg_ott_score: Optional[float] = None
    sg_app_score: Optional[float] = None
    sg_arg_score: Optional[float] = None
    sg_putt_score: Optional[float] = None
    # Ball Striking scores
    driving_dist_score: Optional[float] = None
    fairways_pct_score: Optional[float] = None
    gir_pct_score: Optional[float] = None
    # Short Game scores
    scrambling_pct_score: Optional[float] = None
    putting_avg_score: Optional[float] = None
    # Scoring scores
    birdie_pct_score: Optional[float] = None
    par5_scoring_score: Optional[float] = None
    bogey_avoid_pct_score: Optional[float] = None
    # Context scores
    course_fit_score: Optional[float] = None
    odds_score: Optional[float] = None
    # Probabilities
    odds: Optional[str] = None
    win_prob: float
    top5_prob: float
    top10_prob: float
    make_cut_prob: float
    season_action: str
    pick_rank: Optional[int] = None
    reason: str


class SeasonRecommendation(BaseModel):
    """Season-aware recommendation details."""
    premium_events: int
    major_events: int
    elite_count: int
    elite_threshold: float
    surplus: int
    is_premium_week: bool
    recommended_pick: str
    recommended_ev: float


class RecommendationResponse(BaseModel):
    """Response from /recommendations/calculate."""
    tournament_name: str
    tournament_date: str
    purse: int
    field_size: int
    field_strength: float
    golfers: list[GolferEV]
    season_recommendation: SeasonRecommendation


class AdvancedRecommendationResponse(BaseModel):
    """Response from /recommendations/calculate-advanced."""
    tournament_name: str
    tournament_date: str
    purse: int
    field_size: int
    field_strength: float
    golfers: list[AdvancedGolferEV]
    season_recommendation: SeasonRecommendation


class Tournament(BaseModel):
    """Tournament details."""
    id: str
    name: str
    start_date: str
    purse: Optional[int] = None
    major: bool = False
    status: str
    field_size: int = 0


class UsedGolfer(BaseModel):
    """A golfer that has been used."""
    name: str
    tournament: Optional[str] = None
    earnings: Optional[float] = None


class AddGolferRequest(BaseModel):
    """Request to add a used golfer."""
    name: str
    tournament: Optional[str] = None


class SeasonSummary(BaseModel):
    """Season summary stats."""
    total_earnings: float
    picks_made: int
    completed: int
    picks: list[UsedGolfer]


class GolferSearchResult(BaseModel):
    """Golfer search result for autocomplete."""
    name: str
    rank: Optional[int] = None
    skill_score: Optional[float] = None
