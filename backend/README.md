# CodeTantra Automation Backend

FastAPI backend with SQLite database for user management, authentication, and credits system.

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Configure email settings in `email_service.py`:
   - Replace `SENDER_EMAIL` with your Gmail address
   - Replace `SENDER_PASSWORD` with your Gmail App Password (not regular password)
   - Get App Password from: https://myaccount.google.com/apppasswords

3. Initialize database:
```bash
python database.py
```

This creates the SQLite database and an admin user:
- Email: admin@codetantra.local
- Password: admin123
- Credits: Unlimited

4. Run the server:
```bash
python main.py
```

Or with uvicorn:
```bash
uvicorn main:app --reload
```

Server runs on http://localhost:8000

## API Documentation

Once running, visit:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Key Endpoints

### Authentication
- POST `/api/auth/register` - Register new user
- GET `/api/auth/verify-email` - Verify email with token
- POST `/api/auth/login` - User login
- POST `/api/auth/forgot-password` - Request password reset
- POST `/api/auth/reset-password` - Reset password with token

### User
- GET `/api/user/profile` - Get user profile
- GET `/api/user/credits` - Get user credits
- POST `/api/credits/deduct` - Deduct credits for problem
- GET `/api/user/usage-history` - Get usage history
- GET `/api/user/transactions` - Get transaction history

### Admin
- GET `/api/admin/users` - List all users
- POST `/api/admin/credits` - Add/remove user credits
- POST `/api/admin/suspend-user` - Suspend user
- POST `/api/admin/activate-user` - Activate user
- GET `/api/admin/stats` - Platform statistics

## Credits System

- New users: 80 free credits
- Code completion success: 5 credits
- Other problems success: 3 credits
- Failed problem: 1 credit
- Referral bonus: 70 credits per referral

## Deployment

For Render:
1. Create new Web Service
2. Connect your GitHub repository
3. Set build command: `pip install -r requirements.txt`
4. Set start command: `uvicorn main:app --host 0.0.0.0 --port $PORT`
5. Add environment variables if needed

## Security Notes

- Change `SECRET_KEY` in `auth.py` for production
- Use environment variables for sensitive data
- Enable HTTPS in production
- Update CORS settings for specific origins

