import asyncio
import json
import os
import aiohttp
from pprint import pprint

# Base URL for API - make sure this matches your FastAPI server
API_BASE = "http://localhost:8000/api/v1/ai"  # Updated with correct path

# Test user credentials
TEST_EMAIL = "test email"
TEST_PASSWORD = "test password"

async def run_ai_tests():
    """Run tests for the AI flashcard generation API"""
    print("\n🧠 Testing FlashForge AI Flashcard Generation API...\n")
    
    # Even longer timeout for AI processing
    timeout = aiohttp.ClientTimeout(total=180)  # 3 minutes timeout
    
    try:
        # Create a session with TCP keepalive and longer timeouts
        connector = aiohttp.TCPConnector(
            keepalive_timeout=60,
            force_close=False,
            enable_cleanup_closed=True
        )
        
        async with aiohttp.ClientSession(timeout=timeout, connector=connector) as session:
            # Step 1: Login to get access token
            print("🔐 Logging in...")
            login_data = {
                "username": TEST_EMAIL,
                "password": TEST_PASSWORD
            }
            
            login_url = "http://localhost:8000/api/v1/auth/token"
            
            try:
                async with session.post(login_url, data=login_data) as response:
                    if response.status != 200:
                        print(f"❌ Login failed with status {response.status}")
                        print(await response.text())
                        return
                    
                    login_result = await response.json()
                    token = login_result["access_token"]
                    headers = {"Authorization": f"Bearer {token}"}
                    print("✅ Successfully logged in")
            except Exception as e:
                print(f"❌ Login error: {str(e)}")
                return
            
            # Step 2: Test topic-based flashcard generation
            print("\n📚 Testing flashcard generation from topic...")
            topic_data = {
                "input_type": "topic",
                "number": 3,
                "content": "Solar System"
            }
            
            # Add retries for more robust testing
            max_retries = 2
            retry_count = 0
            
            while retry_count <= max_retries:
                try:
                    print(f"Making request to {API_BASE}/generate (attempt {retry_count+1})...")
                    async with session.post(
                        f"{API_BASE}/generate",
                        json=topic_data,
                        headers=headers,
                        timeout=aiohttp.ClientTimeout(total=120)  # Specific timeout for this request
                    ) as response:
                        print(f"Response status: {response.status}")
                        if response.status != 200:
                            print(f"❌ Topic-based generation failed with status {response.status}")
                            response_text = await response.text()
                            print(f"Response text: {response_text}")
                        else:
                            result = await response.json()
                            print(f"✅ Generated {len(result['flashcards'])} flashcards from topic:")
                            for i, card in enumerate(result['flashcards'], 1):
                                print(f"   {i}. Q: {card['question']}")
                                print(f"      A: {card['answer']}")
                            # If successful, break the retry loop
                            break
                except (aiohttp.ClientError, asyncio.TimeoutError) as e:
                    retry_count += 1
                    if retry_count > max_retries:
                        print(f"❌ Failed after {max_retries} attempts: {str(e)}")
                    else:
                        print(f"⚠️ Request failed, retrying ({retry_count}/{max_retries}): {str(e)}")
                        await asyncio.sleep(2)  # Wait before retrying
            
            # Similar retry pattern for text-based generation
            print("\n📝 Testing flashcard generation from text with deck saving...")
            text_data = {
                "input_type": "text",
                "number": 3,
                "content": "Jupiter is the largest planet in our solar system.",
                "save_to_deck": True,
                "deck_name": "AI Generated Astronomy"
            }
            
            retry_count = 0
            while retry_count <= max_retries:
                try:
                    async with session.post(
                        f"{API_BASE}/generate",
                        json=text_data,
                        headers=headers,
                        timeout=aiohttp.ClientTimeout(total=120)
                    ) as response:
                        if response.status != 200:
                            print(f"❌ Text-based generation failed with status {response.status}")
                            print(await response.text())
                        else:
                            result = await response.json()
                            print(f"✅ Generated {len(result['flashcards'])} flashcards from text and saved to deck:")
                            for i, card in enumerate(result['flashcards'], 1):
                                print(f"   {i}. Q: {card['question']}")
                                print(f"      A: {card['answer']}")
                            break  # Success, exit retry loop
                except (aiohttp.ClientError, asyncio.TimeoutError) as e:
                    retry_count += 1
                    if retry_count > max_retries:
                        print(f"❌ Failed after {max_retries} attempts: {str(e)}")
                    else:
                        print(f"⚠️ Request failed, retrying ({retry_count}/{max_retries}): {str(e)}")
                        await asyncio.sleep(2)  # Wait before retrying
            
            # Optional: Test image-based flashcard generation
            image_file_path = "test_image.jpg"
            if os.path.exists(image_file_path):
                print("\n🖼️ Testing flashcard generation from image...")
                
                retry_count = 0
                while retry_count <= max_retries:
                    try:
                        data = aiohttp.FormData()
                        data.add_field('input_type', 'image')
                        data.add_field('number', '3')
                        data.add_field('save_to_deck', 'false')
                        
                        # Open file in each retry attempt to avoid issues with closed file handles
                        with open(image_file_path, 'rb') as f:
                            data.add_field('files', 
                                f,
                                filename='test_image.jpg',
                                content_type='image/jpeg'
                            )
                            
                            async with session.post(
                                f"{API_BASE}/generate-with-files",
                                data=data,
                                headers={"Authorization": f"Bearer {token}"},
                                timeout=aiohttp.ClientTimeout(total=180)  # Longer timeout for image processing
                            ) as response:
                                if response.status != 200:
                                    print(f"❌ Image-based generation failed with status {response.status}")
                                    print(await response.text())
                                else:
                                    result = await response.json()
                                    print(f"✅ Generated {len(result['flashcards'])} flashcards from image:")
                                    for i, card in enumerate(result['flashcards'], 1):
                                        print(f"   {i}. Q: {card['question']}")
                                        print(f"      A: {card['answer']}")
                                    break  # Success, exit retry loop
                    except (aiohttp.ClientError, asyncio.TimeoutError) as e:
                        retry_count += 1
                        if retry_count > max_retries:
                            print(f"❌ Failed after {max_retries} attempts: {str(e)}")
                        else:
                            print(f"⚠️ Request failed, retrying ({retry_count}/{max_retries}): {str(e)}")
                            await asyncio.sleep(2)  # Wait before retrying
            
            print("\n🎯 AI flashcard generation tests completed!")
    
    except Exception as e:
        print(f"❌ Test script error: {str(e)}")
        import traceback
        print(traceback.format_exc())

if __name__ == "__main__":
    asyncio.run(run_ai_tests())