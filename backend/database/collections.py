import math
from datetime import datetime, timezone

import pandas as pd
from pymongo.errors import PyMongoError

from database.connection import db


polymers_collection = db["polymers"]
properties_collection = db["polymer_properties"]
sources_collection = db["property_sources"]
applications_collection = db["applications"]
history_collection = db["recommendation_history"]
users_collection = db["users"]

users_collection.create_index("email", unique=True)
history_collection.create_index([("user_id", 1), ("created_at", -1)])


def make_json_safe(value):
    """Recursively convert NaN/Infinity and NumPy values to JSON-safe values."""
    if value is None:
        return None

    if isinstance(value, float):
        return value if math.isfinite(value) else None

    # Handles NumPy scalar types such as np.float64 / np.int64.
    if hasattr(value, "item") and callable(value.item):
        try:
            return make_json_safe(value.item())
        except (ValueError, TypeError):
            pass

    if isinstance(value, dict):
        return {str(key): make_json_safe(item) for key, item in value.items()}

    if isinstance(value, (list, tuple)):
        return [make_json_safe(item) for item in value]

    return value


def get_polymers():
    documents = list(polymers_collection.find({}, {"_id": 0}))
    return pd.DataFrame(documents)


def get_polymer_properties():
    documents = list(properties_collection.find({}, {"_id": 0}))
    return pd.DataFrame(documents)


def get_property_sources():
    documents = list(sources_collection.find({}, {"_id": 0}))
    return pd.DataFrame(documents)


def get_applications():
    documents = list(applications_collection.find({}, {"_id": 0}))
    return pd.DataFrame(documents)


def save_recommendation_history(history_data, user_id):
    # Clean NaN/Infinity before inserting so future history records are valid JSON/API data.
    history_data = make_json_safe(history_data.copy())
    history_data["created_at"] = datetime.now(timezone.utc)
    history_data["user_id"] = user_id

    result = history_collection.insert_one(history_data)
    return str(result.inserted_id)


def get_recommendation_history():
    documents = list(
        history_collection.find({}, {"_id": 0}).sort("created_at", -1)
    )

    # Existing records may contain NaN values from earlier recommendations.
    # Convert those values to None before FastAPI serializes the response.
    return make_json_safe(documents)
