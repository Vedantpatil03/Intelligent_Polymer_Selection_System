import os
import pandas as pd



BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")


POLYMERS_FILE = os.path.join(DATA_DIR, "final_polymers.csv")
PROPERTIES_FILE = os.path.join(DATA_DIR, "final_polymer_properties.csv")
SOURCES_FILE = os.path.join(DATA_DIR, "final_property_sources.csv")
APPLICATIONS_FILE = os.path.join(DATA_DIR, "final_application_requirements.csv")



def check_file_exists(file_path):
    if os.path.exists(file_path):
        print(f"✓ File found: {os.path.basename(file_path)}")
        return True
    else:
        print(f"✗ File missing: {os.path.basename(file_path)}")
        return False


def check_columns(df, required_columns, file_name):
    missing_columns = [
        column for column in required_columns
        if column not in df.columns
    ]

    if missing_columns:
        print(f"✗ {file_name}: Missing columns:")
        for column in missing_columns:
            print(f"    - {column}")
        return False

    print(f"✓ {file_name}: Required columns are present")
    return True


def check_duplicates(df, file_name):
    duplicates = df.duplicated().sum()

    if duplicates == 0:
        print(f"✓ {file_name}: No duplicate rows")
        return True

    print(f"✗ {file_name}: {duplicates} duplicate rows found")
    return False


def check_missing_values(df, file_name):
    missing = df.isnull().sum()
    missing = missing[missing > 0]

    if len(missing) == 0:
        print(f"✓ {file_name}: No missing values")
        return True

    print(f"⚠ {file_name}: Missing values found")

    for column, count in missing.items():
        print(f"    - {column}: {count}")

    return True


# ---------------------------------------------------------
# Main Validation
# ---------------------------------------------------------

def main():

    print("INTELLIGENT POLYMER MATERIAL SELECTION SYSTEM")
    print("DATA VALIDATION")

    # -----------------------------------------------------
    # 1. Check Files
    # -----------------------------------------------------

    print("\n[1] Checking CSV files...")

    files = [
        POLYMERS_FILE,
        PROPERTIES_FILE,
        SOURCES_FILE,
        APPLICATIONS_FILE
    ]

    all_files_exist = all(check_file_exists(file) for file in files)

    if not all_files_exist:
        print("\n✗ Validation stopped because one or more files are missing.")
        return

    # -----------------------------------------------------
    # 2. Load CSV files
    # -----------------------------------------------------

    print("\n[2] Loading CSV files...")

    try:
        polymers = pd.read_csv(POLYMERS_FILE)
        properties = pd.read_csv(PROPERTIES_FILE)
        sources = pd.read_csv(SOURCES_FILE)
        applications = pd.read_csv(APPLICATIONS_FILE)

        print("✓ All CSV files loaded successfully")

    except Exception as e:
        print(f"✗ Error loading CSV files: {e}")
        return

    # -----------------------------------------------------
    # 3. Display Dataset Sizes
    # -----------------------------------------------------

    print("\n[3] Dataset sizes...")

    print(f"✓ Polymers              : {len(polymers)} rows")
    print(f"✓ Polymer Properties    : {len(properties)} rows")
    print(f"✓ Property Sources      : {len(sources)} rows")
    print(f"✓ Application Requirements: {len(applications)} rows")

    # -----------------------------------------------------
    # 4. Check Required Columns
    # -----------------------------------------------------

    print("\n[4] Checking required columns...")

    polymer_columns = [
        "Polymer_ID",
        "Polymer_Name",
        "Polymer_Family",
        "Material_Type",
        "Manufacturer",
        "Grade",
        "Common_Applications",
        "Processing_Method",
        "Recyclability",
        "Description"
    ]

    property_columns = [
        "Polymer_ID",
        "Density_Value",
        "Tensile_Strength_Value",
        "Tensile_Modulus_Value",
        "Impact_Strength_Value",
        "Max_Service_Temperature_Value",
        "Water_Absorption_Value",
        "Chemical_Resistance",
        "Wear_Resistance",
        "UV_Resistance",
        "Heat_Resistance",
        "Optical_Transparency",
        "Cost_Category",
        "Injection_Molding_Suitability"
    ]

    source_columns = [
        "Source_ID",
        "Polymer_ID",
        "Property_Name",
        "Property_Value",
        "Unit",
        "Test_Method",
        "Source_Type",
        "Source_Name",
        "Manufacturer",
        "Document_Title"
    ]

    application_columns = [
        "Analysis_ID",
        "Application_Name",
        "Property_Name",
        "Required_Value",
        "Required_Unit",
        "Requirement_Level",
        "Weight_Percentage",
        "Hard_Constraint",
        "Notes"
    ]

    check_columns(
        polymers,
        polymer_columns,
        "final_polymers.csv"
    )

    check_columns(
        properties,
        property_columns,
        "final_polymer_properties.csv"
    )

    check_columns(
        sources,
        source_columns,
        "final_property_sources.csv"
    )

    check_columns(
        applications,
        application_columns,
        "final_application_requirements.csv"
    )

    # -----------------------------------------------------
    # 5. Check Duplicates
    # -----------------------------------------------------

    print("\n[5] Checking duplicate rows...")

    check_duplicates(polymers, "final_polymers.csv")
    check_duplicates(properties, "final_polymer_properties.csv")
    check_duplicates(sources, "final_property_sources.csv")
    check_duplicates(applications, "final_application_requirements.csv")

    # -----------------------------------------------------
    # 6. Check Missing Values
    # -----------------------------------------------------

    print("\n[6] Checking missing values...")

    check_missing_values(polymers, "final_polymers.csv")
    check_missing_values(properties, "final_polymer_properties.csv")
    check_missing_values(sources, "final_property_sources.csv")
    check_missing_values(
        applications,
        "final_application_requirements.csv"
    )

    # -----------------------------------------------------
    # 7. Check Polymer IDs
    # -----------------------------------------------------

    print("\n[7] Checking Polymer IDs...")

    polymer_ids = set(polymers["Polymer_ID"].dropna())

    property_ids = set(properties["Polymer_ID"].dropna())
    source_ids = set(sources["Polymer_ID"].dropna())

    missing_property_ids = polymer_ids - property_ids
    extra_property_ids = property_ids - polymer_ids

    missing_source_ids = polymer_ids - source_ids
    extra_source_ids = source_ids - polymer_ids

    if not missing_property_ids and not extra_property_ids:
        print("✓ Polymer IDs match between polymers and properties")
    else:
        print("✗ Polymer ID mismatch between polymers and properties")

    if not missing_source_ids and not extra_source_ids:
        print("✓ Polymer IDs in sources belong to polymer database")
    else:
        print("⚠ Polymer ID mismatch found in sources")

    print(f"✓ Total unique polymers: {len(polymer_ids)}")

    # -----------------------------------------------------
    # 8. Check Application Scenarios
    # -----------------------------------------------------

    print("\n[8] Checking application scenarios...")

    scenario_ids = applications["Analysis_ID"].unique()

    print(f"✓ Total application scenarios: {len(scenario_ids)}")

    for scenario in scenario_ids:

        scenario_data = applications[
            applications["Analysis_ID"] == scenario
        ]

        application_name = scenario_data["Application_Name"].iloc[0]

        requirement_count = len(scenario_data)

        weight_total = scenario_data["Weight_Percentage"].sum()

        print(
            f"\n  {scenario} - {application_name}"
        )

        print(
            f"    Requirements : {requirement_count}"
        )

        print(
            f"    Weight total : {weight_total}%"
        )

        if requirement_count == 5:
            print("    ✓ Contains 5 requirements")
        else:
            print("    ⚠ Requirement count is not 5")

        if weight_total == 100:
            print("    ✓ Weights total 100%")
        else:
            print("    ✗ Weights do not total 100%")

    # -----------------------------------------------------
    # 9. Check Property Name Compatibility
    # -----------------------------------------------------

    print("\n[9] Checking property names...")

    requirement_properties = set(
        applications["Property_Name"].dropna()
    )

    property_database_names = {
        column.replace("_Value", "")
        for column in properties.columns
        if column.endswith("_Value")
    }

    categorical_properties = {
        "Chemical_Resistance",
        "Wear_Resistance",
        "UV_Resistance",
        "Heat_Resistance",
        "Optical_Transparency",
        "Cost_Category",
        "Injection_Molding_Suitability"
    }

    available_properties = (
        property_database_names
        | categorical_properties
    )

    missing_properties = (
        requirement_properties - available_properties
    )

    if not missing_properties:
        print("✓ All application properties exist in property database")
    else:
        print("✗ Missing properties:")
        for prop in missing_properties:
            print(f"    - {prop}")

    # -----------------------------------------------------
    # 10. Check Hard Constraints
    # -----------------------------------------------------

    print("\n[10] Checking hard constraints...")

    hard_values = set(
        applications["Hard_Constraint"]
        .dropna()
        .astype(str)
        .str.strip()
        .str.lower()
    )

    valid_hard_values = {"yes", "no"}

    invalid_hard_values = hard_values - valid_hard_values

    if not invalid_hard_values:
        print("✓ Hard constraint values are valid")
    else:
        print("✗ Invalid hard constraint values:")
        print(invalid_hard_values)

    print("DATA VALIDATION COMPLETED")

    print("\nYour datasets are ready for the next phase:")
    print("→ MCDM Recommendation Engine")
    print()


if __name__ == "__main__":
    main()