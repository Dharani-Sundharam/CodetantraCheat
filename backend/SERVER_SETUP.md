# CodeTantra Automation Backend Server Setup

## Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Start the Server
**Option A: Using the batch file (Windows)**
```bash
start_server.bat
```

**Option B: Using Python directly**
```bash
python start_server.py
```

**Option C: Using uvicorn directly**
```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

### 3. Access the Application
- **Frontend**: Open `index.html` in your browser
- **API Documentation**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/api/health

## Database Configuration

The server is configured to use PostgreSQL. The DATABASE_URL is automatically set by Render from the database service environment variables.

## Troubleshooting

### "Network Error" when trying to login
1. Make sure the backend server is running on http://localhost:8000
2. Check the browser console for error messages
3. Verify the server started successfully (look for "Server is running" message)

### Database Connection Issues
1. Check your internet connection (PostgreSQL is hosted on Render)
2. Verify the DATABASE_URL is correct
3. Check if the database service is running on Render

### Port Already in Use
If port 8000 is already in use, you can change it in `start_server.py`:
```python
uvicorn.run("main:app", host="0.0.0.0", port=8001, reload=True)
```

## Default Admin Account
- **Email**: admin@codetantra.ac.in
- **Password**: admin123

## API Endpoints

- `POST /api/auth/login` - User login
- `POST /api/auth/register` - User registration
- `GET /api/health` - Health check
- `GET /api/user/profile` - Get user profile (requires authentication)
- `GET /api/user/usage-history` - Get usage history (requires authentication)

## Development

The server runs with auto-reload enabled, so changes to the code will automatically restart the server.

For production deployment, remove the `reload=True` parameter and use a proper WSGI server like Gunicorn.
