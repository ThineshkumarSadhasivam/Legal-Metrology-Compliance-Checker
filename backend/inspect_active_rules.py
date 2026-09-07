from app.core.database import SessionLocal
from app.models.rule_version import RuleVersion
from app.models.compliance_rule import ComplianceRule


db = SessionLocal()

try:
    rows = (
        db.query(
            ComplianceRule.id,
            RuleVersion.version_code,
            RuleVersion.effective_from,
            ComplianceRule.rule_number,
            ComplianceRule.sub_rule,
            ComplianceRule.title,
            ComplianceRule.is_active,
        )
        .join(
            RuleVersion,
            RuleVersion.id == ComplianceRule.rule_version_id,
        )
        .filter(
            ComplianceRule.is_active.is_(True)
        )
        .order_by(
            RuleVersion.effective_from.asc(),
            ComplianceRule.rule_number.asc(),
            ComplianceRule.id.asc(),
        )
        .all()
    )

    print("\n==========================================")
    print("ACTIVE COMPLIANCE RULES")
    print("==========================================")
    print(f"Total active rules: {len(rows)}\n")

    for row in rows:
        print(
            f"ID={row.id} | "
            f"VERSION={row.version_code} | "
            f"EFFECTIVE={row.effective_from} | "
            f"RULE={row.rule_number} | "
            f"SUB_RULE={row.sub_rule} | "
            f"TITLE={row.title} | "
            f"ACTIVE={row.is_active}"
        )

    print("\n==========================================")

finally:
    db.close()