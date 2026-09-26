"""
explanation.py

Dynamic comparative engineering explanation engine for the
Intelligent Polymer Material Selection and Recommendation System.

This module does NOT make a new recommendation. It explains the
recommendation already produced by the MCDM engine.

Inputs:
    - polymer properties DataFrame
    - requirement DataFrame
    - MCDM result for all eligible materials
    - selected/recommended polymer

Output:
    Structured, data-driven engineering explanation suitable for
    a React frontend.
"""

import math
import pandas as pd

from .constraints import (
    HIGHER_IS_BETTER,
    LOWER_IS_BETTER,
    LEVEL_MAPPING,
    satisfies_requirement,
)


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

DISPLAY_NAMES = {
    "Tensile_Strength": "Tensile Strength",
    "Tensile_Modulus": "Tensile Modulus",
    "Impact_Strength": "Impact Strength",
    "Max_Service_Temperature": "Maximum Service Temperature",
    "Melting_or_Softening_Temperature": "Melting / Softening Temperature",
    "Density": "Density",
    "Water_Absorption": "Water Absorption",
    "Chemical_Resistance": "Chemical Resistance",
    "Wear_Resistance": "Wear Resistance",
    "UV_Resistance": "UV Resistance",
    "Heat_Resistance": "Heat Resistance",
    "Optical_Transparency": "Optical Transparency",
    "Cost_Category": "Cost Category",
    "Injection_Molding_Suitability": "Injection Molding Suitability",
}


def _clean(value):
    if value is None:
        return None
    try:
        if pd.isna(value):
            return None
    except Exception:
        pass
    return value


def _is_missing(value):
    value = _clean(value)
    if value is None:
        return True
    if isinstance(value, str) and value.strip().lower() in {"", "n/a", "na", "nan", "none", "null"}:
        return True
    return False


def _fmt(value):
    value = _clean(value)
    if value is None:
        return "not available"

    if isinstance(value, float):
        if math.isnan(value):
            return "not available"
        if value.is_integer():
            return str(int(value))
        return f"{value:.4g}"

    return str(value)


def _unit(requirement):
    unit = requirement.get("Required_Unit", requirement.get("required_unit", ""))
    unit = _clean(unit)
    if unit is None:
        return ""
    text = str(unit).strip()
    return "" if text.lower() in {"nan", "none", "null"} else text


def _hard(requirement):
    value = str(requirement.get("Hard_Constraint", "")).strip().lower()
    return value in {"yes", "true", "1"}


def _weight(requirement):
    try:
        return float(requirement.get("Weight", 0))
    except (TypeError, ValueError):
        return 0.0


def _display_property(name):
    return DISPLAY_NAMES.get(name, name.replace("_", " "))


def _actual_value(polymer_row, property_name):
    column = PROPERTY_COLUMN_MAP.get(property_name, property_name)
    if column not in polymer_row.index:
        return None
    return _clean(polymer_row[column])


def _status(actual, required, property_name):
    if _is_missing(actual):
        return "unavailable"

    try:
        return "pass" if satisfies_requirement(
            property_name, actual, required
        ) else "fail"
    except Exception:
        return "pass" if str(actual).strip().lower() == str(required).strip().lower() else "fail"


def _direction(property_name):
    if property_name in LOWER_IS_BETTER:
        return "lower"
    return "higher"


def _comparison_sentence(property_name, actual, required, status):
    name = _display_property(property_name)
    actual_text = _fmt(actual)
    required_text = _fmt(required)

    if status == "unavailable":
        return f"{name} could not be compared because the material value is not available."

    direction = _direction(property_name)

    if property_name == "Cost_Category":
        if status == "pass":
            return (
                f"{name} is {actual_text} against the required {required_text} "
                f"category, so the cost requirement is satisfied."
            )
        return (
            f"{name} is {actual_text} against the required {required_text} "
            f"category, making cost a disadvantage for this material."
        )

    if property_name in HIGHER_IS_BETTER:
        if status == "pass":
            return (
                f"{name} is {actual_text} against a required minimum of "
                f"{required_text}, so the material meets or exceeds the target."
            )
        return (
            f"{name} is {actual_text} against a required minimum of "
            f"{required_text}, so the target is not met."
        )

    if direction == "lower":
        if status == "pass":
            return (
                f"{name} is {actual_text} against a required maximum of "
                f"{required_text}, so the material is within the target."
            )
        return (
            f"{name} is {actual_text} against a required maximum of "
            f"{required_text}, so the target is exceeded."
        )

    return f"{name} is {actual_text} against the required value {required_text}."


