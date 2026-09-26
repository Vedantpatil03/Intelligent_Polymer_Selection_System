import pandas as pd


# =========================================================
# Criteria Direction
# =========================================================

HIGHER_IS_BETTER = {
    "Tensile_Strength",
    "Tensile_Modulus",
    "Impact_Strength",
    "Max_Service_Temperature",
    "Chemical_Resistance",
    "Wear_Resistance",
    "UV_Resistance",
    "Heat_Resistance",
    "Optical_Transparency",
    "Injection_Molding_Suitability"
}


LOWER_IS_BETTER = {
    "Density",
    "Water_Absorption",
    "Cost_Category"
}


# =========================================================
# Categorical Value Mapping
# =========================================================

LEVEL_MAPPING = {
    "low": 1,
    "medium": 2,
    "high": 3
}


# =========================================================
# Get Property Column
# =========================================================

def get_property_column(property_name, properties):

    numeric_column = f"{property_name}_Value"

    if numeric_column in properties.columns:
        return numeric_column

    if property_name in properties.columns:
        return property_name

    return None


# =========================================================
# Normalize Numeric Values
# =========================================================

def normalize_numeric(
    value,
    min_value,
    max_value,
    higher_is_better=True
):
    """
    Converts a numeric property into a score between 0 and 1.
    """

    if pd.isna(value):
        return None

    if max_value == min_value:
        return 1.0

    if higher_is_better:

        score = (
            value - min_value
        ) / (
            max_value - min_value
        )

    else:

        score = (
            max_value - value
        ) / (
            max_value - min_value
        )

    return max(0.0, min(1.0, score))


# =========================================================
# Score Categorical Values
# =========================================================

def score_categorical(value):

    if pd.isna(value):
        return None

    value = str(value).strip().lower()

    return LEVEL_MAPPING.get(value)


# =========================================================
# Calculate Scores for One Criterion
# =========================================================

def calculate_criterion_scores(
    eligible_properties,
    requirement
):

    property_name = requirement["Property_Name"]

    column = get_property_column(
        property_name,
        eligible_properties
    )

    if column is None:
        raise ValueError(
            f"Property '{property_name}' "
            f"not found in polymer properties."
        )

    values = eligible_properties[column]

    # -----------------------------------------------------
    # Numeric Criteria
    # -----------------------------------------------------

    if property_name in {
        "Tensile_Strength",
        "Tensile_Modulus",
        "Impact_Strength",
        "Max_Service_Temperature",
        "Density",
        "Water_Absorption"
    }:

        numeric_values = pd.to_numeric(
            values,
            errors="coerce"
        )

        min_value = numeric_values.min()

        max_value = numeric_values.max()

        higher_is_better = (
            property_name in HIGHER_IS_BETTER
        )

        scores = numeric_values.apply(
            lambda value: normalize_numeric(
                value,
                min_value,
                max_value,
                higher_is_better
            )
        )

        return scores

    # -----------------------------------------------------
    # Categorical Criteria
    # -----------------------------------------------------

    scores = values.apply(
        score_categorical
    )

    return scores / 3.0


# =========================================================
# Test
# =========================================================

if __name__ == "__main__":

    from recommendation.loader import load_data
    from recommendation.constraints import apply_hard_constraints

    data = load_data()

    properties = data["properties"]
    applications = data["applications"]

    # -----------------------------------------------------
    # Test Application
    # -----------------------------------------------------

    analysis_id = "A001"

    eligible_ids, rejected = apply_hard_constraints(
        properties,
        applications,
        analysis_id
    )

    eligible_properties = properties[
        properties["Polymer_ID"].isin(eligible_ids)
    ].copy()

    print("\n" + "=" * 60)
    print("SCORING & NORMALIZATION TEST")
    print("=" * 60)

    print(
        f"\nApplication: {analysis_id}"
    )

    print(
        f"Eligible polymers: {len(eligible_properties)}"
    )

    # -----------------------------------------------------
    # Get A001 Requirements
    # -----------------------------------------------------

    requirements = applications[
        applications["Analysis_ID"] == analysis_id
    ]

    # -----------------------------------------------------
    # Calculate Scores
    # -----------------------------------------------------

    for _, requirement in requirements.iterrows():

        property_name = requirement["Property_Name"]

        scores = calculate_criterion_scores(
            eligible_properties,
            requirement
        )

        print(
            f"\n{property_name}"
        )

        for polymer_id, score in zip(
            eligible_properties["Polymer_ID"],
            scores
        ):

            if pd.isna(score):
                print(
                    f"  {polymer_id}: N/A"
                )
            else:
                print(
                    f"  {polymer_id}: "
                    f"{score:.4f}"
                )

   
    print("SCORING TEST COMPLETED")
   