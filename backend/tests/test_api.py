"""
API Integration Tests
"""

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession


@pytest.mark.asyncio
class TestHealthAPI:
    """Health check API tests"""

    async def test_health_check(self, client: AsyncClient):
        """Test health check endpoint"""
        response = await client.get("/api/v1/health")
        assert response.status_code == 200
        data = response.json()
        assert data["data"]["status"] == "healthy"


@pytest.mark.asyncio
class TestTicketsAPI:
    """Tickets API tests"""

    async def test_list_tickets(self, client: AsyncClient):
        """Test listing tickets"""
        response = await client.get("/api/v1/tickets")
        assert response.status_code == 200
        data = response.json()
        assert "data" in data

    async def test_create_ticket(self, client: AsyncClient, db: AsyncSession):
        """Test creating a ticket"""
        ticket_data = {
            "hotel_id": "test-hotel",
            "title": "测试工单",
            "description": "这是一个测试工单",
            "category": "maintenance",
            "priority": "P2",
        }
        response = await client.post("/api/v1/tickets", json=ticket_data)
        assert response.status_code == 200
        data = response.json()
        assert data["data"]["title"] == "测试工单"

    async def test_get_ticket_by_id(self, client: AsyncClient, db: AsyncSession):
        """Test getting ticket by ID"""
        # First create a ticket
        ticket_data = {
            "hotel_id": "test-hotel",
            "title": "查询测试工单",
            "category": "inquiry",
            "priority": "P3",
        }
        create_response = await client.post("/api/v1/tickets", json=ticket_data)
        ticket_id = create_response.json()["data"]["id"]

        # Then get it
        response = await client.get(f"/api/v1/tickets/{ticket_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["data"]["id"] == ticket_id


@pytest.mark.asyncio
class TestReportsAPI:
    """Reports API tests"""

    async def test_dashboard_summary(self, client: AsyncClient):
        """Test dashboard summary endpoint"""
        response = await client.get("/api/v1/reports/dashboard", params={"hotel_id": "test-hotel"})
        assert response.status_code == 200
        data = response.json()
        assert "total_tickets" in data["data"]

    async def test_ticket_report(self, client: AsyncClient):
        """Test ticket report endpoint"""
        response = await client.get("/api/v1/reports/tickets", params={"hotel_id": "test-hotel"})
        assert response.status_code == 200
        data = response.json()
        assert "total" in data["data"]

    async def test_staff_report(self, client: AsyncClient):
        """Test staff report endpoint"""
        response = await client.get("/api/v1/reports/staff", params={"hotel_id": "test-hotel"})
        assert response.status_code == 200
        data = response.json()
        assert "total_staff" in data["data"]


@pytest.mark.asyncio
class TestRulesAPI:
    """Rules API tests"""

    async def test_get_rules_summary(self, client: AsyncClient):
        """Test getting rules summary"""
        response = await client.get("/api/v1/rules/summary", params={"hotel_id": "test-hotel"})
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data["data"], list)

    async def test_rule_matching(self, client: AsyncClient):
        """Test rule matching"""
        test_request = {
            "message_content": "房间空调坏了，需要维修",
            "category": "maintenance",
        }
        response = await client.post(
            "/api/v1/rules/test",
            params={"hotel_id": "test-hotel"},
            json=test_request
        )
        assert response.status_code == 200
        data = response.json()
        assert "matched_rule" in data["data"]
        assert "assigned_staff" in data["data"]


@pytest.mark.asyncio
class TestPermissionsAPI:
    """Permissions API tests"""

    async def test_list_permissions(self, client: AsyncClient):
        """Test listing all permissions"""
        response = await client.get("/api/v1/permissions/list")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data["data"], list)

    async def test_list_roles(self, client: AsyncClient):
        """Test listing all roles"""
        response = await client.get("/api/v1/permissions/roles")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data["data"], list)

    async def test_get_permission_matrix(self, client: AsyncClient):
        """Test getting permission matrix"""
        response = await client.get("/api/v1/permissions/matrix")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data["data"], dict)


@pytest.mark.asyncio
class TestAuditAPI:
    """Audit API tests"""

    async def test_get_audit_logs(self, client: AsyncClient):
        """Test getting audit logs"""
        response = await client.get(
            "/api/v1/audit",
            params={"hotel_id": "test-hotel", "limit": 50}
        )
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data["data"], list)

    async def test_get_audit_summary(self, client: AsyncClient):
        """Test getting audit summary"""
        response = await client.get(
            "/api/v1/audit/summary",
            params={"hotel_id": "test-hotel", "days": 7}
        )
        assert response.status_code == 200
        data = response.json()
        assert "total_actions" in data["data"]


@pytest.mark.asyncio
class TestBatchAPI:
    """Batch operations API tests"""

    async def test_batch_assign_tickets(self, client: AsyncClient):
        """Test batch assigning tickets"""
        # First create some tickets
        ticket_ids = []
        for i in range(3):
            ticket_data = {
                "hotel_id": "test-hotel",
                "title": f"批量测试工单 {i+1}",
                "category": "maintenance",
                "priority": "P3",
            }
            response = await client.post("/api/v1/tickets", json=ticket_data)
            ticket_ids.append(response.json()["data"]["id"])

        # Then batch assign
        assign_request = {
            "ticket_ids": ticket_ids,
            "staff_id": "test-staff",
            "comment": "批量分配测试",
        }
        response = await client.post("/api/v1/batch/assign", json=assign_request)
        assert response.status_code == 200
        data = response.json()
        assert data["data"]["success_count"] >= 0
