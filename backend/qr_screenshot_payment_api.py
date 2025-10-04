"""
QR Code + Screenshot Payment System
Simple QR code generation with screenshot verification for UPI payments
"""

import qrcode
import io
import base64
import uuid
import os
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from pathlib import Path

from fastapi import APIRouter, HTTPException, Depends, Request, UploadFile, File, Form
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
    "upi_id": "ctautomationpro@paytm",  # Your UPI ID
    "merchant_name": "CodeTantra Automation",
    "merchant_code": "CTPRO"
}

# Create uploads directory
UPLOAD_DIR = Path("backend/uploads/screenshots")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

def generate_upi_qr_code(amount: int, order_id: str, merchant_name: str, upi_id: str) -> str:
    """Generate UPI QR code with payment details"""
    
    # UPI payment string format
    upi_string = f"upi://pay?pa={upi_id}&pn={merchant_name}&am={amount}&cu=INR&tn=CodeTantra Credits - Order {order_id}&tr={order_id}"
    
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

def save_screenshot(screenshot_file: UploadFile, order_id: str) -> str:
    """Save screenshot to disk and return file path"""
    
    # Create filename
    file_extension = screenshot_file.filename.split('.')[-1] if '.' in screenshot_file.filename else 'png'
    filename = f"{order_id}_screenshot.{file_extension}"
    file_path = UPLOAD_DIR / filename
    
    # Save file
    with open(file_path, 'wb') as f:
        content = screenshot_file.file.read()
        f.write(content)
    
    return str(file_path)

def verify_screenshot_content(screenshot_path: str, expected_upi_id: str, expected_amount: int) -> bool:
    """Basic verification of screenshot content"""
    
    # For now, we'll do basic file validation
    # In production, you could use OCR to extract UPI ID and amount from screenshot
    
    if not os.path.exists(screenshot_path):
        return False
    
    # Check file size (should be reasonable for a screenshot)
    file_size = os.path.getsize(screenshot_path)
    if file_size < 1000 or file_size > 10 * 1024 * 1024:  # 1KB to 10MB
        return False
    
    # For now, we'll accept any valid screenshot
    # You can add OCR here to verify UPI ID and amount
    return True

# API Endpoints
@router.post("/generate", response_model=QRPaymentResponse)
async def generate_qr_payment(
    request: QRPaymentRequest,
    db: Session = Depends(get_db)
):
    """Generate QR code for payment"""
    
    # Verify user credentials
    user = verify_user_credentials(db, request.username, request.password)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid username or password")
    
    # Get credit package
    package = db.query(CreditPackage).filter(
        CreditPackage.id == request.package_id,
        CreditPackage.is_active == True
    ).first()
    
    if not package:
        raise HTTPException(status_code=404, detail="Credit package not found")
    
    # Create payment transaction
    amount_paise = package.price * 100  # Convert to paise
    transaction = create_qr_payment_transaction(
        db, user.id, package.id, amount_paise, package.credits
    )
    
    # Generate QR code
    qr_code = generate_upi_qr_code(
        package.price,
        transaction.order_id,
        UPI_PAYMENT_DETAILS["merchant_name"],
        UPI_PAYMENT_DETAILS["upi_id"]
    )
    
    # Set expiration time (30 minutes)
    expires_at = datetime.utcnow() + timedelta(minutes=30)
    
    return QRPaymentResponse(
        qr_code=qr_code,
        upi_id=UPI_PAYMENT_DETAILS["upi_id"],
        amount=package.price,
        order_id=transaction.order_id,
        payment_reference=transaction.order_id,
        expires_at=expires_at.isoformat()
    )

@router.post("/verify")
async def verify_screenshot_payment(
    order_id: str = Form(...),
    upi_reference: str = Form(...),
    screenshot: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """Verify payment using screenshot and UPI reference"""
    
    # Get transaction
    transaction = db.query(PaymentTransaction).filter(
        PaymentTransaction.order_id == order_id
    ).first()
    
    if not transaction:
        return JSONResponse(
            status_code=404,
            content={"verified": False, "status": "error", "message": "Transaction not found"}
        )
    
    if transaction.status != PaymentStatus.PENDING:
        return JSONResponse(
            status_code=400,
            content={"verified": False, "status": "already_processed", "message": "Transaction already processed"}
        )
    
    # Check if UPI reference is valid (basic validation)
    if not upi_reference or len(upi_reference) < 10:
        return JSONResponse(
            status_code=400,
            content={"verified": False, "status": "invalid_reference", "message": "Invalid UPI reference number"}
        )
    
    try:
        # Save screenshot
        screenshot_path = save_screenshot(screenshot, order_id)
        
        # Verify screenshot content
        if not verify_screenshot_content(screenshot_path, UPI_PAYMENT_DETAILS["upi_id"], transaction.amount_in_rupees):
            return JSONResponse(
                status_code=400,
                content={"verified": False, "status": "invalid_screenshot", "message": "Invalid screenshot format or content"}
            )
        
        # Payment verified
        transaction.status = PaymentStatus.SUCCESS
        transaction.paytm_txn_id = upi_reference
        transaction.completed_at = datetime.utcnow()
        transaction.paytm_response = f'{{"UPI_REFERENCE": "{upi_reference}", "SCREENSHOT_PATH": "{screenshot_path}"}}'
        
        # Add credits to user
        add_credits_to_user(db, transaction.user_id, transaction.credits, transaction.id)
        
        db.commit()
        
        return JSONResponse(
            status_code=200,
            content={
                "verified": True,
                "status": "success",
                "message": "Payment verified and credits added",
                "credits_added": transaction.credits
            }
        )
        
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"verified": False, "status": "error", "message": f"Error processing screenshot: {str(e)}"}
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

@router.get("/screenshot/{order_id}")
async def get_screenshot(order_id: str, db: Session = Depends(get_db)):
    """Get screenshot for a transaction (for verification purposes)"""
    
    transaction = db.query(PaymentTransaction).filter(
        PaymentTransaction.order_id == order_id
    ).first()
    
    if not transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")
    
    # Extract screenshot path from paytm_response
    import json
    try:
        response_data = json.loads(transaction.paytm_response or "{}")
        screenshot_path = response_data.get("SCREENSHOT_PATH")
        
        if not screenshot_path or not os.path.exists(screenshot_path):
            raise HTTPException(status_code=404, detail="Screenshot not found")
        
        # Return file
        return FileResponse(screenshot_path)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving screenshot: {str(e)}")
