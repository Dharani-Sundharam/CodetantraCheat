"""
Migration script to move from SQLite to PostgreSQL
Run this script to migrate existing data
"""

import os
import sys
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from models import Base, User, Transaction, UsageLog
from database import pwd_context
import json

def migrate_data():
    """Migrate data from SQLite to PostgreSQL"""
    
    # Check if DATABASE_URL is set (PostgreSQL)
    postgres_url = os.getenv("DATABASE_URL")
    if not postgres_url:
        print("ERROR: DATABASE_URL environment variable not set!")
        print("Please set DATABASE_URL to your PostgreSQL connection string")
        return False
    
    # Convert to SQLAlchemy format
    if postgres_url.startswith("postgresql://"):
        postgres_url = postgres_url.replace("postgresql://", "postgresql+psycopg2://", 1)
    
    # SQLite database path (development)
    root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    sqlite_url = f"sqlite:///{os.path.join(root_dir, 'codetantra.db')}"
    
    try:
        # Connect to both databases
        print("Connecting to databases...")
        sqlite_engine = create_engine(sqlite_url, connect_args={"check_same_thread": False})
        postgres_engine = create_engine(postgres_url, pool_pre_ping=True)
        
        sqlite_session = sessionmaker(bind=sqlite_engine)()
        postgres_session = sessionmaker(bind=postgres_engine)()
        
        # Create tables in PostgreSQL
        print("Creating tables in PostgreSQL...")
        Base.metadata.create_all(bind=postgres_engine)
        
        # Migrate Users
        print("Migrating users...")
        users = sqlite_session.query(User).all()
        for user in users:
            # Check if user already exists
            existing_user = postgres_session.query(User).filter(User.email == user.email).first()
            if not existing_user:
                new_user = User(
                    name=user.name,
                    email=user.email,
                    college_name=user.college_name,
                    age=user.age,
                    password_hash=user.password_hash,
                    credits=user.credits,
                    is_active=user.is_active,
                    is_admin=user.is_admin,
                    referral_code=user.referral_code,
                    referred_by=user.referred_by,
                    created_at=user.created_at,
                    last_login=user.last_login
                )
                postgres_session.add(new_user)
        
        # Migrate Transactions
        print("Migrating transactions...")
        transactions = sqlite_session.query(Transaction).all()
        for transaction in transactions:
            # Get the user from PostgreSQL
            user = postgres_session.query(User).filter(User.email == transaction.user.email).first()
            if user:
                new_transaction = Transaction(
                    user_id=user.id,
                    amount=transaction.amount,
                    transaction_type=transaction.transaction_type,
                    description=transaction.description,
                    created_at=transaction.created_at
                )
                postgres_session.add(new_transaction)
        
        # Migrate Usage Logs
        print("Migrating usage logs...")
        usage_logs = sqlite_session.query(UsageLog).all()
        for log in usage_logs:
            # Get the user from PostgreSQL
            user = postgres_session.query(User).filter(User.email == log.user.email).first()
            if user:
                new_log = UsageLog(
                    user_id=user.id,
                    problem_type=log.problem_type,
                    credits_used=log.credits_used,
                    success=log.success,
                    timestamp=log.timestamp,
                    details=log.details
                )
                postgres_session.add(new_log)
        
        # Commit all changes
        print("Committing changes...")
        postgres_session.commit()
        
        print("Migration completed successfully!")
        print(f"Migrated {len(users)} users, {len(transactions)} transactions, {len(usage_logs)} usage logs")
        
        return True
        
    except Exception as e:
        print(f"Migration failed: {str(e)}")
        postgres_session.rollback()
        return False
    
    finally:
        sqlite_session.close()
        postgres_session.close()

def create_admin_user():
    """Create default admin user in PostgreSQL"""
    postgres_url = os.getenv("DATABASE_URL")
    if not postgres_url:
        print("ERROR: DATABASE_URL not set!")
        return False
    
    if postgres_url.startswith("postgresql://"):
        postgres_url = postgres_url.replace("postgresql://", "postgresql+psycopg2://", 1)
    
    try:
        engine = create_engine(postgres_url, pool_pre_ping=True)
        session = sessionmaker(bind=engine)()
        
        # Check if admin exists
        admin = session.query(User).filter(User.email == "admin@codetantra.local").first()
        if not admin:
            admin_user = User(
                name="Admin",
                email="admin@codetantra.local",
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
            print("Admin user already exists!")
        
        session.close()
        return True
        
    except Exception as e:
        print(f"Failed to create admin user: {str(e)}")
        return False

if __name__ == "__main__":
    print("CodeTantra Database Migration Tool")
    print("==================================")
    
    if len(sys.argv) > 1 and sys.argv[1] == "admin":
        create_admin_user()
    else:
        migrate_data()
