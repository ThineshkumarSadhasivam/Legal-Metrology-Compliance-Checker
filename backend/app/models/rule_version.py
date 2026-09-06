from datetime import date, datetime

from sqlalchemy import (
    Column,
    Integer,
    String,
    Date,
    DateTime,
    Boolean,
    Text,
)

from app.core.database import Base


class RuleVersion(Base):
    __tablename__ = "rule_versions"

    id = Column(
        Integer,
        primary_key=True,
        index=True,
    )

    # -----------------------------------------------------
    # Version identification
    # -----------------------------------------------------

    version_code = Column(
        String(50),
        unique=True,
        nullable=False,
        index=True,
    )

    title = Column(
        String(255),
        nullable=False,
    )

    amendment_year = Column(
        Integer,
        nullable=True,
    )

    notification_number = Column(
        String(100),
        nullable=True,
    )

    notification_date = Column(
        Date,
        nullable=True,
    )

    # -----------------------------------------------------
    # Legal effectiveness
    # -----------------------------------------------------

    effective_from = Column(
        Date,
        nullable=False,
        index=True,
    )

    effective_to = Column(
        Date,
        nullable=True,
        index=True,
    )

    is_base_version = Column(
        Boolean,
        nullable=False,
        default=False,
    )

    is_active = Column(
        Boolean,
        nullable=False,
        default=True,
    )

    # -----------------------------------------------------
    # Source / audit information
    # -----------------------------------------------------

    source_name = Column(
        String(255),
        nullable=True,
    )

    source_reference = Column(
        Text,
        nullable=True,
    )

    notes = Column(
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