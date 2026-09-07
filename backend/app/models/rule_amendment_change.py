from datetime import datetime

from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    DateTime,
    ForeignKey,
)

from app.core.database import Base


class RuleAmendmentChange(Base):
    __tablename__ = "rule_amendment_changes"

    id = Column(
        Integer,
        primary_key=True,
        index=True,
    )

    rule_version_id = Column(
        Integer,
        ForeignKey("rule_versions.id"),
        nullable=False,
        index=True,
    )

    rule_number = Column(
        String(20),
        nullable=False,
        index=True,
    )

    sub_rule = Column(
        String(20),
        nullable=True,
        index=True,
    )

    change_type = Column(
        String(30),
        nullable=False,
    )

    previous_text = Column(
        Text,
        nullable=True,
    )

    new_text = Column(
        Text,
        nullable=True,
    )

    legal_effect = Column(
        Text,
        nullable=True,
    )

    source_reference = Column(
        Text,
        nullable=False,
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
    )