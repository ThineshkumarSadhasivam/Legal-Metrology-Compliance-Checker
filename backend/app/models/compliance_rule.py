from datetime import datetime

from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    Boolean,
    DateTime,
    ForeignKey,
)

from app.core.database import Base


class ComplianceRule(Base):
    __tablename__ = "compliance_rules"

    id = Column(
        Integer,
        primary_key=True,
        index=True,
    )

    # -----------------------------------------------------
    # Rule version
    # -----------------------------------------------------

    rule_version_id = Column(
        Integer,
        ForeignKey("rule_versions.id"),
        nullable=False,
        index=True,
    )

    # -----------------------------------------------------
    # Legal provision identification
    # -----------------------------------------------------

    rule_number = Column(
        String(50),
        nullable=False,
        index=True,
    )

    sub_rule = Column(
        String(50),
        nullable=True,
    )

    title = Column(
        String(255),
        nullable=False,
    )

    # -----------------------------------------------------
    # Rule content
    # -----------------------------------------------------

    requirement_summary = Column(
        Text,
        nullable=False,
    )

    legal_text = Column(
        Text,
        nullable=True,
    )

    # -----------------------------------------------------
    # Applicability
    # -----------------------------------------------------

    inspection_type = Column(
        String(30),
        nullable=True,
    )

    commodity_category = Column(
        String(100),
        nullable=True,
    )

    applicability_condition = Column(
        Text,
        nullable=True,
    )

    # -----------------------------------------------------
    # Evidence / evaluation
    # -----------------------------------------------------

    evidence_required = Column(
        Text,
        nullable=True,
    )

    evaluation_method = Column(
        String(100),
        nullable=True,
    )

    # -----------------------------------------------------
    # Enforcement classification
    # -----------------------------------------------------

    severity = Column(
        String(30),
        nullable=True,
    )

    is_active = Column(
        Boolean,
        nullable=False,
        default=True,
    )

    # -----------------------------------------------------
    # Audit
    # -----------------------------------------------------

    source_reference = Column(
        Text,
        nullable=True,
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
    )

    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )