"""
PostgreSQL Setup Script for Local Development
This script helps you set up PostgreSQL for local development
"""

import os
import subprocess
import sys

def check_postgresql_installed():
    """Check if PostgreSQL is installed locally"""
    try:
        result = subprocess.run(['psql', '--version'], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✓ PostgreSQL found: {result.stdout.strip()}")
            return True
        else:
            print("✗ PostgreSQL not found")
            return False
    except FileNotFoundError:
        print("✗ PostgreSQL not found")
        return False

def create_local_database():
    """Create local PostgreSQL database"""
    print("\n=== Creating Local PostgreSQL Database ===")
    
    # Database configuration
    db_name = "codetantra_local"
    db_user = "codetantra_user"
    db_password = "codetantra123"
    
    try:
        # Create database
        print(f"Creating database: {db_name}")
        subprocess.run([
            'createdb', 
            '-U', 'postgres',
            db_name
        ], check=True)
        
        # Create user
        print(f"Creating user: {db_user}")
        subprocess.run([
            'psql', 
            '-U', 'postgres',
            '-c', f"CREATE USER {db_user} WITH PASSWORD '{db_password}';"
        ], check=True)
        
        # Grant privileges
        print(f"Granting privileges to {db_user}")
        subprocess.run([
            'psql', 
            '-U', 'postgres',
            '-c', f"GRANT ALL PRIVILEGES ON DATABASE {db_name} TO {db_user};"
        ], check=True)
        
        # Set DATABASE_URL
        database_url = f"postgresql://{db_user}:{db_password}@localhost:5432/{db_name}"
        
        print(f"\n✓ Database created successfully!")
        print(f"Database URL: {database_url}")
        print(f"\nTo use this database, set the environment variable:")
        print(f"export DATABASE_URL='{database_url}'")
        print(f"\nOr create a .env file with:")
        print(f"DATABASE_URL={database_url}")
        
        return database_url
        
    except subprocess.CalledProcessError as e:
        print(f"✗ Error creating database: {e}")
        return None
    except FileNotFoundError:
        print("✗ PostgreSQL commands not found. Please install PostgreSQL first.")
        return None

def main():
    print("=== CodeTantra PostgreSQL Setup ===")
    print("This script will help you set up PostgreSQL for local development")
    print()
    
    # Check if PostgreSQL is installed
    if not check_postgresql_installed():
        print("\nPlease install PostgreSQL first:")
        print("1. Download from: https://www.postgresql.org/download/")
        print("2. Install with default settings")
        print("3. Make sure to remember the postgres user password")
        print("4. Run this script again")
        return
    
    # Check if DATABASE_URL is already set
    if os.getenv("DATABASE_URL"):
        print(f"✓ DATABASE_URL is already set: {os.getenv('DATABASE_URL')}")
        response = input("Do you want to create a new database anyway? (y/N): ")
        if response.lower() != 'y':
            print("Using existing DATABASE_URL")
            return
    
    # Create database
    database_url = create_local_database()
    
    if database_url:
        print("\n=== Next Steps ===")
        print("1. Set the DATABASE_URL environment variable")
        print("2. Run: python init_database.py")
        print("3. Start your application: python main.py")
        print("\nFor Windows, you can set the environment variable with:")
        print(f"set DATABASE_URL={database_url}")
        print("\nFor Linux/Mac, you can set the environment variable with:")
        print(f"export DATABASE_URL={database_url}")

if __name__ == "__main__":
    main()
