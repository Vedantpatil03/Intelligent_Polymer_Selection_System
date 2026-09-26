from database.collections import (
    get_polymers,
    get_polymer_properties,
    get_property_sources,
    get_applications,
)


def load_data_from_mongodb():
    """
    Load all project datasets from MongoDB Atlas.

    Returns:
        dict: DataFrames containing project data.
    """

    data = {
        "polymers": get_polymers(),
        "properties": get_polymer_properties(),
        "sources": get_property_sources(),
        "applications": get_applications(),
    }

    return data


if __name__ == "__main__":
    data = load_data_from_mongodb()

    print("MongoDB data loaded successfully!")
    print(f"Polymers: {len(data['polymers'])}")
    print(f"Properties: {len(data['properties'])}")
    print(f"Sources: {len(data['sources'])}")
    print(f"Applications: {len(data['applications'])}")