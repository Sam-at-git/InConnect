"""
Rule testing service for previewing routing results
"""

from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
import json

from app.models.routing_rule import RoutingRule, RoutingRuleType
from app.models.staff import Staff, StaffStatus
from app.models.ticket import TicketCategory, TicketPriority


class RuleTestService:
    """Service for testing routing rules"""

    @staticmethod
    def parse_json_field(value: str | None) -> Any:
        """Parse JSON field"""
        if not value:
            return []
        try:
            return json.loads(value)
        except (json.JSONDecodeError, TypeError):
            return []

    @staticmethod
    def test_message(
        db: Session,
        hotel_id: str,
        message_content: str,
        category: str | None = None,
        priority: str | None = None,
    ) -> Dict[str, Any]:
        """
        Test which rule would match a message

        Args:
            db: Database session
            hotel_id: Hotel ID
            message_content: Message content to test
            category: Optional ticket category
            priority: Optional ticket priority

        Returns:
            Test result with matched rule and assigned staff
        """
        # Get active rules for hotel, ordered by priority
        rules = (
            db.query(RoutingRule)
            .filter(
                RoutingRule.hotel_id == hotel_id,
                RoutingRule.is_active == True,
            )
            .order_by(RoutingRule.priority_level.desc())
            .all()
        )

        matched_rule = None
        assigned_staff = []

        for rule in rules:
            # Check if rule matches
            match = False

            if rule.rule_type == RoutingRuleType.KEYWORD.value:
                keywords = RuleTestService.parse_json_field(rule.keywords)
                if keywords:
                    match = any(
                        kw.lower() in message_content.lower() for kw in keywords
                    )

            elif rule.rule_type == RoutingRuleType.CATEGORY.value:
                if category:
                    match = rule.category == category

            elif rule.rule_type == RoutingRuleType.PRIORITY.value:
                if priority:
                    match = rule.priority == priority

            elif rule.rule_type == RoutingRuleType.MANUAL.value:
                # Manual rule always matches if reached
                match = True

            if match:
                matched_rule = rule
                # Get assigned staff
                staff_ids = RuleTestService.parse_json_field(rule.target_staff_ids)
                if staff_ids:
                    assigned_staff = (
                        db.query(Staff)
                        .filter(
                            Staff.id.in_(staff_ids),
                            Staff.status == StaffStatus.ACTIVE.value,
                            Staff.is_available == True,
                        )
                        .all()
                    )
                break

        return {
            "matched_rule": {
                "id": matched_rule.id if matched_rule else None,
                "name": matched_rule.name if matched_rule else "默认规则",
                "type": matched_rule.rule_type if matched_rule else "default",
                "priority_level": matched_rule.priority_level if matched_rule else 0,
            },
            "assigned_staff": [
                {"id": s.id, "name": s.name, "department": s.department}
                for s in assigned_staff
            ],
            "message_content": message_content,
            "category": category,
            "priority": priority,
        }

    @staticmethod
    def get_rule_summary(db: Session, hotel_id: str) -> List[Dict[str, Any]]:
        """
        Get summary of all rules for a hotel

        Args:
            db: Database session
            hotel_id: Hotel ID

        Returns:
            List of rule summaries
        """
        rules = (
            db.query(RoutingRule)
            .filter(RoutingRule.hotel_id == hotel_id)
            .order_by(RoutingRule.priority_level.desc())
            .all()
        )

        summaries = []
        for rule in rules:
            keywords = RuleTestService.parse_json_field(rule.keywords)
            staff_ids = RuleTestService.parse_json_field(rule.target_staff_ids)

            # Get staff count
            staff_count = (
                db.query(Staff)
                .filter(
                    Staff.id.in_(staff_ids),
                    Staff.status == StaffStatus.ACTIVE.value,
                )
                .count()
            )

            summaries.append({
                "id": rule.id,
                "name": rule.name,
                "type": rule.rule_type,
                "keywords": keywords,
                "category": rule.category,
                "priority": rule.priority,
                "target_staff_count": staff_count,
                "rule_priority": rule.priority_level,
                "is_active": rule.is_active,
            })

        return summaries


rule_test_service = RuleTestService()
