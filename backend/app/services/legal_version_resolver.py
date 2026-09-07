# app/services/legal_version_resolver.py

from datetime import date, datetime
from typing import Optional

from sqlalchemy.orm import Session

from app.core.database import SessionLocal

from app.models.rule_version import RuleVersion
from app.models.compliance_rule import ComplianceRule
from app.models.rule_requirement import RuleRequirement


# ============================================================
# DATA CLASSIFICATION
# ============================================================

def normalize_inspection_date(
    inspection_date: Optional[date] = None,
) -> date:
    """
    Returns a valid inspection date.

    If no date is supplied, today's date is used.
    """

    if inspection_date is None:
        return date.today()

    if isinstance(inspection_date, datetime):
        return inspection_date.date()

    return inspection_date


# ============================================================
# VERSION TIMELINE
# ============================================================

def get_effective_versions(
    db: Session,
    inspection_date: date,
):
    """
    Returns all RuleVersion records that are legally effective
    on the supplied inspection date.

    This does NOT assume that the latest amendment is a
    complete replacement of the Rules.
    """

    inspection_date = normalize_inspection_date(
        inspection_date
    )

    versions = (
        db.query(RuleVersion)
        .filter(
            RuleVersion.is_active.is_(True),
            RuleVersion.effective_from <= inspection_date,
            (
                RuleVersion.effective_to.is_(None)
                |
                (
                    RuleVersion.effective_to
                    >= inspection_date
                )
            ),
        )
        .order_by(
            RuleVersion.effective_from.asc(),
            RuleVersion.id.asc(),
        )
        .all()
    )

    return versions


# ============================================================
# BASE VERSION
# ============================================================

def get_base_version(
    db: Session,
    inspection_date: date,
):
    """
    Finds the base PCR version applicable before amendments.
    """

    inspection_date = normalize_inspection_date(
        inspection_date
    )

    return (
        db.query(RuleVersion)
        .filter(
            RuleVersion.is_active.is_(True),
            RuleVersion.is_base_version.is_(True),
            RuleVersion.effective_from <= inspection_date,
        )
        .order_by(
            RuleVersion.effective_from.desc(),
            RuleVersion.id.desc(),
        )
        .first()
    )


# ============================================================
# LATEST EFFECTIVE AMENDMENT
# ============================================================

def get_latest_amendment(
    db: Session,
    inspection_date: date,
):
    """
    Returns the latest amendment event effective on the
    supplied date.

    This is informational/audit metadata and is NOT used
    by itself as the complete legal rule set.
    """

    inspection_date = normalize_inspection_date(
        inspection_date
    )

    return (
        db.query(RuleVersion)
        .filter(
            RuleVersion.is_active.is_(True),
            RuleVersion.is_base_version.is_(False),
            RuleVersion.effective_from <= inspection_date,
            (
                RuleVersion.effective_to.is_(None)
                |
                (
                    RuleVersion.effective_to
                    >= inspection_date
                )
            ),
        )
        .order_by(
            RuleVersion.effective_from.desc(),
            RuleVersion.id.desc(),
        )
        .first()
    )


# ============================================================
# RULE RESOLUTION
# ============================================================

def get_effective_rules(
    db: Session,
    inspection_date: date,
):
    """
    Returns rules associated with all RuleVersion events that
    are effective on the inspection date.

    Rules are deduplicated by:

        rule_number + sub_rule

    Later effective versions take precedence when the same
    provision is represented multiple times.
    """

    inspection_date = normalize_inspection_date(
        inspection_date
    )

    versions = get_effective_versions(
        db,
        inspection_date,
    )

    if not versions:
        return []

    resolved = {}

    for version in versions:

        rules = (
            db.query(ComplianceRule)
            .filter(
                ComplianceRule.rule_version_id
                == version.id,

                ComplianceRule.is_active.is_(True),
            )
            .order_by(
                ComplianceRule.rule_number.asc(),
                ComplianceRule.id.asc(),
            )
            .all()
        )

        for rule in rules:

            key = (
                rule.rule_number,
                rule.sub_rule,
            )

            resolved[key] = {
                "rule": rule,
                "version": version,
            }

    return list(
        resolved.values()
    )


# ============================================================
# REQUIREMENTS
# ============================================================

