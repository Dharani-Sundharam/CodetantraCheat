"""
Email Service for Verification and Password Reset
Gmail SMTP integration
"""

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional

# Email configuration - REPLACE WITH YOUR CREDENTIALS
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
SENDER_EMAIL = "ctphead25@gmail.com"  # REPLACE THIS
SENDER_PASSWORD = "admin!@#$"  # REPLACE THIS (use App Password, not regular password)
APP_URL = "http://localhost:8000"  # Change to your domain in production

def send_email(to_email: str, subject: str, html_content: str) -> bool:
    """Send email via Gmail SMTP"""
    try:
        # Create message
        message = MIMEMultipart("alternative")
        message["Subject"] = subject
        message["From"] = SENDER_EMAIL
        message["To"] = to_email
        
        # Add HTML content
        html_part = MIMEText(html_content, "html")
        message.attach(html_part)
        
        # Send email
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(SENDER_EMAIL, SENDER_PASSWORD)
            server.sendmail(SENDER_EMAIL, to_email, message.as_string())
        
        print(f"Email sent successfully to {to_email}")
        return True
    except Exception as e:
        print(f"Failed to send email to {to_email}: {str(e)}")
        return False

def send_verification_email(to_email: str, token: str, user_name: str) -> bool:
    """Send email verification link"""
    verification_url = f"{APP_URL}/verify-email?token={token}"
    
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
            .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
            .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0; }}
            .content {{ background: #f9f9f9; padding: 30px; border-radius: 0 0 10px 10px; }}
            .button {{ display: inline-block; padding: 12px 30px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; text-decoration: none; border-radius: 5px; margin: 20px 0; }}
            .footer {{ text-align: center; margin-top: 20px; font-size: 12px; color: #666; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>Welcome to CodeTantra Automation!</h1>
            </div>
            <div class="content">
                <p>Hi {user_name},</p>
                <p>Thank you for signing up! Please verify your email address by clicking the button below:</p>
                <center>
                    <a href="{verification_url}" class="button">Verify Email Address</a>
                </center>
                <p>Or copy and paste this link into your browser:</p>
                <p style="word-break: break-all; color: #667eea;">{verification_url}</p>
                <p><strong>This link will expire in 1 hour.</strong></p>
                <p>If you didn't create an account, please ignore this email.</p>
            </div>
            <div class="footer">
                <p>CodeTantra Automation Service</p>
                <p>This is an automated email. Please do not reply.</p>
            </div>
        </div>
    </body>
    </html>
    """
    
    return send_email(to_email, "Verify Your Email - CodeTantra Automation", html_content)

def send_password_reset_email(to_email: str, token: str, user_name: str) -> bool:
    """Send password reset link"""
    reset_url = f"{APP_URL}/reset-password?token={token}"
    
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
            .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
            .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0; }}
            .content {{ background: #f9f9f9; padding: 30px; border-radius: 0 0 10px 10px; }}
            .button {{ display: inline-block; padding: 12px 30px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; text-decoration: none; border-radius: 5px; margin: 20px 0; }}
            .footer {{ text-align: center; margin-top: 20px; font-size: 12px; color: #666; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>Password Reset Request</h1>
            </div>
            <div class="content">
                <p>Hi {user_name},</p>
                <p>We received a request to reset your password. Click the button below to reset it:</p>
                <center>
                    <a href="{reset_url}" class="button">Reset Password</a>
                </center>
                <p>Or copy and paste this link into your browser:</p>
                <p style="word-break: break-all; color: #667eea;">{reset_url}</p>
                <p><strong>This link will expire in 1 hour.</strong></p>
                <p>If you didn't request a password reset, please ignore this email. Your password will remain unchanged.</p>
            </div>
            <div class="footer">
                <p>CodeTantra Automation Service</p>
                <p>This is an automated email. Please do not reply.</p>
            </div>
        </div>
    </body>
    </html>
    """
    
    return send_email(to_email, "Password Reset - CodeTantra Automation", html_content)

def send_welcome_email(to_email: str, user_name: str, referral_code: str) -> bool:
    """Send welcome email after verification"""
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
            .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
            .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0; }}
            .content {{ background: #f9f9f9; padding: 30px; border-radius: 0 0 10px 10px; }}
            .credits-box {{ background: white; border: 2px solid #667eea; border-radius: 10px; padding: 20px; margin: 20px 0; text-align: center; }}
            .referral-box {{ background: #e0e7ff; border-radius: 5px; padding: 15px; margin: 15px 0; }}
            .footer {{ text-align: center; margin-top: 20px; font-size: 12px; color: #666; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>Welcome to CodeTantra Automation!</h1>
            </div>
            <div class="content">
                <p>Hi {user_name},</p>
                <p>Your account has been successfully verified!</p>
                <div class="credits-box">
                    <h2 style="color: #667eea; margin: 0;">80 Free Credits</h2>
                    <p style="margin: 5px 0 0 0;">Have been added to your account!</p>
                </div>
                <p><strong>What's next?</strong></p>
                <ol>
                    <li>Download the desktop application from your dashboard</li>
                    <li>Log in with your credentials</li>
                    <li>Start automating your CodeTantra problems!</li>
                </ol>
                <div class="referral-box">
                    <h3 style="margin: 0 0 10px 0;">Earn More Credits!</h3>
                    <p style="margin: 0;">Share your referral code with friends:</p>
                    <p style="font-size: 24px; font-weight: bold; color: #667eea; margin: 10px 0;">{referral_code}</p>
                    <p style="margin: 0; font-size: 14px;">You'll get 70 credits for each friend who signs up!</p>
                </div>
                <p>If you have any questions, feel free to reach out to our support team.</p>
                <p>Happy automating!</p>
            </div>
            <div class="footer">
                <p>CodeTantra Automation Service</p>
                <p>This is an automated email. Please do not reply.</p>
            </div>
        </div>
    </body>
    </html>
    """
    
    return send_email(to_email, "Welcome to CodeTantra Automation!", html_content)

