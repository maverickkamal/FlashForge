# Testing the Deck API Endpoints with curl

Use these curl commands to test your FlashForge decks API. You'll need to execute them from a terminal.

## 1. Login and Get Token

First, get an authentication token:

```bash
curl -X POST "http://localhost:8000/api/v1/auth/token" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=YOUR_EMAIL&password=YOUR_PASSWORD"
```

Save the `access_token` value from the response:

```json
{"access_token":"eyJhbGc...","token_type":"bearer"}
```

## 2. Create a New Deck

Create a new flashcard deck:

```bash
curl -X POST "http://localhost:8000/api/v1/decks" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE" \
  -H "Content-Type: application/json" \
  -d '{"name": "Math Basics"}'
```

Response should be:

```json
{"name": "Math Basics", "id": 1}
```

## 3. Get All Decks

List all your decks:

```bash
curl -X GET "http://localhost:8000/api/v1/decks" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

## 4. Get a Specific Deck

Get a single deck by ID:

```bash
curl -X GET "http://localhost:8000/api/v1/decks/1" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

## 5. Update a Deck

Rename a deck:

```bash
curl -X PUT "http://localhost:8000/api/v1/decks/1" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE" \
  -H "Content-Type: application/json" \
  -d '{"name": "Advanced Mathematics"}'
```

## 6. Delete a Deck

Delete a deck:

```bash
curl -X DELETE "http://localhost:8000/api/v1/decks/1" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

Response should be empty with status code 204.

## Notes

- Replace `YOUR_EMAIL` and `YOUR_PASSWORD` with your actual login credentials.
- Replace `YOUR_TOKEN_HERE` with the JWT token you received from the login step.
- Replace deck ID `1` with actual deck IDs from your system.