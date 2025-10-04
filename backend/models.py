"""
Database Models for CodeTantra Automation Service
PostgreSQL + SQLAlchemy ORM (PostgreSQL ONLY)
"""

from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Float, Text, Enum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime
import secrets
import re
import enum

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


# Payment-related models
class PaymentStatus(enum.Enum):
    PENDING = "pending"
    SUCCESS = "success"
    FAILED = "failed"
    CANCELLED = "cancelled"
    REFUNDED = "refunded"


class CreditPackage(Base):
    __tablename__ = "credit_packages"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    credits = Column(Integer, nullable=False)
    price = Column(Float, nullable=False)  # Price in rupees
    description = Column(String, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class PaymentTransaction(Base):
    __tablename__ = "payment_transactions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    package_id = Column(Integer, ForeignKey("credit_packages.id"))
    order_id = Column(String, unique=True, index=True, nullable=False)
    upi_transaction_id = Column(String, unique=True, index=True, nullable=True)  # UPI Transaction ID (12-digit)
    paytm_txn_id = Column(String, nullable=True)  # UPI reference or transaction ID
    paytm_txn_token = Column(String, nullable=True)
    amount = Column(Integer, nullable=False)  # Amount in paise
    credits = Column(Integer, nullable=False)
    status = Column(Enum(PaymentStatus), default=PaymentStatus.PENDING)
    paytm_response = Column(Text, nullable=True)  # JSON response from payment gateway
    checksum_hash = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)
    
    # Relationships
    user = relationship("User")
    package = relationship("CreditPackage")
    
    @property
    def amount_in_rupees(self) -> float:
        """Convert amount from paise to rupees"""
        return self.amount / 100.0
    
    @property
    def is_successful(self) -> bool:
        """Check if payment was successful"""
        return self.status == PaymentStatus.SUCCESS
    
    @property
    def is_pending(self) -> bool:
        """Check if payment is pending"""
        return self.status == PaymentStatus.PENDING

