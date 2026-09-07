from app.core.database import SessionLocal
from app.models.rule_version import RuleVersion
from app.models.compliance_rule import ComplianceRule


db = SessionLocal()

try:
    # ========================================================
    # VERIFIED RULES THAT MUST REMAIN ACTIVE
    # ========================================================

    verified_rules = {
        "PCR_2011_BASE": {
            ("2", None),
            ("6", None),
            ("7", None),
            ("8", None),
            ("9", None),
            ("26", None),
        },

        "PCR_2017_AMENDMENT": {
            ("6", "10"),
            ("7", None),
        },

        "PCR_2022_AMENDMENT": {
            ("6", None),
        },

        "PCR_2026_AMENDMENT": {
            ("6", "10A"),
        },

        "PCR_2026_SECOND_AMENDMENT": {
            ("6", "10A"),
        },
    }

    # ========================================================
    # LOAD ACTIVE RULES
    # ========================================================

    rules = (
        db.query(
            ComplianceRule,
            RuleVersion
        )
        .join(
            RuleVersion,
            RuleVersion.id
            == ComplianceRule.rule_version_id
        )
        .filter(
            ComplianceRule.is_active.is_(True)
        )
        .all()
    )

    deactivated = []
    kept = []

    # ========================================================
    # CLEAN GENERIC RULES
    # ========================================================

    for rule, version in rules:

        allowed = verified_rules.get(
            version.version_code,
            set()
        )

        key = (
            rule.rule_number,
            rule.sub_rule
        )

        if key in allowed:
            kept.append(
                (
                    rule.id,
                    version.version_code,
                    rule.rule_number,
                    rule.sub_rule,
                    rule.title,
                )
            )
        else:
            rule.is_active = False

            deactivated.append(
                (
                    rule.id,
                    version.version_code,
                    rule.rule_number,
                    rule.sub_rule,
                    rule.title,
                )
            )

    db.commit()

    # ========================================================
    # OUTPUT
    # ========================================================

    print("\n==========================================")
    print("RULE CATALOGUE CLEANUP")
    print("==========================================")

    print(
        f"Kept active rules       : {len(kept)}"
    )

    print(
        f"Deactivated rules       : {len(deactivated)}"
    )

    print("\nKEPT RULES:")
    print("------------------------------------------")

    for item in kept:
        print(
            f"ID={item[0]} | "
            f"VERSION={item[1]} | "
            f"RULE={item[2]} | "
            f"SUB_RULE={item[3]} | "
            f"TITLE={item[4]}"
        )

    print("\nDEACTIVATED RULES:")
    print("------------------------------------------")

    for item in deactivated:
        print(
            f"ID={item[0]} | "
            f"VERSION={item[1]} | "
            f"RULE={item[2]} | "
            f"SUB_RULE={item[3]} | "
            f"TITLE={item[4]}"
        )

    print("\n==========================================")
    print("Cleanup completed successfully.")
    print("==========================================")

finally:
    db.close()