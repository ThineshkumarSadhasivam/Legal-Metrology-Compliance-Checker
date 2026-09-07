# app/services/amendment_overlay_resolver.py

from datetime import date, datetime
from typing import Optional

from sqlalchemy.orm import Session

from app.core.database import SessionLocal
from app.models.rule_version import RuleVersion
from app.models.compliance_rule import ComplianceRule
from app.models.rule_requirement import RuleRequirement


# ============================================================
# NORMALIZATION
# ============================================================

def normalize_rule_number(
    rule_number: str,
    sub_rule: Optional[str] = None,
):
    """
    Normalizes representations such as:

        6
        6(10)
        6(10A)

    into:

        ("6", None)
        ("6", "10")
        ("6", "10A")
    """

    if not rule_number:
        return "", sub_rule

    value = str(rule_number).strip()

    # Existing seed may contain:
    # "6(10)"
    # "6(10A)"
    if value.startswith("6(") and value.endswith(")"):

        extracted = value[2:-1].strip()

        return "6", extracted

    return value, sub_rule


# ============================================================
# DATE NORMALIZATION
# ============================================================

def normalize_date(
    inspection_date: Optional[date] = None,
):
    """
    Converts datetime -> date and uses today's date
    when no date is supplied.
    """

    if inspection_date is None:
        return date.today()

    if isinstance(
        inspection_date,
        datetime,
    ):
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
    Returns every active legal version/amendment event
    effective on the inspection date.
    """

    inspection_date = normalize_date(
        inspection_date
    )

    versions = (
        db.query(RuleVersion)
        .filter(
            RuleVersion.is_active.is_(True),

            RuleVersion.effective_from
            <= inspection_date,

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
    Returns the applicable base PCR Rules version.
    """

    inspection_date = normalize_date(
        inspection_date
    )

    return (
        db.query(RuleVersion)
        .filter(
            RuleVersion.is_active.is_(True),
            RuleVersion.is_base_version.is_(True),
            RuleVersion.effective_from
            <= inspection_date,
        )
        .order_by(
            RuleVersion.effective_from.desc(),
            RuleVersion.id.desc(),
        )
        .first()
    )


# ============================================================
# LOAD RULES
# ============================================================

def load_rules_for_version(
    db: Session,
    version_id: int,
):
    """
    Loads active compliance rules for a RuleVersion.
    """

    return (
        db.query(ComplianceRule)
        .filter(
            ComplianceRule.rule_version_id
            == version_id,

            ComplianceRule.is_active.is_(True),
        )
        .order_by(
            ComplianceRule.id.asc()
        )
        .all()
    )


# ============================================================
# RULE KEY
# ============================================================

def rule_key(rule):
    """
    Creates a normalized unique key for a rule.
    """

    rule_number, sub_rule = normalize_rule_number(
        rule.rule_number,
        rule.sub_rule,
    )

    return (
        rule_number,
        sub_rule,
    )


# ============================================================
# REQUIREMENT LOADING
# ============================================================

def load_requirements_for_rule(
    db: Session,
    rule_id: int,
):
    """
    Loads active requirements belonging to a rule.
    """

    return (
        db.query(RuleRequirement)
        .filter(
            RuleRequirement.compliance_rule_id
            == rule_id,

            RuleRequirement.is_active.is_(True),
        )
        .order_by(
            RuleRequirement.id.asc()
        )
        .all()
    )


# ============================================================
# REQUIREMENT KEY
# ============================================================

def requirement_key(requirement):
    return requirement.requirement_code


# ============================================================
# APPLY RULE OVERLAY
# ============================================================

