"""
Migration script to add payment-related tables to PostgreSQL database
"""

import os
import sys
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from models import Base, CreditPackage, PaymentTransaction, PaymentStatus

# Database configuration
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    print("Error: DATABASE_URL environment variable not set")
    sys.exit(1)

def create_payment_tables():
    """Create payment-related tables"""
    try:
        engine = create_engine(DATABASE_URL)
        
        # Create all tables (this will only create new ones)
        Base.metadata.create_all(bind=engine)
        print("Payment tables created successfully")
        
        return True
    except Exception as e:
        print(f"Error creating payment tables: {e}")
        return False

def populate_credit_packages():
    """Populate credit packages with default data"""
    try:
        engine = create_engine(DATABASE_URL)
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        db = SessionLocal()
        
        # Check if packages already exist
        existing_packages = db.query(CreditPackage).count()
        if existing_packages > 0:
            print("Credit packages already exist, skipping population")
            db.close()
            return True
        
        # Create default credit packages
        packages = [
            CreditPackage(
                name="Starter Pack",
                credits=100,
                price=39.0,
                description="Perfect for getting started with 100 credits"
            ),
            CreditPackage(
                name="Popular Pack",
                credits=500,
                price=169.0,
                description="Most popular choice with 500 credits"
            ),
            CreditPackage(
                name="Pro Pack",
                credits=1000,
                price=349.0,
                description="Best value with 1000 credits"
            )
        ]
        
        for package in packages:
            db.add(package)
        
        db.commit()
        print("Credit packages populated successfully")
        db.close()
        
        return True
    except Exception as e:
        print(f"Error populating credit packages: {e}")
        return False

def verify_tables():
    """Verify that all tables exist"""
    try:
        engine = create_engine(DATABASE_URL)
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        db = SessionLocal()
        
        # Check if tables exist
        result = db.execute(text("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND table_name IN ('credit_packages', 'payment_transactions')
        """))
        
        tables = [row[0] for row in result.fetchall()]
        
        if 'credit_packages' in tables and 'payment_transactions' in tables:
            print("All payment tables verified successfully")
            
            # Check package count
            package_count = db.query(CreditPackage).count()
            print(f"Credit packages available: {package_count}")
            
            db.close()
            return True
        else:
            print(f"Missing tables. Found: {tables}")
            db.close()
            return False
            
    except Exception as e:
        print(f"Error verifying tables: {e}")
        return False

def main():
    """Main migration function"""
    print("Starting payment models migration...")
    
    # Step 1: Create tables
    if not create_payment_tables():
        print("Failed to create payment tables")
        return False
    
    # Step 2: Populate credit packages
    if not populate_credit_packages():
        print("Failed to populate credit packages")
        return False
    
    # Step 3: Verify tables
    if not verify_tables():
        print("Failed to verify tables")
        return False
    
    print("Payment models migration completed successfully!")
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
