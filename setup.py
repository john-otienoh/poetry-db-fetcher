"""
Database setup script.
Run this first to create the database schema.
"""
import os
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from dotenv import load_dotenv

load_dotenv()

def create_database():
    """Create the database if it doesn't exist."""
    db_name = os.getenv('DB_NAME', 'poetry_data')
    user = os.getenv('DB_USER', 'postgres')
    password = os.getenv('DB_PASSWORD', 'postgres')
    host = os.getenv('DB_HOST', 'localhost')
    port = os.getenv('DB_PORT', '5432')
    
    try:
        # Connect to default postgres database
        conn = psycopg2.connect(
            host=host,
            port=port,
            database='postgres',
            user=user,
            password=password
        )
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = conn.cursor()
        
        # Check if database exists
        cursor.execute(f"SELECT 1 FROM pg_database WHERE datname = '{db_name}'")
        exists = cursor.fetchone()
        
        if not exists:
            cursor.execute(f"CREATE DATABASE {db_name}")
            print(f"✓ Database '{db_name}' created successfully")
        else:
            print(f"✓ Database '{db_name}' already exists")
        
        cursor.close()
        conn.close()
        return True
        
    except Exception as e:
        print(f"✗ Failed to create database: {e}")
        return False


def run_schema():
    """Run the schema.sql file."""
    try:
        # Read schema file
        with open('schema.sql', 'r') as f:
            schema = f.read()
        
        # Connect to the database
        conn = psycopg2.connect(
            host=os.getenv('DB_HOST', 'localhost'),
            port=os.getenv('DB_PORT', '5432'),
            database=os.getenv('DB_NAME', 'poetry_data'),
            user=os.getenv('DB_USER', 'postgres'),
            password=os.getenv('DB_PASSWORD', 'postgres')
        )
        cursor = conn.cursor()
        
        # Execute schema
        cursor.execute(schema)
        conn.commit()
        
        print("✓ Schema created successfully")
        
        cursor.close()
        conn.close()
        return True
        
    except Exception as e:
        print(f"✗ Failed to create schema: {e}")
        return False


def main():
    """Setup the database."""
    print("DATABASE SETUP")
    print("=" * 60)
    
    # Step 1: Create database
    if not create_database():
        print("Setup failed at database creation")
        return
    
    # Step 2: Create schema
    if not run_schema():
        print("Setup failed at schema creation")
        return
    
    print("\nDatabase setup complete!")

if __name__ == "__main__":
    main()