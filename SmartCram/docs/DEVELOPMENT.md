# SMARTCRAM Development Guide

## Overview

This guide covers the development setup, coding standards, testing procedures, and contribution guidelines for the SMARTCRAM project. The application follows modern development practices and is built with scalability and maintainability in mind.

## Development Environment Setup

### Prerequisites

- Python 3.8+
- MySQL 8.0+
- Git
- Docker and Docker Compose (optional but recommended)

### Local Development Setup

1. **Clone the repository:**
```bash
git clone <repository-url>
cd SMARTCRAM
```

2. **Setup Python virtual environment:**
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r backend/requirements.txt
```

3. **Setup database:**
```bash
# Start MySQL (if using Docker)
docker-compose up -d mysql

# Or install MySQL locally
sudo apt install mysql-server  # Ubuntu/Debian
```

4. **Configure environment:**
```bash
cp .env.example .env
# Edit .env with your local development settings
```

5. **Run database migrations:**
```bash
cd backend
alembic upgrade head
```

6. **Start the development server:**
```bash
# Backend
cd backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Frontend (serve static files)
cd frontend
python -m http.server 8080
```

## Project Structure

```
SMARTCRAM/
├── backend/
│   ├── app/
│   │   ├── core/           # Configuration, security, OpenAI client
│   │   ├── db/             # Database models and connection
│   │   ├── routers/        # API endpoints
│   │   └── schemas/        # Pydantic models
│   ├── alembic/            # Database migrations
│   └── requirements.txt    # Python dependencies
├── frontend/
│   ├── index.html          # Main HTML file
│   ├── styles.css          # CSS styles
│   └── script.js           # JavaScript functionality
├── docs/                   # Documentation
└── docker-compose.yml      # Docker services
```

## Coding Standards

### Python (Backend)

- Follow PEP 8 style guide
- Use Black for code formatting
- Use type hints for all functions
- Use Pydantic models for data validation
- Add docstrings for all functions

### JavaScript (Frontend)

- Use ES6+ features
- Use meaningful variable names
- Add comments for complex logic
- Use consistent indentation (2 spaces)

## Testing

### Backend Testing

```bash
# Install testing dependencies
pip install pytest pytest-asyncio pytest-cov httpx

# Run tests
pytest
pytest --cov=app
```

### Frontend Testing

- Manual testing checklist
- Browser compatibility testing
- Responsive design testing

## Development Workflow

1. Create feature branch
2. Make changes following coding standards
3. Write tests for new features
4. Update documentation
5. Submit pull request

## Debugging

### Backend Debugging

```python
import logging
logger = logging.getLogger(__name__)

# Enable debug logging
uvicorn app.main:app --reload --log-level debug
```

### Frontend Debugging

- Use browser developer tools
- Console logging for JavaScript
- Network tab for API calls

## Security Best Practices

- Input validation with Pydantic
- SQL injection prevention with SQLAlchemy
- CORS configuration
- JWT token security
- XSS prevention in frontend

## Contributing

1. Fork the repository
2. Create a feature branch
3. Follow coding standards
4. Write tests for new features
5. Update documentation
6. Submit a pull request

## Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)
- [Pydantic Documentation](https://pydantic-docs.helpmanual.io/)
- [JavaScript Best Practices](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Guide)
