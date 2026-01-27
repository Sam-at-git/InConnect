"""
Unit Tests for Services
"""

import pytest
from datetime import datetime, timedelta
from unittest.mock import Mock, AsyncMock, patch
from sqlalchemy.orm import Session

from app.services.routing_service import routing_service
from app.services.auto_ticket_service import AutoTicketService
from app.services.batch_service import BatchOperationService
from app.services.rule_test_service import rule_test_service
from app.models.ticket import TicketStatus, TicketPriority, TicketCategory
from app.models.routing_rule import RoutingRuleType
from app.models.staff import Staff, StaffStatus
from app.models.auto_rule import TriggerType


@pytest.mark.asyncio
class TestRoutingService:
    """Routing service unit tests"""

    async def test_find_available_staff(self, db_session):
        """Test finding available staff for ticket"""
        # Create test staff
        staff1 = Staff(
            id="staff-001",
            hotel_id="hotel-001",
            name="张三",
            role="staff",
            department="客房部",
            status=StaffStatus.ACTIVE.value,
            is_available=True,
        )
        staff2 = Staff(
            id="staff-002",
            hotel_id="hotel-001",
            name="李四",
            role="staff",
            department="客房部",
            status=StaffStatus.ACTIVE.value,
            is_available=False,
        )
        db_session.add(staff1)
        db_session.add(staff2)
        await db_session.commit()

        # Find available staff
        available = await routing_service.find_available_staff(
            db_session,
            hotel_id="hotel-001",
            department="客房部",
        )

        assert len(available) == 1
        assert available[0].id == "staff-001"

    async def test_auto_assign_ticket(self, db_session):
        """Test auto assigning ticket to staff"""
        # Create test staff
        staff = Staff(
            id="staff-003",
            hotel_id="hotel-002",
            name="王五",
            role="staff",
            department="维修部",
            status=StaffStatus.ACTIVE.value,
            is_available=True,
        )
        db_session.add(staff)
        await db_session.commit()

        # Create ticket
        ticket = Ticket(
            id="TK001",
            hotel_id="hotel-002",
            title="维修请求",
            category=TicketCategory.MAINTENANCE.value,
            priority=TicketPriority.P2.value,
            status=TicketStatus.PENDING.value,
        )
        db_session.add(ticket)
        await db_session.commit()

        # Auto assign
        result = await routing_service.auto_assign_ticket(
            db_session,
            ticket_id="TK001",
        )

        assert result.assigned_to == "staff-003"
        assert result.status == TicketStatus.ASSIGNED.value


@pytest.mark.asyncio
class TestAutoTicketService:
    """Auto ticket service unit tests"""

    async def test_check_keyword_trigger(self, db_session):
        """Test keyword trigger detection"""
        # Create auto rule
        from app.models.auto_rule import AutoTicketRule

        rule = AutoTicketRule(
            id="rule-001",
            hotel_id="hotel-003",
            name="空调维修规则",
            trigger_type=TriggerType.KEYWORD.value,
            keywords='["空调", "AC", "冷气"]',
            category=TicketCategory.MAINTENANCE.value,
            priority=TicketPriority.P2.value,
            sla_hours=4,
            is_enabled=True,
        )
        db_session.add(rule)
        await db_session.commit()

        service = AutoTicketService()

        # Test matching message
        result = await service.should_create_ticket(
            db_session,
            hotel_id="hotel-003",
            message_content="房间空调不制冷了",
        )

        assert result.should_create is True
        assert result.rule_id == "rule-001"
        assert result.category == "maintenance"

        # Test non-matching message
        result2 = await service.should_create_ticket(
            db_session,
            hotel_id="hotel-003",
            message_content="你好，请问餐厅几点开门",
        )

        assert result2.should_create is False


@pytest.mark.asyncio
class TestBatchOperationService:
    """Batch operation service unit tests"""

    async def test_batch_assign_tickets(self, db_session):
        """Test batch assigning tickets"""
        # Create staff
        staff = Staff(
            id="staff-batch",
            hotel_id="hotel-batch",
            name="批量员工",
            role="staff",
            department="客房部",
            status=StaffStatus.ACTIVE.value,
            is_available=True,
        )
        db_session.add(staff)
        await db_session.commit()

        # Create tickets
        ticket_ids = []
        for i in range(3):
            ticket = Ticket(
                id=f"TBATCH{i}",
                hotel_id="hotel-batch",
                title=f"批量测试工单{i}",
                category=TicketCategory.OTHER.value,
                priority=TicketPriority.P3.value,
                status=TicketStatus.PENDING.value,
            )
            db_session.add(ticket)
            ticket_ids.append(f"TBATCH{i}")
        await db_session.commit()

        # Batch assign
        service = BatchOperationService()
        result = service.batch_assign_tickets(
            db_session,
            ticket_ids=ticket_ids,
            staff_id="staff-batch",
            comment="批量分配测试",
        )

        assert result.success_count == 3
        assert result.failed_count == 0

    async def test_batch_update_status(self, db_session):
        """Test batch updating ticket status"""
        # Create tickets
        ticket_ids = []
        for i in range(2):
            ticket = Ticket(
                id=f"TSTATUS{i}",
                hotel_id="hotel-status",
                title=f"状态测试工单{i}",
                category=TicketCategory.OTHER.value,
                priority=TicketPriority.P3.value,
                status=TicketStatus.ASSIGNED.value,
            )
            db_session.add(ticket)
            ticket_ids.append(f"TSTATUS{i}")
        await db_session.commit()

        # Batch update status
        service = BatchOperationService()
        result = service.batch_update_status(
            db_session,
            ticket_ids=ticket_ids,
            status=TicketStatus.IN_PROGRESS.value,
            comment="批量状态更新",
        )

        assert result.success_count == 2

        # Verify status was updated
        for ticket_id in ticket_ids:
            ticket = await db_session.get(Ticket, ticket_id)
            assert ticket.status == TicketStatus.IN_PROGRESS.value


