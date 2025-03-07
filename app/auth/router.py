from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel, EmailStr, ConfigDict
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import timedelta
import uuid
import os

from app.auth.auth import (
    Token, UserOut, authenticate_user, create_access_token, 
    get_current_active_user, get_password_hash, ACCESS_TOKEN_EXPIRE_MINUTES
)
from app.auth.models import User
from app.db.database import get_db, supabase

# User creation request model
class UserCreate(BaseModel):
    email: EmailStr
    password: str

# Create auth router
auth_router = APIRouter(prefix="/auth", tags=["auth"])

@auth_router.post("/register", response_model=UserOut)
async def register_user(user_data: UserCreate, db: AsyncSession = Depends(get_db)):
    """Register a new user"""
    # Check if user already exists
    from app.auth.auth import get_user_by_email
    
    user = await get_user_by_email(db, user_data.email)
    if user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Generate user ID
    user_id = str(uuid.uuid4())
    
    # Create new user
    hashed_password = get_password_hash(user_data.password)
    new_user = User(
        id=user_id,
        email=user_data.email,
        hashed_password=hashed_password,
        is_active=True,
        is_superuser=False,
        is_verified=False
    )
    
    # ALWAYS try Supabase first - only use SQLite as fallback
    supabase_success = False
    if supabase:
        try:
            # Insert user directly via Supabase API
            user_data = new_user.to_dict()
            response = supabase.table('users').insert(user_data).execute()
            if response and response.data:
                print(f"✅ User created in Supabase: {new_user.email}")
                supabase_success = True
            else:
                print(f"⚠️ Empty response when creating user in Supabase")
        except Exception as e:
            print(f"❌ Error creating user in Supabase: {e}")
    
    # Only use SQLite if Supabase failed or isn't available
    if not supabase_success:
        print(f"⚠️ Falling back to SQLite for user {new_user.email}")
        db.add(new_user)
        await db.commit()
        await db.refresh(new_user)
    
    return new_user

@auth_router.post("/token", response_model=Token)
@auth_router.post("/jwt/login", response_model=Token)  # Adding alternative login endpoint
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_db)):
    """Get an access token using username and password"""
    user = await authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    
    return {"access_token": access_token, "token_type": "bearer"}

@auth_router.get("/me", response_model=UserOut)
async def read_users_me(current_user: User = Depends(get_current_active_user)):
    """Get current user information"""
    return current_user