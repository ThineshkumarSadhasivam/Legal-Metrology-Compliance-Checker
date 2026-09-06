from datetime import date
from typing import Optional

from sqlalchemy.orm import Session

from app.models.rule_version import RuleVersion
from app.models.compliance_rule import ComplianceRule
from app.models.rule_requirement import RuleRequirement


# =========================================================
# RULE VERSION REPOSITORY
# =========================================================

class RulesRepository:
    """
    Central repository for Legal Metrology rule versions.

    This class is responsible for retrieving legal rules.
    It does NOT decide whether a product is compliant.
    """

    def __init__(self, db: Session):
        self.db = db

    # =====================================================
    # RULE VERSION
    # =====================================================

    def get_rule_version(
        self,
        version_code: str,
    ) -> Optional[RuleVersion]:

        return (
            self.db.query(RuleVersion)
            .filter(
                RuleVersion.version_code == version_code
            )
            .first()
        )

    # =====================================================
    # FIND VERSION APPLICABLE ON A DATE
    # =====================================================

    def get_version_for_date(
        self,
        inspection_date: date,
    ) -> Optional[RuleVersion]:

        versions = (
            self.db.query(RuleVersion)
            .filter(
                RuleVersion.effective_from <= inspection_date,
                RuleVersion.is_active == True,
            )
            .order_by(
                RuleVersion.effective_from.desc()
            )
            .all()
        )

        for version in versions:

            # No end date means the version is currently
            # open-ended.
            if version.effective_to is None:
                return version

            if inspection_date <= version.effective_to:
                return version

        return None

    # =====================================================
    # CREATE RULE VERSION
    # =====================================================

    def create_rule_version(
        self,
        version_code: str,
        title: str,
        effective_from: date,
        amendment_year: Optional[int] = None,
        notification_number: Optional[str] = None,
        notification_date: Optional[date] = None,
        effective_to: Optional[date] = None,
        is_base_version: bool = False,
        source_name: Optional[str] = None,
        source_reference: Optional[str] = None,
        notes: Optional[str] = None,
    ) -> RuleVersion:

        existing = self.get_rule_version(
            version_code
        )

        if existing:
            return existing

        version = RuleVersion(
            version_code=version_code,
            title=title,
            amendment_year=amendment_year,
            notification_number=notification_number,
            notification_date=notification_date,
            effective_from=effective_from,
            effective_to=effective_to,
            is_base_version=is_base_version,
            is_active=True,
            source_name=source_name,
            source_reference=source_reference,
            notes=notes,
        )

        self.db.add(version)
        self.db.flush()

        return version

    # =====================================================
    # COMPLIANCE RULE
    # =====================================================

    def get_rule(
        self,
        rule_version_id: int,
        rule_number: str,
        sub_rule: Optional[str] = None,
    ) -> Optional[ComplianceRule]:

        query = (
            self.db.query(ComplianceRule)
            .filter(
                ComplianceRule.rule_version_id
                == rule_version_id,

                ComplianceRule.rule_number
                == rule_number,
            )
        )

        if sub_rule is None:

            query = query.filter(
                ComplianceRule.sub_rule.is_(None)
            )

        else:

            query = query.filter(
                ComplianceRule.sub_rule
                == sub_rule
            )

        return query.first()

    # =====================================================
    # GET RULES FOR VERSION
    # =====================================================

    def get_rules_for_version(
        self,
        rule_version_id: int,
    ):

        return (
            self.db.query(ComplianceRule)
            .filter(
                ComplianceRule.rule_version_id
                == rule_version_id,

                ComplianceRule.is_active == True,
            )
            .order_by(
                ComplianceRule.rule_number.asc()
            )
            .all()
        )

    # =====================================================
    # GET REQUIREMENTS FOR RULE
    # =====================================================

    def get_requirements_for_rule(
        self,
        compliance_rule_id: int,
    ):

        return (
            self.db.query(RuleRequirement)
            .filter(
                RuleRequirement.compliance_rule_id
                == compliance_rule_id,

                RuleRequirement.is_active == True,
            )
            .order_by(
                RuleRequirement.id.asc()
            )
            .all()
        )

    # =====================================================
    # GET COMPLETE RULE WITH REQUIREMENTS
    # =====================================================

    def get_rule_with_requirements(
        self,
        rule_version_id: int,
        rule_number: str,
        sub_rule: Optional[str] = None,
    ):

        rule = self.get_rule(
            rule_version_id=rule_version_id,
            rule_number=rule_number,
            sub_rule=sub_rule,
        )

        if not rule:
            return None

        requirements = (
            self.get_requirements_for_rule(
                rule.id
            )
        )

        return {
            "rule": rule,
            "requirements": requirements,
        }

    # =====================================================
    # GET APPLICABLE RULES
    # =====================================================

    def get_applicable_rules(
        self,
        inspection_date: date,
        rule_numbers: list[str],
    ):

        version = self.get_version_for_date(
            inspection_date
        )

        if not version:
            return {
                "version": None,
                "rules": [],
            }

        rules = (
            self.db.query(ComplianceRule)
            .filter(
                ComplianceRule.rule_version_id
                == version.id,

                ComplianceRule.rule_number.in_(
                    rule_numbers
                ),

                ComplianceRule.is_active == True,
            )
            .order_by(
                ComplianceRule.rule_number.asc()
            )
            .all()
        )

        return {
            "version": version,
            "rules": rules,
        }

    # =====================================================
    # GET COMPLETE APPLICABLE RULE SET
    # =====================================================

    def get_applicable_rule_set(
        self,
        inspection_date: date,
        rule_numbers: list[str],
    ):

        result = self.get_applicable_rules(
            inspection_date=inspection_date,
            rule_numbers=rule_numbers,
        )

        version = result["version"]
        rules = result["rules"]

        if not version:
            return {
                "version": None,
                "rules": [],
            }

        complete_rules = []

        for rule in rules:

            requirements = (
                self.get_requirements_for_rule(
                    rule.id
                )
            )

            complete_rules.append(
                {
                    "rule": rule,
                    "requirements": requirements,
                }
            )

        return {
            "version": version,
            "rules": complete_rules,
        }