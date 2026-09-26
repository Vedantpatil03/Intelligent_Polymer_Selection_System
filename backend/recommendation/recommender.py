"""
recommender.py

Recommendation layer with dynamic comparative engineering
explanations.

IMPORTANT:
- The existing MCDM logic remains unchanged.
- Custom UI does NOT expose weights.
- Custom requirements receive automatic internal weights.
- Explanation is generated after MCDM ranking.
"""

import pandas as pd

from .mcdm import (
    calculate_mcdm,
    calculate_mcdm_for_application,
)
from .explanation import add_explanations_to_results


SUPPORTED_PROPERTIES = {
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
    "Density",
    "Water_Absorption",
    "Cost_Category",
}


def validate_top_n(top_n):
    try:
        top_n = int(top_n)
    except (ValueError, TypeError):
        raise ValueError("top_n must be an integer.")

    if top_n <= 0:
        raise ValueError("top_n must be greater than zero.")

    return top_n


def recommend_materials(
    properties,
    applications,
    analysis_id,
    top_n=5,
):
    top_n = validate_top_n(top_n)

    analysis_id = str(analysis_id).strip()

    application_rows = applications[
        applications["Analysis_ID"].astype(str).str.strip()
        == analysis_id
    ]

    if application_rows.empty:
        raise ValueError(
            f"Application '{analysis_id}' not found."
        )

    application_name = str(
        application_rows["Application_Name"].iloc[0]
    ).strip()

    # Existing MCDM calculation.
    mcdm_result = calculate_mcdm_for_application(
        properties,
        applications,
        analysis_id,
    )

    all_ranked_results = mcdm_result["results"]

    recommendations = all_ranked_results[:top_n]

    # Requirements used by this predefined application.
    requirements_df = application_rows.copy()

    # Normalize predefined weight column so the explanation module
    # can use either the CSV/MongoDB Weight_Percentage field or Weight.
    if "Weight" not in requirements_df.columns:
        if "Weight_Percentage" in requirements_df.columns:
            requirements_df["Weight"] = pd.to_numeric(
                requirements_df["Weight_Percentage"],
                errors="coerce",
            )
        else:
            requirements_df["Weight"] = 0.0

    # Generate explanations using ALL eligible materials, not only top-N.
    recommendations = add_explanations_to_results(
        recommendations,
        properties_df=properties,
        requirements_df=requirements_df,
        all_results=all_ranked_results,
    )

    return {
        "analysis_id": analysis_id,
        "application_name": application_name,
        "total_eligible": len(mcdm_result["eligible_ids"]),
        "recommendations": recommendations,
        "rejected_count": len(mcdm_result["rejected"]),
        "rejected_polymers": mcdm_result["rejected"],
    }


def recommend_custom_materials(
    properties,
    requirements,
    application_name="Custom Material Selection",
    top_n=5,
):
    top_n = validate_top_n(top_n)

    if isinstance(requirements, list):
        requirements_df = pd.DataFrame(requirements)
    elif isinstance(requirements, pd.DataFrame):
        requirements_df = requirements.copy()
    else:
        raise ValueError(
            "Requirements must be a list or pandas DataFrame."
        )

    if requirements_df.empty:
        raise ValueError(
            "At least one requirement is required."
        )

    required_columns = {
        "Property_Name",
        "Required_Value",
        "Hard_Constraint",
    }

    missing = required_columns - set(requirements_df.columns)

    if missing:
        raise ValueError(
            f"Missing requirement columns: {sorted(missing)}"
        )

    requirements_df["Property_Name"] = (
        requirements_df["Property_Name"]
        .astype(str)
        .str.strip()
    )

    if requirements_df["Property_Name"].duplicated().any():
        duplicates = (
            requirements_df[
                requirements_df["Property_Name"].duplicated(keep=False)
            ]["Property_Name"]
            .unique()
            .tolist()
        )

        raise ValueError(
            "Duplicate properties are not allowed: "
            f"{duplicates}"
        )

    invalid_properties = (
        set(requirements_df["Property_Name"])
        - SUPPORTED_PROPERTIES
    )

    if invalid_properties:
        raise ValueError(
            "Unsupported properties: "
            f"{sorted(invalid_properties)}"
        )

    valid_hard_values = {
        "yes",
        "no",
        "true",
        "false",
        "1",
        "0",
    }

    normalized_hard = (
        requirements_df["Hard_Constraint"]
        .astype(str)
        .str.strip()
        .str.lower()
    )

    invalid_hard = set(normalized_hard) - valid_hard_values

    if invalid_hard:
        raise ValueError(
            "Hard_Constraint must contain Yes/No or True/False values."
        )

    requirements_df["Hard_Constraint"] = normalized_hard.map(
        lambda value:
            "Yes"
            if value in {"yes", "true", "1"}
            else "No"
    )

    # ------------------------------------------------------------
    # INTERNAL MCDM WEIGHTS
    # ------------------------------------------------------------
    # Weight is NOT entered by the user.
    # For custom selection, requirements are equally weighted.
    number_of_requirements = len(requirements_df)
    requirements_df["Weight"] = 100.0 / number_of_requirements

    application_name = str(application_name).strip()

    if not application_name:
        application_name = "Custom Material Selection"

    # Existing MCDM calculation.
    mcdm_result = calculate_mcdm(
        properties,
        requirements_df,
    )

    all_ranked_results = mcdm_result["results"]

    recommendations = all_ranked_results[:top_n]

    # Dynamic comparative explanation.
    recommendations = add_explanations_to_results(
        recommendations,
        properties_df=properties,
        requirements_df=requirements_df,
        all_results=all_ranked_results,
    )

    return {
        "analysis_id": None,
        "application_name": application_name,
        "total_eligible": len(mcdm_result["eligible_ids"]),
        "recommendations": recommendations,
        "rejected_count": len(mcdm_result["rejected"]),
        "rejected_polymers": mcdm_result["rejected"],
    }
