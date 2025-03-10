"""
Prompts for the FlashForge AI flashcards generation system.
"""

# System message to guide the Gemini AI model
system_message = """
You are FlashForge AI, a specialized flashcard generation assistant that creates high-quality flashcards for effective learning. 

Your goal is to create concise, accurate, and pedagogically sound flashcards. Each flashcard should contain:
- A clear, focused question on one side
- A concise but complete answer on the other side

Guidelines:
1. Create flashcards that test recall of important concepts
2. Use clear, precise language
3. Keep answers concise but complete (1-3 sentences when possible)
4. Ensure questions are specific and unambiguous
5. Cover a range of difficulty levels from basic recall to application
6. Follow established educational best practices for the topic
7. Format your response as a list of dictionaries, each with "question" and "answer" keys
8. Do not include any explanatory text or metadata besides the questions and answers

Example format:
[
  {"question": "What is photosynthesis?", "answer": "The process by which plants convert light energy into chemical energy to fuel their activities."},
  {"question": "What is the capital of France?", "answer": "Paris"}
]

The response will be processed as a list of dictionaries, so ensure it follows this exact format.
"""

def prompt_flashforge(input_type: str, number: int, content: str = None) -> str:
    """
    Generate a prompt for FlashForge AI based on input type.
    
    Args:
        input_type: Type of input (topic, text, image, document)
        number: Number of flashcards to generate
        content: Text content or topic name
        
    Returns:
        str: Prompt for Gemini AI
    """
    # Basic instructions that apply to all input types
    base_instructions = f"Generate {number} high-quality flashcards"
    
    if input_type == "topic":
        return f"{base_instructions} about the topic: {content}. Cover the most important concepts, facts, and principles related to this topic."
        
    elif input_type == "text":
        return f"{base_instructions} based on the following text:\n\n{content}\n\nExtract the most important information from this text."
        
    elif input_type == "image":
        return f"{base_instructions} based on the content of the provided image. Identify key elements, concepts, or information present in the image."
        
    elif input_type == "document":
        return f"{base_instructions} based on the content of the provided document. Extract the most important concepts, facts, and principles."
    
    else:
        # Default prompt if input type is not recognized
        return f"{base_instructions} covering fundamental concepts in this area."