def _property_difference_text(property_name, recommended_actual, other_actual):
    if _is_missing(recommended_actual) or _is_missing(other_actual):
        return None

    if property_name == "Cost_Category":
        try:
            rec = LEVEL_MAPPING.get(str(recommended_actual).strip().lower())
            other = LEVEL_MAPPING.get(str(other_actual).strip().lower())
            if rec is None or other is None or rec == other:
                return None
            if rec < other:
                return "lower cost"
            return "higher cost"
        except Exception:
            return None

    try:
        rec = float(recommended_actual)
        other = float(other_actual)
        if rec == other:
            return None

        if property_name in LOWER_IS_BETTER:
            return "lower value" if rec < other else "higher value"

        return "higher value" if rec > other else "lower value"
    except (TypeError, ValueError):
        rec_text = str(recommended_actual).strip().lower()
        other_text = str(other_actual).strip().lower()

        rec_level = LEVEL_MAPPING.get(rec_text)
        other_level = LEVEL_MAPPING.get(other_text)

        if rec_level is not None and other_level is not None:
            if rec_level > other_level:
                return "higher level"
            if rec_level < other_level:
                return "lower level"

    return None


def _make_requirement_analysis(polymer_row, requirement, result):
    property_name = str(
        requirement.get("Property_Name", requirement.get("property_name", ""))
    ).strip()

    required = requirement.get(
        "Required_Value", requirement.get("required_value")
    )
    actual = _actual_value(polymer_row, property_name)

    criterion_scores = result.get("criterion_scores", {})
    contributions = result.get("weighted_contributions", {})

    score = criterion_scores.get(property_name)
    contribution = contributions.get(property_name)

    status = _status(actual, required, property_name)
    hard = _hard(requirement)

    if hard and status == "pass":
        constraint_result = "mandatory requirement satisfied"
    elif hard and status == "fail":
        constraint_result = "mandatory requirement failed"
    elif hard:
        constraint_result = "mandatory requirement could not be evaluated"
    elif status == "pass":
        constraint_result = "preferred requirement satisfied"
    elif status == "fail":
        constraint_result = "preferred requirement not satisfied"
    else:
        constraint_result = "preferred requirement could not be evaluated"

    return {
        "property": property_name,
        "display_name": _display_property(property_name),
        "required_value": _clean(required),
        "actual_value": actual,
        "unit": _unit(requirement),
        "constraint_type": "Hard" if hard else "Soft",
        "status": status,
        "constraint_result": constraint_result,
        "criterion_score": score,
        "weight": round(_weight(requirement), 4),
        "weighted_contribution": contribution,
        "analysis": _comparison_sentence(
            property_name, actual, required, status
        ),
    }


def _requirement_phrase(property_name, actual, required, status):
    """Create a concise, human-readable requirement statement."""
    name = _display_property(property_name)
    actual_text = _fmt(actual)
    required_text = _fmt(required)

    if status == "unavailable":
        return f"{name} data is not available for this material"

    if property_name == "Cost_Category":
        if status == "pass":
            return f"the {name.lower()} is {actual_text}, meeting the preferred {required_text} category"
        return f"the {name.lower()} is {actual_text}, above the preferred {required_text} category"

    if property_name in LOWER_IS_BETTER:
        if status == "pass":
            return f"{name} is {actual_text}, within the required maximum of {required_text}"
        return f"{name} is {actual_text}, above the required maximum of {required_text}"

    if property_name in HIGHER_IS_BETTER:
        if status == "pass":
            return f"{name} is {actual_text}, meeting or exceeding the required minimum of {required_text}"
        return f"{name} is {actual_text}, below the required minimum of {required_text}"

    if status == "pass":
        return f"{name} is {actual_text}, meeting the required {required_text} level"
    return f"{name} is {actual_text}, below the required {required_text} level"


def _build_concise_rationale(rec_id, recommended_result, requirement_analysis, rec_score):
    """Build a concise 5-sentence engineering rationale without weights."""
    valid = [item for item in requirement_analysis if item["status"] != "unavailable"]
    passed = [item for item in valid if item["status"] == "pass"]
    failed = [item for item in valid if item["status"] == "fail"]

    # Prioritize hard requirements, then the highest-weight criteria, while
    # keeping the explanation short and representative of the actual inputs.
    prioritized = sorted(
        valid,
        key=lambda item: (
            1 if item["constraint_type"] == "Hard" else 0,
            float(item.get("weight") or 0),
        ),
        reverse=True,
    )
    highlights = prioritized[:3]
    highlight_text = "; ".join(
        _requirement_phrase(
            item["property"],
            item["actual_value"],
            item["required_value"],
            item["status"],
        )
        for item in highlights
    )

    if highlights:
        first_sentence = (
            f"{rec_id} is suitable for the specified application because "
            f"it provides the required performance across the key selected criteria."
        )
        second_sentence = f"In particular, {highlight_text}."
    else:
        first_sentence = (
            f"{rec_id} is the selected material based on the available engineering criteria."
        )
        second_sentence = "The available property data did not provide enough detail for a more specific comparison."

    if failed:
        tradeoff_names = [_display_property(item["property"]) for item in failed[:2]]
        if len(tradeoff_names) == 1:
            tradeoff_text = tradeoff_names[0]
        else:
            tradeoff_text = " and ".join(tradeoff_names)
        third_sentence = (
            f"The main trade-off is {tradeoff_text}, which does not fully meet the preferred target "
            f"and reduces the overall MCDM score."
        )
    elif len(passed) == len(valid) and valid:
        third_sentence = (
            "The material meets all available selected targets, with the final result determined by "
            "the combined performance of the criteria."
        )
    else:
        third_sentence = (
            "The final result reflects the combined performance of the available selected criteria."
        )

    fourth_sentence = (
        "These properties indicate that the material can address the engineering demands represented "
        "by the selected application requirements."
    )
    fifth_sentence = (
        f"Considering all selected criteria together, the MCDM evaluation gives {rec_id} a score of "
        f"{rec_score:.4f} and Rank #{recommended_result.get('rank')}."
    )

    return " ".join(
        [first_sentence, second_sentence, third_sentence, fourth_sentence, fifth_sentence]
    )


