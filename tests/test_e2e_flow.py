"""
End-to-End Workflow Verification Test:
Simulates the entire primary user journey from Guest/Login through questionnaire,
recommendation, destination selection, budget calculation, itinerary generation,
and Dijkstra shortest route calculation.
"""

import pytest
from app import create_app
from database.models import Destination


@pytest.fixture
def client():
    app = create_app()
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


def test_full_primary_user_journey(client):
    """
    Simulates:
    1. Open Home page
    2. Continue as Guest (or Register)
    3. Fill Questionnaire (Travel History: Dehradun, Interests: Mountains/Nature, Budget: 5k-10k, 3 Days)
    4. View Recommendations (Mussoorie, Dhanaulti, etc.)
    5. Select Destination (Mussoorie) & View Destination Details
    6. Compute Dijkstra Shortest Route (Dehradun -> Mussoorie = 35 km, or Delhi -> Mussoorie = 285 km)
    7. Calculate Dynamic Budget for 2 travelers, 3 days, standard hotel, train
    8. Generate 3-Day Itinerary with Attractions and Dining
    """
    # Step 1: Open Website Home Page
    res_home = client.get("/")
    assert res_home.status_code == 200
    assert b"Travel" in res_home.data

    # Step 2: Continue as Guest
    res_guest = client.get("/guest", follow_redirects=True)
    assert res_guest.status_code == 200
    assert b"Personalized Travel Questionnaire" in res_guest.data

    # Step 3: Submit Travel Questionnaire
    res_plan = client.post("/plan", data={
        "current_city": "Dehradun",
        "visited_destinations": ["Dehradun", "Rishikesh"],
        "interests": ["Mountains", "Nature"],
        "budget": "5000_10000",
        "duration": "2_3_days",
        "companion": "Friends",
        "distance": "within_100",
        "transport": "car"
    }, follow_redirects=True)
    assert res_plan.status_code == 200

    # Step 4: Verify Recommendations page loaded with ranked cards
    assert b"Top Destinations Curated For You" in res_plan.data
    assert b"Mussoorie" in res_plan.data or b"Dhanaulti" in res_plan.data
    assert b"Why Recommended for You" in res_plan.data

    # Step 5: Select Destination: Mussoorie (id=2)
    res_dest = client.get("/destination/2")
    assert res_dest.status_code == 200
    assert b"Mussoorie" in res_dest.data
    assert b"Kempty Falls" in res_dest.data
    assert b"Gun Hill" in res_dest.data
    assert b"Cafe By The Way" in res_dest.data

    # Step 6: Execute Dijkstra Shortest Path: Dehradun -> Dhanaulti
    res_route = client.post("/api/route", json={
        "source": "Dehradun",
        "destination": "Dhanaulti"
    })
    assert res_route.status_code == 200
    route_json = res_route.get_json()
    assert route_json["success"] is True
    assert route_json["total_distance"] == 95.0
    assert route_json["path"] == ["Dehradun", "Mussoorie", "Dhanaulti"]
    assert len(route_json["waypoints"]) == 3
    assert len(route_json["relaxation_steps"]) > 0

    # Step 7: Calculate Dynamic Trip Budget
    res_budget = client.post("/api/calculate-budget", json={
        "distance_km": 95.0,
        "days": 3,
        "travelers": 2,
        "transport_mode": "car",
        "hotel_tier": "standard",
        "food_tier": "moderate",
        "destination_id": 2
    })
    assert res_budget.status_code == 200
    budget_json = res_budget.get_json()
    assert budget_json["success"] is True
    b = budget_json["budget"]
    assert b["total_estimated_budget"] > 0
    assert b["breakdown"]["transportation"] > 0
    assert b["breakdown"]["accommodation"] > 0
    assert b["breakdown"]["food"] > 0

    # Step 8: Generate Day-Wise Itinerary for 3 days
    res_itinerary = client.post("/api/generate-itinerary", json={
        "destination_id": 2,
        "days": 3
    })
    assert res_itinerary.status_code == 200
    itinerary_json = res_itinerary.get_json()
    assert itinerary_json["success"] is True
    assert len(itinerary_json["days"]) == 3
    day1_slots = itinerary_json["days"][0]["slots"]
    assert len(day1_slots) >= 4
