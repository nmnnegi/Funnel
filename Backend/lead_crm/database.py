from pymongo import MongoClient
from django.conf import settings

# Initialize MongoDB client
mongo_client = MongoClient(settings.MONGODB_CONFIG["uri"])
database = mongo_client[settings.MONGODB_CONFIG["database"]]

# Separate collections
leads_collection = database[settings.MONGODB_CONFIG["collections"]["leads"]]
stages_collection = database[settings.MONGODB_CONFIG["collections"]["stages"]]
configs_collection = database[settings.MONGODB_CONFIG["collections"]["configs"]]


def get_collection(collection_name):
    """Get a specific collection by name"""
    return database[
        settings.MONGODB_CONFIG["collections"].get(collection_name, collection_name)
    ]


def get_database():
    """Get the database instance"""
    return database


def create_indexes():
    """
    Create recommended indexes for better performance.
    Run this once during initial setup.
    """
    # Leads collection indexes
    leads_collection.create_index([("uid", 1)], unique=True)
    leads_collection.create_index([("item_id", 1)], unique=True)
    leads_collection.create_index([("current_stage", 1)])
    leads_collection.create_index([("config", 1)])
    leads_collection.create_index([("created_at", -1)])
    leads_collection.create_index([("assigned_to", 1)])

    # Stages collection indexes
    stages_collection.create_index([("uid", 1)], unique=True)
    stages_collection.create_index([("config", 1)])
    stages_collection.create_index([("order", 1)])

    # Configs collection indexes
    configs_collection.create_index([("uid", 1)], unique=True)

    print("MongoDB indexes created successfully")


if __name__ == "__main__":
    # Create indexes when run directly
    create_indexes()
