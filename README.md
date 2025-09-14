#  AI Flashcards & Quiz Generator

Welcome to **Sarcastic Panda**: an AI-powered web app that turns your notes into interactive flashcards and quizzes. This project is a full-stack solution for students, teachers, and lifelong learners who want to study smarter, not harder (because pandas are lazy, but clever).

## What Does It Do?
- **AI Generation**: Converts your text into Q&A flashcards and multiple-choice quizzes using OpenAI.
- **Interactive Study**: Flip flashcards, take quizzes, and track your progress.
- **User Accounts**: Register, log in, and keep your study sets safe.
- **Import/Export**: Download and upload flashcard/quiz sets as JSON.
- **Modern UI**: Responsive, clean, and works on any device.

## How Does It Work?
- **Backend**: FastAPI (Python) with MySQL for data, SQLAlchemy ORM, and OpenAI for content generation.
- **Frontend**: HTML, CSS, and vanilla JavaScript. No frameworks, just pure panda power.
- **Auth**: JWT tokens for secure login.

## Quickstart (Local)
1. **Clone the repo**
   ```bash
   git clone <this-repo-url>
   cd SmartCram
   cp .env.example .env
   # Edit .env with your OpenAI key and MySQL info
   ```
2. **Set up MySQL**
   - Create a database and user (see below)
   ```sql
   CREATE DATABASE sarcasticpanda;
   CREATE USER 'sarcasticpanda'@'localhost' IDENTIFIED BY 'pandapass';
   GRANT ALL PRIVILEGES ON sarcasticpanda.* TO 'sarcasticpanda'@'localhost';
   FLUSH PRIVILEGES;
   ```
3. **Backend setup**
   ```bash
   cd backend
   python -m venv venv
   venv\Scripts\activate  # On Windows
   pip install -r requirements.txt
   alembic upgrade head
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```
4. **Frontend**
   - Open `frontend/index.html` in your browser (or use a local server for CORS).

## Docker (Recommended)
1. Copy `.env.example` to `.env` and fill in your secrets.
2. Run:
   ```bash
   docker compose up --build
   ```
3. Visit:
   - Frontend: http://localhost:8080
   - Backend: http://localhost:8000
   - API Docs: http://localhost:8000/docs

## API Endpoints
- `/auth/register` - Register
- `/auth/login` - Login
- `/flashcards/generate` - Generate flashcards
- `/quiz/generate` - Generate quiz
- `/flashcards/` - List flashcard sets
- `/quiz/` - List quizzes
- `/transfer/export/flashcards/{set_id}` - Export flashcards
- `/transfer/import/flashcards` - Import flashcards
- `/transfer/export/quiz/{quiz_id}` - Export quiz
- `/transfer/import/quiz` - Import quiz

## Why Sarcastic Panda?
Because pandas are chill, but this app is serious about helping you learn. If you get stuck, check the `docs/` folder or open an issue. Pull requests welcome!

---
MIT License. Created by Sarcastic Panda.