@pytest.mark.asyncio
class TestRuleTestService:
    """Rule test service unit tests"""

    def test_parse_json_field(self):
        """Test JSON field parsing"""
        service = rule_test_service

        # Valid JSON
        result = service.parse_json_field('["keyword1", "keyword2"]')
        assert result == ["keyword1", "keyword2"]

        # Invalid JSON
        result2 = service.parse_json_field("invalid json")
        assert result2 == []

        # None
        result3 = service.parse_json_field(None)
        assert result3 == []

    async def test_get_rule_summary(self, db_session):
        """Test getting rule summary"""
        # Create test rule
        from app.models.routing_rule import RoutingRule

        rule = RoutingRule(
            id="rule-test-001",
            hotel_id="hotel-test",
            name="测试规则",
            rule_type=RoutingRuleType.KEYWORD.value,
            keywords='["测试"]',
            target_staff_ids='["staff-001"]',
            priority_level=10,
            is_active=True,
        )
        db_session.add(rule)
        await db_session.commit()

        # Get summary
        service = rule_test_service
        summary = service.get_rule_summary(db_session, "hotel-test")

        assert len(summary) == 1
        assert summary[0]["id"] == "rule-test-001"
        assert summary[0]["name"] == "测试规则"


@pytest.mark.asyncio
class TestReportService:
    """Report service unit tests"""

    async def test_get_ticket_report(self, db_session):
        """Test ticket report generation"""
        from app.services.report_service import ReportService
        from app.schemas.report import TimeRangeRequest

        # Create test tickets
        for status in [TicketStatus.PENDING, TicketStatus.ASSIGNED, TicketStatus.RESOLVED]:
            ticket = Ticket(
                id=f"T{status.value}",
                hotel_id="hotel-report",
                title=f"{status.value}工单",
                category=TicketCategory.OTHER.value,
                priority=TicketPriority.P3.value,
                status=status.value,
            )
            if status == TicketStatus.RESOLVED:
                ticket.resolved_at = datetime.utcnow()
            db_session.add(ticket)
        await db_session.commit()

        # Generate report
        service = ReportService()
        report = service.get_ticket_report(
            db_session,
            hotel_id="hotel-report",
            range_request=TimeRangeRequest(range_type="this_week"),
        )

        assert report.total == 3
        assert len(report.by_status) == 3
        assert report.resolved_in_period >= 1

    async def test_get_staff_performance(self, db_session):
        """Test staff performance report"""
        from app.services.report_service import ReportService
        from app.schemas.report import TimeRangeRequest

        # Create staff with tickets
        staff = Staff(
            id="staff-perf",
            hotel_id="hotel-perf",
            name="绩效员工",
            role="staff",
            department="客房部",
            status=StaffStatus.ACTIVE.value,
            is_available=True,
        )
        db_session.add(staff)

        # Create assigned tickets
        for i in range(5):
            status = TicketStatus.RESOLVED if i < 3 else TicketStatus.IN_PROGRESS
            ticket = Ticket(
                id=f"TPERF{i}",
                hotel_id="hotel-perf",
                title=f"绩效工单{i}",
                category=TicketCategory.OTHER.value,
                priority=TicketPriority.P3.value,
                status=status.value,
                assigned_to="staff-perf",
            )
            if status == TicketStatus.RESOLVED:
                ticket.resolved_at = datetime.utcnow()
            db_session.add(ticket)
        await db_session.commit()

        # Generate report
        service = ReportService()
        report = service.get_staff_report(
            db_session,
            hotel_id="hotel-perf",
            range_request=TimeRangeRequest(range_type="this_month"),
        )

        assert report.total_staff == 1
        assert len(report.staff_stats) == 1
        staff_stat = report.staff_stats[0]
        assert staff_stat.total_assigned == 5
        assert staff_stat.total_resolved == 3
        assert staff_stat.resolution_rate == 60.0
