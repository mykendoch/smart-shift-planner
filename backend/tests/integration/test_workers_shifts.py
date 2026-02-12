"""Integration tests for workers and shifts API endpoints.

Tests cover:
- Worker CRUD operations (create, list)
- Shift logging and retrieval
- Income guarantee top-up calculation
"""
import pytest
from datetime import datetime, timedelta


def test_create_worker(client):
    """Test creating a new worker via API."""
    response = client.post("/api/v1/workers", json={
        "name": "Alice Smith",
        "email": "alice@example.com"
    })
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Alice Smith"
    assert data["email"] == "alice@example.com"
    assert "id" in data


def test_create_worker_duplicate_email(client, sample_worker):
    """Test that duplicate emails are rejected."""
    response = client.post("/api/v1/workers", json={
        "name": "Another User",
        "email": sample_worker.email
    })
    assert response.status_code == 400
    assert "already exists" in response.json()["detail"]


def test_list_workers(client, sample_worker):
    """Test listing workers."""
    response = client.get("/api/v1/workers")
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 1
    assert any(w["id"] == sample_worker.id for w in data)


def test_create_shift(client, sample_worker):
    """Test creating a shift via API."""
    start = datetime.utcnow()
    end = start + timedelta(hours=5)
    
    response = client.post("/api/v1/shifts", json={
        "worker_id": sample_worker.id,
        "start_time": start.isoformat(),
        "end_time": end.isoformat(),
        "predicted_earnings": 75.0
    })
    assert response.status_code == 201
    data = response.json()
    assert data["worker_id"] == sample_worker.id
    assert data["predicted_earnings"] == 75.0


def test_create_shift_invalid_worker(client):
    """Test that shifts for non-existent workers are rejected."""
    start = datetime.utcnow()
    response = client.post("/api/v1/shifts", json={
        "worker_id": 9999,
        "start_time": start.isoformat(),
        "predicted_earnings": 50.0
    })
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()


def test_list_shifts(client, sample_shift):
    """Test listing shifts."""
    response = client.get("/api/v1/shifts")
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 1
    assert any(s["id"] == sample_shift.id for s in data)


def test_compute_topup_below_threshold(client, db, sample_worker):
    """Test income guarantee top-up calculation when earnings fall below guarantee.
    
    With 90% threshold and predicted=$100:
    - If actual=$80, top-up should be $10 (90% of 100 = 90, gap = 90-80)
    """
    from src.models import Shift
    
    now = datetime.utcnow()
    shift = Shift(
        worker_id=sample_worker.id,
        start_time=now,
        end_time=now + timedelta(hours=5),
        earnings=80.0,  # Actual earnings
        predicted_earnings=100.0  # Predicted earnings
    )
    db.add(shift)
    db.commit()
    db.refresh(shift)
    
    response = client.get(f"/api/v1/shifts/{shift.id}/topup")
    assert response.status_code == 200
    data = response.json()
    
    # Expected: (100 * 0.9) - 80 = 90 - 80 = 10
    assert data["top_up"] == pytest.approx(10.0, abs=0.01)


def test_compute_topup_meets_guarantee(client, db, sample_worker):
    """Test top-up when actual earnings meet/exceed guarantee threshold.
    
    With 90% threshold and predicted=$100:
    - If actual=$95, top-up should be $0 (95 >= 90)
    """
    from src.models import Shift
    
    now = datetime.utcnow()
    shift = Shift(
        worker_id=sample_worker.id,
        start_time=now,
        end_time=now + timedelta(hours=5),
        earnings=95.0,  # Exceeds guarantee
        predicted_earnings=100.0
    )
    db.add(shift)
    db.commit()
    db.refresh(shift)
    
    response = client.get(f"/api/v1/shifts/{shift.id}/topup")
    assert response.status_code == 200
    data = response.json()
    
    # Expected: max(0, 90 - 95) = 0
    assert data["top_up"] == 0.0
