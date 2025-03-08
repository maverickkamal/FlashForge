from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship

from app.db.database import Base

class Flashcard(Base):
    """Flashcard model for question-answer pairs"""
    __tablename__ = "flashcards"
    
    id = Column(Integer, primary_key=True, index=True)
    question = Column(String, nullable=False)
    answer = Column(String, nullable=False)
    deck_id = Column(Integer, ForeignKey("decks.id", ondelete="CASCADE"), nullable=False)
    
    # Relationship to deck
    deck = relationship("Deck", back_populates="flashcards")
    
    # Convert to dict for Supabase API
    def to_dict(self):
        return {
            "id": self.id,
            "question": self.question,
            "answer": self.answer,
            "deck_id": self.deck_id
        }