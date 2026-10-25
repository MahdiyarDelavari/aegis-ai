import unittest
from datetime import datetime, timezone
from unittest.mock import MagicMock, Mock

from fastapi.testclient import TestClient

from backend.main import app
from backend.dependencies import get_db


class TestAnalyticsAPI(unittest.TestCase):

    def setUp(self):
        self.db = MagicMock()

        app.dependency_overrides[get_db] = (
            lambda: self.db
        )

        self.client = TestClient(app)

    def tearDown(self):
        self.client.close()
        app.dependency_overrides.clear()

    def test_health(self):
        response = self.client.get("/api/health")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.json()["status"],
            "ok"
        )

    def test_database_health(self):
        self.db.execute.return_value.fetchone.return_value = (
            1,
        )

        response = self.client.get("/api/health/db")

        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json()["connected"])

    def test_overview(self):
        self.db.execute.return_value.fetchone.return_value = (
            100, 75, 25, 3
        )

        response = self.client.get("/api/overview")

        self.assertEqual(response.status_code, 200)

        data = response.json()

        self.assertEqual(data["total_flows"], 100)
        self.assertEqual(data["attack_flows"], 25)
        self.assertEqual(data["attack_percentage"], 25.0)

    def test_traffic_classes(self):
        self.db.execute.return_value.fetchall.return_value = [
            (0, 75, 100),
            (1, 25, 100)
        ]

        response = self.client.get(
            "/api/traffic/classes"
        )

        self.assertEqual(response.status_code, 200)

        data = response.json()

        self.assertEqual(len(data), 2)
        self.assertEqual(data[1]["name"], "Attack")
        self.assertEqual(data[1]["percentage"], 25.0)

    def test_attack_analytics(self):
        self.db.execute.return_value.fetchall.return_value = [
            ("Exploits", 10, 0.53)
        ]

        response = self.client.get(
            "/api/attacks/top?limit=5"
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.json()[0]["attack_category"],
            "Exploits"
        )

    def test_protocol_analytics(self):
        self.db.execute.return_value.fetchall.return_value = [
            ("tcp", 10, 1000, 2000)
        ]

        response = self.client.get(
            "/api/protocols/top?limit=5"
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.json()[0]["protocol"],
            "tcp"
        )

    def test_invalid_limit(self):
        response = self.client.get(
            "/api/attacks/top?limit=1000"
        )

        self.assertEqual(response.status_code, 422)
        self.db.execute.assert_not_called()

    def test_flow_pagination(self):
        self.db.execute.side_effect = [
            Mock(fetchone=lambda: (1,)),
            Mock(
                fetchall=lambda: [
                    (42, 1, "Exploits", "tcp", 0.5, 100, 300)
                ]
            )
        ]

        response = self.client.get(
            "/api/flows?page=1&size=10&label=1"
        )

        self.assertEqual(response.status_code, 200)

        data = response.json()

        self.assertEqual(data["total"], 1)
        self.assertEqual(data["items"][0]["source_id"], 42)

        # Verify that SQL received bound parameters
        params = self.db.execute.call_args_list[1].args[1]

        self.assertEqual(
            params,
            ("training", 1, 10, 0)
        )

    def test_pipeline_runs(self):
        now = datetime.now(timezone.utc)

        self.db.execute.return_value.fetchall.return_value = [
            (1, "succeeded", 100, 0, now, now)
        ]

        response = self.client.get(
            "/api/pipeline/runs"
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.json()[0]["status"],
            "succeeded"
        )

    def test_cors(self):
        response = self.client.get(
            "/api/health",
            headers={
                "Origin": "http://127.0.0.1:5500"
            }
        )

        self.assertEqual(
            response.headers.get(
                "access-control-allow-origin"
            ),
            "http://127.0.0.1:5500"
        )


if __name__ == "__main__":
    unittest.main()