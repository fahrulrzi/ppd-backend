import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'change-me')
    
    # Get the database URL from environment
    db_url = os.getenv('DATABASE_URL', 'postgresql://postgres:pass@db:5432/mydb')
    
    # Fix for Supabase: add sslmode if not present
    # Supabase requires SSL connection
    if 'supabase.co' in db_url and 'sslmode' not in db_url:
        # Add sslmode=require for Supabase
        if '?' in db_url:
            db_url += '&sslmode=require'
        else:
            db_url += '?sslmode=require'
    
    SQLALCHEMY_DATABASE_URI = db_url
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Optional: Configure connection pool for production
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_size': 10,
        'pool_recycle': 3600, 
        'pool_pre_ping': True, 
        'max_overflow': 20
    }
    
    JWT_SECRET = os.getenv('JWT_SECRET', 'another-change-me')