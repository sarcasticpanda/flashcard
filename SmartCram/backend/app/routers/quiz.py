"""
Quiz router for generating, managing, and exporting quizzes.
Handles AI-powered quiz generation and CRUD operations following the flowchart pattern.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
import json
from datetime import datetime

from ..db.database import get_db
from ..db.models import User, Quiz, QuizQuestion
from ..schemas.quiz import (
    QuizGenerateRequest,
    QuizResponse,
    QuizListResponse,
    QuizUpdateRequest,
    QuizSubmissionRequest,
    QuizResultResponse
)
from ..core.openai_client import openai_client
from .auth import get_current_user

# Initialize router
router = APIRouter(prefix="/quiz", tags=["Quiz"])


@router.post("/generate", response_model=QuizResponse, status_code=status.HTTP_201_CREATED)
async def generate_quiz(
    request: QuizGenerateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Generate quiz using AI from source text following the flowchart pattern.
    
    Args:
        request: Quiz generation request
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        QuizResponse: Generated quiz with questions
        
    Raises:
        HTTPException: If generation fails
    """
    try:
        # Generate quiz using OpenAI (following flowchart: "Construct AI Prompt & Call OpenAI API")
        generated_quiz = openai_client.generate_quiz(
            topic=request.topic,
            source_text=request.source_text,
            num_questions=request.num_questions
        )
        
        if not generated_quiz or not generated_quiz.get("questions"):
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to generate quiz"
            )
        
        # Create quiz (following flowchart: "Save New Topic & Q/A to MySQL Database")
        quiz = Quiz(
            user_id=current_user.id,
            topic=request.topic,
            title=generated_quiz.get("title", f"Quiz: {request.topic}")
        )
        db.add(quiz)
        db.flush()  # Get the ID without committing
        
        # Create individual quiz questions
        for question_data in generated_quiz["questions"]:
            quiz_question = QuizQuestion(
                quiz_id=quiz.id,
                question=question_data["question"],
                option_a=question_data["options"][0],
                option_b=question_data["options"][1],
                option_c=question_data["options"][2],
                option_d=question_data["options"][3],
                correct_index=question_data["correct_index"]
            )
            db.add(quiz_question)
        
        db.commit()
        db.refresh(quiz)
        
        # Return response with quiz questions (following flowchart: "Format Data for Frontend")
        return QuizResponse(
            id=quiz.id,
            topic=quiz.topic,
            title=quiz.title,
            num_questions=len(quiz.questions),
            created_at=quiz.created_at,
            questions=[
                {
                    "id": q.id,
                    "question": q.question,
                    "option_a": q.option_a,
                    "option_b": q.option_b,
                    "option_c": q.option_c,
                    "option_d": q.option_d,
                    "correct_index": q.correct_index,
                    "created_at": q.created_at
                }
                for q in quiz.questions
            ]
        )
        
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generating quiz: {str(e)}"
        )


@router.get("/", response_model=List[QuizListResponse])
async def list_quizzes(
    skip: int = 0,
    limit: int = 50,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    List user's quizzes with pagination.
    
    Args:
        skip: Number of records to skip
        limit: Maximum number of records to return
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        List[QuizListResponse]: List of quizzes
    """
    quizzes = db.query(Quiz).filter(
        Quiz.user_id == current_user.id
    ).offset(skip).limit(limit).all()
    
    return [
        QuizListResponse(
            id=quiz.id,
            topic=quiz.topic,
            title=quiz.title,
            num_questions=len(quiz.questions),
            created_at=quiz.created_at
        )
        for quiz in quizzes
    ]


@router.get("/{quiz_id}", response_model=QuizResponse)
async def get_quiz(
    quiz_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get a specific quiz by ID.
    
    Args:
        quiz_id: Quiz ID
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        QuizResponse: Quiz with questions
        
    Raises:
        HTTPException: If quiz not found or not owned by user
    """
    quiz = db.query(Quiz).filter(
        Quiz.id == quiz_id,
        Quiz.user_id == current_user.id
    ).first()
    
    if not quiz:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Quiz not found"
        )
    
    return QuizResponse(
        id=quiz.id,
        topic=quiz.topic,
        title=quiz.title,
        num_questions=len(quiz.questions),
        created_at=quiz.created_at,
        questions=[
            {
                "id": q.id,
                "question": q.question,
                "option_a": q.option_a,
                "option_b": q.option_b,
                "option_c": q.option_c,
                "option_d": q.option_d,
                "correct_index": q.correct_index,
                "created_at": q.created_at
            }
            for q in quiz.questions
        ]
    )


