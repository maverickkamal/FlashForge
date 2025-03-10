from google import genai
from PIL import Image
import io
from typing import List, Union, Dict, Optional
from fastapi import UploadFile
import os
from dotenv import load_dotenv

# Import settings from app config
from app.config import settings

load_dotenv()

# Use the key from settings
client = genai.Client(api_key=settings.LLM_API_KEY)

async def load_images(files: Union[UploadFile, List[UploadFile]]) -> List[Image.Image]:
    """
    Loads images from FastAPI's UploadFile objects and opens each with PIL.
    
    Args:
        files: Either a single UploadFile or a list of UploadFile objects
    
    Returns:
        list: A list of opened PIL Image objects
    """
    images = []
    
    # Convert to list if single file
    if not isinstance(files, list):
        files = [files]
    
    # Process each file
    for file in files:
        try:
            # Read file content asynchronously
            contents = await file.read()
            
            # Open image with PIL
            img = Image.open(io.BytesIO(contents))
            images.append(img)
            
            # Reset file pointer for potential reuse
            await file.seek(0)
            
        except Exception as e:
            print(f"Error loading image: {e}")
            # Continue with other images
    
    return images

async def upload_documents(files: Union[UploadFile, List[UploadFile]], mime_types: Optional[Dict[str, str]] = None) -> List:
    """
    Uploads documents from FastAPI's UploadFile objects to Google Generative AI.
    
    Args:
        files: Either a single UploadFile or a list of UploadFile objects
        mime_types: Optional dictionary mapping filename to mime_type override
    
    Returns:
        list: A list of uploaded file objects from Google Generative AI client
    """
    uploaded_files = []
    
    # Convert to list if single file
    if not isinstance(files, list):
        files = [files]
    
    # Initialize mime_types dict if None
    if mime_types is None:
        mime_types = {}
    
    # Process each file
    for file in files:
        try:
            # Read file content asynchronously
            contents = await file.read()
            
            # Determine mime type (use provided or infer from content_type)
            mime_type = mime_types.get(file.filename, file.content_type)
            
            # Supported mime types mapping
            supported_types = {
                'application/pdf': 'application/pdf',
                'text/javascript': 'text/javascript',
                'application/x-javascript': 'application/x-javascript',
                'application/x-python': 'application/x-python',
                'text/x-python': 'text/x-python',
                'text/plain': 'text/plain',
                'text/html': 'text/html',
                'text/css': 'text/css',
                'text/markdown': 'text/md',
                'text/csv': 'text/csv',
                'text/xml': 'text/xml',
                'text/rtf': 'text/rtf'
            }
            
            # Check if mime type is supported
            if mime_type not in supported_types:
                print(f"Warning: Mime type {mime_type} may not be supported. Proceeding anyway.")
            
            # Convert to BytesIO for upload
            file_data = io.BytesIO(contents)
            
            # Upload to Google Generative AI client
            uploaded_file = client.files.upload(
                file=file_data,
                config=dict(mime_type=mime_type)
            )
            
            uploaded_files.append(uploaded_file)
            
            # Reset file pointer for potential reuse
            await file.seek(0)
            
        except Exception as e:
            print(f"Error uploading document {file.filename}: {e}")
            # Continue with other documents
    
    return uploaded_files