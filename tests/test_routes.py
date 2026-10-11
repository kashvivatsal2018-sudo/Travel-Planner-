"""Unit tests for Flask HTTP routes, forms, and JSON APIs."""
import json
import pytest
from app import create_app
from database.models import Destination


@pytest.fixture
def client():
    app = create_app()
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


def test_home_page(client):
    response = client.get("/")
    assert response.status_code == 200
    assert b"Travel" in response.data
    assert b"Dijkstra" in response.data


def test_destinations_catalog(client):
    response = client.get("/destinations")
    assert response.status_code == 200
    assert b"Dehradun" in response.data
    assert b"Mussoorie" in response.data


def test_destination_detail(client):
    response = client.get("/destination/1")
    assert response.status_code == 200
    assert b"Dehradun" in response.data
    assert b"Top Tourist Attractions" in response.data


def test_destination_not_found(client):
    response = client.get("/destination/99999")
    assert response.status_code == 404


def test_questionnaire_and_recommendation_flow(client):
    # 1. GET Questionnaire
    res_get = client.get("/plan")
    assert res_get.status_code == 200

    # 2. POST Questionnaire
    res_post = client.post("/plan", data={
        "current_city": "Delhi",
        "visited_destinations": ["Dehradun"],
        "interests": ["Mountains", "Nature"],
        "budget": "5000_10000",
        "duration": "2_3_days",
        "companion": "Friends",
        "distance": "within_300",
        "transport": "train"
    }, follow_redirects=True)

    assert res_post.status_code == 200
    # Must arrive at /recommendations
    assert b"Top Destinations Curated For You" in res_post.data
    assert b"Why Recommended" in res_post.data


def test_route_planner_view(client):
    response = client.get("/route?source=Dehradun&destination=Dhanaulti")
    assert response.status_code == 200
    assert b"95.0 km" in response.data or b"95 km" in response.data
    assert b"Mussoorie" in response.data


def test_api_route_calculation(client):
    response = client.post("/api/route", json={
        "source": "Delhi",
        "destination": "Mussoorie"
    })
    assert response.status_code == 200
    data = response.get_json()
    assert data["success"] is True
    assert data["total_distance"] == 285.0
    assert data["path"] == ["Delhi", "Dehradun", "Mussoorie"]
    assert len(data["waypoints"]) == 3


def test_api_budget_calculation(client):
    response = client.post("/api/calculate-budget", json={
        "distance_km": 100,
        "days": 2,
        "travelers": 2,
        "transport_mode": "bus",
        "hotel_tier": "standard",
        "food_tier": "moderate"
    })
    assert response.status_code == 200
    data = response.get_json()
    assert data["success"] is True
    assert "total_estimated_budget" in data["budget"]


def test_api_generate_itinerary(client):
    response = client.post("/api/generate-itinerary", json={
        "destination_id": 2,
        "days": 3
    })
    assert response.status_code == 200
    data = response.get_json()
    assert data["success"] is True
    assert len(data["days"]) == 3