def apply_rule_overlay(
    db: Session,
    effective_versions,
    base_version,
):
    """
    Builds the current legal rule catalogue by starting with
    the base Rules and overlaying rules represented by later
    amendment/version records.

    Later effective records take precedence for the same:

        rule_number + sub_rule

    This is deliberately conservative.

    An amendment record that contains no replacement rule
    does NOT erase the base rule.
    """

    resolved_rules = {}

    # --------------------------------------------------------
    # 1. BASE RULES
    # --------------------------------------------------------

    if base_version:

        base_rules = load_rules_for_version(
            db,
            base_version.id,
        )

        for rule in base_rules:

            key = rule_key(rule)

            resolved_rules[key] = {
                "rule": rule,
                "version": base_version,
            }

    # --------------------------------------------------------
    # 2. AMENDMENT OVERLAYS
    # --------------------------------------------------------

    for version in effective_versions:

        if version.is_base_version:
            continue

        version_rules = load_rules_for_version(
            db,
            version.id,
        )

        for rule in version_rules:

            key = rule_key(rule)

            # ------------------------------------------------
            # IMPORTANT
            #
            # Only rules actually stored under this amendment
            # are allowed to override the base rule.
            #
            # Other base provisions remain active.
            # ------------------------------------------------

            resolved_rules[key] = {
                "rule": rule,
                "version": version,
            }

    return resolved_rules


# ============================================================
# APPLY REQUIREMENT OVERLAY
# ============================================================

def build_resolved_requirements(
    db: Session,
    resolved_rules,
):
    """
    Builds requirements for the resolved rule set.

    Requirements are associated with their final resolved rule.

    Requirement codes are used for deduplication.
    """

    result = {}

    for key, item in resolved_rules.items():

        rule = item["rule"]
        version = item["version"]

        requirements = load_requirements_for_rule(
            db,
            rule.id,
        )

        for requirement in requirements:

            req_key = (
                key,
                requirement_key(
                    requirement
                ),
            )

            result[req_key] = {
                "requirement": requirement,
                "rule": rule,
                "version": version,
            }

    return result


# ============================================================
# INSPECTION TYPE FILTER
# ============================================================

def matches_inspection_type(
    rule,
    inspection_type: Optional[str],
):
    """
    Determines whether a rule belongs to the requested
    inspection channel.
    """

    if not inspection_type:
        return True

    inspection_type = (
        inspection_type.upper()
    )

    rule_type = (
        rule.inspection_type
        or "BOTH"
    ).upper()

    if rule_type == "BOTH":
        return True

    return rule_type == inspection_type


# ============================================================
# RULE NUMBER FILTER
# ============================================================

def matches_rule_number(
    rule,
    rule_numbers: Optional[list[str]],
):
    """
    Filters rules by rule number.

    Behavior:

        ["6"]
            -> Rule 6
            -> Rule 6(10)
            -> Rule 6(10A)
            -> all other Rule 6 sub-rules

        ["6(10A)"]
            -> only Rule 6(10A)

        ["6", "7"]
            -> Rule 6 family + Rule 7 family
    """

    if not rule_numbers:
        return True

    rule_number, sub_rule = normalize_rule_number(
        rule.rule_number,
        rule.sub_rule,
    )

    for requested in rule_numbers:

        requested_number, requested_sub_rule = (
            normalize_rule_number(
                str(requested)
            )
        )

        # --------------------------------------------------
        # Bare rule number:
        #
        # "6" matches:
        # 6
        # 6(10)
        # 6(10A)
        # --------------------------------------------------

        if requested_sub_rule is None:

            if rule_number == requested_number:
                return True

        # --------------------------------------------------
        # Specific sub-rule:
        #
        # "6(10A)" matches only 6(10A)
        # --------------------------------------------------

        else:

            if (
                rule_number == requested_number
                and sub_rule == requested_sub_rule
            ):
                return True

    return False


# ============================================================
# LEGAL STATE
# ============================================================

