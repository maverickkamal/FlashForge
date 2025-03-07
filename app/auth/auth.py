import uuid
from datetime import datetime, timedelta
from typing import Optional
import os

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.models import User
from app.config import settings
from app.db.database import get_db, supabase

# JWT token configuration
SECRET_KEY = settings.SECRET_KEY
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = settings.ACCESS_TOKEN_EXPIRE_MINUTES

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# OAuth2 scheme for token extraction - updated to match our endpoint
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/v1/auth/jwt/login")

# Token model
class Token(BaseModel):
    access_token: str
    token_type: str

# Token data model
class TokenData(BaseModel):
    email: Optional[str] = None

# User data model for responses
class UserOut(BaseModel):
    id: str
    email: str
    is_active: bool
    is_superuser: bool

    class Config:
        from_attributes = True

def verify_password(plain_password, hashed_password):
    """Verify a password against its hash"""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    """Generate password hash"""
    return pwd_context.hash(password)

async def get_user_by_email(db: AsyncSession, email: str):
    """Get a user by email from SQLite or Supabase"""
    # First try SQLite through SQLAlchemy
    result = await db.execute(select(User).where(User.email == email))
    user = result.scalar_one_or_none()
    
    # If user not found in SQLite, try Supabase
    if user is None and not os.getenv("USE_SQLITE", "false").lower() == "true" and supabase:
        try:
            response = supabase.table('users').select('*').eq('email', email).execute()
            if response.data and len(response.data) > 0:
                user_data = response.data[0]
                # Create a User object from Supabase data
                user = User(
                    id=user_data.get('id'),
                    email=user_data.get('email'),
                    hashed_password=user_data.get('hashed_password'),
                    is_active=user_data.get('is_active', True),
                    is_superuser=user_data.get('is_superuser', False),
                    is_verified=user_data.get('is_verified', False)
                )
                print(f"User found in Supabase: {user.email}")
        except Exception as e:
            print(f"Error checking Supabase for user: {e}")
    
    return user

async def authenticate_user(db: AsyncSession, email: str, password: str):
    """Authenticate a user by email and password"""
    user = await get_user_by_email(db, email)
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Create a JWT access token"""
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_user(token: str = Depends(oauth2_scheme), db: AsyncSession = Depends(get_db)):
    """Get current user from JWT token"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
        token_data = TokenData(email=email)
    except JWTError:
        raise credentials_exception
    
    user = await get_user_by_email(db, token_data.email)
    if user is None:
        raise credentials_exception
    return user

async def get_current_active_user(current_user: User = Depends(get_current_user)):
    """Get current active user"""
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user

async def get_current_superuser(current_user: User = Depends(get_current_user)):
    """Get current superuser"""
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    return current_user