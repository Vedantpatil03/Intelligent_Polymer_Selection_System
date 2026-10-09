from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from bson import ObjectId

import math
import os
import json
from datetime import datetime

from recommendation.mongo_loader import load_data_from_mongodb

from recommendation.recommender import (
    recommend_materials,
    recommend_custom_materials,
    SUPPORTED_PROPERTIES,
)

from database.collections import (
    save_recommendation_history,
    get_recommendation_history,
    history_collection,
)

from api.schemas import (
    RecommendationRequest,
    CustomRecommendationRequest,
    RegisterRequest,
    LoginRequest,
)
from api.auth import (
    clear_session_cookie,
    get_current_user,
    hash_password,
    normalize_email,
    public_user,
    set_session_cookie,
    verify_password,
)
from database.collections import users_collection
from pymongo.errors import DuplicateKeyError


# ============================================================
# ROUTER
# ============================================================

router = APIRouter(dependencies=[Depends(get_current_user)])
auth_router = APIRouter(prefix="/auth")

_login_attempts = {}
_MAX_LOGIN_ATTEMPTS = 10
_LOGIN_WINDOW_SECONDS = 300


@auth_router.post("/register")
def register(request: RegisterRequest, response: Response):
    email = normalize_email(str(request.email))
    now = datetime.utcnow()
    try:
        user_id = users_collection.insert_one(
            {
                "email": email,
                "display_name": request.display_name.strip(),
                "organization": request.organization,
                "password_hash": hash_password(request.password),
                "created_at": now,
                "updated_at": now,
            }
        ).inserted_id
    except DuplicateKeyError:
        raise HTTPException(status_code=409, detail="An account with that email already exists.")

    user = users_collection.find_one({"_id": user_id})
    set_session_cookie(response, str(user_id))
    return {"user": public_user(user)}


@auth_router.post("/login")
def login(request: LoginRequest, response: Response, http_request: Request):
    now = datetime.utcnow().timestamp()
    key = f"{http_request.client.host if http_request.client else 'unknown'}:{normalize_email(str(request.email))}"
    attempts = [timestamp for timestamp in _login_attempts.get(key, []) if now - timestamp < _LOGIN_WINDOW_SECONDS]
    if len(attempts) >= _MAX_LOGIN_ATTEMPTS:
        raise HTTPException(status_code=429, detail="Too many login attempts. Please try again later.")
    attempts.append(now)
    _login_attempts[key] = attempts

    user = users_collection.find_one({"email": normalize_email(str(request.email))})
    if not user or not verify_password(request.password, user["password_hash"]):
        raise HTTPException(status_code=401, detail="Invalid email or password.")

    _login_attempts.pop(key, None)
    set_session_cookie(response, str(user["_id"]))
    return {"user": public_user(user)}


@auth_router.get("/me")
def me(user=Depends(get_current_user)):
    return {"user": public_user(user)}


@auth_router.post("/logout")
def logout(response: Response):
    clear_session_cookie(response)
    return {"message": "Logged out successfully."}


# ============================================================
# JSON-SAFE VALUE NORMALIZATION
# ============================================================

def make_json_safe(value):
    """Recursively convert NaN/Infinity and NumPy scalars to JSON-safe values."""
    if value is None:
        return None

    if isinstance(value, float):
        return value if math.isfinite(value) else None

    # NumPy scalar values (if present)
    if hasattr(value, "item") and callable(value.item):
        try:
            return make_json_safe(value.item())
        except (ValueError, TypeError):
            pass

    if isinstance(value, dict):
        return {str(key): make_json_safe(item) for key, item in value.items()}

    if isinstance(value, (list, tuple)):
        return [make_json_safe(item) for item in value]

    return value


# ============================================================
# LOAD DATA FROM MONGODB ATLAS
# ============================================================

DATA = load_data_from_mongodb()

polymers_df = DATA["polymers"]
properties_df = DATA["properties"]
sources_df = DATA["sources"]
applications_df = DATA["applications"]


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
# GET APPLICATIONS
# ============================================================