def _build_key_observation(rec_id, requirement_analysis, rec_score):
    valid = [item for item in requirement_analysis if item["status"] != "unavailable"]
    failed = [item for item in valid if item["status"] == "fail"]

    if failed:
        names = [_display_property(item["property"]) for item in failed[:2]]
        if len(names) == 1:
            limiting = names[0]
        else:
            limiting = " and ".join(names)
        return f"{rec_id} meets the key requirements overall, while {limiting} is the main factor limiting its MCDM score."

    if valid:
        # Identify the strongest criterion by actual contribution, if available.
        strongest = max(
            valid,
            key=lambda item: float(item.get("weighted_contribution") or 0),
        )
        return (
            f"{rec_id} meets the selected requirements overall, with "
            f"{_display_property(strongest['property'])} providing one of the strongest contributions to the final score."
        )

    return f"{rec_id} was selected from the available materials with an MCDM score of {rec_score:.4f}."


def generate_engineering_explanation(
    recommended_result,
    all_results,
    properties_df,
    requirements_df,
    top_alternatives=3,
):
    """Generate a concise, data-driven engineering explanation."""
    if requirements_df is None or requirements_df.empty:
        raise ValueError("Requirements are required for explanation.")

    rec_id = str(recommended_result.get("polymer_id")).strip()
    polymer_match = properties_df[
        properties_df["Polymer_ID"].astype(str).str.strip() == rec_id
    ]
    if polymer_match.empty:
        raise ValueError(f"Polymer '{rec_id}' not found in property data.")

    polymer_row = polymer_match.iloc[0]
    requirement_analysis = [
        _make_requirement_analysis(polymer_row, requirement, recommended_result)
        for _, requirement in requirements_df.iterrows()
    ]

    rec_score = float(recommended_result.get("mcdm_score", 0))
    hard_items = [item for item in requirement_analysis if item["constraint_type"] == "Hard"]
    failed_hard = [item for item in hard_items if item["status"] != "pass"]

    if failed_hard:
        overall_suitability = "Not eligible"
        overall_statement = "The material does not satisfy all mandatory requirements."
    elif rec_score >= 0.75:
        overall_suitability = "High"
        overall_statement = "The material achieves a strong overall MCDM score across the selected criteria."
    elif rec_score >= 0.50:
        overall_suitability = "Moderate"
        overall_statement = "The material remains eligible but has meaningful trade-offs across the selected criteria."
    else:
        overall_suitability = "Lower"
        overall_statement = "The material remains eligible, but its combined criterion performance produces a lower MCDM score."

    why_suitable = _build_concise_rationale(
        rec_id, recommended_result, requirement_analysis, rec_score
    )
    key_observation = _build_key_observation(
        rec_id, requirement_analysis, rec_score
    )

    return {
        "recommended_polymer_id": rec_id,
        "rank": recommended_result.get("rank"),
        "mcdm_score": round(rec_score, 4),
        "overall_suitability": overall_suitability,
        "overall_statement": overall_statement,
        "why_this_material_is_suitable": why_suitable,
        "key_observation": key_observation,
        # Retain the structured fields for backward compatibility with stored
        # records/API consumers, but the frontend does not display them.
        "hard_constraint_summary": None,
        "requirement_analysis": requirement_analysis,
        "strongest_factors": [],
        "trade_offs": [],
        "alternative_comparison": [],
        "final_summary": why_suitable,
    }

def add_explanations_to_results(
    results,
    properties_df,
    requirements_df,
    all_results=None,
):
    """
    Add engineering_explanation to every returned recommendation.

    all_results should preferably be the complete eligible MCDM result list,
    so the comparison is not limited to the displayed top-N.
    """
    complete_results = all_results or results
    enriched = []

    for result in results:
        explanation = generate_engineering_explanation(
            recommended_result=result,
            all_results=complete_results,
            properties_df=properties_df,
            requirements_df=requirements_df,
        )

        enriched_result = dict(result)
        enriched_result["engineering_explanation"] = explanation
        enriched.append(enriched_result)

    return enriched
