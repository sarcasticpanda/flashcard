# SMARTCRAM API Documentation

## Overview

The SMARTCRAM API is a RESTful service built with FastAPI that provides AI-powered flashcard and quiz generation capabilities. The API follows REST principles and uses JSON for data exchange.

**Base URL:** `http://localhost:8000/api/v1`

## Authentication

The API uses JWT (JSON Web Tokens) for authentication. Most endpoints require authentication via the `Authorization` header:

```
Authorization: Bearer <X4DER4JMQSZ3HDUB4RQLNPN7>
```

## Endpoints

### Authentication

#### POST /auth/register
Register a new user account.

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "securepassword123",
  "full_name": "John Doe"
}
```

**Response:**
```json
{
  "message": "User registered successfully"
}
```

#### POST /auth/login
Authenticate and receive a JWT token.

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "securepassword123"
}
```

**Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

#### GET /auth/me
Get current user information.

**Headers:** `Authorization: Bearer <token>`

**Response:**
```json
{
  "id": 1,
  "email": "user@example.com",
  "full_name": "John Doe",
  "is_active": true,
  "created_at": "2024-01-01T00:00:00Z"
}
```

#### PUT /auth/me
Update current user information.

**Headers:** `Authorization: Bearer <token>`

**Request Body:**
```json
{
  "full_name": "John Smith"
}
```

#### PUT /auth/change-password
Change user password.

**Headers:** `Authorization: Bearer <token>`

**Request Body:**
```json
{
  "old_password": "oldpassword123",
  "new_password": "newpassword123"
}
```

#### DELETE /auth/me
Deactivate user account.

**Headers:** `Authorization: Bearer <token>`

#### GET /auth/verify-token
Verify if a token is valid.

**Headers:** `Authorization: Bearer <token>`

### Flashcards

#### POST /flashcards/generate
Generate flashcards using AI.

**Headers:** `Authorization: Bearer <token>`

**Request Body:**
```json
{
  "topic": "Python Programming",
  "source_text": "Optional source text for context",
  "num_cards": 10,
  "description": "Basic Python concepts"
}
```

**Response:**
```json
{
  "id": 1,
  "user_id": 1,
  "topic": "Python Programming",
  "description": "Basic Python concepts",
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-01T00:00:00Z",
  "flashcards": [
    {
      "id": 1,
      "question": "What is a variable in Python?",
      "answer": "A variable is a container for storing data values.",
      "created_at": "2024-01-01T00:00:00Z"
    }
  ]
}
```

#### GET /flashcards
Get all flashcard sets for the current user.

**Headers:** `Authorization: Bearer <token>`

**Response:**
```json
[
  {
    "id": 1,
    "topic": "Python Programming",
    "description": "Basic Python concepts",
    "created_at": "2024-01-01T00:00:00Z",
    "updated_at": "2024-01-01T00:00:00Z",
    "num_cards": 10
  }
]
```

#### GET /flashcards/{set_id}
Get a specific flashcard set.

**Headers:** `Authorization: Bearer <token>`

**Response:** Same as POST /flashcards/generate

#### PUT /flashcards/{set_id}
Update flashcard set metadata.

**Headers:** `Authorization: Bearer <token>`

**Request Body:**
```json
{
  "topic": "Updated Topic",
  "description": "Updated description"
}
```

#### DELETE /flashcards/{set_id}
Delete a flashcard set.

**Headers:** `Authorization: Bearer <token>`

#### GET /flashcards/{set_id}/export
Export flashcard set as JSON.

**Headers:** `Authorization: Bearer <token>`

**Response:** JSON file download

#### POST /flashcards/import
Import flashcard set from JSON.

**Headers:** `Authorization: Bearer <token>`

**Request Body:** JSON file upload

### Quizzes

#### POST /quiz/generate
Generate quiz using AI.

**Headers:** `Authorization: Bearer <token>`

**Request Body:**
```json
{
  "topic": "JavaScript Fundamentals",
  "source_text": "Optional source text for context",
  "num_questions": 15
}
```

**Response:**
```json
{
  "id": 1,
  "user_id": 1,
  "topic": "JavaScript Fundamentals",
  "title": "JavaScript Fundamentals Quiz",
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-01T00:00:00Z",
  "questions": [
    {
      "id": 1,
      "question": "What is the correct way to declare a variable in JavaScript?",
      "option_a": "var x = 5;",
      "option_b": "variable x = 5;",
      "option_c": "v x = 5;",
      "option_d": "declare x = 5;",
      "correct_index": 0,
      "created_at": "2024-01-01T00:00:00Z"
    }
  ]
}
```

