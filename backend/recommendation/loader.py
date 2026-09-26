import os
import pandas as pd


# ---------------------------------------------------------
# Project Paths
# ---------------------------------------------------------

BASE_DIR = os.path.dirname(
    os.path.dirname(
        os.path.dirname(os.path.abspath(__file__))
    )
)

DATA_DIR = os.path.join(BASE_DIR, "data")


# ---------------------------------------------------------
# CSV File Paths
# ---------------------------------------------------------

POLYMERS_FILE = os.path.join(
    DATA_DIR,
    "final_polymers.csv"
)

PROPERTIES_FILE = os.path.join(
    DATA_DIR,
    "final_polymer_properties.csv"
)

SOURCES_FILE = os.path.join(
    DATA_DIR,
    "final_property_sources.csv"
)

APPLICATIONS_FILE = os.path.join(
    DATA_DIR,
    "final_application_requirements.csv"
)


# ---------------------------------------------------------
# Load All Data
# ---------------------------------------------------------

def load_data():

    polymers = pd.read_csv(POLYMERS_FILE)

    properties = pd.read_csv(PROPERTIES_FILE)

    sources = pd.read_csv(SOURCES_FILE)

    applications = pd.read_csv(APPLICATIONS_FILE)

    return {
        "polymers": polymers,
        "properties": properties,
        "sources": sources,
        "applications": applications
    }


# ---------------------------------------------------------
# Test Loader
# ---------------------------------------------------------

if __name__ == "__main__":

    data = load_data()

    print("POLYMER DATA LOADER")


    print(
        f"\nPolymers              : "
        f"{len(data['polymers'])} records"
    )

    print(
        f"Polymer Properties    : "
        f"{len(data['properties'])} records"
    )

    print(
        f"Property Sources      : "
        f"{len(data['sources'])} records"
    )

    print(
        f"Application Requirements: "
        f"{len(data['applications'])} records"
    )

    print("\n✓ All datasets loaded successfully.")