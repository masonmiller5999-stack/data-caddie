"""FastAPI backend for Fantasy Golf Optimizer."""

import sys
import os

# Add project root to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.routes import tournaments, recommendations, golfers, config

app = FastAPI(
    title="Fantasy Golf Optimizer API",
    description="API for the Fantasy Golf Optimizer - Splash Sports League",
    version="1.0.0",
)

# CORS for React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(tournaments.router, prefix="/api/tournaments", tags=["tournaments"])
app.include_router(recommendations.router, prefix="/api/recommendations", tags=["recommendations"])
app.include_router(golfers.router, prefix="/api/golfers", tags=["golfers"])
app.include_router(config.router, prefix="/api/config", tags=["config"])


@app.get("/")
def root():
    """Health check endpoint."""
    return {"status": "ok", "message": "Fantasy Golf Optimizer API"}


@app.get("/api/health")
def health():
    """Health check endpoint."""
    return {"status": "ok"}