@router.get("/applications")
def get_applications():

    applications = (
        applications_df[
            [
                "Analysis_ID",
                "Application_Name",
            ]
        ]
        .drop_duplicates()
        .to_dict(orient="records")
    )

    return {
        "applications": applications
    }


# ============================================================
# GET POLYMERS
# ============================================================

@router.get("/polymers")
def get_polymers():

    # Always return Polymer_ID.
    columns = ["Polymer_ID"]

    # Polymer master-data fields.
    possible_columns = [
        "Polymer_Name",
        "Polymer_Family",
        "Material_Type",
        "Manufacturer",
        "Grade",
        "Common_Applications",
        "Processing_Method",
        "Processing",
        "Processing Method",
        "Recyclability",
        "Description",
    ]

    # Add only columns that actually exist in MongoDB.
    for column in possible_columns:

        if column in polymers_df.columns and column not in columns:
            columns.append(column)

    polymers = (
        polymers_df[
            columns
        ]
        .fillna("")
        .to_dict(orient="records")
    )

    # Normalize possible processing-column variations
    # to one frontend-friendly field.
    for polymer in polymers:

        if not polymer.get("Processing_Method"):

            if polymer.get("Processing"):
                polymer["Processing_Method"] = polymer["Processing"]

            elif polymer.get("Processing Method"):
                polymer["Processing_Method"] = polymer["Processing Method"]

            else:
                polymer["Processing_Method"] = ""

        # Remove alternate internal names from API response.
        polymer.pop("Processing", None)
        polymer.pop("Processing Method", None)

    return {
        "polymers": polymers
    }


# ============================================================
# GET SUPPORTED PROPERTIES
# ============================================================

@router.get("/properties")
def get_supported_properties():

    properties = []

    for property_name in sorted(
        SUPPORTED_PROPERTIES
    ):

        if property_name in PROPERTY_COLUMN_MAP:

            actual_column = PROPERTY_COLUMN_MAP[
                property_name
            ]

            if actual_column in properties_df.columns:

                properties.append(
                    {
                        "property_name": property_name,
                        "data_column": actual_column,
                    }
                )

    return {
        "properties": properties
    }


# ============================================================
# PREDEFINED RECOMMENDATION
# ============================================================

@router.post(
    "/recommend",
    response_model=None,
)
def recommend(
    request: RecommendationRequest,
    user=Depends(get_current_user),
):

    try:

        result = recommend_materials(
            properties_df,
            applications_df,
            request.analysis_id,
            request.top_n,
        )

        # ----------------------------------------------------
        # Save predefined recommendation to history
        # ----------------------------------------------------

        predefined_requirements = (
            applications_df[
                applications_df["Analysis_ID"]
                == result["analysis_id"]
            ]
            .fillna("")
            .to_dict(orient="records")
        )

        history_data = {
            "analysis_id": result["analysis_id"],
            "application_name": result["application_name"],
            "total_eligible": result["total_eligible"],
            "recommendations": result["recommendations"],
            "rejected_count": result["rejected_count"],
            "rejected_polymers": result["rejected_polymers"],
            "requirements": make_json_safe(
                predefined_requirements
            ),
        }

        history_id = save_recommendation_history(history_data, user["_id"])
        result["history_id"] = history_id

        return make_json_safe(result)

    except ValueError as error:

        raise HTTPException(
            status_code=400,
            detail=str(error),
        )

    except Exception as error:

        raise HTTPException(
            status_code=500,
            detail=(
                "Recommendation failed: "
                f"{str(error)}"
            ),
        )


# ============================================================
# CUSTOM RECOMMENDATION
# ============================================================

