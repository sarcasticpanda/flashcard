"""
Pydantic schemas for flashcard requests and responses.
Defines data validation for flashcard generation and management.
"""

from pydantic import BaseModel, Field, validator
from typing import List, Optional
from datetime import datetime


class FlashcardGenerateRequest(BaseModel):
    """Schema for flashcard generation request."""
    
    topic: str = Field(
        ..., 
        min_length=1, 
        max_length=255,
        description="Topic or subject for the flashcards"
    )
    source_text: str = Field(
        ..., 
        min_length=10,
        description="Source text to generate flashcards from"
    )
    num_cards: int = Field(
        default=8,
        ge=1,
        le=30,
        description="Number of flashcards to generate (1-30)"
    )
    description: Optional[str] = Field(
        None,
        max_length=500,
        description="Optional description for the flashcard set"
    )
    
    @validator('topic')
    def validate_topic(cls, v):
        """Validate topic is not empty and properly formatted."""
        if not v.strip():
            raise ValueError('Topic cannot be empty')
        return v.strip()
    
    @validator('source_text')
    def validate_source_text(cls, v):
        """Validate source text has sufficient content."""
        if len(v.strip()) < 10:
            raise ValueError('Source text must be at least 10 characters long')
        return v.strip()
    
    class Config:
        schema_extra = {
            "example": {
                "topic": "Photosynthesis",
                "source_text": "Photosynthesis is the process by which plants convert light energy into chemical energy...",
                "num_cards": 8,
                "description": "Basic concepts of photosynthesis"
            }
        }


class FlashcardResponse(BaseModel):
    """Schema for individual flashcard response."""
    
    id: int = Field(..., description="Flashcard ID")
    question: str = Field(..., description="Flashcard question")
    answer: str = Field(..., description="Flashcard answer")
    created_at: datetime = Field(..., description="Creation timestamp")
    
    class Config:
        from_attributes = True
        schema_extra = {
            "example": {
                "id": 1,
                "question": "What is photosynthesis?",
                "answer": "Photosynthesis is the process by which plants convert light energy into chemical energy.",
                "created_at": "2024-01-01T00:00:00Z"
            }
        }


class FlashcardSetResponse(BaseModel):
    """Schema for flashcard set response."""
    
    id: int = Field(..., description="Flashcard set ID")
    topic: str = Field(..., description="Topic of the flashcard set")
    description: Optional[str] = Field(None, description="Description of the set")
    num_cards: int = Field(..., description="Number of flashcards in the set")
    created_at: datetime = Field(..., description="Creation timestamp")
    flashcards: List[FlashcardResponse] = Field(..., description="List of flashcards")
    
    class Config:
        from_attributes = True
        schema_extra = {
            "example": {
                "id": 1,
                "topic": "Photosynthesis",
                "description": "Basic concepts of photosynthesis",
                "num_cards": 8,
                "created_at": "2024-01-01T00:00:00Z",
                "flashcards": [
                    {
                        "id": 1,
                        "question": "What is photosynthesis?",
                        "answer": "Photosynthesis is the process by which plants convert light energy into chemical energy.",
                        "created_at": "2024-01-01T00:00:00Z"
                    }
                ]
            }
        }


class FlashcardSetListResponse(BaseModel):
    """Schema for flashcard set list response."""
    
    id: int = Field(..., description="Flashcard set ID")
    topic: str = Field(..., description="Topic of the flashcard set")
    description: Optional[str] = Field(None, description="Description of the set")
    num_cards: int = Field(..., description="Number of flashcards in the set")
    created_at: datetime = Field(..., description="Creation timestamp")
    
    class Config:
        from_attributes = True
        schema_extra = {
            "example": {
                "id": 1,
                "topic": "Photosynthesis",
                "description": "Basic concepts of photosynthesis",
                "num_cards": 8,
                "created_at": "2024-01-01T00:00:00Z"
            }
        }


class FlashcardUpdateRequest(BaseModel):
    """Schema for flashcard update request."""
    
    question: Optional[str] = Field(None, description="Updated question")
    answer: Optional[str] = Field(None, description="Updated answer")
    
    @validator('question')
    def validate_question(cls, v):
        """Validate question if provided."""
        if v is not None and not v.strip():
            raise ValueError('Question cannot be empty')
        return v.strip() if v else v
    
    @validator('answer')
    def validate_answer(cls, v):
        """Validate answer if provided."""
        if v is not None and not v.strip():
            raise ValueError('Answer cannot be empty')
        return v.strip() if v else v
    
    class Config:
        schema_extra = {
            "example": {
                "question": "What is the primary function of photosynthesis?",
                "answer": "The primary function of photosynthesis is to convert light energy into chemical energy."
            }
        }


class FlashcardSetUpdateRequest(BaseModel):
    """Schema for flashcard set update request."""
    
    topic: Optional[str] = Field(None, description="Updated topic")
    description: Optional[str] = Field(None, description="Updated description")
    
    @validator('topic')
    def validate_topic(cls, v):
        """Validate topic if provided."""
        if v is not None and not v.strip():
            raise ValueError('Topic cannot be empty')
        return v.strip() if v else v
    
    class Config:
        schema_extra = {
            "example": {
                "topic": "Advanced Photosynthesis",
                "description": "Advanced concepts and mechanisms of photosynthesis"
            }
        }
