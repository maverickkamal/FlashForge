import uuid
from sqlalchemy import Column, String, Boolean
from sqlalchemy.dialects.postgresql import UUID

from app.db.database import Base

class User(Base):
    """User model for authentication"""
    __tablename__ = "users"
    
    id = Column(
        String(length=36), 
        primary_key=True,
        default=lambda: str(uuid.uuid4())
    )
    email = Column(String(length=320), unique=True, index=True, nullable=False)
    hashed_password = Column(String(length=1024), nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    is_superuser = Column(Boolean, default=False, nullable=False)
    is_verified = Column(Boolean, default=False, nullable=False)