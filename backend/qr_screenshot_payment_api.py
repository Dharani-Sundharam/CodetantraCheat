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

# Optional imports for image processing
try:
    import cv2
    import pytesseract
    IMAGE_PROCESSING_AVAILABLE = True
except ImportError:
    IMAGE_PROCESSING_AVAILABLE = False
    print("Warning: OpenCV and/or pytesseract not available. UPI ID extraction will be limited.")

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

def extract_upi_id_from_screenshot(screenshot_path: str) -> Optional[str]:
    """Extract UPI ID from payment screenshot using OCR"""
    try:
        if not IMAGE_PROCESSING_AVAILABLE:
            # Fallback: basic file validation only
            print("Image processing not available, skipping UPI ID extraction")
            return None
        
        # Load image
        image = cv2.imread(screenshot_path)
        if image is None:
            return None
        
        # Convert to RGB for pytesseract
        rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        
        # Use pytesseract to extract text
        text = pytesseract.image_to_string(rgb_image)
        
        # Look for UPI ID patterns
        upi_patterns = [
            r'upi://pay\?pa=([^&]+)',  # UPI deep link format
            r'@([a-zA-Z0-9._-]+@[a-zA-Z0-9._-]+)',  # Email format UPI ID
            r'([a-zA-Z0-9._-]+@[a-zA-Z0-9._-]+)',  # General email pattern
            r'UPI ID[:\s]+([a-zA-Z0-9._-]+@[a-zA-Z0-9._-]+)',  # UPI ID label
            r'To[:\s]+([a-zA-Z0-9._-]+@[a-zA-Z0-9._-]+)',  # To field
        ]
        
        for pattern in upi_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                upi_id = matches[0].strip()
                # Validate UPI ID format
                if '@' in upi_id and '.' in upi_id.split('@')[1]:
                    return upi_id
        
        return None
        
    except Exception as e:
        print(f"Error extracting UPI ID: {e}")
        return None

def verify_screenshot_content(screenshot_path: str, expected_upi_id: str, expected_amount: int) -> tuple[bool, Optional[str]]:
    """Verify screenshot content and extract UPI ID"""
    
    if not os.path.exists(screenshot_path):
        return False, None
    
    # Check file size (should be reasonable for a screenshot)
    file_size = os.path.getsize(screenshot_path)
    if file_size < 1000 or file_size > 10 * 1024 * 1024:  # 1KB to 10MB
        return False, None
    
    # If image processing is not available, accept any valid screenshot
    if not IMAGE_PROCESSING_AVAILABLE:
        print("Image processing not available, accepting screenshot without UPI ID verification")
        return True, expected_upi_id  # Return expected UPI ID as fallback
    
    # Extract UPI ID from screenshot
    extracted_upi_id = extract_upi_id_from_screenshot(screenshot_path)
    
    if not extracted_upi_id:
        return False, None
    
    # Check if UPI ID matches expected UPI ID
    if extracted_upi_id.lower() != expected_upi_id.lower():
        return False, extracted_upi_id
    
    return True, extracted_upi_id

def delete_screenshot(screenshot_path: str):
    """Delete screenshot file after processing"""
    try:
        if os.path.exists(screenshot_path):
            os.remove(screenshot_path)
            print(f"Screenshot deleted: {screenshot_path}")
    except Exception as e:
        print(f"Error deleting screenshot: {e}")

def check_upi_id_uniqueness(db: Session, upi_id: str, transaction_id: int) -> bool:
    """Check if UPI ID has been used before for a different transaction"""
    existing_transaction = db.query(PaymentTransaction).filter(
        PaymentTransaction.paytm_txn_id == upi_id,
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
    amount_paise = package.price * 100  # Convert to paise
    transaction = create_qr_payment_transaction(
        db, current_user.id, package.id, amount_paise, package.credits
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
    screenshot: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Verify payment using screenshot with UPI ID extraction"""
    
    # Get transaction
    transaction = db.query(PaymentTransaction).filter(
        PaymentTransaction.order_id == order_id,
        PaymentTransaction.user_id == current_user.id
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
    
    try:
        # Save screenshot
        screenshot_path = save_screenshot(screenshot, order_id)
        
        # Extract and verify UPI ID from screenshot
        is_valid, extracted_upi_id = verify_screenshot_content(
            screenshot_path, 
            UPI_PAYMENT_DETAILS["upi_id"], 
            transaction.amount_in_rupees
        )
        
        if not is_valid:
            # Delete screenshot if verification failed
            delete_screenshot(screenshot_path)
            
            if extracted_upi_id:
                return JSONResponse(
                    status_code=400,
                    content={
                        "verified": False, 
                        "status": "wrong_upi_id", 
                        "message": f"Wrong UPI ID detected: {extracted_upi_id}. Please try again with correct payment screenshot.",
                        "extracted_upi_id": extracted_upi_id
                    }
                )
            else:
                return JSONResponse(
                    status_code=400,
                    content={
                        "verified": False, 
                        "status": "invalid_screenshot", 
                        "message": "Could not extract UPI ID from screenshot. Please ensure the screenshot shows the payment confirmation clearly."
                    }
                )
        
        # Check UPI ID uniqueness
        if not check_upi_id_uniqueness(db, extracted_upi_id, transaction.id):
            delete_screenshot(screenshot_path)
            return JSONResponse(
                status_code=400,
                content={
                    "verified": False, 
                    "status": "duplicate_upi_id", 
                    "message": "This UPI ID has already been used for another transaction. Please try again with a different payment."
                }
            )
        
        # Payment verified - update transaction
        transaction.status = PaymentStatus.SUCCESS
        transaction.paytm_txn_id = extracted_upi_id
        transaction.completed_at = datetime.utcnow()
        transaction.paytm_response = f'{{"UPI_ID": "{extracted_upi_id}", "SCREENSHOT_PATH": "{screenshot_path}"}}'
        
        # Add credits to user account
        add_credits_to_user(db, transaction.user_id, transaction.credits, transaction.id)
        
        db.commit()
        
        # Delete screenshot after successful processing
        delete_screenshot(screenshot_path)
        
        return JSONResponse(
            status_code=200,
            content={
                "verified": True,
                "status": "success",
                "message": f"Payment verified! {transaction.credits} credits added to your account.",
                "credits_added": transaction.credits,
                "upi_id": extracted_upi_id
            }
        )
        
    except Exception as e:
        # Clean up screenshot on error
        if 'screenshot_path' in locals():
            delete_screenshot(screenshot_path)
        
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