def get_effective_requirements(
    db: Session,
    inspection_date: date,
):
    """
    Returns requirements belonging to the resolved rules.

    Requirements are deduplicated by requirement_code.
    """

    resolved_rules = get_effective_rules(
        db,
        inspection_date,
    )

    resolved_requirements = {}

    for item in resolved_rules:

        rule = item["rule"]
        version = item["version"]

        requirements = (
            db.query(RuleRequirement)
            .filter(
                RuleRequirement.compliance_rule_id
                == rule.id,

                RuleRequirement.is_active.is_(True),
            )
            .order_by(
                RuleRequirement.id.asc()
            )
            .all()
        )

        for requirement in requirements:

            resolved_requirements[
                requirement.requirement_code
            ] = {
                "requirement": requirement,
                "rule": rule,
                "version": version,
            }

    return list(
        resolved_requirements.values()
    )


# ============================================================
# RULE FILTER
# ============================================================

def filter_rules(
    resolved_rules,
    inspection_type: Optional[str] = None,
    rule_numbers: Optional[list[str]] = None,
):
    """
    Filters resolved rules according to inspection type
    and/or requested rule numbers.
    """

    result = []

    normalized_type = None

    if inspection_type:
        normalized_type = (
            inspection_type.upper()
        )

    normalized_numbers = None

    if rule_numbers:
        normalized_numbers = {
            str(number)
            for number in rule_numbers
        }

    for item in resolved_rules:

        rule = item["rule"]

        # --------------------------------------------
        # Rule number filter
        # --------------------------------------------

        if (
            normalized_numbers is not None
            and rule.rule_number
            not in normalized_numbers
        ):
            continue

        # --------------------------------------------
        # Inspection type filter
        # --------------------------------------------

        if normalized_type:

            rule_type = (
                rule.inspection_type
                or "BOTH"
            ).upper()

            if (
                rule_type != "BOTH"
                and rule_type != normalized_type
            ):
                continue

        result.append(item)

    return result


# ============================================================
# MAIN LEGAL CONTEXT
# ============================================================

def resolve_legal_context(
    db: Session,
    inspection_date: Optional[date] = None,
    inspection_type: Optional[str] = None,
    rule_numbers: Optional[list[str]] = None,
):
    """
    Main resolver.

    Returns the legal context applicable to an inspection date.

    The response intentionally contains audit information so
    the compliance engine can later explain WHY a rule was used.
    """

    inspection_date = normalize_inspection_date(
        inspection_date
    )

    # --------------------------------------------
    # Base rules
    # --------------------------------------------

    base_version = get_base_version(
        db,
        inspection_date,
    )

    # --------------------------------------------
    # All effective amendment events
    # --------------------------------------------

    effective_versions = get_effective_versions(
        db,
        inspection_date,
    )

    # --------------------------------------------
    # Latest effective amendment
    # --------------------------------------------

    latest_amendment = get_latest_amendment(
        db,
        inspection_date,
    )

    # --------------------------------------------
    # Resolve rules
    # --------------------------------------------

    resolved_rules = get_effective_rules(
        db,
        inspection_date,
    )

    # --------------------------------------------
    # Filter
    # --------------------------------------------

    filtered_rules = filter_rules(
        resolved_rules,
        inspection_type=inspection_type,
        rule_numbers=rule_numbers,
    )

    # --------------------------------------------
    # Resolve requirements
    # --------------------------------------------

    all_requirements = get_effective_requirements(
        db,
        inspection_date,
    )

    requirement_map = {}

    for item in all_requirements:

        rule = item["rule"]

        key = (
            rule.rule_number,
            rule.sub_rule,
        )

        requirement_map.setdefault(
            key,
            []
        ).append(item)

    # --------------------------------------------
    # Build response
    # --------------------------------------------

    rules_response = []

    for item in filtered_rules:

        rule = item["rule"]
        version = item["version"]

        key = (
            rule.rule_number,
            rule.sub_rule,
        )

        requirements = requirement_map.get(
            key,
            [],
        )

        rules_response.append(
            {
                "rule_id": rule.id,
                "rule_number": rule.rule_number,
                "sub_rule": rule.sub_rule,
                "title": rule.title,
                "inspection_type": rule.inspection_type,
                "evaluation_method": rule.evaluation_method,
                "severity": rule.severity,
                "requirement_summary": (
                    rule.requirement_summary
                ),
                "applicability_condition": (
                    rule.applicability_condition
                ),
                "evidence_required": (
                    rule.evidence_required
                ),
                "source_reference": (
                    rule.source_reference
                ),
                "resolved_from_version": {
                    "id": version.id,
                    "version_code": (
                        version.version_code
                    ),
                    "effective_from": (
                        version.effective_from.isoformat()
                    ),
                    "effective_to": (
                        version.effective_to.isoformat()
                        if version.effective_to
                        else None
                    ),
                },
                "requirements": [
                    {
                        "id": (
                            req["requirement"].id
                        ),
                        "requirement_code": (
                            req["requirement"]
                            .requirement_code
                        ),
                        "title": (
                            req["requirement"]
                            .requirement_title
                        ),
                        "description": (
                            req["requirement"]
                            .requirement_description
                        ),
                        "evidence_type": (
                            req["requirement"]
                            .evidence_type
                        ),
                        "evidence_fields": (
                            req["requirement"]
                            .evidence_fields
                        ),
                        "evaluation_method": (
                            req["requirement"]
                            .evaluation_method
                        ),
                        "severity": (
                            req["requirement"]
                            .severity
                        ),
                        "violation_condition": (
                            req["requirement"]
                            .violation_condition
                        ),
                        "inconclusive_condition": (
                            req["requirement"]
                            .inconclusive_condition
                        ),
                        "source_reference": (
                            req["requirement"]
                            .source_reference
                        ),
                    }
                    for req in requirements
                ],
            }
        )

    return {
        "inspection_date": (
            inspection_date.isoformat()
        ),

        "base_version": (
            {
                "id": base_version.id,
                "version_code": (
                    base_version.version_code
                ),
                "effective_from": (
                    base_version
                    .effective_from
                    .isoformat()
                ),
            }
            if base_version
            else None
        ),

        "effective_versions": [
            {
                "id": version.id,
                "version_code": (
                    version.version_code
                ),
                "title": version.title,
                "amendment_year": (
                    version.amendment_year
                ),
                "notification_number": (
                    version.notification_number
                ),
                "notification_date": (
                    version.notification_date.isoformat()
                    if version.notification_date
                    else None
                ),
                "effective_from": (
                    version.effective_from.isoformat()
                ),
                "effective_to": (
                    version.effective_to.isoformat()
                    if version.effective_to
                    else None
                ),
                "source_reference": (
                    version.source_reference
                ),
            }
            for version in effective_versions
        ],

        "latest_amendment": (
            {
                "id": latest_amendment.id,
                "version_code": (
                    latest_amendment.version_code
                ),
                "title": latest_amendment.title,
                "effective_from": (
                    latest_amendment
                    .effective_from
                    .isoformat()
                ),
                "effective_to": (
                    latest_amendment
                    .effective_to
                    .isoformat()
                    if latest_amendment.effective_to
                    else None
                ),
                "source_reference": (
                    latest_amendment
                    .source_reference
                ),
            }
            if latest_amendment
            else None
        ),

        "rule_count": len(
            rules_response
        ),

        "rules": rules_response,
    }


