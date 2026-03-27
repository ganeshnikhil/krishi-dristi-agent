from pymongo import MongoClient
from dotenv import load_dotenv
import os

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
DB_NAME = os.getenv("DB_NAME", "krishi_dristi")

# Shared client — created once at import time
_client = MongoClient(MONGO_URI)

def get_db():
    """Return the application database instance."""
    return _client[DB_NAME]
