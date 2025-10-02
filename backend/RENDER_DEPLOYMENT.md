# Render Deployment Guide

## Quick Fix for Rust Compilation Error

The error you're seeing is due to packages requiring Rust compilation. Here's how to fix it:

### Option 1: Use Simple Requirements (Recommended)

1. **Update your Render service to use:**
   - **Build Command:** `pip install -r requirements-simple.txt`
   - **Start Command:** `cd backend && python main.py`

2. **Or manually change requirements.txt to:**
   ```
   fastapi==0.104.1
   uvicorn==0.24.0
   sqlalchemy==2.0.23
   PyJWT==2.8.0
   passlib[bcrypt]==1.7.4
   bcrypt==4.0.1
   python-multipart==0.0.6
   email-validator==2.1.0
   python-dotenv==1.0.0
   pydantic==2.5.0
   gunicorn==21.2.0
   ```

### Option 2: Use Pre-compiled Packages

1. **In Render dashboard:**
   - Go to your service settings
   - Add environment variable: `PIP_NO_BUILD_ISOLATION=false`
   - Add environment variable: `PIP_PREFER_BINARY=true`

2. **Update build command to:**
   ```bash
   pip install --upgrade pip && pip install -r requirements.txt --prefer-binary
   ```

### Option 3: Use Docker (Advanced)

Create a `Dockerfile` in your project root:

```dockerfile
FROM python:3.10-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python packages
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY backend/ .
COPY frontend/ ../frontend/

# Expose port
EXPOSE 8000

# Run the application
CMD ["python", "main.py"]
```

## Environment Variables for Render

Add these in your Render service settings:

```
SECRET_KEY=your-super-secret-key-here
SENDER_EMAIL=your-email@gmail.com
SENDER_PASSWORD=your-app-password
APP_URL=https://your-app.onrender.com
```

## Build Commands

### For requirements-simple.txt:
- **Build:** `pip install -r requirements-simple.txt`
- **Start:** `cd backend && python main.py`

### For regular requirements.txt:
- **Build:** `pip install --upgrade pip && pip install -r requirements.txt --prefer-binary`
- **Start:** `cd backend && python main.py`

## Troubleshooting

### If you still get Rust errors:
1. Use `requirements-simple.txt` instead
2. Make sure you're using Python 3.10 or 3.11
3. Check that all packages are available as wheels

### If bcrypt still fails:
1. The auth.py file has fallback to direct bcrypt
2. Make sure bcrypt==4.0.1 is installed
3. Check the fix_bcrypt.py script

## Success Indicators

After successful deployment:
- Visit `https://your-app.onrender.com` - should show API status
- Visit `https://your-app.onrender.com/docs` - should show API documentation
- Frontend should be accessible at the root URL

## Need Help?

If you're still having issues:
1. Check Render build logs for specific errors
2. Try the simple requirements first
3. Use the Docker approach for maximum compatibility
