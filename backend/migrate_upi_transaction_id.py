#!/usr/bin/env python3
"""
Migration script to add upi_transaction_id column to payment_transactions table
"""

import os
import sys
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from models import Base, PaymentTransaction
from config import DATABASE_URL

def migrate_upi_transaction_id():
    """Add upi_transaction_id column to payment_transactions table"""
    
    print("Starting UPI Transaction ID migration...")
    
    try:
        # Create engine
        engine = create_engine(DATABASE_URL)
        
        # Check if column already exists
        with engine.connect() as conn:
            result = conn.execute(text("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = 'payment_transactions' 
                AND column_name = 'upi_transaction_id'
            """))
            
            if result.fetchone():
                print("✅ upi_transaction_id column already exists. Skipping migration.")
                return
        
        # Add the new column
        with engine.connect() as conn:
            conn.execute(text("""
                ALTER TABLE payment_transactions 
                ADD COLUMN upi_transaction_id VARCHAR UNIQUE
            """))
            conn.commit()
            
        print("✅ Successfully added upi_transaction_id column to payment_transactions table")
        
        # Create index for better performance
        with engine.connect() as conn:
            conn.execute(text("""
                CREATE INDEX IF NOT EXISTS idx_payment_transactions_upi_txn_id 
                ON payment_transactions(upi_transaction_id)
            """))
            conn.commit()
            
        print("✅ Created index on upi_transaction_id column")
        
    except Exception as e:
        print(f"❌ Error during migration: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    migrate_upi_transaction_id()
    print("Migration completed successfully!")
