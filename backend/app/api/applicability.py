from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_user

from app.models.user import User
from app.models.inspection import Inspection
from app.models.applicability import Applicability
from app.models.product_classification import ProductClassification

from app.services.applicability_service import classify_applicability


router = APIRouter(tags=["Applicability"])


# =========================================================
# REQUEST MODEL
# =========================================================

class ApplicabilityRequest(BaseModel):
    """
    Applicability is now derived automatically from
    ProductClassification.

    No manual commodity/package input is required.
    """
    pass


# =========================================================
# POST - DETERMINE APPLICABILITY
# =========================================================

@router.post("/inspections/{inspection_id}/applicability")
def create_applicability(
    inspection_id: int,
    payload: ApplicabilityRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    # -----------------------------------------------------
    # 1. Verify inspection belongs to logged-in officer
    # -----------------------------------------------------

    inspection = (
        db.query(Inspection)
        .filter(
            Inspection.id == inspection_id,
            Inspection.officer_id == current_user.id,
        )
        .first()
    )

    if not inspection:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Inspection not found",
        )

    # -----------------------------------------------------
    # 2. Get automatic product classification
    # -----------------------------------------------------

    classification = (
        db.query(ProductClassification)
        .filter(
            ProductClassification.inspection_id == inspection_id
        )
        .first()
    )

    if not classification:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                "Product classification not found. "
                "Run product classification before applicability analysis."
            ),
        )

    # -----------------------------------------------------
    # 3. Make sure classification is usable
    # -----------------------------------------------------

    if classification.status == "INCONCLUSIVE":
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=(
                "Product classification is inconclusive. "
                "Additional product evidence is required."
            ),
        )

    # -----------------------------------------------------
    # 4. Run applicability engine
    # -----------------------------------------------------

    try:
        result = classify_applicability(
            inspection_type=inspection.inspection_type,
            commodity_category=classification.commodity_category,
            package_type=classification.package_type,
            is_imported=classification.is_imported,
            is_multi_piece=classification.is_multi_piece,
            is_combination=classification.is_combination,
            is_group_package=classification.is_group_package,
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        )

    # -----------------------------------------------------
    # 5. Check existing applicability
    # -----------------------------------------------------

    existing = (
        db.query(Applicability)
        .filter(
            Applicability.inspection_id == inspection_id
        )
        .first()
    )

    # -----------------------------------------------------
    # 6. Update existing result
    # -----------------------------------------------------

    if existing:

        existing.inspection_type = (
            inspection.inspection_type
        )

        existing.commodity_category = (
            classification.commodity_category
        )

        existing.package_type = (
            classification.package_type
        )

        existing.is_imported = (
            classification.is_imported
        )

        existing.is_multi_piece = (
            classification.is_multi_piece
        )

        existing.is_combination = (
            classification.is_combination
        )

        existing.is_group_package = (
            classification.is_group_package
        )

        existing.exemption_status = (
            result["exemption_status"]
        )

        existing.exemption_reason = (
            result["exemption_reason"]
        )

        existing.rule_version = (
            result["rule_version"]
        )

        existing.applicable_provisions = str(
            result["applicable_provisions"]
        )

        existing.classification_confidence = (
            classification.confidence
        )

        existing.classification_status = (
            classification.status
        )

        db.commit()
        db.refresh(existing)

        applicability = existing

    # -----------------------------------------------------
    # 7. Create new result
    # -----------------------------------------------------

    else:

        applicability = Applicability(
            inspection_id=inspection.id,

            inspection_type=(
                inspection.inspection_type
            ),

            commodity_category=(
                classification.commodity_category
            ),

            package_type=(
                classification.package_type
            ),

            is_imported=(
                classification.is_imported
            ),

            is_multi_piece=(
                classification.is_multi_piece
            ),

            is_combination=(
                classification.is_combination
            ),

            is_group_package=(
                classification.is_group_package
            ),

            exemption_status=(
                result["exemption_status"]
            ),

            exemption_reason=(
                result["exemption_reason"]
            ),

            rule_version=(
                result["rule_version"]
            ),

            applicable_provisions=str(
                result["applicable_provisions"]
            ),

            classification_confidence=(
                classification.confidence
            ),

            classification_status=(
                classification.status
            ),
        )

        db.add(applicability)
        db.commit()
        db.refresh(applicability)

    # -----------------------------------------------------
    # 8. Return result
    # -----------------------------------------------------

    return {
        "message": "Applicability classification completed",

        "inspection_id": inspection.id,

        "inspection_number": (
            inspection.inspection_number
        ),

        "source_classification": {
            "commodity_category": (
                classification.commodity_category
            ),

            "package_type": (
                classification.package_type
            ),

            "is_imported": (
                classification.is_imported
            ),

            "is_multi_piece": (
                classification.is_multi_piece
            ),

            "is_combination": (
                classification.is_combination
            ),

            "is_group_package": (
                classification.is_group_package
            ),

            "confidence": (
                classification.confidence
            ),

            "status": (
                classification.status
            ),
        },

        "applicability": {
            "id": applicability.id,

            "inspection_type": (
                applicability.inspection_type
            ),

            "commodity_category": (
                applicability.commodity_category
            ),

            "package_type": (
                applicability.package_type
            ),

            "is_imported": (
                applicability.is_imported
            ),

            "is_multi_piece": (
                applicability.is_multi_piece
            ),

            "is_combination": (
                applicability.is_combination
            ),

            "is_group_package": (
                applicability.is_group_package
            ),

            "exemption_status": (
                applicability.exemption_status
            ),

            "exemption_reason": (
                applicability.exemption_reason
            ),

            "rule_version": (
                applicability.rule_version
            ),

            "applicable_provisions": (
                applicability.applicable_provisions
            ),

            "classification_confidence": (
                applicability.classification_confidence
            ),

            "classification_status": (
                applicability.classification_status
            ),
        },
    }


