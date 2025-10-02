"""
Database Models for CodeTantra Automation Service
SQLite + SQLAlchemy ORM
"""

from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime
import secrets
import re

Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    college_name = Column(String, nullable=False)
    age = Column(Integer, nullable=False)
    password_hash = Column(String, nullable=False)
    credits = Column(Integer, default=80)  # 80 free credits on signup
    is_active = Column(Boolean, default=True)
    is_admin = Column(Boolean, default=False)
    referral_code = Column(String, unique=True, index=True)
    referred_by = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_login = Column(DateTime, nullable=True)
    
    # Relationships
    transactions = relationship("Transaction", back_populates="user")
    usage_logs = relationship("UsageLog", back_populates="user")
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if not self.referral_code:
            self.referral_code = secrets.token_urlsafe(8)
    
    @staticmethod
    def is_educational_email(email: str) -> bool:
        """Check if email is from an educational domain"""
        educational_domains = ['.ac.in', '.edu.in', '.edu', '.ac.uk', '.edu.au']
        return any(email.lower().endswith(domain) for domain in educational_domains)


class Transaction(Base):
    __tablename__ = "transactions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    amount = Column(Integer, nullable=False)
    transaction_type = Column(String, nullable=False)  # 'signup', 'referral', 'purchase', 'usage', 'admin_add'
    description = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="transactions")


class UsageLog(Base):
    __tablename__ = "usage_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    problem_type = Column(String, nullable=False)  # 'code_completion', 'other'
    credits_used = Column(Integer, nullable=False)
    success = Column(Boolean, nullable=False)
    problem_number = Column(Integer, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="usage_logs")


class VerificationToken(Base):
    __tablename__ = "verification_tokens"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    token = Column(String, unique=True, index=True)
    token_type = Column(String, nullable=False)  # 'email_verification', 'password_reset'
    expires_at = Column(DateTime, nullable=False)
    used = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

