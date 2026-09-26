"""
constraints.py

Hard-constraint filtering for the
Intelligent Polymer Material Selection and Recommendation System.
"""

import pandas as pd


# ============================================================
# PROPERTY COLUMN MAPPING
# ============================================================

PROPERTY_COLUMN_MAP = {
    "Tensile_Strength": "Tensile_Strength_Value",
    "Tensile_Modulus": "Tensile_Modulus_Value",
    "Impact_Strength": "Impact_Strength_Value",
    "Max_Service_Temperature": "Max_Service_Temperature_Value",
    "Melting_or_Softening_Temperature": "Melting_or_Softening_Temperature_Value",
    "Density": "Density_Value",
    "Water_Absorption": "Water_Absorption_Value",

    "Chemical_Resistance": "Chemical_Resistance",
    "Wear_Resistance": "Wear_Resistance",
    "UV_Resistance": "UV_Resistance",
    "Heat_Resistance": "Heat_Resistance",
    "Optical_Transparency": "Optical_Transparency",
    "Cost_Category": "Cost_Category",
    "Injection_Molding_Suitability": "Injection_Molding_Suitability",
}


# ============================================================
# PROPERTY DIRECTION
# ============================================================

HIGHER_IS_BETTER = {
    "Tensile_Strength",
    "Tensile_Modulus",
    "Impact_Strength",
    "Max_Service_Temperature",
    "Melting_or_Softening_Temperature",
    "Chemical_Resistance",
    "Wear_Resistance",
    "UV_Resistance",
    "Heat_Resistance",
    "Optical_Transparency",
    "Injection_Molding_Suitability",
}


LOWER_IS_BETTER = {
    "Density",
    "Water_Absorption",
    "Cost_Category",
}


# ============================================================
# NUMERIC PROPERTIES
# ============================================================

NUMERIC_PROPERTIES = {
    "Tensile_Strength",
    "Tensile_Modulus",
    "Impact_Strength",
    "Max_Service_Temperature",
    "Melting_or_Softening_Temperature",
    "Density",
    "Water_Absorption",
}


# ============================================================
# CATEGORICAL LEVELS
# ============================================================

LEVEL_MAPPING = {
    "low": 1,
    "medium": 2,
    "high": 3,
}


# ============================================================
# HELPER FUNCTIONS
# ============================================================

def normalize_text(value):
    """Normalize a value to lowercase text."""

    if pd.isna(value):
        return None

    return str(value).strip().lower()


def numeric_value(value):
    """Convert a value to float."""

    if pd.isna(value):
        return None

    try:
        return float(value)
    except (ValueError, TypeError):
        return None


def categorical_level(value):
    """
    Convert Low/Medium/High into numerical levels.

    Low    = 1
    Medium = 2
    High   = 3
    """

    value = normalize_text(value)

    if value is None:
        return None

    return LEVEL_MAPPING.get(value)


def get_property_column(property_name):
    """
    Convert logical property name to actual CSV column name.
    """

    property_name = str(property_name).strip()

    return PROPERTY_COLUMN_MAP.get(
        property_name,
        property_name
    )


# ============================================================
# CHECK ONE REQUIREMENT
# ============================================================

def satisfies_requirement(
    property_name,
    actual_value,
    required_value
):
    """
    Determine whether a polymer satisfies a requirement.
    """

    # --------------------------------------------------------
    # Missing value
    # --------------------------------------------------------

    if pd.isna(actual_value):
        return False


    # --------------------------------------------------------
    # Numeric property
    # --------------------------------------------------------

    if property_name in NUMERIC_PROPERTIES:

        actual = numeric_value(actual_value)
        required = numeric_value(required_value)

        if actual is None or required is None:
            return False

        # Higher is better
        if property_name in HIGHER_IS_BETTER:
            return actual >= required

        # Lower is better
        if property_name in LOWER_IS_BETTER:
            return actual <= required


    # --------------------------------------------------------
    # Cost category
    # --------------------------------------------------------

    if property_name == "Cost_Category":

        actual_level = categorical_level(actual_value)
        required_level = categorical_level(required_value)

        if actual_level is None or required_level is None:
            return False

        # Lower cost is better
        return actual_level <= required_level


    # --------------------------------------------------------
    # Other categorical properties
    # --------------------------------------------------------

    if property_name in HIGHER_IS_BETTER:

        actual_level = categorical_level(actual_value)
        required_level = categorical_level(required_value)

        if actual_level is None or required_level is None:
            return False

        return actual_level >= required_level


    # --------------------------------------------------------
    # Exact match fallback
    # --------------------------------------------------------

    return (
        normalize_text(actual_value)
        == normalize_text(required_value)
    )


# ============================================================
# APPLY HARD CONSTRAINTS
# ============================================================

def apply_hard_constraints(
    properties_df,
    requirements_df
):
    """
    Apply only hard constraints.

    Returns:
        eligible_ids
        rejected
    """

    # --------------------------------------------------------
    # Validate input columns
    # --------------------------------------------------------

    required_columns = {
        "Property_Name",
        "Required_Value",
        "Hard_Constraint",
    }

    missing = required_columns - set(
        requirements_df.columns
    )

    if missing:
        raise ValueError(
            f"Missing requirement columns: {missing}"
        )


    # --------------------------------------------------------
    # IMPORTANT:
    #
    # Only Yes / True / 1 are hard constraints.
    #
    # "No" must NOT be treated as True.
    # --------------------------------------------------------

    hard_requirements = requirements_df[
        requirements_df["Hard_Constraint"]
        .astype(str)
        .str.strip()
        .str.lower()
        .isin(["yes", "true", "1"])
    ].copy()


    # --------------------------------------------------------
    # DEBUG SAFETY CHECK
    # --------------------------------------------------------

    # For A001 this should contain exactly:
    #
    # Tensile_Strength
    # Max_Service_Temperature
    # Chemical_Resistance
    #

    eligible_ids = []
    rejected = []


    # --------------------------------------------------------
    # Check every polymer
    # --------------------------------------------------------

    for _, polymer in properties_df.iterrows():

        polymer_id = polymer["Polymer_ID"]

        failures = []


        # ----------------------------------------------------
        # Check HARD requirements only
        # ----------------------------------------------------

        for _, requirement in hard_requirements.iterrows():

            property_name = str(
                requirement["Property_Name"]
            ).strip()

            required_value = requirement[
                "Required_Value"
            ]


            # Map logical property to CSV column
            actual_column = get_property_column(
                property_name
            )


            # Check column exists
            if actual_column not in properties_df.columns:

                failures.append(
                    f"{property_name}: "
                    f"column '{actual_column}' not found"
                )

                continue


            # Actual polymer value
            actual_value = polymer[
                actual_column
            ]


            # Check requirement
            passed = satisfies_requirement(
                property_name,
                actual_value,
                required_value
            )


            if not passed:

                failures.append(
                    f"{property_name}: "
                    f"actual={actual_value}, "
                    f"required={required_value}"
                )


        # ----------------------------------------------------
        # Eligible / Rejected
        # ----------------------------------------------------

        if len(failures) == 0:

            eligible_ids.append(
                polymer_id
            )

        else:

            rejected.append(
                {
                    "Polymer_ID": polymer_id,
                    "Failures": failures
                }
            )


    return eligible_ids, rejected


# ============================================================
# MAIN TEST
# ============================================================

if __name__ == "__main__":

    from recommendation.loader import load_data


    print()
    print("=" * 70)
    print("HARD CONSTRAINT TEST")
    print("=" * 70)


    # --------------------------------------------------------
    # Load datasets
    # --------------------------------------------------------

    data = load_data()

    polymers_df = data["properties"]
    applications_df = data["applications"]


    # --------------------------------------------------------
    # Select A001
    # --------------------------------------------------------

    analysis_id = "A001"

    requirements_df = applications_df[
        applications_df["Analysis_ID"].astype(str).str.strip()
        == analysis_id
    ].copy()


    print()
    print(f"Application: {analysis_id}")


    # --------------------------------------------------------
    # Show hard constraints being used
    # --------------------------------------------------------

    hard_requirements = requirements_df[
        requirements_df["Hard_Constraint"]
        .astype(str)
        .str.strip()
        .str.lower()
        .isin(["yes", "true", "1"])
    ]


    print()
    print("Hard Constraints Used:")

    for _, row in hard_requirements.iterrows():

        print(
            f" - {row['Property_Name']}: "
            f"{row['Required_Value']}"
        )


    # --------------------------------------------------------
    # Apply constraints
    # --------------------------------------------------------

    eligible_ids, rejected = apply_hard_constraints(
        polymers_df,
        requirements_df
    )


    # --------------------------------------------------------
    # Results
    # --------------------------------------------------------

    print()
    print(
        f"Eligible Materials: {len(eligible_ids)}"
    )

    print(
        f"Rejected Materials: {len(rejected)}"
    )


    print()
    print("Eligible Polymer IDs:")

    for polymer_id in eligible_ids:

        print(f" - {polymer_id}")


    print()
    print("=" * 70)