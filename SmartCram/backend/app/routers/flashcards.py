"""
Flashcards router for generating, managing, and exporting flashcard sets.
Handles AI-powered flashcard generation and CRUD operations.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
import json
from datetime import datetime

from ..db.database import get_db
from ..db.models import User, FlashcardSet, Flashcard
from ..schemas.flashcards import (
    FlashcardGenerateRequest,
    FlashcardSetResponse,
    FlashcardSetListResponse,
    FlashcardUpdateRequest,
    FlashcardSetUpdateRequest
)
from ..core.openai_client import openai_client
from .auth import get_current_user

# Initialize router
router = APIRouter(prefix="/flashcards", tags=["Flashcards"])


@router.post("/generate", response_model=FlashcardSetResponse, status_code=status.HTTP_201_CREATED)
async def generate_flashcards(
    request: FlashcardGenerateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Generate flashcards using AI from source text.
    
    Args:
        request: Flashcard generation request
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        FlashcardSetResponse: Generated flashcard set
        
    Raises:
        HTTPException: If generation fails
    """
    try:
        # Generate flashcards using OpenAI
        generated_cards = openai_client.generate_flashcards(
            topic=request.topic,
            source_text=request.source_text,
            num_cards=request.num_cards
        )
        
        if not generated_cards:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to generate flashcards"
            )
        
        # Create flashcard set
        flashcard_set = FlashcardSet(
            user_id=current_user.id,
            topic=request.topic,
            description=request.description
        )
        db.add(flashcard_set)
        db.flush()  # Get the ID without committing
        
        # Create individual flashcards
        for card_data in generated_cards:
            flashcard = Flashcard(
                flashcard_set_id=flashcard_set.id,
                question=card_data["question"],
                answer=card_data["answer"]
            )
            db.add(flashcard)
        
        db.commit()
        db.refresh(flashcard_set)
        
        # Return response with flashcards
        return FlashcardSetResponse(
            id=flashcard_set.id,
            topic=flashcard_set.topic,
            description=flashcard_set.description,
            num_cards=len(flashcard_set.flashcards),
            created_at=flashcard_set.created_at,
            flashcards=[
                {
                    "id": card.id,
                    "question": card.question,
                    "answer": card.answer,
                    "created_at": card.created_at
                }
                for card in flashcard_set.flashcards
            ]
        )
        
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generating flashcards: {str(e)}"
        )


@router.get("/", response_model=List[FlashcardSetListResponse])
async def list_flashcard_sets(
    skip: int = 0,
    limit: int = 50,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    List user's flashcard sets with pagination.
    
    Args:
        skip: Number of records to skip
        limit: Maximum number of records to return
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        List[FlashcardSetListResponse]: List of flashcard sets
    """
    flashcard_sets = db.query(FlashcardSet).filter(
        FlashcardSet.user_id == current_user.id
    ).offset(skip).limit(limit).all()
    
    return [
        FlashcardSetListResponse(
            id=set.id,
            topic=set.topic,
            description=set.description,
            num_cards=len(set.flashcards),
            created_at=set.created_at
        )
        for set in flashcard_sets
    ]


@router.get("/{set_id}", response_model=FlashcardSetResponse)
async def get_flashcard_set(
    set_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get a specific flashcard set by ID.
    
    Args:
        set_id: Flashcard set ID
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        FlashcardSetResponse: Flashcard set with cards
        
    Raises:
        HTTPException: If set not found or not owned by user
    """
    flashcard_set = db.query(FlashcardSet).filter(
        FlashcardSet.id == set_id,
        FlashcardSet.user_id == current_user.id
    ).first()
    
    if not flashcard_set:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Flashcard set not found"
        )
    
    return FlashcardSetResponse(
        id=flashcard_set.id,
        topic=flashcard_set.topic,
        description=flashcard_set.description,
        num_cards=len(flashcard_set.flashcards),
        created_at=flashcard_set.created_at,
        flashcards=[
            {
                "id": card.id,
                "question": card.question,
                "answer": card.answer,
                "created_at": card.created_at
            }
            for card in flashcard_set.flashcards
        ]
    )


