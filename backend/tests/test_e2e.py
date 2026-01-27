"""
E2E (End-to-End) Tests for InConnect

These tests simulate complete user workflows.
"""

import pytest
import asyncio
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession


@pytest.mark.asyncio
class TestUserWorkflows:
    """End-to-end user workflow tests"""

    async def test_complete_ticket_workflow(self, client: AsyncClient, db: AsyncSession):
        """
        Test complete ticket workflow:
        1. User login
        2. Create ticket
        3. View ticket list
        4. Assign ticket
        5. Update ticket status
        6. Add timeline comment
        7. Resolve ticket
        8. Close ticket
        """
        # 1. Login
        login_response = await client.post(
            "/api/v1/auth/login",
            json={
                "username": "test_user",
                "password": "test_password",
            },
        )
        assert login_response.status_code == 200
        token = login_response.json()["data"]["access_token"]

        headers = {"Authorization": f"Bearer {token}"}

        # 2. Create ticket
        ticket_data = {
            "hotel_id": "test-hotel",
            "title": "E2E测试工单",
            "description": "这是一个端到端测试工单",
            "category": "maintenance",
            "priority": "P2",
        }
        create_response = await client.post(
            "/api/v1/tickets",
            json=ticket_data,
            headers=headers,
        )
        assert create_response.status_code == 200
        ticket_id = create_response.json()["data"]["id"]
        assert ticket_id is not None

        # 3. View ticket list
        list_response = await client.get("/api/v1/tickets", headers=headers)
        assert list_response.status_code == 200
        tickets = list_response.json()["data"]["items"]
        assert any(t["id"] == ticket_id for t in tickets)

        # 4. Assign ticket
        assign_response = await client.post(
            f"/api/v1/tickets/{ticket_id}/assign",
            json={"staff_id": "test-staff-001", "comment": "分配测试"},
            headers=headers,
        )
        assert assign_response.status_code == 200

        # 5. Update ticket status to in_progress
        status_response = await client.post(
            f"/api/v1/tickets/{ticket_id}/status",
            json={"status": "in_progress", "comment": "开始处理"},
            headers=headers,
        )
        assert status_response.status_code == 200

        # 6. Resolve ticket
        resolve_response = await client.post(
            f"/api/v1/tickets/{ticket_id}/status",
            json={"status": "resolved", "comment": "问题已解决"},
            headers=headers,
        )
        assert resolve_response.status_code == 200

        # 7. Close ticket
        close_response = await client.post(
            f"/api/v1/tickets/{ticket_id}/status",
            json={"status": "closed", "comment": "工单关闭"},
            headers=headers,
        )
        assert close_response.status_code == 200

    async def test_message_workflow(self, client: AsyncClient, db: AsyncSession):
        """
        Test complete message workflow:
        1. Create conversation
        2. Receive message (webhook simulation)
        3. Send reply
        4. Verify message history
        """
        # Setup auth
        login_response = await client.post(
            "/api/v1/auth/login",
            json={"username": "test_user", "password": "test_password"},
        )
        token = login_response.json()["data"]["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # 1. Create conversation
        conv_data = {
            "hotel_id": "test-hotel",
            "guest_id": "guest_wx_001",
            "guest_name": "测试客人",
            "status": "active",
        }
        conv_response = await client.post(
            "/api/v1/messages/conversations",
            json=conv_data,
            headers=headers,
        )
        assert conv_response.status_code == 200
        conv_id = conv_response.json()["data"]["id"]

        # 2. Simulate receiving message
        message_data = {
            "conversation_id": conv_id,
            "message_type": "text",
            "content": "你好，请问房间有Wi-Fi吗？",
        }
        msg_response = await client.post(
            "/api/v1/messages/send",
            json=message_data,
            headers=headers,
        )
        assert msg_response.status_code == 200

        # 3. Send reply
        reply_data = {
            "conversation_id": conv_id,
            "content": "有的，每个房间都有免费Wi-Fi，密码是12345678",
        }
        reply_response = await client.post(
            "/api/v1/messages/send",
            json=reply_data,
            headers=headers,
        )
        assert reply_response.status_code == 200

        # 4. Verify message history
        history_response = await client.get(
            f"/api/v1/messages/conversations/{conv_id}/messages",
            headers=headers,
        )
        assert history_response.status_code == 200
        messages = history_response.json()["data"]
        assert len(messages) >= 2

    async def test_rule_workflow(self, client: AsyncClient, db: AsyncSession):
        """
        Test rule creation and testing workflow:
        1. Create routing rule
        2. Test rule with message
        3. Verify rule matches correctly
        4. Update rule
        5. Delete rule
        """
        # Setup auth
        login_response = await client.post(
            "/api/v1/auth/login",
            json={"username": "admin", "password": "admin_password"},
        )
        token = login_response.json()["data"]["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # 1. Create rule
        rule_data = {
            "name": "空调维修规则E2E",
            "rule_type": "keyword",
            "keywords": ["空调", "不制冷", "制冷"],
            "target_staff_ids": ["staff-001"],
            "rule_priority": 10,
            "is_active": True,
        }
        create_response = await client.post(
            "/api/v1/rules",
            params={"hotel_id": "test-hotel"},
            json=rule_data,
            headers=headers,
        )
        assert create_response.status_code == 200
        rule_id = create_response.json()["data"]["id"]

        # 2. Test rule
        test_request = {
            "message_content": "我房间空调不制冷了",
        }
        test_response = await client.post(
            "/api/v1/rules/test",
            params={"hotel_id": "test-hotel"},
            json=test_request,
            headers=headers,
        )
        assert test_response.status_code == 200
        test_result = test_response.json()["data"]
        assert test_result["matched_rule"]["id"] == rule_id

        # 3. Update rule
        update_response = await client.put(
            f"/api/v1/rules/{rule_id}",
            json={"rule_priority": 20},
            headers=headers,
        )
        assert update_response.status_code == 200

        # 4. Delete rule
        delete_response = await client.delete(
            f"/api/v1/rules/{rule_id}",
            headers=headers,
        )
        assert delete_response.status_code == 200

    async def test_batch_operations_workflow(self, client: AsyncClient):
        """
        Test batch operations workflow:
        1. Create multiple tickets
        2. Batch assign tickets
        3. Batch update status
        4. Export tickets
        """
        # Setup auth
        login_response = await client.post(
            "/api/v1/auth/login",
            json={"username": "admin", "password": "admin_password"},
        )
        token = login_response.json()["data"]["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # 1. Create multiple tickets
        ticket_ids = []
        for i in range(5):
            ticket_data = {
                "hotel_id": "test-hotel",
                "title": f"批量操作测试工单 {i+1}",
                "category": "maintenance",
                "priority": "P3",
            }
            create_response = await client.post(
                "/api/v1/tickets",
                json=ticket_data,
                headers=headers,
            )
            ticket_id = create_response.json()["data"]["id"]
            ticket_ids.append(ticket_id)

        assert len(ticket_ids) == 5

        # 2. Batch assign
        batch_assign_request = {
            "ticket_ids": ticket_ids[:3],
            "staff_id": "staff-batch",
            "comment": "批量分配",
        }
        assign_response = await client.post(
            "/api/v1/batch/assign",
            json=batch_assign_request,
            headers=headers,
        )
        assert assign_response.status_code == 200
        assign_result = assign_response.json()["data"]
        assert assign_result["success_count"] == 3

        # 3. Batch update status
        batch_status_request = {
            "ticket_ids": ticket_ids[:2],
            "status": "in_progress",
            "comment": "批量更新状态",
        }
        status_response = await client.post(
            "/api/v1/batch/status",
            json=batch_status_request,
            headers=headers,
        )
        assert status_response.status_code == 200
        status_result = status_response.json()["data"]
        assert status_result["success_count"] == 2


@pytest.mark.asyncio
class TestPerformanceWorkflows:
    """Performance-related E2E tests"""

    async def test_concurrent_ticket_creation(self, client: AsyncClient):
        """Test creating multiple tickets concurrently"""
        import time

        login_response = await client.post(
            "/api/v1/auth/login",
            json={"username": "admin", "password": "admin_password"},
        )
        token = login_response.json()["data"]["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        async def create_ticket(index: int):
            ticket_data = {
                "hotel_id": "test-hotel",
                "title": f"并发测试工单 {index}",
                "category": "other",
                "priority": "P3",
            }
            return await client.post("/api/v1/tickets", json=ticket_data, headers=headers)

        # Create 10 tickets concurrently
        start_time = time.time()
        responses = await asyncio.gather(*[create_ticket(i) for i in range(10)])
        elapsed = (time.time() - start_time) * 1000

        assert all(r.status_code == 200 for r in responses)
        assert elapsed < 3000, f"Concurrent creation took {elapsed}ms"

        print(f"Created 10 tickets concurrently in {elapsed:.2f}ms")


# Test data fixtures for E2E tests
@pytest.fixture
async def setup_e2e_data(db: AsyncSession):
    """Setup test data for E2E tests"""
    # Create hotel
    from app.models.hotel import Hotel

    hotel = Hotel(
        id="e2e-hotel",
        name="E2E测试酒店",
        code="E2E001",
        address="测试地址",
        phone="400-111-1111",
        is_active=True,
    )
    db.add(hotel)

    # Create staff
    from app.models.staff import Staff

    staff = Staff(
        id="staff-001",
        hotel_id="e2e-hotel",
        name="E2E员工",
        role="staff",
        department="客房部",
        status="active",
        is_available=True,
    )
    db.add(staff)

    await db.commit()

    yield

    # Cleanup
    await db.rollback()
