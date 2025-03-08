from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel

from app.db.database import get_db
from app.auth.auth import get_current_active_user
from app.auth.models import User
from app.decks.service import DeckService
from app.flashcards.service import FlashcardService

# Response and request models
class FlashcardBase(BaseModel):
    question: str
    answer: str

class FlashcardCreate(FlashcardBase):
    pass

class FlashcardResponse(FlashcardBase):
    id: int
    deck_id: int
    
    class Config:
        from_attributes = True

# For bulk creation
class FlashcardBulkCreate(BaseModel):
    flashcards: List[FlashcardBase]

# Create flashcards router
flashcards_router = APIRouter(prefix="/decks/{deck_id}/flashcards", tags=["flashcards"])

@flashcards_router.post("", response_model=FlashcardResponse, status_code=status.HTTP_201_CREATED)
async def create_flashcard(
    deck_id: int,
    flashcard_data: FlashcardCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Create a new flashcard in the deck"""
    # First check if deck exists and belongs to user
    deck = await DeckService.get_deck(db, deck_id, current_user.id)
    if not deck:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Deck with ID {deck_id} not found"
        )
    
    # Create the flashcard
    flashcard = await FlashcardService.create_flashcard(
        db, 
        flashcard_data.question, 
        flashcard_data.answer, 
        deck_id
    )
    
    return FlashcardResponse.model_validate(flashcard)

@flashcards_router.post("/bulk", response_model=List[FlashcardResponse], status_code=status.HTTP_201_CREATED)
async def create_flashcards_bulk(
    deck_id: int,
    flashcards_data: FlashcardBulkCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Create multiple flashcards at once in the deck"""
    # First check if deck exists and belongs to user
    deck = await DeckService.get_deck(db, deck_id, current_user.id)
    if not deck:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Deck with ID {deck_id} not found"
        )
    
    # Prepare data for bulk creation
    cards_data = [
        {"question": card.question, "answer": card.answer}
        for card in flashcards_data.flashcards
    ]
    
    # Create flashcards in bulk
    flashcards = await FlashcardService.create_flashcards_bulk(
        db, 
        cards_data, 
        deck_id
    )
    
    return [FlashcardResponse.model_validate(card) for card in flashcards]

@flashcards_router.get("", response_model=List[FlashcardResponse])
async def get_flashcards(
    deck_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get all flashcards in a deck"""
    # First check if deck exists and belongs to user
    deck = await DeckService.get_deck(db, deck_id, current_user.id)
    if not deck:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Deck with ID {deck_id} not found"
        )
    
    # Get flashcards for the deck
    flashcards = await FlashcardService.get_flashcards(db, deck_id)
    return [FlashcardResponse.model_validate(card) for card in flashcards]

@flashcards_router.get("/{flashcard_id}", response_model=FlashcardResponse)
async def get_flashcard(
    deck_id: int,
    flashcard_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get a specific flashcard by ID"""
    # First check if deck exists and belongs to user
    deck = await DeckService.get_deck(db, deck_id, current_user.id)
    if not deck:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Deck with ID {deck_id} not found"
        )
    
    # Get the flashcard
    flashcard = await FlashcardService.get_flashcard(db, flashcard_id, deck_id)
    if not flashcard:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Flashcard with ID {flashcard_id} not found in deck {deck_id}"
        )
    
    return FlashcardResponse.model_validate(flashcard)

@flashcards_router.put("/{flashcard_id}", response_model=FlashcardResponse)
async def update_flashcard(
    deck_id: int,
    flashcard_id: int,
    flashcard_data: FlashcardCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Update a flashcard's content"""
    # First check if deck exists and belongs to user
    deck = await DeckService.get_deck(db, deck_id, current_user.id)
    if not deck:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Deck with ID {deck_id} not found"
        )
    
    # Update the flashcard
    flashcard = await FlashcardService.update_flashcard(
        db,
        flashcard_id,
        deck_id,
        flashcard_data.question,
        flashcard_data.answer
    )
    
    if not flashcard:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Flashcard with ID {flashcard_id} not found in deck {deck_id}"
        )
    
    return FlashcardResponse.model_validate(flashcard)

@flashcards_router.delete("/{flashcard_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_flashcard(
    deck_id: int,
    flashcard_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Delete a flashcard"""
    # First check if deck exists and belongs to user
    deck = await DeckService.get_deck(db, deck_id, current_user.id)
    if not deck:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Deck with ID {deck_id} not found"
        )
    
    # Delete the flashcard
    success = await FlashcardService.delete_flashcard(db, flashcard_id, deck_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Flashcard with ID {flashcard_id} not found in deck {deck_id}"
        )
    
    return None