# =========================================================
# GET - RETRIEVE APPLICABILITY
# =========================================================

@router.get("/inspections/{inspection_id}/applicability")
def get_applicability(
    inspection_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    # -----------------------------------------------------
    # 1. Verify inspection
    # -----------------------------------------------------

    inspection = (
        db.query(Inspection)
        .filter(
            Inspection.id == inspection_id,
            Inspection.officer_id == current_user.id,
        )
        .first()
    )

    if not inspection:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Inspection not found",
        )

    # -----------------------------------------------------
    # 2. Get applicability
    # -----------------------------------------------------

    applicability = (
        db.query(Applicability)
        .filter(
            Applicability.inspection_id == inspection_id
        )
        .first()
    )

    if not applicability:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Applicability classification not found",
        )

    # -----------------------------------------------------
    # 3. Return stored result
    # -----------------------------------------------------

    return {
        "inspection_id": inspection.id,

        "inspection_number": (
            inspection.inspection_number
        ),

        "applicability": {
            "id": applicability.id,

            "inspection_type": (
                applicability.inspection_type
            ),

            "commodity_category": (
                applicability.commodity_category
            ),

            "package_type": (
                applicability.package_type
            ),

            "is_imported": (
                applicability.is_imported
            ),

            "is_multi_piece": (
                applicability.is_multi_piece
            ),

            "is_combination": (
                applicability.is_combination
            ),

            "is_group_package": (
                applicability.is_group_package
            ),

            "exemption_status": (
                applicability.exemption_status
            ),

            "exemption_reason": (
                applicability.exemption_reason
            ),

            "rule_version": (
                applicability.rule_version
            ),

            "applicable_provisions": (
                applicability.applicable_provisions
            ),

            "classification_confidence": (
                applicability.classification_confidence
            ),

            "classification_status": (
                applicability.classification_status
            ),
        },
    }