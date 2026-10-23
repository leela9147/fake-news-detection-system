from sqlalchemy import Column, Integer, String, Float, DateTime, Text, ForeignKey, JSON
from sqlalchemy.sql import func
from app.database import Base

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String(120), nullable=False)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

class PasswordResetToken(Base):
    __tablename__ = 'password_reset_tokens'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    token_hash = Column(String(64), nullable=False, index=True)
    expires_at = Column(DateTime(timezone=True), nullable=False)
    used_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class Prediction(Base):
    __tablename__ = 'predictions'
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    headline = Column(Text, nullable=False)
    article_content = Column(Text, nullable=False)
    ml_prediction = Column(String(30), nullable=False)  # LIKELY REAL / LIKELY FAKE / NEEDS VERIFICATION
    ml_confidence = Column(Float, nullable=False)
    model_name = Column(String(60), nullable=False)
    simple_explanation = Column(Text, nullable=False)
    technical_explanation = Column(JSON, nullable=False)
    verification_status = Column(String(30), nullable=False)  # SUPPORTING / CONTRADICTING / INSUFFICIENT / UNAVAILABLE
    verification_summary = Column(Text, nullable=False)
    sources = Column(JSON, nullable=False)
    final_assessment = Column(String(30), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
