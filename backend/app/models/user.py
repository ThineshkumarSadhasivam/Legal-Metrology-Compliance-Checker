from sqlalchemy import Column, Integer, String, Boolean

from app.core.database import Base


class User(Base):

    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)

    officer_id = Column(
        String(50),
        unique=True,
        nullable=False,
        index=True
    )

    full_name = Column(
        String(150),
        nullable=False
    )

    email = Column(
        String(150),
        unique=True,
        nullable=False
    )

    password_hash = Column(
        String(255),
        nullable=False
    )

    role = Column(
        String(50),
        default="ENFORCEMENT_OFFICER",
        nullable=False
    )

    is_active = Column(
        Boolean,
        default=True
    )