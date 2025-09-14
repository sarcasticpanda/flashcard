"""
SQLAlchemy models for the SMARTCRAM application.
Defines database tables for users, flashcards, and quizzes.
"""

from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, ForeignKey, Index
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .database import Base


class User(Base):
    """User model for authentication and user management."""
    
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    flashcard_sets = relationship("FlashcardSet", back_populates="user", cascade="all, delete-orphan")
    quizzes = relationship("Quiz", back_populates="user", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<User(id={self.id}, email='{self.email}')>"


class FlashcardSet(Base):
    """Flashcard set model representing a collection of flashcards."""
    
    __tablename__ = "flashcard_sets"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    topic = Column(String(255), nullable=False, index=True)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="flashcard_sets")
    flashcards = relationship("Flashcard", back_populates="flashcard_set", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<FlashcardSet(id={self.id}, topic='{self.topic}')>"


class Flashcard(Base):
    """Individual flashcard model with question and answer."""
    
    __tablename__ = "flashcards"
    
    id = Column(Integer, primary_key=True, index=True)
    flashcard_set_id = Column(Integer, ForeignKey("flashcard_sets.id", ondelete="CASCADE"), nullable=False, index=True)
    question = Column(Text, nullable=False)
    answer = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    flashcard_set = relationship("FlashcardSet", back_populates="flashcards")
    
    def __repr__(self):
        return f"<Flashcard(id={self.id}, question='{self.question[:50]}...')>"


class Quiz(Base):
    """Quiz model representing a multiple-choice quiz."""
    
    __tablename__ = "quizzes"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    topic = Column(String(255), nullable=False, index=True)
    title = Column(String(255), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="quizzes")
    questions = relationship("QuizQuestion", back_populates="quiz", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Quiz(id={self.id}, title='{self.title}')>"


class QuizQuestion(Base):
    """Individual quiz question model with multiple choice options."""
    
    __tablename__ = "quiz_questions"
    
    id = Column(Integer, primary_key=True, index=True)
    quiz_id = Column(Integer, ForeignKey("quizzes.id", ondelete="CASCADE"), nullable=False, index=True)
    question = Column(Text, nullable=False)
    option_a = Column(Text, nullable=False)
    option_b = Column(Text, nullable=False)
    option_c = Column(Text, nullable=False)
    option_d = Column(Text, nullable=False)
    correct_index = Column(Integer, nullable=False, default=0)  # 0=A, 1=B, 2=C, 3=D
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    quiz = relationship("Quiz", back_populates="questions")
    
    def __repr__(self):
        return f"<QuizQuestion(id={self.id}, question='{self.question[:50]}...')>"


# Create indexes for better query performance
Index('idx_users_email', User.email)
Index('idx_flashcard_sets_user_topic', FlashcardSet.user_id, FlashcardSet.topic)
Index('idx_flashcards_set_id', Flashcard.flashcard_set_id)
Index('idx_quizzes_user_topic', Quiz.user_id, Quiz.topic)
Index('idx_quiz_questions_quiz_id', QuizQuestion.quiz_id)
