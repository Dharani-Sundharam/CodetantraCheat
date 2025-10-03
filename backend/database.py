"""
Database Configuration and Session Management
PostgreSQL + SQLAlchemy ORM (PostgreSQL ONLY - No SQLite fallback)
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from models import Base, User
from passlib.context import CryptContext
from contextlib import contextmanager
import os

# Database URL configuration - PostgreSQL ONLY
# DATABASE_URL must be set as environment variable
DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise ValueError("DATABASE_URL environment variable is required but not set. Please configure PostgreSQL connection.")

# Convert to postgresql+psycopg2:// for SQLAlchemy
if DATABASE_URL.startswith("postgresql://"):
    DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+psycopg2://", 1)

print("Using PostgreSQL for production")

# Create PostgreSQL engine
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,  # Verify connections before use
    pool_recycle=300,    # Recycle connections every 5 minutes
    echo=False           # Set to True for SQL debugging
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def create_tables():
    """Create all database tables"""
    Base.metadata.create_all(bind=engine)
    print("Database tables created successfully")

def get_db():
    """Get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@contextmanager
def get_db_context():
    """Get database session as context manager"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def create_admin_user():
    """Create default admin user with unlimited credits"""
    with get_db_context() as db:
        # Check if admin exists by email
        admin = db.query(User).filter(User.email == "admin@codetantra.ac.in").first()
        if not admin:
            # Check if ADMIN referral code exists
            existing_admin = db.query(User).filter(User.referral_code == "ADMIN").first()
            if existing_admin:
                # Update existing admin to new email
                existing_admin.email = "admin@codetantra.ac.in"
                existing_admin.name = "Admin"
                existing_admin.college_name = "System"
                existing_admin.age = 25
                existing_admin.password_hash = pwd_context.hash("admin123")
                existing_admin.credits = 999999
                existing_admin.is_admin = True
                db.commit()
                print("Admin user updated: admin@codetantra.ac.in / admin123")
            else:
                # Create new admin
                admin = User(
                    name="Admin",
                    email="admin@codetantra.ac.in",
                    college_name="System",
                    age=25,
                    password_hash=pwd_context.hash("admin123"),
                    credits=999999,
                    is_admin=True,
                    referral_code="ADMIN"
                )
                db.add(admin)
                db.commit()
                print("Admin user created: admin@codetantra.ac.in / admin123")
        else:
            print("Admin user already exists")

def init_database():
    """Initialize database with tables and admin user"""
    create_tables()
    create_admin_user()

if __name__ == "__main__":
    init_database()

