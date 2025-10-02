# CodeTantra Automation - Complete Deployment Guide

## 🚨 **CRITICAL: Use Python 3.11.9**

**Exact Python Version:** `3.11.9` (or any 3.11.x version)

**Why not Python 3.13?** Python 3.13 is too new and has compatibility issues with FastAPI, Pydantic, and other packages.

## 🚀 **Render Deployment (Recommended)**

### **Step 1: Create Render Service**
1. Go to [Render.com](https://render.com)
2. Create new "Web Service"
3. Connect your GitHub repository

### **Step 2: Configure Service Settings**
- **Name:** `codetantra-automation`
- **Environment:** `Python 3`
- **Python Version:** `3.11.9` (or 3.11.x)
- **Build Command:** `pip install -r requirements.txt`
- **Start Command:** `cd backend && python main.py`

### **Step 3: Environment Variables**
Add these in Render service settings:
```
SECRET_KEY=your-super-secret-key-change-this-in-production
SENDER_EMAIL=your-email@gmail.com
SENDER_PASSWORD=your-app-password
APP_URL=https://your-app.onrender.com
```

### **Step 4: Deploy**
- Click "Create Web Service"
- Wait for build to complete
- Your API will be available at the provided URL

## 🖥️ **Local Development**

### **Prerequisites**
- Python 3.11.9 (or 3.11.x)
- Git

### **Installation**
```bash
# Clone repository
git clone <your-repo-url>
cd CodetantraCheat

# Install dependencies
pip install -r requirements.txt

# Run backend
cd backend
python main.py
```

### **Access Points**
- **API:** http://localhost:8000
- **API Docs:** http://localhost:8000/docs
- **Frontend:** http://localhost:8000 (served by FastAPI)

## 📋 **Package Requirements**

```txt
# Web Framework
fastapi==0.104.1
uvicorn[standard]==0.24.0

# Database
sqlalchemy==2.0.23
alembic==1.12.1

# Authentication
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
bcrypt==4.0.1
python-multipart==0.0.6

# Email validation
email-validator==2.1.0

# Environment variables
python-dotenv==1.0.0

# Pydantic
pydantic==2.5.0
```

## 🔧 **System Architecture**

### **Backend (FastAPI)**
- **Location:** `backend/`
- **Main File:** `backend/main.py`
- **Database:** SQLite (`codetantra.db`)
- **Authentication:** JWT tokens
- **Email:** Gmail SMTP

### **Frontend (HTML/CSS/JS)**
- **Location:** `frontend/`
- **Served by:** FastAPI static files
- **Access:** Root URL of the service

### **Desktop App (Tkinter)**
- **Location:** `desktop-app/`
- **Main File:** `desktop-app/main.py`
- **Dependencies:** `desktop-app/requirements.txt`

## 🎯 **API Endpoints**

### **Authentication**
- `POST /auth/register` - User registration
- `POST /auth/login` - User login
- `POST /auth/verify-email` - Email verification
- `POST /auth/forgot-password` - Password reset request
- `POST /auth/reset-password` - Password reset confirmation

### **User Management**
- `GET /users/profile` - Get user profile
- `PUT /users/profile` - Update user profile
- `GET /users/credits` - Get user credits

### **Admin Panel**
- `GET /admin/users` - List all users
- `POST /admin/credits` - Add credits to user
- `GET /admin/usage` - Get usage statistics

### **Automation**
- `POST /automation/deduct-credits` - Deduct credits for automation
- `POST /automation/log-usage` - Log automation usage

## 🔐 **Default Admin Account**

After deployment, use these credentials:
- **Email:** `admin@codetantra.local`
- **Password:** `admin123`

**⚠️ Change these credentials in production!**

## 🛠️ **Troubleshooting**

### **Common Issues**

#### **1. Python Version Error**
```
Error: FastAPI/Pydantic compatibility issues
Solution: Use Python 3.11.9, not 3.13
```

#### **2. Database Error**
```
Error: Database tables not created
Solution: Check database.py initialization
```

#### **3. Email Error**
```
Error: Email sending failed
Solution: Check Gmail app password and SMTP settings
```

#### **4. Authentication Error**
```
Error: JWT token issues
Solution: Check SECRET_KEY environment variable
```

### **Build Errors on Render**

#### **Rust Compilation Error**
```
Error: maturin failed, Rust compilation
Solution: Use Python 3.11.9 (not 3.13)
```

#### **Package Installation Error**
```
Error: Package not found
Solution: Check requirements.txt syntax
```

## 📱 **Desktop Application**

### **Installation**
```bash
cd desktop-app
pip install -r requirements.txt
python main.py
```

### **Features**
- User login/logout
- Automation settings
- Usage logging
- Credit management

### **Build Executable**
```bash
# Windows
pyinstaller --onefile --windowed main.py

# Or use the provided batch file
build_exe.bat
```

## 🔄 **Development Workflow**

### **1. Backend Changes**
```bash
cd backend
# Make changes to Python files
python main.py  # Test locally
git add .
git commit -m "Backend changes"
git push
```

### **2. Frontend Changes**
```bash
# Make changes to HTML/CSS/JS in frontend/
# Test by running backend
cd backend
python main.py
# Visit http://localhost:8000
```

### **3. Database Changes**
```bash
cd backend
# Modify models.py
python database.py  # Recreate tables
```

## 📊 **Monitoring & Logs**

### **Render Logs**
- Go to Render dashboard
- Click on your service
- View "Logs" tab

### **Local Logs**
- Check terminal output when running `python main.py`
- Database logs in `codetantra.db`

## 🚀 **Production Checklist**

- [ ] Change `SECRET_KEY` to a secure random string
- [ ] Update admin credentials
- [ ] Configure proper email settings
- [ ] Set up domain name (optional)
- [ ] Enable HTTPS (Render provides this)
- [ ] Monitor usage and performance
- [ ] Set up backups (if needed)

## 📞 **Support**

### **Common Commands**
```bash
# Check Python version
python --version

# Install dependencies
pip install -r requirements.txt

# Run backend
cd backend && python main.py

# Test API
curl http://localhost:8000/

# Check database
sqlite3 codetantra.db
```

### **File Structure**
```
CodetantraCheat/
├── backend/           # FastAPI backend
│   ├── main.py       # Main application
│   ├── models.py     # Database models
│   ├── auth.py       # Authentication
│   └── database.py   # Database setup
├── frontend/         # HTML/CSS/JS frontend
├── desktop-app/      # Tkinter desktop app
├── requirements.txt  # Python dependencies
└── README.md        # This file
```

## ✅ **Success Indicators**

After successful deployment:
- ✅ API accessible at your Render URL
- ✅ Frontend loads at root URL
- ✅ API documentation at `/docs`
- ✅ Admin login works
- ✅ User registration works
- ✅ Email verification works

**🎉 Your CodeTantra Automation system is now live!**