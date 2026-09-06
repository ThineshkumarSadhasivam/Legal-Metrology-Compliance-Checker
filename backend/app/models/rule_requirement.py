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


class RuleRequirement(Base):
    __tablename__ = "rule_requirements"

    id = Column(
        Integer,
        primary_key=True,
        index=True,
    )

    compliance_rule_id = Column(
        Integer,
        ForeignKey("compliance_rules.id"),
        nullable=False,
        index=True,
    )

    requirement_code = Column(
        String(100),
        nullable=False,
        index=True,
    )

    requirement_title = Column(
        String(255),
        nullable=False,
    )

    requirement_description = Column(
        Text,
        nullable=False,
    )

    evidence_type = Column(
        String(100),
        nullable=True,
    )

    evidence_fields = Column(
        Text,
        nullable=True,
    )

    evaluation_method = Column(
        String(100),
        nullable=True,
    )

    violation_condition = Column(
        Text,
        nullable=True,
    )

    inconclusive_condition = Column(
        Text,
        nullable=True,
    )

    severity = Column(
        String(30),
        nullable=True,
    )

    is_mandatory = Column(
        Boolean,
        nullable=False,
        default=True,
    )

    is_active = Column(
        Boolean,
        nullable=False,
        default=True,
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

    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )