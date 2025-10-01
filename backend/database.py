"""
Database Configuration and Session Management
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from models import Base, User
from passlib.context import CryptContext
from contextlib import contextmanager

DATABASE_URL = "sqlite:///./codetantra.db"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
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
        admin = db.query(User).filter(User.email == "admin@codetantra.local").first()
        if not admin:
            admin = User(
                name="Admin",
                email="admin@codetantra.local",
                college_name="System",
                age=25,
                password_hash=pwd_context.hash("admin123"),  # Change this in production
                credits=999999,  # Unlimited credits
                is_verified=True,
                is_admin=True,
                referral_code="ADMIN"
            )
            db.add(admin)
            db.commit()
            print("Admin user created: admin@codetantra.local / admin123")
        else:
            print("Admin user already exists")

def init_database():
    """Initialize database with tables and admin user"""
    create_tables()
    create_admin_user()

if __name__ == "__main__":
    init_database()