# ============================================================
# CONVENIENCE FUNCTION
# ============================================================

def resolve_for_inspection(
    db: Session,
    inspection,
):
    """
    Convenience wrapper for an Inspection object.

    Uses the inspection's created_at date and inspection_type.
    """

    inspection_date = None

    if inspection.created_at:

        if isinstance(
            inspection.created_at,
            datetime,
        ):
            inspection_date = (
                inspection.created_at.date()
            )

        elif isinstance(
            inspection.created_at,
            date,
        ):
            inspection_date = (
                inspection.created_at
            )

    return resolve_legal_context(
        db=db,
        inspection_date=inspection_date,
        inspection_type=inspection.inspection_type,
    )


# ============================================================
# SIMPLE CLI TEST
# ============================================================

if __name__ == "__main__":

    db = SessionLocal()

    try:

        context = resolve_legal_context(
            db=db,
            inspection_date=date.today(),
        )

        print(
            "\n=========================================="
        )

        print(
            "LEGAL VERSION RESOLVER TEST"
        )

        print(
            "=========================================="
        )

        print(
            f"Inspection date : "
            f"{context['inspection_date']}"
        )

        print(
            f"Base version    : "
            f"{context['base_version']}"
        )

        print(
            "\nEffective versions:"
        )

        for version in (
            context["effective_versions"]
        ):

            print(
                f"  ✓ {version['version_code']}"
                f" | effective "
                f"{version['effective_from']}"
            )

        print(
            "\nLatest amendment:"
        )

        print(
            f"  {context['latest_amendment']}"
        )

        print(
            f"\nResolved rules: "
            f"{context['rule_count']}"
        )

        for rule in context["rules"]:

            sub_rule = (
                f"({rule['sub_rule']})"
                if rule["sub_rule"]
                else ""
            )

            print(
                f"  ✓ Rule "
                f"{rule['rule_number']}"
                f"{sub_rule}"
                f" - "
                f"{rule['title']}"
            )

        print(
            "\n=========================================="
        )

    finally:

        db.close()