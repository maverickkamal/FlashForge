from fastapi import APIRouter, UploadFile, File, HTTPException, Depends, Form, Body
from fastapi.params import Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional, Union
from enum import Enum
from pydantic import BaseModel
import json

from app.db.database import get_db
from app.auth.auth import get_current_active_user
from app.auth.models import User
from app.decks.service import DeckService 
from app.flashcards.service import FlashcardService

from app.AI.generator import generate_flashcards

# Define the input types as an Enum for validation
class InputType(str, Enum):
    topic = "topic"
    text = "text"
    image = "image"
    document = "document"

# Request model for generating flashcards
class FlashcardGenerationRequest(BaseModel):
    input_type: InputType
    number: int = 10
    content: Optional[str] = None
    save_to_deck: Optional[bool] = False
    deck_name: Optional[str] = None

# Response model for generated flashcards
class FlashcardItem(BaseModel):
    question: str
    answer: str

class FlashcardsResponse(BaseModel):
    flashcards: List[FlashcardItem]

# Create AI router
ai_router = APIRouter(prefix="/ai", tags=["ai"])

# Create a separate endpoint for file uploads
@ai_router.post("/generate-with-files", response_model=FlashcardsResponse)
async def generate_flashcards_with_files(
    input_type: str = Form(...),
    number: int = Form(10),
    content: Optional[str] = Form(None),
    save_to_deck: bool = Form(False),
    deck_name: Optional[str] = Form(None),
    files: List[UploadFile] = File(...),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Generate flashcards using AI based on image or document files.
    """
    try:
        # Validate input type
        try:
            input_type_enum = InputType(input_type)
        except ValueError:
            raise HTTPException(
                status_code=400, 
                detail=f"Invalid input type: {input_type}"
            )
        
        if input_type_enum not in [InputType.image, InputType.document]:
            raise HTTPException(
                status_code=400,
                detail=f"This endpoint is only for image or document uploads"
            )
            
        # Generate flashcards using the AI service
        result = await generate_flashcards(
            input_types=input_type_enum,
            number=number, 
            input_content=content,
            files=files
        )
        
        # Parse the result into FlashcardItem objects
        try:
            import json
            flashcards_data = json.loads(result)
            flashcards_list = [FlashcardItem(question=card["question"], answer=card["answer"]) 
                               for card in flashcards_data]
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to parse AI response: {str(e)}"
            )
        
        # Save to deck if requested
        if save_to_deck and deck_name:
            # Create a new deck
            new_deck = await DeckService.create_deck(db, deck_name, current_user.id)
            
            # Add flashcards to the deck
            flashcards_to_add = [{"question": card.question, "answer": card.answer} 
                                for card in flashcards_list]
            
            await FlashcardService.create_flashcards_bulk(
                db=db,
                flashcards_data=flashcards_to_add, 
                deck_id=new_deck.id
            )
        
        return FlashcardsResponse(flashcards=flashcards_list)
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate flashcards: {str(e)}"
        )

# Keep the original endpoint for text/topic inputs
@ai_router.post("/generate", response_model=FlashcardsResponse)
async def generate_flashcards_endpoint(
    request: FlashcardGenerationRequest,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Generate flashcards using AI based on topic or text input.
    """
    try:
        # Validate input based on input type
        if request.input_type in [InputType.topic, InputType.text] and not request.content:
            raise HTTPException(
                status_code=400,
                detail=f"Content is required for input type '{request.input_type}'"
            )
        
        if request.input_type in [InputType.image, InputType.document]:
            raise HTTPException(
                status_code=400,
                detail=f"For file uploads, use the /ai/generate-with-files endpoint"
            )
            
        # Generate flashcards using the AI service
        result = await generate_flashcards(
            input_types=request.input_type,
            number=request.number, 
            input_content=request.content,
            files=None
        )
        
        # Parse the result into FlashcardItem objects
        try:
            import json
            flashcards_data = json.loads(result)
            flashcards_list = [FlashcardItem(question=card["question"], answer=card["answer"]) 
                              for card in flashcards_data]
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to parse AI response: {str(e)}"
            )
        
        # Save to deck if requested
        if request.save_to_deck and request.deck_name:
            # Create a new deck
            new_deck = await DeckService.create_deck(db, request.deck_name, current_user.id)
            
            # Add flashcards to the deck
            flashcards_to_add = [{"question": card.question, "answer": card.answer} 
                                for card in flashcards_list]
            
            await FlashcardService.create_flashcards_bulk(
                db=db,
                flashcards_data=flashcards_to_add, 
                deck_id=new_deck.id
            )
        
        return FlashcardsResponse(flashcards=flashcards_list)
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate flashcards: {str(e)}"
        )