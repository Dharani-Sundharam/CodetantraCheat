# CodeTantra Automation Service - Web Platform

## Overview

This is the web platform branch containing the backend API and frontend website for the CodeTantra Automation Service. This branch focuses on the web-based components including user management, credits system, and admin panel.

## Components

### Backend API (`backend/`)
- **FastAPI** application with SQLite database
- **JWT Authentication** with email verification
- **Credits Management** system
- **Referral System** (70 credits per referral)
- **Admin Panel** APIs
- **Email Service** for verification and password reset

### Frontend Website (`frontend/`)
- **Modern HTML/CSS/JS** interface
- **User Registration** and login
- **Dashboard** with credits and usage tracking
- **Admin Panel** for user management
- **Password Reset** functionality
- **Responsive Design** for all devices

## Features

- User registration with email verification
- Secure JWT-based authentication
- Credits system (80 free credits on signup)
- Referral program with bonus credits
- Real-time usage tracking
- Admin panel for user management
- Password reset via email
- Modern, responsive UI

## Quick Start

### Backend Setup
```bash
cd backend
pip install -r requirements.txt
python database.py  # Initialize database
python main.py      # Start server
```

### Frontend Setup
```bash
cd frontend
# Serve with any static file server
python -m http.server 8080
# Or deploy to Netlify/Vercel
```

## API Endpoints

### Authentication
- `POST /api/auth/register` - User registration
- `POST /api/auth/login` - User login
- `GET /api/auth/verify-email` - Email verification
- `POST /api/auth/forgot-password` - Password reset request
- `POST /api/auth/reset-password` - Password reset

### User Operations
- `GET /api/user/profile` - Get user profile
- `GET /api/user/credits` - Get credits balance
- `POST /api/credits/deduct` - Deduct credits
- `GET /api/user/usage-history` - Usage logs
- `GET /api/user/transactions` - Transaction history

### Admin Operations
- `GET /api/admin/users` - List all users
- `POST /api/admin/credits` - Manage user credits
- `POST /api/admin/suspend-user` - Suspend user
- `GET /api/admin/stats` - Platform statistics

## Configuration

### Backend Configuration
1. Update email settings in `backend/email_service.py`
2. Set secret key in `backend/auth.py`
3. Configure CORS in `backend/main.py`

### Frontend Configuration
1. Update API URL in all HTML files
2. Configure download links
3. Set up domain-specific settings

## Deployment

### Backend (Render)
1. Connect GitHub repository
2. Set build command: `pip install -r requirements.txt`
3. Set start command: `cd backend && python main.py`
4. Add environment variables

### Frontend (Netlify)
1. Connect repository
2. Set build directory: `frontend`
3. Deploy automatically

## Default Admin Account

- Email: `admin@codetantra.local`
- Password: `admin123`
- Credits: Unlimited

**Important:** Change this password in production!

## Credits System

- New user signup: **80 credits**
- Code completion success: **5 credits**
- Other problem success: **3 credits**
- Failed problem: **1 credit**
- Successful referral: **70 credits**

## Database Schema

- **users** - User accounts and profiles
- **credit_transactions** - Credits history
- **usage_logs** - Problem solving logs
- **verification_tokens** - Email verification

## Security Features

- JWT token authentication
- Password hashing with bcrypt
- Email verification required
- CORS protection
- Input validation
- SQL injection protection

## Monitoring

- API documentation at `/docs`
- Admin panel for user management
- Usage statistics and analytics
- Error logging and monitoring

## Support

For issues or questions:
1. Check the API documentation
2. Review logs in admin panel
3. Contact support with error details

## License

Educational purposes only. Use responsibly.

---

**Note:** This is the web platform branch. For the complete system with desktop app, see the main branch.