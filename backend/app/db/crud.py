from pymongo import MongoClient
from dotenv import load_dotenv
import os

# =========================
# LOAD ENV VARIABLES
# =========================
load_dotenv()

MONGO_URI = os.getenv("MONGO_URI")
DB_NAME = os.getenv("DB_NAME")

# =========================
# CONNECT TO MONGODB
# =========================
client = MongoClient(MONGO_URI)
db = client[DB_NAME]

print("✅ Connected to MongoDB")

