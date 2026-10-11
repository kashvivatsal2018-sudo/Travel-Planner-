"""
REST API Endpoints: JSON APIs for asynchronous frontend calculations and Leaflet map data.
"""

from flask import Blueprint, request, jsonify, session
from services.route_service import RouteService
from services.budget_service import BudgetService
from services.itinerary_service import ItineraryService
from database.models import Destination

api_bp = Blueprint("api", __name__, url_prefix="/api")


@api_bp.route("/route", methods=["POST"])
def get_route():
    """
    Calculate Dijkstra shortest path between source and destination.
    Returns: JSON with path, distance, waypoints, segments, and relaxation steps.
    """
    data = request.get_json() or {}
    source = data.get("source", "").strip()
    destination = data.get("destination", "").strip()

    if not source or not destination:
        return jsonify({"success": False, "error": "Both source and destination cities are required."}), 400

    result = RouteService.find_shortest_route(source, destination)
    status_code = 200 if result.get("success") else 404
    return jsonify(result), status_code


@api_bp.route("/calculate-budget", methods=["POST"])
def calculate_budget():
    """
    Calculate dynamic travel budget breakdown based on user inputs.
    """
    data = request.get_json() or {}
    try:
        distance_km = float(data.get("distance_km", 250.0))
        days = int(data.get("days", 3))
        travelers = int(data.get("travelers", 2))
        transport_mode = data.get("transport_mode", "train")
        hotel_tier = data.get("hotel_tier", "standard")
        food_tier = data.get("food_tier", "moderate")
        destination_id = data.get("destination_id")
        if destination_id is not None:
            destination_id = int(destination_id)

        result = BudgetService.calculate_budget(
            distance_km=distance_km,
            days=days,
            travelers=travelers,
            transport_mode=transport_mode,
            hotel_tier=hotel_tier,
            food_tier=food_tier,
            destination_id=destination_id
        )
        return jsonify({"success": True, "budget": result}), 200
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 400


@api_bp.route("/generate-itinerary", methods=["POST"])
def generate_itinerary():
    """
    Generate dynamic day-wise itinerary for destination and duration.
    """
    data = request.get_json() or {}
    destination_id = data.get("destination_id")
    days = data.get("days", 3)

    if not destination_id:
        return jsonify({"success": False, "error": "destination_id is required."}), 400

    try:
        result = ItineraryService.generate_itinerary(int(destination_id), duration_days=int(days))
        status_code = 200 if result.get("success") else 404
        return jsonify(result), status_code
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 400


@api_bp.route("/destinations", methods=["GET"])
def get_destinations_api():
    """Return summary list of all destinations for frontend dropdowns/search."""
    destinations = Destination.query.order_by(Destination.name).all()
    return jsonify({
        "success": True,
        "count": len(destinations),
        "destinations": [
            {
                "id": d.id,
                "name": d.name,
                "category": d.category,
                "rating": d.rating,
                "latitude": d.latitude,
                "longitude": d.longitude
            }
            for d in destinations
        ]
    })


@api_bp.route("/travel-history", methods=["POST"])
def update_travel_history():
    """Add or remove a visited destination from session."""
    data = request.get_json() or {}
    city = data.get("city", "").strip()
    action = data.get("action", "add")  # "add" or "remove"

    if not city:
        return jsonify({"success": False, "error": "City name is required."}), 400

    visited = session.get("visited_destinations", [])
    if action == "add":
        if city not in visited:
            visited.append(city)
    elif action == "remove":
        if city in visited:
            visited.remove(city)

    session["visited_destinations"] = visited
    return jsonify({"success": True, "visited_destinations": visited})
