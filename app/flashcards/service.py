from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.flashcards.models import Flashcard
from app.decks.models import Deck
from app.db.database import supabase

class FlashcardService:
    """Service for flashcard operations"""
    
    @staticmethod
    async def create_flashcard(db: AsyncSession, question: str, answer: str, deck_id: int) -> Flashcard:
        """Create a new flashcard"""
        # Create new flashcard instance
        flashcard = Flashcard(question=question, answer=answer, deck_id=deck_id)
        
        # Try to insert into Supabase first
        supabase_success = False
        if supabase:
            try:
                # Insert flashcard directly via Supabase API
                flashcard_data = flashcard.to_dict()
                # For Supabase, we shouldn't include the id for a table with SERIAL primary key
                if 'id' in flashcard_data:
                    del flashcard_data['id']
                response = supabase.table('flashcards').insert(flashcard_data).execute()
                if response and response.data:
                    # Get the generated ID from Supabase
                    flashcard.id = response.data[0]['id']
                    print(f"✅ Flashcard created in Supabase: {flashcard.id}")
                    supabase_success = True
                else:
                    print(f"⚠️ Empty response when creating flashcard in Supabase")
            except Exception as e:
                print(f"❌ Error creating flashcard in Supabase: {e}")
        
        # Fall back to SQLite if Supabase fails
        if not supabase_success:
            print(f"⚠️ Falling back to SQLite for flashcard creation")
            db.add(flashcard)
            await db.commit()
            await db.refresh(flashcard)
        
        return flashcard
        
    @staticmethod
    async def create_flashcards_bulk(
        db: AsyncSession, flashcards_data: List[dict], deck_id: int
    ) -> List[Flashcard]:
        """Create multiple flashcards at once"""
        created_flashcards = []
        
        # Try to insert into Supabase first (bulk insert)
        supabase_success = False
        if supabase and flashcards_data:
            try:
                # Prepare data for Supabase
                supabase_data = []
                for card_data in flashcards_data:
                    supabase_data.append({
                        "question": card_data.get("question"),
                        "answer": card_data.get("answer"),
                        "deck_id": deck_id
                    })
                
                # Bulk insert via Supabase API
                response = supabase.table('flashcards').insert(supabase_data).execute()
                if response and response.data:
                    # Convert response data to Flashcard objects
                    for card_data in response.data:
                        card = Flashcard(
                            id=card_data.get('id'),
                            question=card_data.get('question'),
                            answer=card_data.get('answer'),
                            deck_id=card_data.get('deck_id')
                        )
                        created_flashcards.append(card)
                    print(f"✅ {len(created_flashcards)} flashcards created in Supabase")
                    supabase_success = True
                else:
                    print(f"⚠️ Empty response when bulk creating flashcards in Supabase")
            except Exception as e:
                print(f"❌ Error bulk creating flashcards in Supabase: {e}")
        
        # Fall back to SQLite if Supabase fails
        if not supabase_success:
            print(f"⚠️ Falling back to SQLite for flashcard bulk creation")
            for card_data in flashcards_data:
                flashcard = Flashcard(
                    question=card_data.get("question"),
                    answer=card_data.get("answer"),
                    deck_id=deck_id
                )
                db.add(flashcard)
                created_flashcards.append(flashcard)
            
            await db.commit()
            # Refresh to get the generated IDs
            for flashcard in created_flashcards:
                await db.refresh(flashcard)
        
        return created_flashcards
    
    @staticmethod
    async def get_flashcards(db: AsyncSession, deck_id: int) -> List[Flashcard]:
        """Get all flashcards for a deck"""
        flashcards = []
        
        # First try Supabase
        if supabase:
            try:
                response = supabase.table('flashcards').select('*').eq('deck_id', deck_id).execute()
                if response and response.data:
                    # Convert to Flashcard objects
                    for card_data in response.data:
                        flashcards.append(Flashcard(**card_data))
                    return flashcards
            except Exception as e:
                print(f"❌ Error fetching flashcards from Supabase: {e}")
        
        # Fall back to SQLite
        query = select(Flashcard).where(Flashcard.deck_id == deck_id)
        result = await db.execute(query)
        sqlite_flashcards = result.scalars().all()
        
        # If we already have flashcards from Supabase, don't add duplicates
        if flashcards:
            # Add any flashcards from SQLite that aren't already in the list
            card_ids = {card.id for card in flashcards}
            for card in sqlite_flashcards:
                if card.id not in card_ids:
                    flashcards.append(card)
        else:
            flashcards = list(sqlite_flashcards)
            
        return flashcards
    
    @staticmethod
    async def get_flashcard(db: AsyncSession, card_id: int, deck_id: int) -> Optional[Flashcard]:
        """Get a specific flashcard by ID"""
        # First try Supabase
        if supabase:
            try:
                response = supabase.table('flashcards').select('*').eq('id', card_id).eq('deck_id', deck_id).execute()
                if response and response.data and len(response.data) > 0:
                    return Flashcard(**response.data[0])
            except Exception as e:
                print(f"❌ Error fetching flashcard from Supabase: {e}")
        
        # Fall back to SQLite
        query = select(Flashcard).where(Flashcard.id == card_id, Flashcard.deck_id == deck_id)
        result = await db.execute(query)
        card = result.scalar_one_or_none()
        
        return card
    
    @staticmethod
    async def update_flashcard(db: AsyncSession, card_id: int, deck_id: int, question: str, answer: str) -> Optional[Flashcard]:
        """Update a flashcard's content"""
        # First get the flashcard to ensure it exists and belongs to the deck
        card = await FlashcardService.get_flashcard(db, card_id, deck_id)
        if not card:
            return None
        
        # Update the content
        card.question = question
        card.answer = answer
        
        # Try to update in Supabase first
        supabase_success = False
        if supabase:
            try:
                response = supabase.table('flashcards').update({
                    "question": question,
                    "answer": answer
                }).eq('id', card_id).eq('deck_id', deck_id).execute()
                
                if response:
                    supabase_success = True
                    print(f"✅ Flashcard updated in Supabase: {card_id}")
            except Exception as e:
                print(f"❌ Error updating flashcard in Supabase: {e}")
        
        # Fall back to SQLite if Supabase update fails
        if not supabase_success:
            print(f"⚠️ Falling back to SQLite for flashcard update")
            await db.commit()
            await db.refresh(card)
        
        return card
    
    @staticmethod
    async def delete_flashcard(db: AsyncSession, card_id: int, deck_id: int) -> bool:
        """Delete a flashcard"""
        # First get the flashcard to ensure it exists and belongs to the deck
        card = await FlashcardService.get_flashcard(db, card_id, deck_id)
        if not card:
            return False
        
        # Try to delete from Supabase first
        supabase_success = False
        if supabase:
            try:
                response = supabase.table('flashcards').delete().eq('id', card_id).eq('deck_id', deck_id).execute()
                if response:
                    supabase_success = True
                    print(f"✅ Flashcard deleted from Supabase: {card_id}")
            except Exception as e:
                print(f"❌ Error deleting flashcard from Supabase: {e}")
        
        # Fall back to SQLite if Supabase delete fails
        if not supabase_success:
            print(f"⚠️ Falling back to SQLite for flashcard deletion")
            await db.delete(card)
            await db.commit()
        
        return True