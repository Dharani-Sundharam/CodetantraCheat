"""
Database initialization script for production deployment
This script safely initializes the database without causing issues on rebuilds
"""

import os
from sqlalchemy import create_engine, inspect
from sqlalchemy.orm import sessionmaker
from models import Base, User
from database import pwd_context

def init_database():
    """Initialize database - safe to run multiple times"""
    
    # Check if DATABASE_URL is set (PostgreSQL)
    postgres_url = os.getenv("DATABASE_URL")
    if not postgres_url:
        print("No DATABASE_URL found - using development mode")
        return True
    
    # Convert to SQLAlchemy format
    if postgres_url.startswith("postgresql://"):
        postgres_url = postgres_url.replace("postgresql://", "postgresql+psycopg2://", 1)
    
    try:
        print("Initializing PostgreSQL database...")
        engine = create_engine(postgres_url, pool_pre_ping=True)
        session = sessionmaker(bind=engine)()
        
        # Create tables (safe to run multiple times)
        print("Creating database tables...")
        Base.metadata.create_all(bind=engine)
        
        # Check if admin user exists
        admin = session.query(User).filter(User.email == "admin@codetantra.ac.in").first()
        if not admin:
            print("Creating admin user...")
            admin_user = User(
                name="Admin",
                email="admin@codetantra.ac.in",
                college_name="System",
                age=25,
                password_hash=pwd_context.hash("admin123"),
                credits=999999,  # Unlimited credits
                is_active=True,
                is_admin=True,
                referral_code="ADMIN001"
            )
            session.add(admin_user)
            session.commit()
            print("Admin user created successfully!")
        else:
            print("Admin user already exists - skipping creation.")
        
        # Check database status
        user_count = session.query(User).count()
        print(f"Database initialized successfully! Total users: {user_count}")
        
        session.close()
        return True
        
    except Exception as e:
        print(f"Database initialization failed: {str(e)}")
        return False

if __name__ == "__main__":
    print("CodeTantra Database Initialization")
    print("==================================")
    init_database()
