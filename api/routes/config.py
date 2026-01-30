"""Configuration API endpoints."""

from fastapi import APIRouter

from api.schemas import Weights, AdvancedWeights
from config import (
    WEIGHT_SKILL, WEIGHT_FORM, WEIGHT_COURSE, WEIGHT_FIELD, WEIGHT_ODDS,
)

router = APIRouter()


@router.get("/weights", response_model=Weights)
def get_default_weights():
    """Get the default model weights."""
    return Weights(
        skill=WEIGHT_SKILL,
        form=WEIGHT_FORM,
        course=WEIGHT_COURSE,
        field=WEIGHT_FIELD,
        odds=WEIGHT_ODDS,
    )


@router.get("/advanced-weights", response_model=AdvancedWeights)
def get_advanced_default_weights():
    """Get the default advanced model weights."""
    return AdvancedWeights(
        # Strokes Gained (40% total)
        sg_ott=0.10,
        sg_app=0.12,
        sg_arg=0.08,
        sg_putt=0.10,
        # Ball Striking (20% total)
        driving_dist=0.05,
        fairways_pct=0.07,
        gir_pct=0.08,
        # Short Game (15% total)
        scrambling_pct=0.10,
        putting_avg=0.05,
        # Scoring (10% total)
        birdie_pct=0.04,
        par5_scoring=0.03,
        bogey_avoid_pct=0.03,
        # Context (15% total)
        course_fit=0.08,
        odds=0.07,
    )
