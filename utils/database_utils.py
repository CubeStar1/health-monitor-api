import os
from typing import Dict, Any
from dotenv import load_dotenv
from utils.custom_types import DBCredentials

# Load environment variables
load_dotenv()

def get_db_credentials() -> DBCredentials:
    """Get database credentials from environment variables"""
    return DBCredentials(
        db_user=os.getenv("DB_USER"),
        db_password=os.getenv("DB_PASSWORD"),
        db_host=os.getenv("DB_HOST"),
        db_port=os.getenv("DB_PORT", "5432"),
        db_name=os.getenv("DB_NAME")
    ) 