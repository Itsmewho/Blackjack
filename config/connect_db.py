import os
import logging
from pymongo import MongoClient
from dotenv import load_dotenv
from utils.helpers import reset, green, red


load_dotenv()

MONGO_URI = os.getenv("MONGO_URI")
MONGO_DBNAME = os.getenv("MONGO_DBNAME")


# Default collection names (fallback to these if not set in the .env file)
MONGO_COLLECTIONS = {
    "admin": os.getenv("MONGO_ADMIN", "admin"),
    "users": os.getenv("MONGO_USERS", "users"),
    "admin_log": os.getenv("MONGO_ADLOG", "admin_log"),
    "user_log": os.getenv("MONGO_USLOG", "user_log"),
    "highscores": os.getenv("MONGO_HIGHSCORES", "highscores"),
}

# Setup logger
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Establish connection with try, catch improvement.
try:
    client = MongoClient(MONGO_URI)
    db = client[MONGO_DBNAME]
    logger.info(green + f"Connected to database: {db.name}{reset}")
except Exception as e:
    logger.error(red + f"Failed to connect to MongoDB: {e}{reset}")


def get_collection(collection_key: str):
    collection_name = MONGO_COLLECTIONS(collection_key)
    if not collection_name:
        logger.info(red + f"Collection key '{collection_key}' not found. {reset}")
        return None

    return db[collection_name] if db else None
