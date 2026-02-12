"""Tests for ML prediction endpoints and models.

Tests cover:
- Earnings prediction
- Demand forecasting
- Shift optimization and recommendations
"""
import pytest
from datetime import datetime


def test_predict_earnings(client):
    """Test earnings prediction endpoint."""
    response = client.get(
        "/api/v1/predictions/earnings",
        params={
            "hour": 18,
            "day_of_week": 4,  # Friday
            "location": "downtown",
            "demand_level": 0.8,
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert data["hour"] == 18
    assert data["location"] == "downtown"
    assert data["predicted_hourly_earnings"] > 0


def test_predict_earnings_peak_vs_offpeak(client):
    """Test that peak hours predict higher earnings than off-peak."""
    # Peak evening
    peak_response = client.get(
        "/api/v1/predictions/earnings",
        params={"hour": 18, "day_of_week": 5, "location": "downtown", "demand_level": 1.0}
    )
    peak_earnings = peak_response.json()["predicted_hourly_earnings"]
    
    # Off-peak night
    offpeak_response = client.get(
        "/api/v1/predictions/earnings",
        params={"hour": 2, "day_of_week": 5, "location": "downtown", "demand_level": 0.2}
    )
    offpeak_earnings = offpeak_response.json()["predicted_hourly_earnings"]
    
    assert peak_earnings > offpeak_earnings


def test_forecast_demand(client):
    """Test demand forecasting endpoint."""
    response = client.get(
        "/api/v1/predictions/demand-forecast",
        params={"location": "downtown"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["location"] == "downtown"
    assert "hourly_demand" in data
    assert len(data["hourly_demand"]) == 24
    assert all(0 <= d <= 1 for d in data["hourly_demand"].values())
    
    # Should have peak hours identified
    assert "peak_hours" in data
    assert len(data["peak_hours"]) > 0


def test_recommend_shifts(client):
    """Test shift recommendation endpoint."""
    response = client.get(
        "/api/v1/predictions/recommend-shifts",
        params={
            "location": "downtown",
            "date_type": "weekday",
            "duration_hours": 4.0,
            "top_n": 3,
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data["recommendations"]) == 3
    
    # Check that recommendations are sorted by earnings (highest first)
    earnings = [r["predicted_earnings"] for r in data["recommendations"]]
    assert earnings == sorted(earnings, reverse=True)


def test_recommend_shifts_weekend_higher_earnings(client):
    """Test that weekend recommendations predict higher earnings."""
    weekday_response = client.get(
        "/api/v1/predictions/recommend-shifts",
        params={
            "location": "downtown",
            "date_type": "weekday",
            "duration_hours": 4.0,
            "top_n": 1,
        }
    )
    weekday_earnings = weekday_response.json()["recommendations"][0]["predicted_earnings"]
    
    weekend_response = client.get(
        "/api/v1/predictions/recommend-shifts",
        params={
            "location": "downtown",
            "date_type": "weekend",
            "duration_hours": 4.0,
            "top_n": 1,
        }
    )
    weekend_earnings = weekend_response.json()["recommendations"][0]["predicted_earnings"]
    
    # Weekend should generally have higher earnings due to demand multipliers
    assert weekend_earnings >= weekday_earnings
