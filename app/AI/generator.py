from google import genai
from google.genai import types
from pydantic import BaseModel
from app.AI.utils import load_images, upload_documents
from fastapi import File, UploadFile
from app.AI.prompts import system_message, prompt_flashforge
import os
from dotenv import load_dotenv
from typing import List, Optional, Union
import json

load_dotenv()

# Use the key from settings
from app.config import settings
client = genai.Client(api_key=settings.LLM_API_KEY)

class Flashcard(BaseModel):
    """Flashcard model for API request and response."""
    question: str
    answer: str

async def generate_flashcards(
    input_types: str, 
    number: int, 
    input_content: Optional[str] = None, 
    files: Optional[Union[UploadFile, List[UploadFile]]] = None
):
    """Generate flashcards based on the input provided.
    
    Args:
        input_types: Type of input (topic, text, image, document)
        number: Number of flashcards to generate
        input_content: Text content for topic or text input types
        files: File(s) for image or document input types
        
    Returns:
        string: JSON string containing the generated flashcards
    """
    # Generate prompt for FlashForge
    prompt = [prompt_flashforge(input_types, number, input_content)]
    
    # Load images or documents if provided
    if files:
        if input_types == "image":
            images = await load_images(files)
            # Add images to prompt
            prompt.extend(images)
        elif input_types == "document":
            documents = await upload_documents(files)
            # Add documents to prompt
            prompt.extend(documents)
    
    # Generate flashcards using Google Generative AI
    try:
        response = client.models.generate_content(
            model="gemini-2.0-flash-lite",
            contents=prompt,
            config=types.GenerateContentConfig(
                system_instruction=system_message,
                max_output_tokens=8192,
                temperature=0.9,
                response_mime_type="application/json",
                response_schema=list[Flashcard],
            )
        )
        
        # Process the response to ensure it's in the expected format
        try:
            # The response.text might contain a JSON array or other format
            # We need to ensure it's formatted as expected by our API
            raw_text = response.text
            
            # Try to parse the JSON response
            parsed_data = json.loads(raw_text)
            
            # If parsed_data is not a list, wrap it in a list
            if not isinstance(parsed_data, list):
                if isinstance(parsed_data, dict) and "flashcards" in parsed_data:
                    # If it's a dict with a "flashcards" key, use that
                    parsed_data = parsed_data["flashcards"]
                else:
                    # Otherwise wrap it in a list
                    parsed_data = [parsed_data]
            
            # Ensure each item has question and answer fields
            for item in parsed_data:
                if not isinstance(item, dict) or "question" not in item or "answer" not in item:
                    raise ValueError("Response items must have 'question' and 'answer' fields")
            
            # Convert back to JSON string in the expected format
            return json.dumps(parsed_data)
            
        except Exception as e:
            print(f"Error processing AI response: {e}")
            print(f"Raw response: {raw_text}")
            raise ValueError(f"Failed to parse AI response: {e}")
    
    except Exception as e:
        # Log the error and re-raise
        print(f"Error generating flashcards: {e}")
        raise e