def resolve_legal_state(
    db: Session,
    inspection_date: Optional[date] = None,
    inspection_type: Optional[str] = None,
    rule_numbers: Optional[list[str]] = None,
):
    """
    Main amendment-overlay resolver.

    Produces the legal rule state applicable on the
    supplied inspection date.
    """

    inspection_date = normalize_date(
        inspection_date
    )

    # --------------------------------------------------------
    # BASE VERSION
    # --------------------------------------------------------

    base_version = get_base_version(
        db,
        inspection_date,
    )

    if not base_version:

        raise RuntimeError(
            "No applicable base Legal Metrology "
            "rule version was found."
        )

    # --------------------------------------------------------
    # EFFECTIVE VERSIONS
    # --------------------------------------------------------

    effective_versions = get_effective_versions(
        db,
        inspection_date,
    )

    # --------------------------------------------------------
    # RESOLVE RULE OVERLAYS
    # --------------------------------------------------------

    resolved_rules = apply_rule_overlay(
        db,
        effective_versions,
        base_version,
    )

    # --------------------------------------------------------
    # REQUIREMENTS
    # --------------------------------------------------------

    resolved_requirements = (
        build_resolved_requirements(
            db,
            resolved_rules,
        )
    )

    # --------------------------------------------------------
    # FILTER RULES
    # --------------------------------------------------------

    final_rules = []

    for key, item in resolved_rules.items():

        rule = item["rule"]
        version = item["version"]

        if not matches_inspection_type(
            rule,
            inspection_type,
        ):
            continue

        if not matches_rule_number(
            rule,
            rule_numbers,
        ):
            continue

        requirements = []

        for (
            req_key,
            req_item,
        ) in resolved_requirements.items():

            req_rule = req_item["rule"]

            if rule_key(req_rule) != key:
                continue

            requirement = (
                req_item["requirement"]
            )

            requirements.append(
                {
                    "id": requirement.id,

                    "requirement_code": (
                        requirement
                        .requirement_code
                    ),

                    "title": (
                        requirement
                        .requirement_title
                    ),

                    "description": (
                        requirement
                        .requirement_description
                    ),

                    "evidence_type": (
                        requirement
                        .evidence_type
                    ),

                    "evidence_fields": (
                        requirement
                        .evidence_fields
                    ),

                    "evaluation_method": (
                        requirement
                        .evaluation_method
                    ),

                    "violation_condition": (
                        requirement
                        .violation_condition
                    ),

                    "inconclusive_condition": (
                        requirement
                        .inconclusive_condition
                    ),

                    "severity": (
                        requirement.severity
                    ),

                    "source_reference": (
                        requirement
                        .source_reference
                    ),

                    "resolved_from_version": {
                        "id": version.id,
                        "version_code": (
                            version.version_code
                        ),
                    },
                }
            )

        rule_number, sub_rule = (
            normalize_rule_number(
                rule.rule_number,
                rule.sub_rule,
            )
        )

        final_rules.append(
            {
                "rule_id": rule.id,

                "rule_number": rule_number,

                "sub_rule": sub_rule,

                "title": rule.title,

                "inspection_type": (
                    rule.inspection_type
                ),

                "evaluation_method": (
                    rule.evaluation_method
                ),

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
                        version
                        .effective_from
                        .isoformat()
                    ),

                    "effective_to": (
                        version
                        .effective_to
                        .isoformat()
                        if version.effective_to
                        else None
                    ),
                },

                "requirements": requirements,
            }
        )

    # --------------------------------------------------------
    # SORT
    # --------------------------------------------------------

    final_rules.sort(
        key=lambda item: (
            int(
                item["rule_number"]
            )
            if item["rule_number"].isdigit()
            else 999,

            item["sub_rule"] or "",
        )
    )

    # --------------------------------------------------------
    # LATEST AMENDMENT
    # --------------------------------------------------------

    amendments = [
        version
        for version in effective_versions
        if not version.is_base_version
    ]

    amendments.sort(
        key=lambda version: (
            version.effective_from,
            version.id,
        ),
        reverse=True,
    )

    latest_amendment = (
        amendments[0]
        if amendments
        else None
    )

    # --------------------------------------------------------
    # RESPONSE
    # --------------------------------------------------------

    return {
        "inspection_date": (
            inspection_date.isoformat()
        ),

        "base_version": {
            "id": base_version.id,

            "version_code": (
                base_version.version_code
            ),

            "title": base_version.title,

            "effective_from": (
                base_version
                .effective_from
                .isoformat()
            ),

            "source_reference": (
                base_version.source_reference
            ),
        },

        "effective_amendments": [
            {
                "id": version.id,

                "version_code": (
                    version.version_code
                ),

                "title": version.title,

                "notification_number": (
                    version.notification_number
                ),

                "notification_date": (
                    version.notification_date.isoformat()
                    if version.notification_date
                    else None
                ),

                "effective_from": (
                    version
                    .effective_from
                    .isoformat()
                ),

                "effective_to": (
                    version
                    .effective_to
                    .isoformat()
                    if version.effective_to
                    else None
                ),

                "source_reference": (
                    version.source_reference
                ),
            }

            for version in effective_versions
            if not version.is_base_version
        ],

        "latest_effective_amendment": (
            {
                "version_code": (
                    latest_amendment
                    .version_code
                ),

                "title": (
                    latest_amendment.title
                ),

                "effective_from": (
                    latest_amendment
                    .effective_from
                    .isoformat()
                ),

                "effective_to": (
                    latest_amendment
                    .effective_to
                    .isoformat()
                    if latest_amendment
                    .effective_to
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

        "inspection_type": inspection_type,

        "rule_count": len(
            final_rules
        ),

        "requirement_count": sum(
            len(rule["requirements"])
            for rule in final_rules
        ),

        "rules": final_rules,
    }


# ============================================================
# INSPECTION CONVENIENCE FUNCTION
# ============================================================

def resolve_for_inspection(
    db: Session,
    inspection,
):
    """
    Resolves the legal state for an Inspection object.
    """

    inspection_date = None

    if inspection.created_at:

        if isinstance(
            inspection.created_at,
            datetime,
        ):
            inspection_date = (
                inspection
                .created_at
                .date()
            )

        elif isinstance(
            inspection.created_at,
            date,
        ):
            inspection_date = (
                inspection.created_at
            )

    return resolve_legal_state(
        db=db,
        inspection_date=inspection_date,
        inspection_type=(
            inspection.inspection_type
        ),
    )


# ============================================================
# CLI TEST
# ============================================================

if __name__ == "__main__":

    db = SessionLocal()

    try:

        inspection_date = date.today()

        result = resolve_legal_state(
            db=db,
            inspection_date=inspection_date,
        )

        print(
            "\n=========================================="
        )

        print(
            "AMENDMENT OVERLAY RESOLVER TEST"
        )

        print(
            "=========================================="
        )

        print(
            f"Inspection date : "
            f"{result['inspection_date']}"
        )

        print(
            "\nBase version:"
        )

        print(
            f"  {result['base_version']['version_code']}"
        )

        print(
            "\nEffective amendments:"
        )

        for amendment in (
            result["effective_amendments"]
        ):

            print(
                f"  ✓ "
                f"{amendment['version_code']}"
                f" | "
                f"{amendment['effective_from']}"
            )

        print(
            "\nLatest effective amendment:"
        )

        latest = (
            result[
                "latest_effective_amendment"
            ]
        )

        if latest:

            print(
                f"  {latest['version_code']}"
            )

        else:

            print(
                "  None"
            )

        print(
            "\nResolved legal rules:"
        )

        for rule in result["rules"]:

            label = (
                rule["rule_number"]
            )

            if rule["sub_rule"]:

                label += (
                    f"({rule['sub_rule']})"
                )

            print(
                f"  ✓ Rule {label}"
                f" - {rule['title']}"
                f" | source: "
                f"{rule['resolved_from_version']['version_code']}"
            )

        print(
            "\n------------------------------------------"
        )

        print(
            f"Total resolved rules   : "
            f"{result['rule_count']}"
        )

        print(
            f"Total resolved requirements : "
            f"{result['requirement_count']}"
        )

        print(
            "==========================================\n"
        )

    except Exception as exc:

        print(
            "\nAMENDMENT OVERLAY RESOLVER FAILED"
        )

        print(
            f"Error: {exc}"
        )

        raise

    finally:

        db.close()