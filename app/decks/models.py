from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship

from app.db.database import Base

class Deck(Base):
    """Deck model for flashcard decks"""
    __tablename__ = "decks"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    
    # Relationship to flashcards - will be defined once we implement flashcards
    # flashcards = relationship("Flashcard", back_populates="deck", cascade="all, delete-orphan")
    
    # Convert to dict for Supabase API
    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "user_id": self.user_id
        }