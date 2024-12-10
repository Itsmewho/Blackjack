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
    "highscore": os.getenv("MONGO_HIGHSCORES", "highscore"),
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
    collection_name = MONGO_COLLECTIONS.get(collection_key)
    if not collection_name:
        logger.error(red + f"Collection key '{collection_key}' not found." + reset)
        return None

    if db is None:  # Ensure db is valid
        logger.error(red + "Database connection is not established." + reset)
        return None

    collection = db[collection_name]  # Corrected way to access collections

    if collection is None:  # Check if collection is None
        logger.error(
            red + f"Collection '{collection_name}' not found in database." + reset
        )
        return None

    return collection
