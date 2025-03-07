from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status

from app.decks.models import Deck
from app.db.database import supabase

class DeckService:
    """Service for deck operations"""
    
    @staticmethod
    async def create_deck(db: AsyncSession, name: str, user_id: str) -> Deck:
        """Create a new deck for a user"""
        # Create new deck instance
        deck = Deck(name=name, user_id=user_id)
        
        # Try to insert into Supabase first
        supabase_success = False
        if supabase:
            try:
                # Insert deck directly via Supabase API
                deck_data = deck.to_dict()
                # For Supabase, we shouldn't include the id for a table with SERIAL primary key
                if 'id' in deck_data:
                    del deck_data['id']
                response = supabase.table('decks').insert(deck_data).execute()
                if response and response.data:
                    # Get the generated ID from Supabase
                    deck.id = response.data[0]['id']
                    print(f"✅ Deck created in Supabase: {deck.id}")
                    supabase_success = True
                else:
                    print(f"⚠️ Empty response when creating deck in Supabase")
            except Exception as e:
                print(f"❌ Error creating deck in Supabase: {e}")
        
        # Fall back to SQLite if Supabase fails
        if not supabase_success:
            print(f"⚠️ Falling back to SQLite for deck creation")
            db.add(deck)
            await db.commit()
            await db.refresh(deck)
        
        return deck
    
    @staticmethod
    async def get_decks(db: AsyncSession, user_id: str) -> List[Deck]:
        """Get all decks for a user"""
        decks = []
        
        # First try Supabase
        if supabase:
            try:
                response = supabase.table('decks').select('*').eq('user_id', user_id).execute()
                if response and response.data:
                    # Convert to Deck objects
                    for deck_data in response.data:
                        decks.append(Deck(**deck_data))
                    return decks
            except Exception as e:
                print(f"❌ Error fetching decks from Supabase: {e}")
        
        # Fall back to SQLite
        query = select(Deck).where(Deck.user_id == user_id)
        result = await db.execute(query)
        sqlite_decks = result.scalars().all()
        
        # If we already have decks from Supabase, don't add duplicates
        if decks:
            # Add any decks from SQLite that aren't already in the list
            deck_ids = {deck.id for deck in decks}
            for deck in sqlite_decks:
                if deck.id not in deck_ids:
                    decks.append(deck)
        else:
            decks = list(sqlite_decks)
            
        return decks
    
    @staticmethod
    async def get_deck(db: AsyncSession, deck_id: int, user_id: str) -> Optional[Deck]:
        """Get a specific deck by ID for a user"""
        # First try Supabase
        if supabase:
            try:
                response = supabase.table('decks').select('*').eq('id', deck_id).eq('user_id', user_id).execute()
                if response and response.data and len(response.data) > 0:
                    return Deck(**response.data[0])
            except Exception as e:
                print(f"❌ Error fetching deck from Supabase: {e}")
        
        # Fall back to SQLite
        query = select(Deck).where(Deck.id == deck_id, Deck.user_id == user_id)
        result = await db.execute(query)
        deck = result.scalar_one_or_none()
        
        return deck
    
    @staticmethod
    async def update_deck(db: AsyncSession, deck_id: int, name: str, user_id: str) -> Optional[Deck]:
        """Update a deck's name"""
        # First get the deck to ensure it exists and belongs to the user
        deck = await DeckService.get_deck(db, deck_id, user_id)
        if not deck:
            return None
        
        # Update the name
        deck.name = name
        
        # Try to update in Supabase first
        supabase_success = False
        if supabase:
            try:
                response = supabase.table('decks').update({"name": name}).eq('id', deck_id).eq('user_id', user_id).execute()
                if response:
                    supabase_success = True
                    print(f"✅ Deck updated in Supabase: {deck_id}")
            except Exception as e:
                print(f"❌ Error updating deck in Supabase: {e}")
        
        # Fall back to SQLite if Supabase update fails
        if not supabase_success:
            print(f"⚠️ Falling back to SQLite for deck update")
            await db.commit()
            await db.refresh(deck)
        
        return deck
    
    @staticmethod
    async def delete_deck(db: AsyncSession, deck_id: int, user_id: str) -> bool:
        """Delete a deck"""
        # First get the deck to ensure it exists and belongs to the user
        deck = await DeckService.get_deck(db, deck_id, user_id)
        if not deck:
            return False
        
        # Try to delete from Supabase first
        supabase_success = False
        if supabase:
            try:
                response = supabase.table('decks').delete().eq('id', deck_id).eq('user_id', user_id).execute()
                if response:
                    supabase_success = True
                    print(f"✅ Deck deleted from Supabase: {deck_id}")
            except Exception as e:
                print(f"❌ Error deleting deck from Supabase: {e}")
        
        # Fall back to SQLite if Supabase delete fails
        if not supabase_success:
            print(f"⚠️ Falling back to SQLite for deck deletion")
            await db.delete(deck)
            await db.commit()
        
        return True