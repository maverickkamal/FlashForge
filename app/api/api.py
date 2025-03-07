from fastapi import APIRouter

from app.auth.router import auth_router
from app.decks.router import decks_router

# Main API router
api_router = APIRouter()

# Include authentication routes
api_router.include_router(auth_router)

# Include deck routes
api_router.include_router(decks_router)

# Later we will include routes for flashcards and AI generation
# api_router.include_router(flashcards_router)
# api_router.include_router(ai_router)