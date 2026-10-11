"""
Main Application Routes: Home, Destinations Explorer, Destination Detail, and Route Planner.
"""

from flask import Blueprint, render_template, request, session
from database import db
from database.models import Destination, TouristPlace, Restaurant, Review, RouteEdge
from services.route_service import RouteService
from services.budget_service import BudgetService
from services.itinerary_service import ItineraryService

main_bp = Blueprint("main", __name__)


@main_bp.route("/")
def index():
    """Home landing page with hero banner, statistics, featured destinations, and quick actions."""
    destinations = Destination.query.order_by(Destination.rating.desc()).all()
    featured = destinations[:6]
    total_cities = len(destinations)
    total_routes = RouteEdge.query.count() // 2
    total_attractions = TouristPlace.query.count()

    return render_template(
        "index.html",
        featured=featured,
        total_cities=total_cities,
        total_routes=total_routes,
        total_attractions=total_attractions
    )


@main_bp.route("/destinations")
def destinations():
    """Explore and filter all destinations in the catalog."""
    category_filter = request.args.get("category", "").strip()
    search_query = request.args.get("q", "").strip()

    query = Destination.query

    if category_filter and category_filter != "all":
        query = query.filter(
            (Destination.category.ilike(f"%{category_filter}%")) |
            (Destination.secondary_categories.ilike(f"%{category_filter}%"))
        )

    if search_query:
        query = query.filter(
            (Destination.name.ilike(f"%{search_query}%")) |
            (Destination.description.ilike(f"%{search_query}%")) |
            (Destination.tagline.ilike(f"%{search_query}%"))
        )

    all_destinations = query.order_by(Destination.rating.desc()).all()

    # Get distinct categories for the filter pill bar
    categories = ["All", "Mountains", "Nature", "Adventure", "Historical", "Religious", "Cultural", "City/Urban"]

    return render_template(
        "destinations.html",
        destinations=all_destinations,
        selected_category=category_filter or "all",
        search_query=search_query,
        categories=categories
    )


@main_bp.route("/destination/<int:dest_id>")
def destination_detail(dest_id):
    """Detailed destination page with attractions, dining, reviews, and quick planners."""
    destination = db.get_or_404(Destination, dest_id)
    all_cities = [d.name for d in Destination.query.order_by(Destination.name).all()]

    # Source city default from user's travel history or Delhi
    visited = session.get("visited_destinations", [])
    default_source = visited[0] if visited else ("Delhi" if destination.name != "Delhi" else "Chandigarh")

    # Initial itinerary and budget previews
    initial_itinerary = ItineraryService.generate_itinerary(dest_id, duration_days=destination.recommended_days)
    initial_budget = BudgetService.calculate_budget(
        distance_km=250.0,
        days=destination.recommended_days,
        travelers=2,
        hotel_tier="standard",
        food_tier="moderate",
        destination_id=dest_id
    )

    return render_template(
        "destination.html",
        destination=destination,
        all_cities=all_cities,
        default_source=default_source,
        initial_itinerary=initial_itinerary,
        initial_budget=initial_budget
    )


@main_bp.route("/route", methods=["GET", "POST"])
def route_planner():
    """
    Dedicated Route Planner page powered by manual Weighted Graph and Dijkstra's algorithm.
    """
    all_destinations = Destination.query.order_by(Destination.name).all()
    city_names = [d.name for d in all_destinations]

    source = request.args.get("source") or request.form.get("source", "Delhi")
    destination = request.args.get("destination") or request.form.get("destination", "Mussoorie")

    route_data = None
    target_destination = None

    if source and destination:
        route_data = RouteService.find_shortest_route(source, destination)
        target_destination = Destination.query.filter(Destination.name.ilike(destination)).first()

    return render_template(
        "route.html",
        city_names=city_names,
        source=source,
        destination=destination,
        route_data=route_data,
        target_destination=target_destination
    )


@main_bp.route("/itinerary")
def itinerary_page():
    """Standalone itinerary viewer page."""
    dest_name = request.args.get("destination", "Mussoorie")
    days = int(request.args.get("days", 3))

    destination = Destination.query.filter(Destination.name.ilike(dest_name)).first()
    if not destination:
        destination = Destination.query.first()

    itinerary_data = ItineraryService.generate_itinerary(destination.id, duration_days=days)
    all_destinations = Destination.query.order_by(Destination.name).all()

    return render_template(
        "itinerary.html",
        destination=destination,
        itinerary=itinerary_data,
        days=days,
        all_destinations=all_destinations
    )
