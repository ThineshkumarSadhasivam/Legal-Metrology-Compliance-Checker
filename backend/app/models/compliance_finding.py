from datetime import datetime

from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, String, Text

from app.core.database import Base


class ComplianceFinding(Base):
    __tablename__ = "compliance_findings"

    id = Column(Integer, primary_key=True, index=True)

    inspection_id = Column(
        Integer,
        ForeignKey("inspections.id"),
        nullable=False,
        index=True,
    )

    rule_requirement_id = Column(
        Integer,
        ForeignKey("rule_requirements.id"),
        nullable=True,
        index=True,
    )

    # Audit snapshot
    legal_version_code = Column(
        String(100),
        nullable=True,
    )

    legal_effective_date = Column(
        String(20),
        nullable=True,
    )

    rule_number = Column(
        String(30),
        nullable=False,
    )

    sub_rule = Column(
        String(30),
        nullable=True,
    )

    requirement_code = Column(
        String(150),
        nullable=False,
    )

    # COMPLIANT / VIOLATION / INCONCLUSIVE / NOT_APPLICABLE
    result = Column(
        String(30),
        nullable=False,
        index=True,
    )

    confidence = Column(
        Float,
        nullable=True,
    )

    evidence_type = Column(
        String(100),
        nullable=True,
    )

    # JSON string containing OCR/declaration/image references
    evidence_reference = Column(
        Text,
        nullable=True,
    )

    observed_value = Column(
        Text,
        nullable=True,
    )

    expected_value = Column(
        Text,
        nullable=True,
    )

    reason = Column(
        Text,
        nullable=False,
    )

    source_reference = Column(
        Text,
        nullable=True,
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
    )