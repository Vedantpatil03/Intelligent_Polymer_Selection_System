from typing import Any, List, Union

from pydantic import BaseModel, Field


# ============================================================
# PREDEFINED RECOMMENDATION REQUEST
# ============================================================

class RecommendationRequest(BaseModel):

    analysis_id: str = Field(
        ...,
        description="Predefined application ID such as A001"
    )

    top_n: int = Field(
        default=5,
        ge=1,
        le=20,
        description="Number of recommendations to return"
    )


# ============================================================
# CUSTOM REQUIREMENT
# ============================================================

class CustomRequirement(BaseModel):

    property_name: str = Field(
        ...,
        description="Logical polymer property name"
    )

    required_value: Union[float, int, str] = Field(
        ...,
        description="Required property value"
    )

    hard_constraint: bool = Field(
        default=False,
        description="Whether this requirement is mandatory"
    )


# ============================================================
# CUSTOM RECOMMENDATION REQUEST
# ============================================================

class CustomRecommendationRequest(BaseModel):

    application_name: str = Field(
        default="Custom Material Selection",
        min_length=1,
        description="Name of the custom application"
    )

    requirements: List[CustomRequirement] = Field(
        ...,
        min_length=1,
        description="User-defined material requirements"
    )

    top_n: int = Field(
        default=5,
        ge=1,
        le=20,
        description="Number of recommendations to return"
    )


# ============================================================
# RECOMMENDATION ITEM
# ============================================================

class RecommendationItem(BaseModel):

    rank: int

    polymer_id: str

    mcdm_score: float

    criterion_scores: dict[str, float]

    weighted_contributions: dict[str, float]


# ============================================================
# REJECTED POLYMER
# ============================================================

class RejectedPolymer(BaseModel):

    polymer_id: str

    # constraints.py returns a list of failure strings
    failures: List[str]


# ============================================================
# RECOMMENDATION RESPONSE
# ============================================================

class RecommendationResponse(BaseModel):

    analysis_id: str | None

    application_name: str

    total_eligible: int

    recommendations: List[RecommendationItem]

    rejected_count: int

    rejected_polymers: List[RejectedPolymer]


# ============================================================
# APPLICATION INFORMATION
# ============================================================

class ApplicationInfo(BaseModel):

    analysis_id: str

    application_name: str


# ============================================================
# POLYMER INFORMATION
# ============================================================

class PolymerInfo(BaseModel):

    polymer_id: str

    polymer_name: str | None = None

    polymer_family: str | None = None

    manufacturer: str | None = None

    grade: str | None = None
