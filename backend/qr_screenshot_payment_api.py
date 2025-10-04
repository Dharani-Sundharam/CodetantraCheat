"""
QR Code + Screenshot Payment System
Simple QR code generation with screenshot verification for UPI payments
"""

import qrcode
import io
import base64
import uuid
import os
import re
from PIL import Image
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from pathlib import Path

from fastapi import APIRouter, HTTPException, Depends, Request
from fastapi.responses import HTMLResponse, JSONResponse, FileResponse
from sqlalchemy.orm import Session
from pydantic import BaseModel

from database import get_db
from models import User, CreditPackage, PaymentTransaction, PaymentStatus, Transaction
from auth import get_current_user

router = APIRouter(prefix="/api/qr-payment", tags=["qr-payment"])

# Pydantic models
class QRPaymentRequest(BaseModel):
    package_id: int
    username: str
    password: str

class QRPaymentResponse(BaseModel):
    qr_code: str  # Base64 encoded QR code
    upi_id: str
    amount: int
    order_id: str
    payment_reference: str
    expires_at: str
    user_email: str

class ScreenshotVerificationRequest(BaseModel):
    order_id: str
    upi_reference: str

class PaymentVerificationResponse(BaseModel):
    verified: bool
    status: str
    message: str
    credits_added: Optional[int] = None

# UPI Payment Details (You can customize these)
UPI_PAYMENT_DETAILS = {
    "upi_id": "paytm.s17np8c@pty",  # Your UPI ID
    "merchant_name": "CodeTantra Automation",
    "merchant_code": "CTPRO"
}

# Create uploads directory

def generate_upi_qr_code(amount: int, order_id: str, merchant_name: str, upi_id: str) -> str:
    """Generate UPI QR code with payment details"""
    
    # UPI payment string format with amount included
    upi_string = f"upi://pay?pa={upi_id}&pn={merchant_name}&am={amount}&cu=INR&tn=CodeTantra Credits Rs{amount} - Order {order_id}&tr={order_id}"
    
    # Generate QR code
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(upi_string)
    qr.make(fit=True)
    
    # Create image
    img = qr.make_image(fill_color="black", back_color="white")
    
    # Convert to base64
    buffer = io.BytesIO()
    img.save(buffer, format='PNG')
    buffer.seek(0)
    
    # Encode as base64
    img_base64 = base64.b64encode(buffer.getvalue()).decode()
    
    return f"data:image/png;base64,{img_base64}"

def verify_user_credentials(db: Session, username: str, password: str) -> Optional[User]:
    """Verify user credentials and return user object"""
    from auth import verify_password
    
    # Try to find user by email (assuming username is email)
    user = db.query(User).filter(User.email == username).first()
    
    if not user:
        return None
    
    if not verify_password(password, user.password_hash):
        return None
    
    return user

def create_qr_payment_transaction(
    db: Session, 
    user_id: int, 
    package_id: int, 
    amount: int, 
    credits: int
) -> PaymentTransaction:
    """Create a new QR payment transaction record"""
    
    transaction = PaymentTransaction(
        user_id=user_id,
        package_id=package_id,
        amount=amount,  # Amount in paise
        credits=credits,
        status=PaymentStatus.PENDING,
        order_id=f"QR_{uuid.uuid4().hex[:12].upper()}"
    )
    
    db.add(transaction)
    db.commit()
    db.refresh(transaction)
    
    return transaction

def add_credits_to_user(db: Session, user_id: int, credits: int, transaction_id: int):
    """Add credits to user account and create transaction record"""
    
    # Update user credits
    user = db.query(User).filter(User.id == user_id).first()
    if user:
        user.credits += credits
        db.commit()
        
        # Create transaction record
        transaction_record = Transaction(
            user_id=user_id,
            amount=credits,
            transaction_type="purchase",
            description=f"Credits purchased via QR payment {transaction_id}"
        )
        db.add(transaction_record)
        db.commit()


def check_transaction_id_uniqueness(db: Session, txn_id: str, transaction_id: int) -> bool:
    """Check if UPI Transaction ID has been used before for a different transaction"""
    existing_transaction = db.query(PaymentTransaction).filter(
        PaymentTransaction.upi_transaction_id == txn_id,
        PaymentTransaction.id != transaction_id,
        PaymentTransaction.status == PaymentStatus.SUCCESS
    ).first()
    
    return existing_transaction is None