@router.post("/{quiz_id}/submit", response_model=QuizResultResponse)
async def submit_quiz(
    quiz_id: int,
    submission: QuizSubmissionRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Submit quiz answers and get results.
    
    Args:
        quiz_id: Quiz ID
        submission: Quiz submission with answers
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        QuizResultResponse: Quiz results with score
        
    Raises:
        HTTPException: If quiz not found or answers don't match
    """
    quiz = db.query(Quiz).filter(
        Quiz.id == quiz_id,
        Quiz.user_id == current_user.id
    ).first()
    
    if not quiz:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Quiz not found"
        )
    
    questions = quiz.questions
    if len(submission.answers) != len(questions):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Number of answers doesn't match number of questions"
        )
    
    # Calculate score
    correct_answers = 0
    for i, answer in enumerate(submission.answers):
        if answer == questions[i].correct_index:
            correct_answers += 1
    
    score_percentage = (correct_answers / len(questions)) * 100
    
    return QuizResultResponse(
        quiz_id=quiz.id,
        total_questions=len(questions),
        correct_answers=correct_answers,
        score_percentage=score_percentage,
        submitted_at=datetime.utcnow()
    )


@router.put("/{quiz_id}", response_model=QuizResponse)
async def update_quiz(
    quiz_id: int,
    update_data: QuizUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update quiz metadata.
    
    Args:
        quiz_id: Quiz ID
        update_data: Update data
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        QuizResponse: Updated quiz
        
    Raises:
        HTTPException: If quiz not found or not owned by user
    """
    quiz = db.query(Quiz).filter(
        Quiz.id == quiz_id,
        Quiz.user_id == current_user.id
    ).first()
    
    if not quiz:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Quiz not found"
        )
    
    # Update fields
    if update_data.topic is not None:
        quiz.topic = update_data.topic
    if update_data.title is not None:
        quiz.title = update_data.title
    
    db.commit()
    db.refresh(quiz)
    
    return QuizResponse(
        id=quiz.id,
        topic=quiz.topic,
        title=quiz.title,
        num_questions=len(quiz.questions),
        created_at=quiz.created_at,
        questions=[
            {
                "id": q.id,
                "question": q.question,
                "option_a": q.option_a,
                "option_b": q.option_b,
                "option_c": q.option_c,
                "option_d": q.option_d,
                "correct_index": q.correct_index,
                "created_at": q.created_at
            }
            for q in quiz.questions
        ]
    )


@router.delete("/{quiz_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_quiz(
    quiz_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Delete a quiz.
    
    Args:
        quiz_id: Quiz ID
        current_user: Current authenticated user
        db: Database session
        
    Raises:
        HTTPException: If quiz not found or not owned by user
    """
    quiz = db.query(Quiz).filter(
        Quiz.id == quiz_id,
        Quiz.user_id == current_user.id
    ).first()
    
    if not quiz:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Quiz not found"
        )
    
    db.delete(quiz)
    db.commit()


@router.get("/{quiz_id}/export")
async def export_quiz(
    quiz_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Export quiz as JSON.
    
    Args:
        quiz_id: Quiz ID
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        dict: Exported quiz data
        
    Raises:
        HTTPException: If quiz not found or not owned by user
    """
    quiz = db.query(Quiz).filter(
        Quiz.id == quiz_id,
        Quiz.user_id == current_user.id
    ).first()
    
    if not quiz:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Quiz not found"
        )
    
    export_data = {
        "type": "quiz",
        "version": "1.0",
        "exported_at": datetime.utcnow().isoformat(),
        "data": {
            "id": quiz.id,
            "topic": quiz.topic,
            "title": quiz.title,
            "created_at": quiz.created_at.isoformat(),
            "questions": [
                {
                    "question": q.question,
                    "options": [q.option_a, q.option_b, q.option_c, q.option_d],
                    "correct_index": q.correct_index
                }
                for q in quiz.questions
            ]
        }
    }
    
    return export_data


@router.post("/import", response_model=QuizResponse, status_code=status.HTTP_201_CREATED)
async def import_quiz(
    import_data: dict,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Import quiz from JSON data.
    
    Args:
        import_data: Import data structure
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        QuizResponse: Imported quiz
        
    Raises:
        HTTPException: If import data is invalid
    """
    try:
        # Validate import data structure
        if not isinstance(import_data, dict):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid import data format"
            )
        
        data = import_data.get("data", {})
        if not data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No data found in import"
            )
        
        topic = data.get("topic", "Imported Quiz")
        title = data.get("title", f"Quiz: {topic}")
        questions = data.get("questions", [])
        
        if not questions:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No questions found in import data"
            )
        
        # Create quiz
        quiz = Quiz(
            user_id=current_user.id,
            topic=topic,
            title=title
        )
        db.add(quiz)
        db.flush()
        
        # Create quiz questions
        for question_data in questions:
            if isinstance(question_data, dict) and "question" in question_data and "options" in question_data:
                options = list(map(str, question_data.get("options", [])))
                while len(options) < 4:
                    options.append("")
                
                quiz_question = QuizQuestion(
                    quiz_id=quiz.id,
                    question=str(question_data["question"]),
                    option_a=options[0],
                    option_b=options[1],
                    option_c=options[2],
                    option_d=options[3],
                    correct_index=int(question_data.get("correct_index", 0)) % 4
                )
                db.add(quiz_question)
        
        db.commit()
        db.refresh(quiz)
        
        return QuizResponse(
            id=quiz.id,
            topic=quiz.topic,
            title=quiz.title,
            num_questions=len(quiz.questions),
            created_at=quiz.created_at,
            questions=[
                {
                    "id": q.id,
                    "question": q.question,
                    "option_a": q.option_a,
                    "option_b": q.option_b,
                    "option_c": q.option_c,
                    "option_d": q.option_d,
                    "correct_index": q.correct_index,
                    "created_at": q.created_at
                }
                for q in quiz.questions
            ]
        )
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error importing quiz: {str(e)}"
        )
