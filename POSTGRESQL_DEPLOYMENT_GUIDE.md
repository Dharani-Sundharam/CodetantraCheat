# PostgreSQL Deployment Guide for Render

## 🚀 Quick Deployment Steps

### 1. Create PostgreSQL Database on Render

1. **Login to Render Dashboard**
2. **Click "New" → "PostgreSQL"**
3. **Configure Database:**
   - **Name**: `codetantra-db`
   - **Database**: `codetantra`
   - **User**: `codetantra_user`
   - **Region**: Choose closest to your app
   - **PostgreSQL Version**: 15
   - **Instance Type**: Starter (free tier)
4. **Click "Create Database"**
5. **Copy the connection string** from the database dashboard

### 2. Deploy Backend with PostgreSQL

#### Option A: Using Render Dashboard (Recommended)

1. **Click "New" → "Web Service"**
2. **Connect your GitHub repository**
3. **Configure Service:**
   - **Name**: `codetantra-backend`
   - **Environment**: `Python 3`
   - **Build Command**: 
     ```bash
     pip install -r backend/requirements.txt
     cd backend && python migrate_to_postgresql.py admin
     ```
   - **Start Command**: 
     ```bash
     cd backend && python main.py
     ```
4. **Add Environment Variables:**
   - `DATABASE_URL`: (Copy from PostgreSQL database)
   - `JWT_SECRET_KEY`: (Generate a strong secret key)
   - `JWT_ALGORITHM`: `HS256`
   - `ACCESS_TOKEN_EXPIRE_MINUTES`: `30`
   - `ENVIRONMENT`: `production`
   - `FRONTEND_URL`: `https://your-frontend-domain.onrender.com`
   - `ADMIN_EMAIL`: `admin@codetantra.local`
   - `ADMIN_PASSWORD`: `admin123`

#### Option B: Using render.yaml (Advanced)

1. **Push render.yaml to your repository**
2. **Connect repository to Render**
3. **Render will automatically detect and deploy**

### 3. Deploy Frontend

1. **Click "New" → "Static Site"**
2. **Connect your GitHub repository**
3. **Configure:**
   - **Name**: `codetantra-frontend`
   - **Build Command**: `echo "Frontend build complete"`
   - **Publish Directory**: `frontend`
4. **Add Environment Variables:**
   - `API_URL`: `https://your-backend-domain.onrender.com`

### 4. Update Frontend API URLs

Update all API calls in your frontend files to use the new backend URL:

```javascript
// In all HTML files, update:
const API_BASE_URL = 'https://your-backend-domain.onrender.com';
```

## 🔧 Environment Variables Reference

### Backend Environment Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `DATABASE_URL` | PostgreSQL connection string | `postgresql://user:pass@host:port/db` |
| `JWT_SECRET_KEY` | Secret key for JWT tokens | `your-super-secret-key` |
| `JWT_ALGORITHM` | JWT algorithm | `HS256` |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Token expiration time | `30` |
| `ENVIRONMENT` | Environment type | `production` |
| `FRONTEND_URL` | Frontend domain | `https://your-frontend.onrender.com` |
| `ADMIN_EMAIL` | Admin account email | `admin@codetantra.local` |
| `ADMIN_PASSWORD` | Admin account password | `admin123` |

### Frontend Environment Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `API_URL` | Backend API URL | `https://your-backend.onrender.com` |

## 📊 Database Migration

### Automatic Migration
The backend will automatically:
1. Create all tables in PostgreSQL
2. Create admin user
3. Migrate existing data (if any)

### Manual Migration (if needed)
```bash
# Connect to your backend service
cd backend
python migrate_to_postgresql.py
```

## 🔍 Verification Steps

### 1. Check Database Connection
- Visit your backend URL: `https://your-backend.onrender.com/docs`
- Check if API documentation loads
- Test a simple endpoint

### 2. Test User Registration
- Visit your frontend URL
- Try registering a new user
- Check if user appears in database

### 3. Test Admin Panel
- Login with admin credentials
- Check if admin panel loads
- Verify user management functions

## 🚨 Troubleshooting

### Common Issues

#### 1. Database Connection Failed
**Error**: `could not connect to server`
**Solution**: 
- Check DATABASE_URL format
- Ensure PostgreSQL service is running
- Verify connection string is correct

#### 2. Migration Failed
**Error**: `migration failed`
**Solution**:
- Check database permissions
- Verify all tables exist
- Run migration manually

#### 3. Frontend Can't Connect to Backend
**Error**: `CORS error` or `API not found`
**Solution**:
- Update API_URL in frontend
- Check CORS settings in backend
- Verify backend is running

#### 4. Admin User Not Created
**Error**: `admin login failed`
**Solution**:
- Run migration script manually
- Check admin credentials
- Verify user creation in database

### Debug Commands

```bash
# Check database connection
psql $DATABASE_URL

# Check backend logs
# Go to Render dashboard → Your service → Logs

# Test API endpoints
curl https://your-backend.onrender.com/api/health
```

## 📈 Performance Optimization

### Database Optimization
- Use connection pooling (already configured)
- Add database indexes for frequently queried fields
- Monitor query performance

### Backend Optimization
- Enable gzip compression
- Use Redis for session storage (optional)
- Implement rate limiting

### Frontend Optimization
- Enable CDN for static assets
- Implement caching headers
- Optimize images and assets

## 🔒 Security Checklist

- [ ] Change default admin password
- [ ] Use strong JWT secret key
- [ ] Enable HTTPS (automatic on Render)
- [ ] Configure CORS properly
- [ ] Validate all inputs
- [ ] Use environment variables for secrets
- [ ] Regular security updates

## 📞 Support

If you encounter issues:
1. Check Render service logs
2. Verify environment variables
3. Test database connection
4. Check API documentation at `/docs`
5. Contact support with specific error messages

---

**Note**: The free tier on Render has limitations. For production use, consider upgrading to paid plans for better performance and reliability.
