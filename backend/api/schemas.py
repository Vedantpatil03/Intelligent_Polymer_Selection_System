from typing import Any, List, Union

from pydantic import BaseModel, Field
from pydantic import EmailStr, field_validator


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


class RegisterRequest(BaseModel):
    email: EmailStr
    display_name: str = Field(..., min_length=1, max_length=80)
    organization: str | None = Field(default=None, max_length=120)
    password: str = Field(..., min_length=8, max_length=128)

    @field_validator("display_name")
    @classmethod
    def display_name_not_blank(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("Name cannot be blank.")
        return value

    @field_validator("organization")
    @classmethod
    def organization_optional(cls, value: str | None) -> str | None:
        if value is None:
            return None
        value = value.strip()
        return value or None


class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=1, max_length=128)


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
