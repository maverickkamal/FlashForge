# FlashForge

FlashForge is an AI-powered flashcard management API that helps users create, organize, and study flashcards more efficiently. The application leverages AI to automatically generate flashcards from various inputs including topics, text, images, and documents.

## Features

- User authentication and account management
- Create and manage flashcard decks
- Add and organize flashcards within decks
- AI-powered flashcard generation from:
  - Topics (e.g., "Introduction to Python Programming")
  - Text passages
  - Images
  - Documents
- RESTful API design for easy integration

## Setup and Installation

### Prerequisites

- Python 3.9 or higher
- PostgreSQL (or SQLite for development)

### Installation

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/FlashForge.git
   cd FlashForge
   ```

2. Create and activate a virtual environment:
   ```
   python -m venv venv
   # On Windows
   venv\Scripts\activate
   # On macOS/Linux
   source venv/bin/activate
   ```

3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

4. Set up environment variables (create a .env file):
   ```
   DATABASE_URL=postgresql://user:password@localhost/flashforge
   SECRET_KEY=your_secret_key
   ALGORITHM=HS256
   ACCESS_TOKEN_EXPIRE_MINUTES=30
   GEMINI_API_KEY=your_gemini_api_key  # For AI features
   ```

5. Initialize the database:
   ```
   python -m app.db.init_db
   ```

6. Start the application:
   ```
   uvicorn main:app --reload
   ```

## API Documentation

### Authentication Endpoints

- `POST /auth/register` - Register a new user
- `POST /auth/token` - Login and get access token
- `GET /auth/me` - Get current user information

### Deck Endpoints

- `GET /decks` - Get all decks for the current user
- `GET /decks/{deck_id}` - Get a specific deck
- `POST /decks` - Create a new deck
- `PUT /decks/{deck_id}` - Update a deck
- `DELETE /decks/{deck_id}` - Delete a deck

### Flashcard Endpoints

- `GET /flashcards/{deck_id}` - Get all flashcards in a deck
- `GET /flashcards/{deck_id}/{flashcard_id}` - Get a specific flashcard
- `POST /flashcards/{deck_id}` - Create a new flashcard
- `PUT /flashcards/{deck_id}/{flashcard_id}` - Update a flashcard
- `DELETE /flashcards/{deck_id}/{flashcard_id}` - Delete a flashcard

### AI Generation Endpoints

- `POST /ai/generate` - Generate flashcards from topic or text
- `POST /ai/generate-with-files` - Generate flashcards from images or documents

## Interactive API Documentation (Swagger UI)

FastAPI automatically generates interactive API documentation that allows you to explore and test all endpoints directly from your browser.

### Accessing the Documentation

1. Start the application:

```bash
uvicorn main:app --reload
```

2. Open your browser and navigate to:

http://localhost:8000/docs

### Using Swagger UI

1. **Authentication**:
- Click the "Authorize" button at the top right
- Enter your JWT token in the format: `Bearer YOUR_ACCESS_TOKEN`
- Click "Authorize" to apply the token to all endpoints

2. **Exploring Endpoints**:
- Endpoints are grouped by tags (auth, decks, flashcards, ai)
- Click on an endpoint to expand its details
- Each endpoint shows required parameters, request body schema, and possible responses

3. **Testing Endpoints**:
- Click the "Try it out" button on any endpoint
- Fill in the required parameters and request body
- Click "Execute" to send the request
- View the server response below

### Testing AI Flashcard Generation

1. **For Topic or Text Generation**:
- Expand the `POST /api/v1/ai/generate` endpoint
- Click "Try it out"
- Enter a request body like:
  ```json
  {
    "input_type": "topic",
    "number": 5,
    "content": "Introduction to Machine Learning",
    "save_to_deck": true,
    "deck_name": "ML Basics"
  }
  ```
- Click "Execute" to generate flashcards

2. **For Image or Document Processing**:
- Expand the `POST /api/v1/ai/generate-with-files` endpoint
- Click "Try it out"
- Fill in the form fields:
  - input_type: "image" or "document"
  - number: number of flashcards to generate
  - save_to_deck: true/false
  - deck_name: name for the new deck (if saving)
- Upload your file(s) using the browse button
- Click "Execute" to generate flashcards

## Usage Examples

### Generating Flashcards from a Topic

```bash
curl -X POST "http://localhost:8000/ai/generate" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "input_type": "topic",
    "content": "Introduction to Machine Learning",
    "number": 5,
    "save_to_deck": true,
    "deck_name": "ML Basics"
  }'
```

### Uploading an Image for Flashcard Generation

```bash
curl -X POST "http://localhost:8000/ai/generate-with-files" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -F "input_type=image" \
  -F "number=5" \
  -F "save_to_deck=true" \
  -F "deck_name=Image Notes" \
  -F "files=@/path/to/your/image.jpg"
```

## Development

The project is structured as follows:

- `main.py` - Application entry point
- `app/` - Main application package
  - `auth/` - Authentication logic and user management
  - `decks/` - Deck management
  - `flashcards/` - Flashcard management
  - `AI/` - AI generation services
  - `db/` - Database connections and models
  - `config.py` - Application configuration

## Technologies Used

- FastAPI - Web framework
- SQLAlchemy - ORM
- Pydantic - Data validation
- Python-jose - JWT token handling
- Gemini API - AI text generation
- PostgreSQL/SQLite - Database

