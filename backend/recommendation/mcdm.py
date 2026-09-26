import pandas as pd

from .constraints import (
    HIGHER_IS_BETTER,
    LOWER_IS_BETTER,
    LEVEL_MAPPING,
    apply_hard_constraints,
)


# ============================================================
# PROPERTY COLUMN MAPPING
# ============================================================

# Logical property name used by the application requirements
# -> Actual column name in final_polymer_properties.csv

PROPERTY_COLUMN_MAP = {
    "Tensile_Strength": "Tensile_Strength_Value",
    "Tensile_Modulus": "Tensile_Modulus_Value",
    "Impact_Strength": "Impact_Strength_Value",
    "Max_Service_Temperature": "Max_Service_Temperature_Value",
    "Melting_or_Softening_Temperature": "Melting_or_Softening_Temperature_Value",
    "Density": "Density_Value",
    "Water_Absorption": "Water_Absorption_Value",

    # Categorical properties already use the logical name
    "Chemical_Resistance": "Chemical_Resistance",
    "Wear_Resistance": "Wear_Resistance",
    "UV_Resistance": "UV_Resistance",
    "Heat_Resistance": "Heat_Resistance",
    "Optical_Transparency": "Optical_Transparency",
    "Cost_Category": "Cost_Category",
    "Injection_Molding_Suitability": "Injection_Molding_Suitability",
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
# GET ACTUAL DATA COLUMN
# ============================================================

def get_property_column(property_name):
    """
    Convert logical property name to the actual
    column name in final_polymer_properties.csv.
    """

    return PROPERTY_COLUMN_MAP.get(property_name)


# ============================================================
# NUMERIC NORMALIZATION
# ============================================================

def normalize_numeric(
    actual_value,
    required_value,
    property_name,
    candidate_values
):
    """
    Convert a numeric material property into a score
    between 0 and 1.

    Higher-is-better:
        Higher actual value = better score.

    Lower-is-better:
        Lower actual value = better score.
    """

    try:

        actual = float(actual_value)
        required = float(required_value)

        values = pd.to_numeric(
            candidate_values,
            errors="coerce"
        ).dropna()

        if len(values) == 0:
            return None

        minimum = float(values.min())
        maximum = float(values.max())

        # ----------------------------------------------------
        # All candidates have same value
        # ----------------------------------------------------

        if maximum == minimum:
            return 1.0

        # ----------------------------------------------------
        # HIGHER IS BETTER
        # ----------------------------------------------------

        if property_name in HIGHER_IS_BETTER:

            # Requirement is below/equal to minimum
            if required <= minimum:

                if maximum == 0:
                    return 1.0

                return min(actual / maximum, 1.0)

            # Requirement lies inside candidate range
            if required < maximum:

                # Actual value below requirement
                if actual <= required:

                    if required == 0:
                        return 1.0

                    return max(
                        0.0,
                        0.5 * (actual / required)
                    )

                # Actual value exceeds requirement
                score = 0.5 + (
                    0.5 *
                    (actual - required) /
                    (maximum - required)
                )

                return min(
                    max(score, 0.0),
                    1.0
                )

            # Requirement >= maximum
            if required != 0:

                return min(
                    actual / required,
                    1.0
                )

            return 1.0

        # ----------------------------------------------------
        # LOWER IS BETTER
        # ----------------------------------------------------

        if property_name in LOWER_IS_BETTER:

            # Requirement >= maximum
            if required >= maximum:

                if actual == 0:
                    return 1.0

                return min(
                    maximum / actual,
                    1.0
                )

            # Requirement lies inside candidate range
            if required > minimum:

                # Actual is worse than requirement
                if actual >= required:

                    if actual == 0:
                        return 1.0

                    return max(
                        0.0,
                        0.5 * (required / actual)
                    )

                # Actual is better than requirement
                score = 0.5 + (
                    0.5 *
                    (required - actual) /
                    (required - minimum)
                )

                return min(
                    max(score, 0.0),
                    1.0
                )

            # Requirement <= minimum
            if actual <= required:

                if actual <= 0:
                    return 1.0

                return min(
                    required / actual,
                    1.0
                )

            return 0.0

        return None

    except (
        ValueError,
        TypeError,
        ZeroDivisionError
    ):
        return None


# ============================================================
# CATEGORICAL SCORING
# ============================================================

def calculate_categorical_score(
    actual_value,
    required_value,
    property_name
):
    """
    Calculate score for categorical properties.
    """

    if pd.isna(actual_value) or pd.isna(required_value):
        return None

    actual = str(actual_value).strip().lower()
    required = str(required_value).strip().lower()

    # --------------------------------------------------------
    # COST CATEGORY
    # --------------------------------------------------------

    if property_name == "Cost_Category":

        actual_level = LEVEL_MAPPING.get(actual)
        required_level = LEVEL_MAPPING.get(required)

        if (
            actual_level is None
            or required_level is None
        ):
            return None

        # Lower cost is better
        if actual_level < required_level:
            return 1.0

        # Same category
        if actual_level == required_level:
            return 0.75

        # Higher cost
        return 0.25

    # --------------------------------------------------------
    # OTHER CATEGORICAL PROPERTIES
    # --------------------------------------------------------

    actual_level = LEVEL_MAPPING.get(actual)
    required_level = LEVEL_MAPPING.get(required)

    if (
        actual_level is not None
        and required_level is not None
    ):

        if actual_level >= required_level:
            return 1.0

        return actual_level / required_level

    # --------------------------------------------------------
    # EXACT MATCH FALLBACK
    # --------------------------------------------------------

    return (
        1.0
        if actual == required
        else 0.0
    )
    # --------------------------------------------------------
    # OTHER CATEGORICAL PROPERTIES
    # --------------------------------------------------------

    actual_level = LEVEL_MAPPING.get(actual)
    required_level = LEVEL_MAPPING.get(required)

    if (
        actual_level is not None
        and required_level is not None
    ):

        if actual_level >= required_level:
            return 1.0

        return actual_level / required_level

    # --------------------------------------------------------
    # EXACT MATCH FALLBACK
    # --------------------------------------------------------

    return (
        1.0
        if actual.lower() == required.lower()
        else 0.0
    )


# ============================================================
# CRITERION SCORE
# ============================================================

def calculate_criterion_score(
    actual_value,
    required_value,
    property_name,
    candidate_values
):
    """
    Calculate score for one criterion.
    """

    if property_name in NUMERIC_PROPERTIES:

        return normalize_numeric(
            actual_value,
            required_value,
            property_name,
            candidate_values
        )

    return calculate_categorical_score(
        actual_value,
        required_value,
        property_name
    )


# ============================================================
# CORE MCDM
# ============================================================

def calculate_mcdm(
    properties_df,
    requirements_df
):
    """
    Main MCDM calculation.

    Supports:

    1. Predefined applications A001-A006
    2. Custom user requirements

    Dataset weight:
        Weight_Percentage

    Custom API weight:
        Weight

    Internally:
        Weight
    """

    # --------------------------------------------------------
    # COPY
    # --------------------------------------------------------

    requirements_df = requirements_df.copy()

    # --------------------------------------------------------
    # BASIC VALIDATION
    # --------------------------------------------------------

    if requirements_df.empty:

        raise ValueError(
            "No requirements provided."
        )

    required_columns = {
        "Property_Name",
        "Required_Value",
        "Hard_Constraint",
    }

    missing = (
        required_columns
        - set(requirements_df.columns)
    )

    if missing:

        raise ValueError(
            f"Missing requirement columns: {missing}"
        )

    # --------------------------------------------------------
    # WEIGHT COLUMN
    # --------------------------------------------------------

    if "Weight" not in requirements_df.columns:

        if "Weight_Percentage" in requirements_df.columns:

            requirements_df["Weight"] = pd.to_numeric(
                requirements_df[
                    "Weight_Percentage"
                ],
                errors="coerce"
            )

        else:

            raise ValueError(
                "Requirement data must contain "
                "'Weight' or 'Weight_Percentage'."
            )

    else:

        requirements_df["Weight"] = pd.to_numeric(
            requirements_df["Weight"],
            errors="coerce"
        )

    # --------------------------------------------------------
    # WEIGHT VALIDATION
    # --------------------------------------------------------

    if requirements_df["Weight"].isna().any():

        raise ValueError(
            "All requirement weights must be numeric."
        )

    if (
        requirements_df["Weight"] <= 0
    ).any():

        raise ValueError(
            "All requirement weights "
            "must be greater than zero."
        )

    total_weight = requirements_df[
        "Weight"
    ].sum()

    if abs(total_weight - 100) > 0.01:

        raise ValueError(
            "Requirement weights must total 100. "
            f"Current total: {total_weight}"
        )

    # --------------------------------------------------------
    # PROPERTY COLUMN VALIDATION
    # --------------------------------------------------------

    for property_name in requirements_df[
        "Property_Name"
    ]:

        actual_column = get_property_column(
            property_name
        )

        if actual_column is None:

            raise ValueError(
                f"Unsupported property: "
                f"'{property_name}'"
            )

        if actual_column not in properties_df.columns:

            raise ValueError(
                f"Property '{property_name}' "
                f"expects column "
                f"'{actual_column}', "
                "but that column is not available "
                "in polymer property data."
            )

    # --------------------------------------------------------
    # HARD CONSTRAINTS
    # --------------------------------------------------------

    eligible_ids, rejected = apply_hard_constraints(
        properties_df,
        requirements_df
    )

    # --------------------------------------------------------
    # NO ELIGIBLE MATERIALS
    # --------------------------------------------------------

    if not eligible_ids:

        return {
            "results": [],
            "eligible_ids": [],
            "rejected": rejected,
        }

    # --------------------------------------------------------
    # ELIGIBLE MATERIALS
    # --------------------------------------------------------

    eligible_properties = properties_df[
        properties_df["Polymer_ID"].isin(
            eligible_ids
        )
    ].copy()

    # --------------------------------------------------------
    # CALCULATE SCORES
    # --------------------------------------------------------

    results = []

    for _, polymer in eligible_properties.iterrows():

        criterion_scores = {}
        weighted_contributions = {}

        total_score = 0.0

        # ----------------------------------------------------
        # EACH REQUIREMENT
        # ----------------------------------------------------

        for _, requirement in requirements_df.iterrows():

            property_name = requirement[
                "Property_Name"
            ]

            required_value = requirement[
                "Required_Value"
            ]

            weight = float(
                requirement["Weight"]
            )

            # Actual CSV column
            actual_column = get_property_column(
                property_name
            )

            # ------------------------------------------------
            # GET ACTUAL VALUE
            # ------------------------------------------------

            actual_value = polymer[
                actual_column
            ]

            # ------------------------------------------------
            # CANDIDATE VALUES
            # ------------------------------------------------

            candidate_values = (
                eligible_properties[
                    actual_column
                ]
            )

            # ------------------------------------------------
            # SCORE
            # ------------------------------------------------

            score = calculate_criterion_score(
                actual_value,
                required_value,
                property_name,
                candidate_values
            )

            # ------------------------------------------------
            # MISSING DATA
            # ------------------------------------------------

            if score is None:

                score = 0.0

            # ------------------------------------------------
            # WEIGHTED SCORE
            # ------------------------------------------------

            weighted_score = (
                score *
                (weight / 100)
            )

            criterion_scores[
                property_name
            ] = round(
                float(score),
                4
            )

            weighted_contributions[
                property_name
            ] = round(
                float(weighted_score),
                4
            )

            total_score += weighted_score

        # ----------------------------------------------------
        # STORE
        # ----------------------------------------------------

        results.append({

            "polymer_id":
                polymer["Polymer_ID"],

            "mcdm_score":
                round(
                    total_score,
                    4
                ),

            "criterion_scores":
                criterion_scores,

            "weighted_contributions":
                weighted_contributions,
        })

    # --------------------------------------------------------
    # FINAL SCORE SAFETY CHECK
    # --------------------------------------------------------
    # MCDM scores must always be finite numbers in the range 0..1.
    # Missing/invalid criterion values are already converted to 0.0
    # above, so this final check prevents NaN/Infinity from affecting
    # the ranking.

    for result in results:
        score = float(result.get("mcdm_score", 0.0))

        if pd.isna(score) or score != score:
            score = 0.0

        result["mcdm_score"] = round(
            min(max(score, 0.0), 1.0),
            4
        )

    # --------------------------------------------------------
    # SORT — HIGHEST SCORE FIRST
    # --------------------------------------------------------
    # IMPORTANT:
    # Rank 1 must ALWAYS be the material with the highest MCDM
    # score. Do not sort by Polymer_ID or the original DataFrame
    # order.

    results = sorted(
        results,
        key=lambda item: item["mcdm_score"],
        reverse=True
    )

    # --------------------------------------------------------
    # RANK — ASSIGN AFTER SORTING
    # --------------------------------------------------------

    for index, result in enumerate(
        results,
        start=1
    ):
        result["rank"] = index

    # --------------------------------------------------------
    # FINAL RANKING CONSISTENCY CHECK
    # --------------------------------------------------------
    # This makes the ranking rule explicit and protects against
    # accidental changes later in the code.

    if results:
        scores = [
            result["mcdm_score"]
            for result in results
        ]

        if any(
            scores[index] < scores[index + 1]
            for index in range(len(scores) - 1)
        ):
            raise RuntimeError(
                "MCDM ranking error: results are not sorted "
                "from highest score to lowest score."
            )

    # --------------------------------------------------------
    # RETURN
    # --------------------------------------------------------

    return {

        "results":
            results,

        "eligible_ids":
            eligible_ids,

        "rejected":
            rejected,
    }


# ============================================================
# PREDEFINED APPLICATION
# ============================================================

def calculate_mcdm_for_application(
    properties_df,
    applications_df,
    analysis_id
):
    """
    Calculate MCDM for A001-A006.
    """

    requirements = applications_df[
        applications_df["Analysis_ID"]
        == analysis_id
    ].copy()

    if requirements.empty:

        raise ValueError(
            f"Application '{analysis_id}' not found."
        )

    return calculate_mcdm(
        properties_df,
        requirements
    )


# ============================================================
# TEST ALL APPLICATIONS
# ============================================================

if __name__ == "__main__":

    from .loader import load_data

    data = load_data()

    # Your loader returns a dictionary
    polymers = data["polymers"]
    properties = data["properties"]
    sources = data["sources"]
    applications = data["applications"]

    print()
    print("=" * 70)
    print(
        "INTELLIGENT POLYMER MATERIAL "
        "SELECTION - MCDM TEST"
    )
    print("=" * 70)

    # --------------------------------------------------------
    # SHOW PROPERTY COLUMNS
    # --------------------------------------------------------

    print("\nProperty columns detected:")
    print(
        list(properties.columns)
    )

    # --------------------------------------------------------
    # TEST ALL APPLICATIONS
    # --------------------------------------------------------

    for analysis_id in sorted(
        applications[
            "Analysis_ID"
        ].unique()
    ):

        print()
        print("-" * 70)
        print(
            f"Application: {analysis_id}"
        )
        print("-" * 70)

        try:

            result = calculate_mcdm_for_application(
                properties,
                applications,
                analysis_id
            )

            print(
                "Eligible Materials: "
                f"{len(result['eligible_ids'])}"
            )

            print(
                "Rejected Materials: "
                f"{len(result['rejected'])}"
            )

            if not result["results"]:

                print(
                    "No eligible materials found."
                )

                continue

            print("\nRanking:")

            for item in result["results"]:

                print(
                    f"{item['rank']}. "
                    f"{item['polymer_id']} "
                    f"-> "
                    f"{item['mcdm_score']:.4f}"
                )

        except Exception as error:

            print(
                f"ERROR for {analysis_id}: "
                f"{error}"
            )

    print()
    print("=" * 70)
    print("MCDM TEST COMPLETED")
    print("=" * 70)