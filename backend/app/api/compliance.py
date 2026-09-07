from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_user

from app.models.user import User
from app.models.inspection import Inspection

from app.services.compliance_evaluator import (
    evaluate_inspection,
)


router = APIRouter(
    tags=["Compliance"]
)


@router.post(
    "/inspections/{inspection_id}/evaluate"
)
def evaluate_inspection_compliance(
    inspection_id: int,
    current_user: User = Depends(
        get_current_user
    ),
    db: Session = Depends(get_db),
):
    # --------------------------------------------------------
    # Verify inspection ownership
    # --------------------------------------------------------

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

    # --------------------------------------------------------
    # Run compliance evaluation
    # --------------------------------------------------------

    try:
        result = evaluate_inspection(
            db=db,
            inspection_id=inspection_id,
        )

        return result

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        )

    except Exception as exc:
        db.rollback()

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=(
                "Compliance evaluation failed: "
                f"{str(exc)}"
            ),
        )


@router.get(
    "/inspections/{inspection_id}/findings"
)
def get_compliance_findings(
    inspection_id: int,
    current_user: User = Depends(
        get_current_user
    ),
    db: Session = Depends(get_db),
):
    from app.models.compliance_finding import (
        ComplianceFinding
    )

    # --------------------------------------------------------
    # Verify inspection ownership
    # --------------------------------------------------------

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

    findings = (
        db.query(ComplianceFinding)
        .filter(
            ComplianceFinding.inspection_id
            == inspection_id
        )
        .order_by(
            ComplianceFinding.id.asc()
        )
        .all()
    )

    return {
        "inspection_id": inspection.id,
        "inspection_number": (
            inspection.inspection_number
        ),
        "count": len(findings),
        "findings": [
            {
                "id": finding.id,
                "rule_number": (
                    finding.rule_number
                ),
                "sub_rule": (
                    finding.sub_rule
                ),
                "requirement_code": (
                    finding.requirement_code
                ),
                "result": (
                    finding.result
                ),
                "confidence": (
                    finding.confidence
                ),
                "evidence_type": (
                    finding.evidence_type
                ),
                "observed_value": (
                    finding.observed_value
                ),
                "expected_value": (
                    finding.expected_value
                ),
                "reason": (
                    finding.reason
                ),
                "legal_version_code": (
                    finding.legal_version_code
                ),
                "legal_effective_date": (
                    finding.legal_effective_date
                ),
                "source_reference": (
                    finding.source_reference
                ),
                "created_at": (
                    finding.created_at
                ),
            }
            for finding in findings
        ],
    }