@router.put("/{set_id}", response_model=FlashcardSetResponse)
async def update_flashcard_set(
    set_id: int,
    update_data: FlashcardSetUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update flashcard set metadata.
    
    Args:
        set_id: Flashcard set ID
        update_data: Update data
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        FlashcardSetResponse: Updated flashcard set
        
    Raises:
        HTTPException: If set not found or not owned by user
    """
    flashcard_set = db.query(FlashcardSet).filter(
        FlashcardSet.id == set_id,
        FlashcardSet.user_id == current_user.id
    ).first()
    
    if not flashcard_set:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Flashcard set not found"
        )
    
    # Update fields
    if update_data.topic is not None:
        flashcard_set.topic = update_data.topic
    if update_data.description is not None:
        flashcard_set.description = update_data.description
    
    db.commit()
    db.refresh(flashcard_set)
    
    return FlashcardSetResponse(
        id=flashcard_set.id,
        topic=flashcard_set.topic,
        description=flashcard_set.description,
        num_cards=len(flashcard_set.flashcards),
        created_at=flashcard_set.created_at,
        flashcards=[
            {
                "id": card.id,
                "question": card.question,
                "answer": card.answer,
                "created_at": card.created_at
            }
            for card in flashcard_set.flashcards
        ]
    )


@router.delete("/{set_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_flashcard_set(
    set_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Delete a flashcard set.
    
    Args:
        set_id: Flashcard set ID
        current_user: Current authenticated user
        db: Database session
        
    Raises:
        HTTPException: If set not found or not owned by user
    """
    flashcard_set = db.query(FlashcardSet).filter(
        FlashcardSet.id == set_id,
        FlashcardSet.user_id == current_user.id
    ).first()
    
    if not flashcard_set:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Flashcard set not found"
        )
    
    db.delete(flashcard_set)
    db.commit()


@router.get("/{set_id}/export")
async def export_flashcard_set(
    set_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Export flashcard set as JSON.
    
    Args:
        set_id: Flashcard set ID
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        dict: Exported flashcard set data
        
    Raises:
        HTTPException: If set not found or not owned by user
    """
    flashcard_set = db.query(FlashcardSet).filter(
        FlashcardSet.id == set_id,
        FlashcardSet.user_id == current_user.id
    ).first()
    
    if not flashcard_set:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Flashcard set not found"
        )
    
    export_data = {
        "type": "flashcard_set",
        "version": "1.0",
        "exported_at": datetime.utcnow().isoformat(),
        "data": {
            "id": flashcard_set.id,
            "topic": flashcard_set.topic,
            "description": flashcard_set.description,
            "created_at": flashcard_set.created_at.isoformat(),
            "cards": [
                {
                    "question": card.question,
                    "answer": card.answer
                }
                for card in flashcard_set.flashcards
            ]
        }
    }
    
    return export_data


@router.post("/import", response_model=FlashcardSetResponse, status_code=status.HTTP_201_CREATED)
async def import_flashcard_set(
    import_data: dict,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Import flashcard set from JSON data.
    
    Args:
        import_data: Import data structure
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        FlashcardSetResponse: Imported flashcard set
        
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
        
        topic = data.get("topic", "Imported Set")
        description = data.get("description")
        cards = data.get("cards", [])
        
        if not cards:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No flashcards found in import data"
            )
        
        # Create flashcard set
        flashcard_set = FlashcardSet(
            user_id=current_user.id,
            topic=topic,
            description=description
        )
        db.add(flashcard_set)
        db.flush()
        
        # Create flashcards
        for card_data in cards:
            if isinstance(card_data, dict) and "question" in card_data and "answer" in card_data:
                flashcard = Flashcard(
                    flashcard_set_id=flashcard_set.id,
                    question=str(card_data["question"]),
                    answer=str(card_data["answer"])
                )
                db.add(flashcard)
        
        db.commit()
        db.refresh(flashcard_set)
        
        return FlashcardSetResponse(
            id=flashcard_set.id,
            topic=flashcard_set.topic,
            description=flashcard_set.description,
            num_cards=len(flashcard_set.flashcards),
            created_at=flashcard_set.created_at,
            flashcards=[
                {
                    "id": card.id,
                    "question": card.question,
                    "answer": card.answer,
                    "created_at": card.created_at
                }
                for card in flashcard_set.flashcards
            ]
        )
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error importing flashcard set: {str(e)}"
        )
