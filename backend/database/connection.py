import os

from dotenv import load_dotenv
from pymongo import MongoClient
from pymongo.errors import PyMongoError


# Load variables from .env
load_dotenv()

MONGODB_URI = os.getenv("MONGODB_URI")
MONGODB_DATABASE = os.getenv("MONGODB_DATABASE", "polymer_selection_db")


if not MONGODB_URI:
    raise ValueError("MONGODB_URI is not set in the .env file")


# Create MongoDB client
client = MongoClient(
    MONGODB_URI,
    serverSelectionTimeoutMS=5000
)

# Select project database
db = client[MONGODB_DATABASE]


def test_connection():
    """
    Test connection to MongoDB Atlas.
    """
    try:
        client.admin.command("ping")
        print("MongoDB Atlas connection successful!")
        print(f"Database: {MONGODB_DATABASE}")
        return True

    except PyMongoError as error:
        print("MongoDB Atlas connection failed!")
        print(f"Error: {error}")
        return False


if __name__ == "__main__":
    test_connection()