@router.post(
    "/recommend/custom",
    response_model=None,
)
def recommend_custom(
    request: CustomRecommendationRequest,
    user=Depends(get_current_user),
):

    try:

        # ----------------------------------------------------
        # Convert Pydantic request objects into the dictionary
        # format expected by recommend_custom_materials().
        #
        # getattr() is intentional here because the current
        # CustomRequirement schema may not define required_unit
        # and/or requirement_level.
        # ----------------------------------------------------

        requirements = []

        for item in request.requirements:

            requirement = {
                "Property_Name": item.property_name,
                "Required_Value": item.required_value,

                # Backward-compatible:
                # use empty string when this field is not
                # present in the current Pydantic schema.
                "Required_Unit": getattr(
                    item,
                    "required_unit",
                    "",
                ),

                # Backward-compatible:
                # use empty string when this field is not
                # present in the current Pydantic schema.
                "Requirement_Level": getattr(
                    item,
                    "requirement_level",
                    "",
                ),

                "Hard_Constraint": item.hard_constraint,
            }

            requirements.append(
                requirement
            )

        # ----------------------------------------------------
        # Run recommendation engine
        # ----------------------------------------------------

        result = recommend_custom_materials(
            properties_df,
            requirements,
            request.application_name,
            request.top_n,
        )

        # ----------------------------------------------------
        # Save custom recommendation to history
        # ----------------------------------------------------

        history_data = {
            "analysis_id": result.get(
                "analysis_id"
            ),
            "application_name": result[
                "application_name"
            ],
            "total_eligible": result[
                "total_eligible"
            ],
            "recommendations": result[
                "recommendations"
            ],
            "rejected_count": result[
                "rejected_count"
            ],
            "rejected_polymers": result[
                "rejected_polymers"
            ],
            "requirements": requirements,
        }

        history_id = save_recommendation_history(history_data, user["_id"])
        result["history_id"] = history_id

        return make_json_safe(result)

    except ValueError as error:

        raise HTTPException(
            status_code=400,
            detail=str(error),
        )

    except Exception as error:

        raise HTTPException(
            status_code=500,
            detail=(
                "Custom recommendation failed: "
                f"{str(error)}"
            ),
        )


# ============================================================
# RECOMMENDATION HISTORY
# ============================================================

@router.get("/history")
def get_history(user=Depends(get_current_user)):

    try:

        documents = list(
            history_collection.find({"user_id": user["_id"]}).sort(
                "created_at",
                -1
            )
        )

        history = []

        for document in documents:

            document["history_id"] = str(
                document.pop("_id")
            )
            document.pop("user_id", None)

            # Backward compatibility for history records created before
            # requirement details were stored. Predefined analyses can
            # recover their requirements from the application master data.
            stored_requirements = document.get("requirements")

            if (
                not isinstance(stored_requirements, list)
                or len(stored_requirements) == 0
            ) and document.get("analysis_id"):

                recovered_requirements = (
                    applications_df[
                        applications_df["Analysis_ID"]
                        == document["analysis_id"]
                    ]
                    .fillna("")
                    .to_dict(orient="records")
                )

                if recovered_requirements:
                    document["requirements"] = make_json_safe(
                        recovered_requirements
                    )

            history.append(document)

        history = make_json_safe(history)

        return {
            "history": history
        }

    except Exception as error:

        raise HTTPException(
            status_code=500,
            detail=(
                "Failed to retrieve recommendation "
                f"history: {str(error)}"
            ),
        )


# ============================================================
# DELETE RECOMMENDATION HISTORY
# ============================================================

@router.get("/history/{history_id}")
def get_history_record(history_id: str, user=Depends(get_current_user)):
    if not ObjectId.is_valid(history_id):
        raise HTTPException(status_code=400, detail="Invalid history record ID.")

    document = history_collection.find_one(
        {"_id": ObjectId(history_id), "user_id": user["_id"]}
    )
    if not document:
        raise HTTPException(status_code=404, detail="History record not found.")

    document["history_id"] = str(document.pop("_id"))
    document.pop("user_id", None)
    return make_json_safe(document)


@router.delete("/history")
def clear_history(user=Depends(get_current_user)):
    history_collection.delete_many({"user_id": user["_id"]})
    return {"message": "Your analysis history was cleared."}


@router.delete("/history/{history_id}")
def delete_history(history_id: str, user=Depends(get_current_user)):

    try:

        if not ObjectId.is_valid(history_id):
            raise HTTPException(
                status_code=400,
                detail="Invalid history record ID."
            )

        result = history_collection.delete_one(
            {"_id": ObjectId(history_id), "user_id": user["_id"]}
        )

        if result.deleted_count == 0:
            raise HTTPException(
                status_code=404,
                detail="History record not found."
            )

        return {
            "message": "Analysis history deleted successfully.",
            "history_id": history_id,
        }

    except HTTPException:
        raise

    except Exception as error:

        raise HTTPException(
            status_code=500,
            detail=(
                "Failed to delete recommendation "
                f"history: {str(error)}"
            ),
        )


