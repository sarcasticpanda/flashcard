"""
Pydantic schemas for quiz requests and responses.
Defines data validation for quiz generation and management.
"""

from pydantic import BaseModel, Field, validator
from typing import List, Optional
from datetime import datetime


class QuizGenerateRequest(BaseModel):
    """Schema for quiz generation request."""
    
    topic: str = Field(
        ..., 
        min_length=1, 
        max_length=255,
        description="Topic or subject for the quiz"
    )
    source_text: str = Field(
        ..., 
        min_length=10,
        description="Source text to generate quiz from"
    )
    num_questions: int = Field(
        default=5,
        ge=1,
        le=20,
        description="Number of questions to generate (1-20)"
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
                "topic": "Cell Biology",
                "source_text": "Cell biology is the study of cells, their structure, function, and behavior...",
                "num_questions": 5
            }
        }


class QuizQuestionResponse(BaseModel):
    """Schema for individual quiz question response."""
    
    id: int = Field(..., description="Question ID")
    question: str = Field(..., description="Question text")
    option_a: str = Field(..., description="Option A")
    option_b: str = Field(..., description="Option B")
    option_c: str = Field(..., description="Option C")
    option_d: str = Field(..., description="Option D")
    correct_index: int = Field(..., description="Index of correct answer (0=A, 1=B, 2=C, 3=D)")
    created_at: datetime = Field(..., description="Creation timestamp")
    
    class Config:
        from_attributes = True
        schema_extra = {
            "example": {
                "id": 1,
                "question": "What is the powerhouse of the cell?",
                "option_a": "Nucleus",
                "option_b": "Mitochondria",
                "option_c": "Endoplasmic reticulum",
                "option_d": "Golgi apparatus",
                "correct_index": 1,
                "created_at": "2024-01-01T00:00:00Z"
            }
        }


class QuizResponse(BaseModel):
    """Schema for quiz response."""
    
    id: int = Field(..., description="Quiz ID")
    topic: str = Field(..., description="Topic of the quiz")
    title: str = Field(..., description="Quiz title")
    num_questions: int = Field(..., description="Number of questions in the quiz")
    created_at: datetime = Field(..., description="Creation timestamp")
    questions: List[QuizQuestionResponse] = Field(..., description="List of quiz questions")
    
    class Config:
        from_attributes = True
        schema_extra = {
            "example": {
                "id": 1,
                "topic": "Cell Biology",
                "title": "Cell Biology Quiz",
                "num_questions": 5,
                "created_at": "2024-01-01T00:00:00Z",
                "questions": [
                    {
                        "id": 1,
                        "question": "What is the powerhouse of the cell?",
                        "option_a": "Nucleus",
                        "option_b": "Mitochondria",
                        "option_c": "Endoplasmic reticulum",
                        "option_d": "Golgi apparatus",
                        "correct_index": 1,
                        "created_at": "2024-01-01T00:00:00Z"
                    }
                ]
            }
        }


class QuizListResponse(BaseModel):
    """Schema for quiz list response."""
    
    id: int = Field(..., description="Quiz ID")
    topic: str = Field(..., description="Topic of the quiz")
    title: str = Field(..., description="Quiz title")
    num_questions: int = Field(..., description="Number of questions in the quiz")
    created_at: datetime = Field(..., description="Creation timestamp")
    
    class Config:
        from_attributes = True
        schema_extra = {
            "example": {
                "id": 1,
                "topic": "Cell Biology",
                "title": "Cell Biology Quiz",
                "num_questions": 5,
                "created_at": "2024-01-01T00:00:00Z"
            }
        }


class QuizUpdateRequest(BaseModel):
    """Schema for quiz update request."""
    
    topic: Optional[str] = Field(None, description="Updated topic")
    title: Optional[str] = Field(None, description="Updated title")
    
    @validator('topic')
    def validate_topic(cls, v):
        """Validate topic if provided."""
        if v is not None and not v.strip():
            raise ValueError('Topic cannot be empty')
        return v.strip() if v else v
    
    @validator('title')
    def validate_title(cls, v):
        """Validate title if provided."""
        if v is not None and not v.strip():
            raise ValueError('Title cannot be empty')
        return v.strip() if v else v
    
    class Config:
        schema_extra = {
            "example": {
                "topic": "Advanced Cell Biology",
                "title": "Advanced Cell Biology Quiz"
            }
        }


class QuizQuestionUpdateRequest(BaseModel):
    """Schema for quiz question update request."""
    
    question: Optional[str] = Field(None, description="Updated question")
    option_a: Optional[str] = Field(None, description="Updated option A")
    option_b: Optional[str] = Field(None, description="Updated option B")
    option_c: Optional[str] = Field(None, description="Updated option C")
    option_d: Optional[str] = Field(None, description="Updated option D")
    correct_index: Optional[int] = Field(None, ge=0, le=3, description="Updated correct answer index")
    
    @validator('question')
    def validate_question(cls, v):
        """Validate question if provided."""
        if v is not None and not v.strip():
            raise ValueError('Question cannot be empty')
        return v.strip() if v else v
    
    @validator('option_a', 'option_b', 'option_c', 'option_d')
    def validate_options(cls, v):
        """Validate options if provided."""
        if v is not None and not v.strip():
            raise ValueError('Options cannot be empty')
        return v.strip() if v else v
    
    class Config:
        schema_extra = {
            "example": {
                "question": "What is the primary function of the nucleus?",
                "option_a": "Energy production",
                "option_b": "Genetic control",
                "option_c": "Protein synthesis",
                "option_d": "Waste removal",
                "correct_index": 1
            }
        }


class QuizSubmissionRequest(BaseModel):
    """Schema for quiz submission request."""
    
    answers: List[int] = Field(..., description="List of answer indices (0-3 for each question)")
    
    @validator('answers')
    def validate_answers(cls, v):
        """Validate answer indices are within valid range."""
        for answer in v:
            if not 0 <= answer <= 3:
                raise ValueError('Answer indices must be between 0 and 3')
        return v
    
    class Config:
        schema_extra = {
            "example": {
                "answers": [1, 0, 2, 3, 1]
            }
        }


class QuizResultResponse(BaseModel):
    """Schema for quiz result response."""
    
    quiz_id: int = Field(..., description="Quiz ID")
    total_questions: int = Field(..., description="Total number of questions")
    correct_answers: int = Field(..., description="Number of correct answers")
    score_percentage: float = Field(..., description="Score as percentage")
    submitted_at: datetime = Field(..., description="Submission timestamp")
    
    class Config:
        schema_extra = {
            "example": {
                "quiz_id": 1,
                "total_questions": 5,
                "correct_answers": 4,
                "score_percentage": 80.0,
                "submitted_at": "2024-01-01T00:00:00Z"
            }
        }