# API Endpoints
@router.post("/generate", response_model=QRPaymentResponse)
async def generate_qr_payment(
    request: QRPaymentRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Generate QR code for payment"""
    
    # Get credit package
    package = db.query(CreditPackage).filter(
        CreditPackage.id == request.package_id,
        CreditPackage.is_active == True
    ).first()
    
    if not package:
        raise HTTPException(status_code=404, detail="Credit package not found")
    
    # Create payment transaction
    amount_paise = int(package.price * 100)  # Convert to paise
    transaction = create_qr_payment_transaction(
        db, current_user.id, package.id, amount_paise, package.credits
    )
    
    # Generate QR code with actual package amount
    qr_code = generate_upi_qr_code(
        package.price,  # Use actual package price
        transaction.order_id,
        UPI_PAYMENT_DETAILS["merchant_name"],
        UPI_PAYMENT_DETAILS["upi_id"]
    )
    
    # Set expiration time (30 minutes)
    expires_at = datetime.utcnow() + timedelta(minutes=30)
    
    return QRPaymentResponse(
        qr_code=qr_code,
        upi_id=UPI_PAYMENT_DETAILS["upi_id"],
        amount=package.price,  # Return actual package price
        order_id=transaction.order_id,
        payment_reference=transaction.order_id,
        expires_at=expires_at.isoformat(),
        user_email=current_user.email
    )


@router.get("/status/{order_id}")
async def get_payment_status(order_id: str, db: Session = Depends(get_db)):
    """Get payment status for an order"""
    
    transaction = db.query(PaymentTransaction).filter(
        PaymentTransaction.order_id == order_id
    ).first()
    
    if not transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")
    
    return {
        "order_id": transaction.order_id,
        "status": transaction.status.value,
        "amount": transaction.amount_in_rupees,
        "credits": transaction.credits,
        "created_at": transaction.created_at.isoformat(),
        "completed_at": transaction.completed_at.isoformat() if transaction.completed_at else None
    }

@router.get("/packages")
async def get_credit_packages(db: Session = Depends(get_db)):
    """Get available credit packages"""
    packages = db.query(CreditPackage).filter(CreditPackage.is_active == True).all()
    return packages


@router.get("/history")
async def get_transaction_history(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    page: int = 1,
    limit: int = 10
):
    """Get user's payment transaction history"""
    
    # Calculate offset for pagination
    offset = (page - 1) * limit
    
    # Get transactions for the user
    transactions = db.query(PaymentTransaction).filter(
        PaymentTransaction.user_id == current_user.id
    ).order_by(PaymentTransaction.created_at.desc()).offset(offset).limit(limit).all()
    
    # Get total count for pagination
    total_count = db.query(PaymentTransaction).filter(
        PaymentTransaction.user_id == current_user.id
    ).count()
    
    # Format transaction data
    transaction_list = []
    for txn in transactions:
        transaction_list.append({
            "id": txn.id,
            "order_id": txn.order_id,
            "upi_transaction_id": txn.upi_transaction_id,
            "package_name": txn.package.name if txn.package else "Unknown Package",
            "amount": txn.amount_in_rupees,
            "credits": txn.credits,
            "status": txn.status.value,
            "created_at": txn.created_at.isoformat(),
            "completed_at": txn.completed_at.isoformat() if txn.completed_at else None,
            "is_successful": txn.is_successful
        })
    
        return {
            "transactions": transaction_list,
            "pagination": {
                "page": page,
                "limit": limit,
                "total": total_count,
                "pages": (total_count + limit - 1) // limit
            }
        }

@router.post("/verify-manual")
async def verify_manual_payment(
    request: dict,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Verify payment using manually entered UPI Transaction ID"""
    
    order_id = request.get("order_id")
    upi_transaction_id = request.get("upi_transaction_id")
    
    if not order_id or not upi_transaction_id:
        return JSONResponse(
            status_code=400,
            content={"verified": False, "status": "error", "message": "Missing order_id or upi_transaction_id"}
        )
    
    # Validate UPI Transaction ID format (12 digits)
    if not re.match(r'^\d{12}$', upi_transaction_id):
        return JSONResponse(
            status_code=400,
            content={"verified": False, "status": "error", "message": "Invalid UPI Transaction ID format. Must be 12 digits."}
        )
    
    # Get transaction
    transaction = db.query(PaymentTransaction).filter(
        PaymentTransaction.order_id == order_id,
        PaymentTransaction.user_id == current_user.id
    ).first()
    
    if not transaction:
        return JSONResponse(
            status_code=400,
            content={"verified": False, "status": "error", "message": f"Transaction not found for order_id: {order_id}"}
        )
    
    if transaction.status != PaymentStatus.PENDING:
        return JSONResponse(
            status_code=400,
            content={"verified": False, "status": "already_processed", "message": "Transaction already processed"}
        )
    
    try:
        # Check for duplicate UPI Transaction ID
        if not check_transaction_id_uniqueness(db, upi_transaction_id, transaction.id):
            return JSONResponse(
                status_code=400,
                content={
                    "verified": False, 
                    "status": "duplicate_transaction_id", 
                    "message": "This UPI Transaction ID has already been used for another transaction. Please try again with a different payment."
                }
            )
        
        # Payment verified - update transaction
        transaction.status = PaymentStatus.SUCCESS
        transaction.upi_transaction_id = upi_transaction_id
        transaction.paytm_txn_id = upi_transaction_id  # Keep for backward compatibility
        transaction.completed_at = datetime.utcnow()
        transaction.paytm_response = f'{{"UPI_TXN_ID": "{upi_transaction_id}", "MANUAL_ENTRY": true}}'
        
        # Add credits to user account
        add_credits_to_user(db, transaction.user_id, transaction.credits, transaction.id)
        
        db.commit()
        
        return JSONResponse(
            status_code=200,
            content={
                "verified": True, 
                "status": "success", 
                "message": f"Payment verified! Amount: Rs. {transaction.amount_in_rupees}, Transaction ID: {upi_transaction_id}. {transaction.credits} credits added to your account.",
                "credits_added": transaction.credits,
                "upi_transaction_id": upi_transaction_id,
                "amount_paid": transaction.amount_in_rupees,
                "transaction_details": {
                    "amount": f"Rs. {transaction.amount_in_rupees}",
                    "transaction_id": upi_transaction_id,
                    "credits_added": transaction.credits
                }
            }
        )
        
    except Exception as e:
        db.rollback()
        return JSONResponse(
            status_code=500,
            content={"verified": False, "status": "error", "message": f"Error processing payment: {str(e)}"}
        )
