"""
CodeTantra Automation Service - Main FastAPI Application
Complete API for authentication, credits, and user management
"""

from fastapi import FastAPI, Depends, HTTPException, status, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime, timedelta

import database
import auth
import email_service
from models import User, Transaction, UsageLog
from database import get_db

# Initialize FastAPI app
app = FastAPI(title="CodeTantra Automation API", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Change to specific origins in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models for request/response
class UserRegister(BaseModel):
    name: str
    email: EmailStr
    college_name: str
    age: int
    password: str
    referral_code: Optional[str] = None

class UserLogin(BaseModel):
    email: EmailStr
    password: str
    remember_me: bool = False

class PasswordReset(BaseModel):
    email: EmailStr

class PasswordResetConfirm(BaseModel):
    token: str
    new_password: str

class CreditDeduction(BaseModel):
    problem_type: str  # 'code_completion' or 'other'
    success: bool
    problem_number: Optional[int] = None

class AdminCreditUpdate(BaseModel):
    user_email: EmailStr
    credits_to_add: int
    reason: str

class UserResponse(BaseModel):
    id: int
    name: str
    email: str
    college_name: str
    age: int
    credits: int
    is_verified: bool
    is_admin: bool
    referral_code: str
    created_at: datetime

# Mount static files (frontend)
app.mount("/", StaticFiles(directory="../frontend", html=True), name="frontend")

# Initialize database on startup
@app.on_event("startup")
async def startup_event():
    database.init_database()

# Health check endpoint
@app.get("/")
async def root():
    return {"status": "ok", "message": "CodeTantra Automation API is running"}

# Authentication endpoints
@app.post("/api/auth/register")
async def register(user_data: UserRegister, db: Session = Depends(get_db)):
    """Register a new user"""
    # Check if email already exists
    existing_user = db.query(User).filter(User.email == user_data.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # Validate referral code if provided
    referrer = None
    if user_data.referral_code:
        referrer = db.query(User).filter(User.referral_code == user_data.referral_code).first()
        if not referrer:
            raise HTTPException(status_code=400, detail="Invalid referral code")
    
    # Create new user
    new_user = User(
        name=user_data.name,
        email=user_data.email,
        college_name=user_data.college_name,
        age=user_data.age,
        password_hash=auth.hash_password(user_data.password),
        referred_by=user_data.referral_code if referrer else None
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    # Create signup transaction
    transaction = Transaction(
        user_id=new_user.id,
        amount=80,
        transaction_type="signup",
        description="Welcome bonus - 80 free credits"
    )
    db.add(transaction)
    db.commit()
    
    # Create verification token and send email
    token = auth.create_verification_token(db, new_user.id, "email_verification")
    email_service.send_verification_email(new_user.email, token, new_user.name)
    
    return {"message": "Registration successful. Please check your email to verify your account."}

@app.get("/api/auth/verify-email")
async def verify_email(token: str, db: Session = Depends(get_db)):
    """Verify user email with token"""
    user = auth.verify_token(token, db, "email_verification")
    if not user:
        raise HTTPException(status_code=400, detail="Invalid or expired verification token")
    
    # Mark user as verified
    user.is_verified = True
    db.commit()
    
    # Send welcome email
    email_service.send_welcome_email(user.email, user.name, user.referral_code)
    
    # Award referral bonus if applicable
    if user.referred_by:
        referrer = db.query(User).filter(User.referral_code == user.referred_by).first()
        if referrer:
            referrer.credits += 70  # 70 credits for referral
            transaction = Transaction(
                user_id=referrer.id,
                amount=70,
                transaction_type="referral",
                description=f"Referral bonus for {user.email}"
            )
            db.add(transaction)
            db.commit()
    
    return {"message": "Email verified successfully! You can now log in."}

@app.post("/api/auth/login")
async def login(credentials: UserLogin, db: Session = Depends(get_db)):
    """User login"""
    user = db.query(User).filter(User.email == credentials.email).first()
    
    if not user or not auth.verify_password(credentials.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid email or password")
    
    if not user.is_verified:
        raise HTTPException(status_code=403, detail="Please verify your email first")
    
    if not user.is_active:
        raise HTTPException(status_code=403, detail="Account suspended. Please contact support.")
    
    # Update last login
    user.last_login = datetime.utcnow()
    db.commit()
    
    # Create access token
    token_expires = timedelta(days=30) if credentials.remember_me else timedelta(days=7)
    access_token = auth.create_access_token(
        data={"sub": user.email},
        expires_delta=token_expires
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": UserResponse(
            id=user.id,
            name=user.name,
            email=user.email,
            college_name=user.college_name,
            age=user.age,
            credits=user.credits,
            is_verified=user.is_verified,
            is_admin=user.is_admin,
            referral_code=user.referral_code,
            created_at=user.created_at
        )
    }

@app.post("/api/auth/forgot-password")
async def forgot_password(data: PasswordReset, db: Session = Depends(get_db)):
    """Request password reset"""
    user = db.query(User).filter(User.email == data.email).first()
    
    if not user:
        # Don't reveal if email exists
        return {"message": "If the email exists, a password reset link has been sent."}
    
    # Create reset token and send email
    token = auth.create_verification_token(db, user.id, "password_reset")
    email_service.send_password_reset_email(user.email, token, user.name)
    
    return {"message": "If the email exists, a password reset link has been sent."}

@app.post("/api/auth/reset-password")
async def reset_password(data: PasswordResetConfirm, db: Session = Depends(get_db)):
    """Reset password with token"""
    user = auth.verify_token(data.token, db, "password_reset")
    if not user:
        raise HTTPException(status_code=400, detail="Invalid or expired reset token")
    
    # Update password
    user.password_hash = auth.hash_password(data.new_password)
    db.commit()
    
    return {"message": "Password reset successfully. You can now log in with your new password."}

# User endpoints
@app.get("/api/user/profile")
async def get_profile(current_user: User = Depends(auth.get_current_user)):
    """Get current user profile"""
    return UserResponse(
        id=current_user.id,
        name=current_user.name,
        email=current_user.email,
        college_name=current_user.college_name,
        age=current_user.age,
        credits=current_user.credits,
        is_verified=current_user.is_verified,
        is_admin=current_user.is_admin,
        referral_code=current_user.referral_code,
        created_at=current_user.created_at
    )

@app.get("/api/user/credits")
async def get_credits(current_user: User = Depends(auth.get_current_user)):
    """Get user credits"""
    return {"credits": current_user.credits}

@app.post("/api/credits/deduct")
async def deduct_credits(
    deduction: CreditDeduction,
    current_user: User = Depends(auth.get_current_user),
    db: Session = Depends(get_db)
):
    """Deduct credits for problem completion"""
    # Determine credits to deduct
    if deduction.success:
        if deduction.problem_type == "code_completion":
            credits_to_deduct = 5
        else:
            credits_to_deduct = 3
    else:
        credits_to_deduct = 1  # Failed problem
    
    # Check if user has enough credits
    if current_user.credits < credits_to_deduct:
        raise HTTPException(status_code=402, detail="Insufficient credits")
    
    # Deduct credits
    current_user.credits -= credits_to_deduct
    
    # Create transaction record
    transaction = Transaction(
        user_id=current_user.id,
        amount=-credits_to_deduct,
        transaction_type="usage",
        description=f"{'Success' if deduction.success else 'Failed'} - {deduction.problem_type} problem {deduction.problem_number or ''}"
    )
    db.add(transaction)
    
    # Create usage log
    usage_log = UsageLog(
        user_id=current_user.id,
        problem_type=deduction.problem_type,
        credits_used=credits_to_deduct,
        success=deduction.success,
        problem_number=deduction.problem_number
    )
    db.add(usage_log)
    
    db.commit()
    
    return {
        "message": "Credits deducted successfully",
        "credits_deducted": credits_to_deduct,
        "remaining_credits": current_user.credits
    }

@app.get("/api/user/usage-history")
async def get_usage_history(
    current_user: User = Depends(auth.get_current_user),
    db: Session = Depends(get_db)
):
    """Get user usage history"""
    logs = db.query(UsageLog).filter(
        UsageLog.user_id == current_user.id
    ).order_by(UsageLog.created_at.desc()).limit(100).all()
    
    return {
        "logs": [
            {
                "id": log.id,
                "problem_type": log.problem_type,
                "credits_used": log.credits_used,
                "success": log.success,
                "problem_number": log.problem_number,
                "created_at": log.created_at
            }
            for log in logs
        ]
    }

@app.get("/api/user/transactions")
async def get_transactions(
    current_user: User = Depends(auth.get_current_user),
    db: Session = Depends(get_db)
):
    """Get user transaction history"""
    transactions = db.query(Transaction).filter(
        Transaction.user_id == current_user.id
    ).order_by(Transaction.created_at.desc()).limit(100).all()
    
    return {
        "transactions": [
            {
                "id": t.id,
                "amount": t.amount,
                "type": t.transaction_type,
                "description": t.description,
                "created_at": t.created_at
            }
            for t in transactions
        ]
    }

# Admin endpoints
@app.get("/api/admin/users")
async def get_all_users(
    skip: int = 0,
    limit: int = 100,
    current_admin: User = Depends(auth.get_current_admin),
    db: Session = Depends(get_db)
):
    """Get all users (admin only)"""
    users = db.query(User).offset(skip).limit(limit).all()
    
    return {
        "users": [
            {
                "id": u.id,
                "name": u.name,
                "email": u.email,
                "college_name": u.college_name,
                "credits": u.credits,
                "is_verified": u.is_verified,
                "is_active": u.is_active,
                "created_at": u.created_at,
                "last_login": u.last_login
            }
            for u in users
        ]
    }

@app.post("/api/admin/credits")
async def admin_add_credits(
    data: AdminCreditUpdate,
    current_admin: User = Depends(auth.get_current_admin),
    db: Session = Depends(get_db)
):
    """Add or remove credits (admin only)"""
    user = db.query(User).filter(User.email == data.user_email).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Update credits
    user.credits += data.credits_to_add
    
    # Create transaction
    transaction = Transaction(
        user_id=user.id,
        amount=data.credits_to_add,
        transaction_type="admin_add",
        description=f"Admin adjustment: {data.reason}"
    )
    db.add(transaction)
    db.commit()
    
    return {"message": f"Credits updated successfully", "new_balance": user.credits}

@app.post("/api/admin/suspend-user")
async def suspend_user(
    user_email: EmailStr,
    current_admin: User = Depends(auth.get_current_admin),
    db: Session = Depends(get_db)
):
    """Suspend a user (admin only)"""
    user = db.query(User).filter(User.email == user_email).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    user.is_active = False
    db.commit()
    
    return {"message": f"User {user_email} suspended successfully"}

@app.post("/api/admin/activate-user")
async def activate_user(
    user_email: EmailStr,
    current_admin: User = Depends(auth.get_current_admin),
    db: Session = Depends(get_db)
):
    """Activate a suspended user (admin only)"""
    user = db.query(User).filter(User.email == user_email).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    user.is_active = True
    db.commit()
    
    return {"message": f"User {user_email} activated successfully"}

@app.get("/api/admin/stats")
async def get_stats(
    current_admin: User = Depends(auth.get_current_admin),
    db: Session = Depends(get_db)
):
    """Get platform statistics (admin only)"""
    total_users = db.query(User).count()
    verified_users = db.query(User).filter(User.is_verified == True).count()
    active_users = db.query(User).filter(User.is_active == True).count()
    total_usage = db.query(UsageLog).count()
    
    return {
        "total_users": total_users,
        "verified_users": verified_users,
        "active_users": active_users,
        "total_problems_solved": total_usage
    }

# Run server
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

