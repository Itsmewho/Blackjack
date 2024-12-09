# CRUD operations for dynamic use.

import logging
from pymongo.errors import PyMongoError
from config.connect_db import get_collection
from utils.helpers import green, red, blue, reset


# Setup logger
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def insert_document(collection_key: str, document: dict):
    try:
        collection = get_collection(collection_key)
        if not collection:
            return False

        result = collection.insert_one(document)
        logger.info(
            green
            + f"Inserted document with ID: {result.inserted_id} into {collection_key}{reset}"
        )
        return True

    except PyMongoError as e:
        logger.error(
            red + f"Failed to insert document into {collection_key}: {e}{reset}"
        )
        return False


def find_documents(
    collection_key: str, query: dict = None, limit: int = 0, sort_by: tuple = None
):
    try:
        collection = get_collection(collection_key)
        if not collection:
            return []
        query = query or {}
        cursor = collection.find(query)

        if sort_by:
            cursor = cursor.sort(sort_by)
        if limit:
            cursor = cursor.limit(limit)

        documents = list(cursor)
        logger.info(
            green + f"Retrieved {len(documents)} documents from {collection_key}{reset}"
        )
        return documents

    except PyMongoError as e:
        logger.error(
            red + f"Failed to retrieve documents from {collection_key}: {e}{reset}"
        )
        return []


def update_documents(
    collection_key: str, query: dict, updata_data: dict, multiple: bool = False
):
    try:
        collection = get_collection(collection_key)
        if not collection:
            return 0
        if "$set" not in updata_data:
            updata_data = {"$set": updata_data}

        result = (
            collection.update_many(query, updata_data)
            if multiple
            else collection.update_one(query, updata_data)
        )
        logger.info(
            green
            + f"Updated: {result.modified_count} document(s) in {collection_key}{reset}"
        )
        return result.modified_count
    except PyMongoError as e:
        logger.error(
            red + f"Failed to update documents in {collection_key}: {e}{reset}"
        )
        return 0


def delete_documents(collection_key: str, query: dict, multiple: bool = False):
    try:
        collection = get_collection(collection_key)
        if not collection:
            return 0
        result = (
            collection.delete_many(query) if multiple else collection.delete_one(query)
        )
        logger.info(
            green
            + f"Deleted {result.deleted_count} document(s) from {collection_key}{reset}"
        )
        return result.deleted_count
    except PyMongoError as e:
        logger.error(
            red + f"Failed to delete documents from {collection_key}: {e}{reset}"
        )
        return 0
