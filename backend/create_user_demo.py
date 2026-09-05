from app.core.database import SessionLocal, Base, engine
from app.core.security import hash_password
from app.models.user import User

Base.metadata.create_all(bind=engine)

db = SessionLocal()

existing_user = (
    db.query(User)
    .filter(User.officer_id == "LM001")
    .first()
)

if existing_user:
    print("Demo officer already exists.")
else:
    user = User(
        officer_id="LM001",
        full_name="Demo Enforcement Officer",
        email="officer@legalmetrology.local",
        password_hash=hash_password("demo123"),
        role="ENFORCEMENT_OFFICER",
        is_active=True
    )

    db.add(user)
    db.commit()

    print("Demo officer created successfully.")
    print("Officer ID: LM001")
    print("Password: demo123")

db.close()