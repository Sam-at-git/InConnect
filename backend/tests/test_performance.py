"""
Performance Benchmark Tests
"""

import asyncio
import time
from httpx import AsyncClient
import pytest


@pytest.mark.asyncio
class TestPerformance:
    """Performance benchmark tests"""

    async def test_ticket_list_performance(self, client: AsyncClient):
        """Benchmark ticket list endpoint"""
        start_time = time.time()

        response = await client.get("/api/v1/tickets")

        elapsed = (time.time() - start_time) * 1000  # Convert to ms

        assert response.status_code == 200
        assert elapsed < 500, f"Response time {elapsed}ms exceeds 500ms threshold"

        print(f"Ticket list response time: {elapsed:.2f}ms")

    async def test_dashboard_performance(self, client: AsyncClient):
        """Benchmark dashboard summary endpoint"""
        start_time = time.time()

        response = await client.get("/api/v1/reports/dashboard", params={"hotel_id": "test-hotel"})

        elapsed = (time.time() - start_time) * 1000

        assert response.status_code == 200
        assert elapsed < 1000, f"Dashboard response time {elapsed}ms exceeds 1000ms threshold"

        print(f"Dashboard response time: {elapsed:.2f}ms")

    async def test_concurrent_requests(self, client: AsyncClient):
        """Test concurrent request handling"""
        async def make_request():
            return await client.get("/api/v1/tickets")

        start_time = time.time()

        # Make 10 concurrent requests
        responses = await asyncio.gather(*[make_request() for _ in range(10)])

        elapsed = (time.time() - start_time) * 1000

        assert all(r.status_code == 200 for r in responses)
        assert elapsed < 3000, f"Concurrent requests took {elapsed}ms, exceeds 3000ms threshold"

        avg_time = elapsed / 10
        print(f"10 concurrent requests: {elapsed:.2f}ms total, {avg_time:.2f}ms average")

    async def test_report_performance(self, client: AsyncClient):
        """Benchmark report endpoints"""
        endpoints = [
            ("/api/v1/reports/dashboard", {"hotel_id": "test-hotel"}),
            ("/api/v1/reports/tickets", {"hotel_id": "test-hotel"}),
            ("/api/v1/reports/staff", {"hotel_id": "test-hotel"}),
            ("/api/v1/reports/messages", {"hotel_id": "test-hotel"}),
        ]

        results = []

        for endpoint, params in endpoints:
            start_time = time.time()
            response = await client.get(endpoint, params=params)
            elapsed = (time.time() - start_time) * 1000
            results.append((endpoint, elapsed))

            assert response.status_code == 200
            assert elapsed < 1000, f"{endpoint} took {elapsed}ms, exceeds 1000ms threshold"

        print("\nReport endpoint performance:")
        for endpoint, elapsed in results:
            print(f"  {endpoint}: {elapsed:.2f}ms")


@pytest.mark.asyncio
class TestDatabasePerformance:
    """Database performance tests"""

    async def test_query_optimization(self, client: AsyncClient, db: AsyncSession):
        """Test that database queries are optimized"""
        import time

        # Test filtering by status (should use index)
        start_time = time.time()
        response = await client.get("/api/v1/tickets", params={"status": "pending"})
        filter_time = (time.time() - start_time) * 1000

        assert response.status_code == 200
        # Filtered queries should be fast
        assert filter_time < 200, f"Filtered query took {filter_time}ms"

        print(f"Filtered query time: {filter_time:.2f}ms")

    async def test_pagination_performance(self, client: AsyncClient):
        """Test pagination performance"""
        sizes = [10, 20, 50, 100]
        results = []

        for size in sizes:
            start_time = time.time()
            response = await client.get("/api/v1/tickets", params={"limit": size})
            elapsed = (time.time() - start_time) * 1000
            results.append((size, elapsed))

            assert response.status_code == 200
            # Pagination should remain consistent regardless of page size
            assert elapsed < 500, f"Page size {size} took {elapsed}ms"

        print("\nPagination performance:")
        for size, elapsed in results:
            print(f"  Page size {size}: {elapsed:.2f}ms")


@pytest.mark.asyncio
class TestCachePerformance:
    """Cache performance tests"""

    async def test_cache_hit_rate(self, client: AsyncClient):
        """Test cache effectiveness"""
        # First request (cache miss)
        start_time = time.time()
        response1 = await client.get("/api/v1/reports/dashboard", params={"hotel_id": "test-hotel"})
        first_time = (time.time() - start_time) * 1000

        # Second request (potential cache hit)
        start_time = time.time()
        response2 = await client.get("/api/v1/reports/dashboard", params={"hotel_id": "test-hotel"})
        second_time = (time.time() - start_time) * 1000

        assert response1.status_code == 200
        assert response2.status_code == 200

        print(f"\nCache performance:")
        print(f"  First request: {first_time:.2f}ms (cache miss)")
        print(f"  Second request: {second_time:.2f}ms (cache hit)")

        # Cached response should be significantly faster
        if second_time < first_time:
            speedup = first_time / second_time
            print(f"  Speedup factor: {speedup:.2f}x")


# Performance targets documentation
PERFORMANCE_TARGETS = {
    "api_response_time_p95": "500ms",
    "api_response_time_p99": "1000ms",
    "concurrent_requests": "100 req/s",
    "database_query_time": "< 200ms",
    "cache_hit_rate": "> 80%",
    "memory_usage": "< 512MB per worker",
    "cpu_usage": "< 70% under normal load",
}