#### GET /quiz
Get all quizzes for the current user.

**Headers:** `Authorization: Bearer <token>`

**Response:**
```json
[
  {
    "id": 1,
    "topic": "JavaScript Fundamentals",
    "title": "JavaScript Fundamentals Quiz",
    "created_at": "2024-01-01T00:00:00Z",
    "updated_at": "2024-01-01T00:00:00Z",
    "num_questions": 15
  }
]
```

#### GET /quiz/{quiz_id}
Get a specific quiz.

**Headers:** `Authorization: Bearer <token>`

**Response:** Same as POST /quiz/generate

#### POST /quiz/{quiz_id}/submit
Submit quiz answers and get results.

**Headers:** `Authorization: Bearer <token>`

**Request Body:**
```json
{
  "answers": [0, 1, 2, 0, 1]
}
```

**Response:**
```json
{
  "correct_answers": 4,
  "total_questions": 5,
  "score_percentage": 80.0,
  "answers": [0, 1, 2, 0, 1]
}
```

#### PUT /quiz/{quiz_id}
Update quiz metadata.

**Headers:** `Authorization: Bearer <token>`

**Request Body:**
```json
{
  "title": "Updated Quiz Title",
  "topic": "Updated Topic"
}
```

#### DELETE /quiz/{quiz_id}
Delete a quiz.

**Headers:** `Authorization: Bearer <token>`

#### GET /quiz/{quiz_id}/export
Export quiz as JSON.

**Headers:** `Authorization: Bearer <token>`

**Response:** JSON file download

#### POST /quiz/import
Import quiz from JSON.

**Headers:** `Authorization: Bearer <token>`

**Request Body:** JSON file upload

### Health Check

#### GET /health
Check API health status.

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2024-01-01T00:00:00Z"
}
```

## Error Responses

All endpoints may return the following error responses:

### 400 Bad Request
```json
{
  "detail": "Validation error message"
}
```

### 401 Unauthorized
```json
{
  "detail": "Not authenticated"
}
```

### 403 Forbidden
```json
{
  "detail": "Not enough permissions"
}
```

### 404 Not Found
```json
{
  "detail": "Resource not found"
}
```

### 422 Unprocessable Entity
```json
{
  "detail": [
    {
      "loc": ["body", "field_name"],
      "msg": "field required",
      "type": "value_error.missing"
    }
  ]
}
```

### 500 Internal Server Error
```json
{
  "detail": "Internal server error"
}
```

## Rate Limiting

The API implements rate limiting to prevent abuse. By default, users are limited to 60 requests per minute.

## Data Models

### User
```json
{
  "id": 1,
  "email": "user@example.com",
  "full_name": "John Doe",
  "is_active": true,
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-01T00:00:00Z"
}
```

### FlashcardSet
```json
{
  "id": 1,
  "user_id": 1,
  "topic": "Topic Name",
  "description": "Description",
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-01T00:00:00Z"
}
```

### Flashcard
```json
{
  "id": 1,
  "flashcard_set_id": 1,
  "question": "Question text",
  "answer": "Answer text",
  "created_at": "2024-01-01T00:00:00Z"
}
```

### Quiz
```json
{
  "id": 1,
  "user_id": 1,
  "topic": "Topic Name",
  "title": "Quiz Title",
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-01T00:00:00Z"
}
```

### QuizQuestion
```json
{
  "id": 1,
  "quiz_id": 1,
  "question": "Question text",
  "option_a": "Option A",
  "option_b": "Option B",
  "option_c": "Option C",
  "option_d": "Option D",
  "correct_index": 0,
  "created_at": "2024-01-01T00:00:00Z"
}
```

## Testing

You can test the API using the interactive documentation at:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Examples

### Complete Workflow Example

1. **Register a user:**
```bash
curl -X POST "http://localhost:8000/api/v1/auth/register" \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com", "password": "password123", "full_name": "Test User"}'
```

2. **Login and get token:**
```bash
curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com", "password": "password123"}'
```

3. **Generate flashcards:**
```bash
curl -X POST "http://localhost:8000/api/v1/flashcards/generate" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"topic": "Python Basics", "num_cards": 5}'
```

4. **Generate quiz:**
```bash
curl -X POST "http://localhost:8000/api/v1/quiz/generate" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"topic": "JavaScript", "num_questions": 10}'
```

## Support

For API support and questions, please refer to the main README.md file or create an issue in the project repository.
