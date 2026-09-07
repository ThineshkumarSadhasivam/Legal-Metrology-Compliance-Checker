from datetime import date

from sqlalchemy.orm import Session

from app.core.database import SessionLocal
from app.models.rule_version import RuleVersion
from app.models.rule_amendment_change import RuleAmendmentChange


def get_version(
    db: Session,
    version_code: str,
):
    return (
        db.query(RuleVersion)
        .filter(
            RuleVersion.version_code
            == version_code
        )
        .first()
    )


def upsert_change(
    db: Session,
    *,
    version_code: str,
    rule_number: str,
    sub_rule: str | None,
    change_type: str,
    previous_text: str | None,
    new_text: str | None,
    legal_effect: str,
    source_reference: str,
):
    version = get_version(
        db,
        version_code,
    )

    if not version:
        raise RuntimeError(
            f"Rule version not found: {version_code}"
        )

    existing = (
        db.query(RuleAmendmentChange)
        .filter(
            RuleAmendmentChange.rule_version_id
            == version.id,

            RuleAmendmentChange.rule_number
            == rule_number,

            RuleAmendmentChange.sub_rule
            == sub_rule,

            RuleAmendmentChange.change_type
            == change_type,
        )
        .first()
    )

    if existing:
        existing.previous_text = previous_text
        existing.new_text = new_text
        existing.legal_effect = legal_effect
        existing.source_reference = source_reference
        return existing

    change = RuleAmendmentChange(
        rule_version_id=version.id,
        rule_number=rule_number,
        sub_rule=sub_rule,
        change_type=change_type,
        previous_text=previous_text,
        new_text=new_text,
        legal_effect=legal_effect,
        source_reference=source_reference,
    )

    db.add(change)

    return change


def seed():
    db = SessionLocal()

    try:

        # --------------------------------------------------
        # 2021 AMENDMENT
        # --------------------------------------------------

        upsert_change(
            db,
            version_code="PCR_2021_AMENDMENT",
            rule_number="2",
            sub_rule="aa",
            change_type="SUBSTITUTE",
            previous_text=(
                "Consumer definition reference "
                "to Consumer Protection Act, 1986."
            ),
            new_text=(
                "Consumer definition reference "
                "to Consumer Protection Act, 2019."
            ),
            legal_effect=(
                "Updates the cross-reference to "
                "the Consumer Protection Act, 2019."
            ),
            source_reference=(
                "G.S.R. 779(E), dated 02-11-2021"
            ),
        )

        upsert_change(
            db,
            version_code="PCR_2021_AMENDMENT",
            rule_number="4",
            sub_rule="2",
            change_type="INSERT",
            previous_text=None,
            new_text=(
                "When one or more packages intended "
                "for retail sale are grouped together "
                "for being sold as a retail package "
                "on promotional offer, every package "
                "of the group shall comply with "
                "provisions of rule 6."
            ),
            legal_effect=(
                "Adds a requirement concerning "
                "packages grouped for promotional "
                "retail sale."
            ),
            source_reference=(
                "G.S.R. 779(E), dated 02-11-2021"
            ),
        )

        # --------------------------------------------------
        # 2026 AMENDMENT
        # --------------------------------------------------

        upsert_change(
            db,
            version_code="PCR_2026_AMENDMENT",
            rule_number="6",
            sub_rule="10A",
            change_type="INSERT",
            previous_text=None,
            new_text=(
                "Every e-commerce entity selling "
                "imported products shall provide "
                "product listings in a searchable "
                "and sortable filter specifying "
                "the country of origin."
            ),
            legal_effect=(
                "Introduces an e-commerce requirement "
                "for country-of-origin filtering "
                "for imported products."
            ),
            source_reference=(
                "G.S.R. 128(E), dated 13-02-2026; "
                "effective 01-07-2026"
            ),
        )

        db.commit()

        print(
            "\n=========================================="
        )
        print(
            "AMENDMENT CHANGE SEED"
        )
        print(
            "=========================================="
        )

        count = (
            db.query(
                RuleAmendmentChange
            ).count()
        )

        print(
            f"Total amendment changes: {count}"
        )

        print(
            "Seed completed successfully."
        )

        print(
            "==========================================\n"
        )

    except Exception:
        db.rollback()
        raise

    finally:
        db.close()


if __name__ == "__main__":
    seed()