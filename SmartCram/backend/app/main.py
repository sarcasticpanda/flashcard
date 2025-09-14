"""
Main FastAPI application for SMARTCRAM.
Implements the complete flow from the flowchart: User Input -> Frontend -> Backend -> OpenAI -> Database -> Response.
"""

from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import logging

from .core.config import settings
from .db.database import engine, create_tables
from .db.models import Base
from .routers import auth, flashcards, quiz

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan manager.
    Handles startup and shutdown events.
    """
    # Startup: Create database tables (following flowchart: "Backend: Python Flask Receives Request")
    logger.info("Starting SMARTCRAM application...")
    try:
        # Create all database tables
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables created successfully")
    except Exception as e:
        logger.error(f"Failed to create database tables: {e}")
        raise
    
    yield
    
    # Shutdown: Clean up resources
    logger.info("Shutting down SMARTCRAM application...")


# Create FastAPI application with lifespan management
app = FastAPI(
    title="SMARTCRAM API",
    description="AI-powered flashcards and quiz generator following the flowchart pattern",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# Configure CORS middleware (following flowchart: "Frontend: HTML/CSS/JS Renders Interface")
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """
    Global exception handler for unhandled errors.
    """
    logger.error(f"Unhandled exception: {exc}")
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "Internal server error"}
    )


# Health check endpoint
@app.get("/health", tags=["Health"])
async def health_check():
    """
    Health check endpoint to verify application status.
    """
    return {
        "status": "healthy",
        "message": "SMARTCRAM API is running",
        "version": "1.0.0"
    }


# Root endpoint
@app.get("/", tags=["Root"])
async def root():
    """
    Root endpoint with application information.
    """
    return {
        "message": "Welcome to SMARTCRAM API",
        "description": "AI-powered flashcards and quiz generator",
        "version": "1.0.0",
        "docs": "/docs",
        "flow": "User Input -> Frontend -> Backend -> OpenAI -> Database -> Response"
    }


# Include routers (following flowchart: "Backend: Python Flask Receives Request")
app.include_router(auth.router, prefix="/api/v1")
app.include_router(flashcards.router, prefix="/api/v1")
app.include_router(quiz.router, prefix="/api/v1")


# Startup event handler
@app.on_event("startup")
async def startup_event():
    """
    Startup event handler.
    Logs application startup and configuration.
    """
    logger.info("=" * 50)
    logger.info("SMARTCRAM API Starting Up")
    logger.info("=" * 50)
    logger.info(f"Environment: {settings.environment}")
    logger.info(f"Debug Mode: {settings.debug}")
    logger.info(f"Database URL: {settings.database_url.split('@')[1] if '@' in settings.database_url else 'Configured'}")
    logger.info(f"OpenAI API: {'Configured' if settings.openai_api_key else 'Not Configured'}")
    logger.info(f"Allowed Origins: {settings.allowed_origins}")
    logger.info("=" * 50)
    
    # Validate critical settings
    if not settings.openai_api_key:
        logger.warning("OpenAI API key not configured. AI generation will not work.")
    
    if not settings.database_url:
        logger.error("Database URL not configured. Application may not work properly.")


# Shutdown event handler
@app.on_event("shutdown")
async def shutdown_event():
    """
    Shutdown event handler.
    Logs application shutdown.
    """
    logger.info("=" * 50)
    logger.info("SMARTCRAM API Shutting Down")
    logger.info("=" * 50)


# API information endpoint
@app.get("/api/info", tags=["API Info"])
async def api_info():
    """
    API information endpoint.
    Returns detailed API information and flow description.
    """
    return {
        "application": "SMARTCRAM",
        "version": "1.0.0",
        "description": "AI-powered flashcards and quiz generator",
        "flowchart_implementation": {
            "step_1": "User Opens Web App",
            "step_2": "Frontend: HTML/CSS/JS Renders Interface",
            "step_3": "User Inputs Topic & Chooses 'Flashcards' or 'Quiz'",
            "step_4": "User Clicks 'Generate'",
            "step_5": "JS Captures Input & Sends Request to Backend API",
            "step_6": "Backend: Python Flask Receives Request",
            "step_7": "Backend Checks MySQL: Topic & Type Cached?",
            "step_8a": "If Cached: Fetch Existing Data from Database",
            "step_8b": "If Not Cached: Construct AI Prompt & Call OpenAI API",
            "step_9": "OpenAI Processes Request & Returns JSON Response",
            "step_10": "Save New Topic & Q/A to MySQL Database",
            "step_11": "Format Data for Frontend",
            "step_12": "Send Generated Content JSON to Frontend",
            "step_13": "Frontend: JS Receives JSON & Dynamically Renders Content",
            "step_14": "User Views Flashcards or Takes Quiz",
            "step_15": "User Studies!"
        },
        "endpoints": {
            "authentication": "/api/v1/auth",
            "flashcards": "/api/v1/flashcards",
            "quiz": "/api/v1/quiz",
            "documentation": "/docs"
        },
        "features": [
            "AI-powered content generation",
            "User authentication with JWT",
            "Database caching for efficiency",
            "Export/import functionality",
            "Real-time content rendering",
            "Responsive design"
        ]
    }


if __name__ == "__main__":
    import uvicorn
    
    # Run the application
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug,
        log_level="info"
    )
