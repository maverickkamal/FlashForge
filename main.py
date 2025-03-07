from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import asyncio

from app.api.api import api_router
from app.config import settings
from app.db.init_db import create_tables

# Create FastAPI application
app = FastAPI(
    title="FlashForge API",
    description="API for flashcard management with AI generation capabilities",
    version="0.1.0",
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API router
app.include_router(api_router, prefix="/api/v1")

# Root endpoint
@app.get("/")
async def root():
    return {
        "message": "Welcome to FlashForge API",
        "docs": "/docs",
        "version": "0.1.0"
    }

# Startup event to initialize database
@app.on_event("startup")
async def on_startup():
    # Create database tables if they don't exist
    await create_tables()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)