# ============================================================
# GROQ AI ENGINEERING CHATBOT
# ============================================================

@router.post("/chat")
def polymer_chat(request: dict, user=Depends(get_current_user)):
    """Interactive engineering assistant powered by Groq.

    The deterministic MCDM engine remains the decision maker.
    Groq only explains the supplied project data and results.
    """
    try:
        message = str(request.get("message", "")).strip()
        if not message:
            raise HTTPException(status_code=400, detail="Message cannot be empty.")

        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            raise HTTPException(
                status_code=500,
                detail="GROQ_API_KEY is not configured on the backend server.",
            )

        from groq import Groq

        context = request.get("context") or {}
        history_id = context.get("history_id")
        if history_id and ObjectId.is_valid(history_id):
            owned_record = history_collection.find_one(
                {"_id": ObjectId(history_id), "user_id": user["_id"]}
            )
            if owned_record:
                context = {
                    **owned_record,
                    "history_id": history_id,
                    "type": "custom" if owned_record.get("requirements") else "predefined",
                }
        history = request.get("history") or []

        # If this is a predefined analysis, recover the exact
        # requirements from MongoDB when the frontend did not send them.
        if (
            context.get("type") == "predefined"
            and context.get("analysis_id")
            and not context.get("requirements")
        ):
            recovered = (
                applications_df[
                    applications_df["Analysis_ID"] == context["analysis_id"]
                ]
                .fillna("")
                .to_dict(orient="records")
            )
            context = {**context, "requirements": make_json_safe(recovered)}

        # Enrich recommendation context with authoritative polymer master data.
        # The frontend may send only Polymer_IDs, so resolve names and metadata
        # on the backend before asking Groq to explain anything.
        recommendation_items = context.get("recommendations") or []
        recommended_ids = []
        for item in recommendation_items:
            if isinstance(item, dict) and item.get("polymer_id"):
                recommended_ids.append(str(item["polymer_id"]))

        if recommended_ids and "Polymer_ID" in polymers_df.columns:
            polymer_rows = polymers_df[
                polymers_df["Polymer_ID"].astype(str).isin(recommended_ids)
            ].fillna("")

            polymer_details = []
            for row in polymer_rows.to_dict(orient="records"):
                details = {
                    "polymer_id": row.get("Polymer_ID", ""),
                }

                for field in [
                    "Polymer_Family",
                    "Polymer_Name",
                    "Material_Type",
                    "Manufacturer",
                    "Grade",
                    "Processing_Method",
                    "Processing",
                    "Processing Method",
                    "Recyclability",
                    "Common_Applications",
                    "Description",
                ]:
                    if field in row and row.get(field) not in (None, ""):
                        details[field] = row.get(field)

                # Normalize processing field for the AI context.
                if not details.get("Processing_Method"):
                    details["Processing_Method"] = (
                        details.get("Processing")
                        or details.get("Processing Method")
                        or ""
                    )

                details.pop("Processing", None)
                details.pop("Processing Method", None)
                polymer_details.append(details)

            context = {**context, "polymer_details": make_json_safe(polymer_details)}

        # Send only the decision data needed for an explanation. The raw
        # recommendation payload can contain long generated explanations and
        # otherwise exceed Groq's token-per-minute limit.
        recommendation_fields = {
            "rank",
            "polymer_id",
            "mcdm_score",
            "criterion_scores",
            "weighted_contributions",
            "explanation",
            "strengths",
            "limitations",
            "tradeoffs",
        }
        compact_recommendations = []
        for item in recommendation_items[:5]:
            if not isinstance(item, dict):
                continue
            compact_item = {
                key: item[key]
                for key in recommendation_fields
                if key in item
            }
            for key in ("explanation", "strengths", "limitations", "tradeoffs"):
                if isinstance(compact_item.get(key), str):
                    compact_item[key] = compact_item[key][:900]
            compact_recommendations.append(compact_item)

        compact_details = []
        for item in context.get("polymer_details", [])[:5]:
            if isinstance(item, dict):
                compact_details.append({
                    key: item[key]
                    for key in (
                        "polymer_id",
                        "Polymer_Family",
                        "Polymer_Name",
                        "Material_Type",
                        "Processing_Method",
                        "Recyclability",
                        "Common_Applications",
                        "Description",
                    )
                    if key in item
                })

        compact_context = {
            "analysis_id": context.get("analysis_id"),
            "application_name": context.get("application_name"),
            "total_eligible": context.get("total_eligible"),
            "rejected_count": context.get("rejected_count"),
            "requirements": (context.get("requirements") or [])[:14],
            "recommendations": compact_recommendations,
            "rejected_polymers": (context.get("rejected_polymers") or [])[:10],
            "polymer_details": compact_details,
        }
        context_text = json.dumps(
            make_json_safe(compact_context),
            ensure_ascii=True,
            separators=(",", ":"),
            default=str,
        )[:16000]

        safe_history = []
        for item in history[-4:]:
            if not isinstance(item, dict):
                continue
            role = item.get("role")
            content = item.get("content")
            if role in {"user", "assistant"} and isinstance(content, str):
                safe_history.append({"role": role, "content": content[:1200]})

        system_prompt = """You are the Polymer Engineering Assistant for an Intelligent Polymer Material Selection and Recommendation System.

Your role is to explain engineering results clearly and accurately. The deterministic Weighted MCDM engine is the decision maker; you must never change, override, recalculate incorrectly, invent, or recommend a different rank or score. Treat the supplied context as the project's factual data. If information is missing, say that it is not available rather than inventing it.

When discussing a selected material:
- Identify materials primarily by Polymer ID and Polymer_Family. If Polymer_Family is available, use it in the form "POL012 — PPS (Polyphenylene Sulfide)" and do not lead with Polymer_Name.
- If Polymer_Family is unavailable for a Polymer_ID, say exactly: "Polymer family information is not available in the current project data." Never infer a family from Polymer_Name.
- Treat questions such as "What is the polymer name?", "Which material is ranked first?", "What material was selected?", and "Tell me about the selected material" as requests for the Polymer ID and Polymer_Family. Mention Polymer_Name only when the user explicitly asks for the specific commercial grade or material name.
- Use the supplied MCDM score and rank exactly.
- Explain relevant property values by comparing them with the application's requirements.
- For comparison questions, identify each material as Polymer ID plus Polymer_Family, for example "POL012 (PPS)" or "POL012 — PPS (Polyphenylene Sulfide)". Use the supplied polymer_details plus recommendation scores/ranks and clearly separate factual differences from interpretation.
- Distinguish hard constraints from soft criteria when that information is supplied.
- Explain important strengths and trade-offs without changing the ranking.
- Do not claim aerospace, medical, automotive, food-contact, or other certification merely from an application name.
- Do not expose internal weight percentages or importance levels unless the user explicitly asks how MCDM works mathematically.
- If asked about MCDM, explain it conceptually and use supplied results; do not invent calculations.
- If asked about a polymer not present in the supplied context, clearly state that the current context does not contain enough project data for a project-specific answer.

Keep normal answers concise: about 3-7 sentences unless the user asks for more detail. Use simple engineering language suitable for a college project/viva."""

        user_prompt = f"""Current project context:
{context_text}

Conversation history:
{safe_history}

User question:
{message}

Answer using only the supplied project context for project-specific claims."""

        client = Groq(api_key=api_key)
        response = client.chat.completions.create(
            model=os.getenv("GROQ_MODEL", "openai/gpt-oss-20b"),
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            temperature=0.2,
            max_tokens=600,
        )

        answer = response.choices[0].message.content or "I could not generate an answer."
        return {
            "answer": answer,
            "model": os.getenv("GROQ_MODEL", "openai/gpt-oss-20b"),
        }

    except HTTPException:
        raise
    except Exception as error:
        raise HTTPException(
            status_code=502,
            detail=f"Groq chatbot failed: {str(error)}",
        )
