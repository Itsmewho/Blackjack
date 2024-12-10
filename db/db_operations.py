# CRUD operations for dynamic use.

import logging
from pymongo.errors import PyMongoError
from config.connect_db import get_collection, MONGO_COLLECTIONS
from utils.helpers import green, blue, red, reset


# Setup logger
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def insert_document(collection_key: str, document: dict):
    try:
        collection_name = MONGO_COLLECTIONS.get(collection_key)
        if not collection_name:
            raise ValueError(f"Invalid collection key: {collection_key}")
        collection = get_collection(collection_name)

        if collection is None:
            raise ValueError(f"Collection '{collection_name}' not found.")

        result = collection.insert_one(document)
        if result.inserted_id:
            logger.info(green + f"Document added to {collection_name}" + reset)
        else:
            logger.warning(
                blue + f"Document insertion failed in {collection_name}" + reset
            )
    except Exception as e:
        logger.error(
            red + f"Error inserting document into {collection_key}: {e}" + reset
        )


def find_documents(
    collection_key: str, query: dict = None, limit: int = 0, sort_by: tuple = None
):

    try:
        collection_name = MONGO_COLLECTIONS.get(collection_key)
        if not collection_name:
            raise ValueError(f"Invalid collection key: {collection_key}")
        collection = get_collection(collection_name)
        query = query or {}
        cursor = collection.find(query)

        if sort_by:
            cursor = cursor.sort(sort_by)
        if limit:
            cursor = cursor.limit(limit)

        documents = list(cursor)
        logger.info(
            green
            + f"Retrieved {len(documents)} documents from {collection_name}"
            + reset
        )
        return documents
    except PyMongoError as e:
        logger.error(
            red + f"Failed to retrieve documents from {collection_key}: {e}" + reset
        )
        return []
    except Exception as e:
        logger.error(
            red
            + f"Unexpected error retrieving documents from {collection_key}: {e}"
            + reset
        )
        return []


def update_documents(
    collection_key: str, query: dict, update_data: dict, multiple: bool = False
):

    try:
        collection_name = MONGO_COLLECTIONS.get(collection_key)
        if not collection_name:
            raise ValueError(f"Invalid collection key: {collection_key}")
        collection = get_collection(collection_name)
        if "$set" not in update_data:
            update_data = {"$set": update_data}

        result = (
            collection.update_many(query, update_data)
            if multiple
            else collection.update_one(query, update_data)
        )
        logger.info(
            green
            + f"Updated: {result.modified_count} document(s) in {collection_name}"
            + reset
        )
        return result.modified_count
    except PyMongoError as e:
        logger.error(
            red + f"Failed to update documents in {collection_key}: {e}" + reset
        )
        return 0
    except Exception as e:
        logger.error(
            red
            + f"Unexpected error updating documents in {collection_key}: {e}"
            + reset
        )
        return 0


def delete_documents(collection_key: str, query: dict, multiple: bool = False):
    try:
        collection_name = MONGO_COLLECTIONS.get(collection_key)
        if not collection_name:
            raise ValueError(f"Invalid collection key: {collection_key}")
        collection = get_collection(collection_name)
        result = (
            collection.delete_many(query) if multiple else collection.delete_one(query)
        )
        logger.info(
            green
            + f"Deleted {result.deleted_count} document(s) from {collection_name}"
            + reset
        )
        return result.deleted_count
    except PyMongoError as e:
        logger.error(
            red + f"Failed to delete documents from {collection_key}: {e}" + reset
        )
        return 0
    except Exception as e:
        logger.error(
            red
            + f"Unexpected error deleting documents from {collection_key}: {e}"
            + reset
        )
        return 0
