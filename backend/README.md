# CodeTantra Automation - Backend

This directory contains the complete CodeTantra Automation application with both backend and frontend in a single folder for simplified deployment.

## 🚀 **Quick Start**

```bash
# Install dependencies
pip install -r requirements.txt

# Run the application
python main.py
```

## 📁 **Structure**

- **`main.py`** - FastAPI application (backend + frontend serving)
- **`models.py`** - Database models
- **`auth.py`** - Authentication system
- **`database.py`** - Database configuration
- **`email_service.py`** - Email functionality
- **`*.html`** - Frontend pages
- **`assets/`** - CSS, JavaScript, and images
- **`requirements.txt`** - Python dependencies

## 🌐 **Access Points**

- **Application:** http://localhost:8000
- **API Documentation:** http://localhost:8000/docs
- **Admin Panel:** http://localhost:8000/admin.html

## 🔧 **Features**

- ✅ User registration and authentication
- ✅ Email verification system
- ✅ Credit management system
- ✅ Admin panel
- ✅ Responsive web interface
- ✅ JWT token authentication
- ✅ SQLite database

## 📧 **Email Configuration**

Set these environment variables:
- `SENDER_EMAIL` - Your Gmail address
- `SENDER_PASSWORD` - Gmail app password
- `APP_URL` - Your application URL

## 🚀 **Deployment**

This structure is optimized for single-service deployment platforms like Render, Heroku, or Railway. Simply deploy the entire directory as a Python application.