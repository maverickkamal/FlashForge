from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel

from app.db.database import get_db
from app.auth.auth import get_current_active_user
from app.auth.models import User
from app.decks.service import DeckService

# Response and request models
class DeckBase(BaseModel):
    name: str

class DeckCreate(DeckBase):
    pass

class DeckResponse(DeckBase):
    id: int
    
    class Config:
        from_attributes = True

# Create decks router
decks_router = APIRouter(prefix="/decks", tags=["decks"])

@decks_router.post("", response_model=DeckResponse, status_code=status.HTTP_201_CREATED)
async def create_deck(
    deck_data: DeckCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Create a new deck for the current user"""
    deck = await DeckService.create_deck(db, deck_data.name, current_user.id)
    return DeckResponse.model_validate(deck)

@decks_router.get("", response_model=List[DeckResponse])
async def get_decks(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get all decks for the current user"""
    decks = await DeckService.get_decks(db, current_user.id)
    return [DeckResponse.model_validate(deck) for deck in decks]

@decks_router.get("/{deck_id}", response_model=DeckResponse)
async def get_deck(
    deck_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get a specific deck by ID"""
    deck = await DeckService.get_deck(db, deck_id, current_user.id)
    if not deck:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Deck with ID {deck_id} not found"
        )
    return DeckResponse.model_validate(deck)

@decks_router.put("/{deck_id}", response_model=DeckResponse)
async def update_deck(
    deck_id: int,
    deck_data: DeckCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Update a deck's name"""
    deck = await DeckService.update_deck(db, deck_id, deck_data.name, current_user.id)
    if not deck:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Deck with ID {deck_id} not found"
        )
    return DeckResponse.model_validate(deck)

@decks_router.delete("/{deck_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_deck(
    deck_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Delete a deck"""
    success = await DeckService.delete_deck(db, deck_id, current_user.id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Deck with ID {deck_id} not found"
        )
    return None