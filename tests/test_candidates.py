"""
Unit tests for the Candidate Management API.
Run with:  pytest tests/ -v
"""
import pytest
from fastapi.testclient import TestClient

from main import app
from app import database


@pytest.fixture(autouse=True)
def clear_store():
    """Reset the in-memory store before every test."""
    database._store.clear()
    yield
    database._store.clear()


client = TestClient(app)


# ── Helpers ───────────────────────────────────────────────────────────────────

def create_candidate(
    name="Alice",
    email="alice@example.com",
    skill="Python",
    status="applied",
):
    return client.post(
        "/candidates",
        json={"name": name, "email": email, "skill": skill, "status": status},
    )


# ── POST /candidates ──────────────────────────────────────────────────────────

class TestCreateCandidate:
    def test_create_returns_201(self):
        res = create_candidate()
        assert res.status_code == 201

    def test_create_returns_candidate_fields(self):
        res = create_candidate()
        body = res.json()
        assert body["name"] == "Alice"
        assert body["email"] == "alice@example.com"
        assert body["skill"] == "Python"
        assert body["status"] == "applied"
        assert "id" in body

    def test_create_default_status_is_applied(self):
        res = client.post(
            "/candidates",
            json={"name": "Bob", "email": "bob@example.com", "skill": "Go"},
        )
        assert res.status_code == 201
        assert res.json()["status"] == "applied"

    def test_create_invalid_email_returns_422(self):
        res = client.post(
            "/candidates",
            json={"name": "Bad", "email": "not-an-email", "skill": "Java"},
        )
        assert res.status_code == 422

    def test_create_invalid_status_returns_422(self):
        res = client.post(
            "/candidates",
            json={
                "name": "Bad",
                "email": "bad@example.com",
                "skill": "Java",
                "status": "hired",          # invalid
            },
        )
        assert res.status_code == 422

    def test_create_empty_name_returns_422(self):
        res = client.post(
            "/candidates",
            json={"name": "   ", "email": "x@example.com", "skill": "C++"},
        )
        assert res.status_code == 422

    def test_create_empty_skill_returns_422(self):
        res = client.post(
            "/candidates",
            json={"name": "Alice", "email": "alice@example.com", "skill": "   "},
        )
        assert res.status_code == 422

    def test_create_all_valid_statuses(self):
        for st in ("applied", "interview", "selected", "rejected"):
            res = client.post(
                "/candidates",
                json={
                    "name": f"Candidate {st}",
                    "email": f"{st}@example.com",
                    "skill": "Python",
                    "status": st,
                },
            )
            assert res.status_code == 201, f"Failed for status={st}"
            assert res.json()["status"] == st


# ── GET /candidates ───────────────────────────────────────────────────────────

class TestGetCandidates:
    def test_empty_list(self):
        res = client.get("/candidates")
        assert res.status_code == 200
        assert res.json() == []

    def test_returns_all_candidates(self):
        create_candidate("A", "a@a.com", "Python")
        create_candidate("B", "b@b.com", "Go")
        res = client.get("/candidates")
        assert res.status_code == 200
        assert len(res.json()) == 2

    def test_filter_by_status(self):
        create_candidate("A", "a@a.com", "Python", status="applied")
        create_candidate("B", "b@b.com", "Go", status="interview")
        create_candidate("C", "c@c.com", "Rust", status="interview")

        res = client.get("/candidates?status=interview")
        assert res.status_code == 200
        results = res.json()
        assert len(results) == 2
        assert all(r["status"] == "interview" for r in results)

    def test_filter_returns_empty_when_no_match(self):
        create_candidate("A", "a@a.com", "Python", status="applied")
        res = client.get("/candidates?status=selected")
        assert res.status_code == 200
        assert res.json() == []

    def test_filter_invalid_status_returns_422(self):
        res = client.get("/candidates?status=unknown")
        assert res.status_code == 422


# ── PUT /candidates/{id}/status ───────────────────────────────────────────────

class TestUpdateStatus:
    def test_update_status_success(self):
        candidate_id = create_candidate().json()["id"]
        res = client.put(
            f"/candidates/{candidate_id}/status",
            json={"status": "interview"},
        )
        assert res.status_code == 200
        assert res.json()["status"] == "interview"

    def test_update_reflects_in_get(self):
        candidate_id = create_candidate().json()["id"]
        client.put(
            f"/candidates/{candidate_id}/status",
            json={"status": "selected"},
        )
        res = client.get("/candidates")
        updated = next(c for c in res.json() if c["id"] == candidate_id)
        assert updated["status"] == "selected"

    def test_update_nonexistent_returns_404(self):
        res = client.put(
            "/candidates/00000000-0000-0000-0000-000000000000/status",
            json={"status": "interview"},
        )
        assert res.status_code == 404

    def test_update_invalid_status_returns_422(self):
        candidate_id = create_candidate().json()["id"]
        res = client.put(
            f"/candidates/{candidate_id}/status",
            json={"status": "promoted"},       # invalid
        )
        assert res.status_code == 422

    def test_update_preserves_other_fields(self):
        original = create_candidate("Alice", "alice@example.com", "Python").json()
        candidate_id = original["id"]
        updated = client.put(
            f"/candidates/{candidate_id}/status",
            json={"status": "rejected"},
        ).json()
        assert updated["name"] == original["name"]
        assert updated["email"] == original["email"]
        assert updated["skill"] == original["skill"]
        assert updated["status"] == "rejected"
