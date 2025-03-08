"""
Test script for flashcards API endpoints.

Usage:
    python test_flashcards.py

This script tests all flashcard endpoints including bulk creation.
"""
import asyncio
import json
import random
from pprint import pprint
import aiohttp

# Base URL for API
API_BASE = "http://localhost:8000/api/v1"

# Test user credentials
TEST_EMAIL = "tammielews@gmail.com"
TEST_PASSWORD = "Kamaludeen@1"

# Test data
test_deck = {"name": "Test Flashcard Deck"}
test_flashcard = {"question": "What is the capital of France?", "answer": "Paris"}
test_flashcards_bulk = {"flashcards": [
    {"question": "What is the capital of Japan?", "answer": "Tokyo"},
    {"question": "What is the capital of Germany?", "answer": "Berlin"},
    {"question": "What is the capital of Italy?", "answer": "Rome"},
    {"question": "What is the capital of Spain?", "answer": "Madrid"},
]}

async def run_tests():
    """Run all tests for flashcards API"""
    print("\n🔍 Testing FlashForge Flashcards API...\n")
    
    # Start a client session
    async with aiohttp.ClientSession() as session:
        # Step 1: Login to get access token
        print("🔐 Logging in...")
        login_data = {
            "username": TEST_EMAIL,
            "password": TEST_PASSWORD
        }
        async with session.post(f"{API_BASE}/auth/token", data=login_data) as response:
            if response.status != 200:
                print(f"❌ Login failed with status {response.status}")
                return
            
            login_result = await response.json()
            token = login_result["access_token"]
            headers = {"Authorization": f"Bearer {token}"}
            print("✅ Successfully logged in")
        
        # Step 2: Create a test deck
        print("\n📚 Creating test deck...")
        async with session.post(f"{API_BASE}/decks", json=test_deck, headers=headers) as response:
            if response.status != 201:
                print(f"❌ Deck creation failed with status {response.status}")
                return
            
            deck = await response.json()
            deck_id = deck["id"]
            print(f"✅ Test deck created with ID: {deck_id}")
        
        # Step 3: Create a single flashcard
        print("\n🔖 Creating single flashcard...")
        async with session.post(
            f"{API_BASE}/decks/{deck_id}/flashcards", 
            json=test_flashcard, 
            headers=headers
        ) as response:
            if response.status != 201:
                print(f"❌ Flashcard creation failed with status {response.status}")
                return
            
            flashcard = await response.json()
            flashcard_id = flashcard["id"]
            print(f"✅ Flashcard created with ID: {flashcard_id}")
            print(f"   Question: {flashcard['question']}")
            print(f"   Answer: {flashcard['answer']}")
        
        # Step 4: Create flashcards in bulk
        print("\n📑 Creating flashcards in bulk...")
        async with session.post(
            f"{API_BASE}/decks/{deck_id}/flashcards/bulk", 
            json=test_flashcards_bulk, 
            headers=headers
        ) as response:
            if response.status != 201:
                print(f"❌ Bulk flashcard creation failed with status {response.status}")
                return
            
            flashcards = await response.json()
            print(f"✅ Created {len(flashcards)} flashcards in bulk:")
            for i, card in enumerate(flashcards, 1):
                print(f"   {i}. Q: {card['question']} | A: {card['answer']}")
        
        # Step 5: Get all flashcards in the deck
        print("\n📋 Getting all flashcards in deck...")
        async with session.get(
            f"{API_BASE}/decks/{deck_id}/flashcards", 
            headers=headers
        ) as response:
            if response.status != 200:
                print(f"❌ Getting flashcards failed with status {response.status}")
                return
            
            flashcards = await response.json()
            print(f"✅ Retrieved {len(flashcards)} flashcards:")
            for i, card in enumerate(flashcards, 1):
                print(f"   {i}. Q: {card['question']} | A: {card['answer']}")
        
        # Step 6: Get a specific flashcard
        print(f"\n🔍 Getting flashcard with ID {flashcard_id}...")
        async with session.get(
            f"{API_BASE}/decks/{deck_id}/flashcards/{flashcard_id}", 
            headers=headers
        ) as response:
            if response.status != 200:
                print(f"❌ Getting flashcard failed with status {response.status}")
                return
            
            flashcard = await response.json()
            print(f"✅ Retrieved flashcard:")
            print(f"   Question: {flashcard['question']}")
            print(f"   Answer: {flashcard['answer']}")
        
        # Step 7: Update a flashcard
        print(f"\n✏️ Updating flashcard with ID {flashcard_id}...")
        updated_data = {
            "question": "What is the capital of France? (Updated)",
            "answer": "Paris, the city of lights!"
        }
        async with session.put(
            f"{API_BASE}/decks/{deck_id}/flashcards/{flashcard_id}", 
            json=updated_data,
            headers=headers
        ) as response:
            if response.status != 200:
                print(f"❌ Updating flashcard failed with status {response.status}")
                return
            
            flashcard = await response.json()
            print(f"✅ Updated flashcard:")
            print(f"   Question: {flashcard['question']}")
            print(f"   Answer: {flashcard['answer']}")
        
        # Step 8: Delete the flashcard
        print(f"\n🗑️ Deleting flashcard with ID {flashcard_id}...")
        async with session.delete(
            f"{API_BASE}/decks/{deck_id}/flashcards/{flashcard_id}", 
            headers=headers
        ) as response:
            if response.status != 204:
                print(f"❌ Deleting flashcard failed with status {response.status}")
                return
            
            print(f"✅ Flashcard deleted successfully")
        
        print("\n🎯 All flashcard tests completed successfully!")

if __name__ == "__main__":
    asyncio.run(run_tests())