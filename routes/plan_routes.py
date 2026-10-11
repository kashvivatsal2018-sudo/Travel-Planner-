"""
Planning and Recommendation Routes: Questionnaire, Recommendation results, and User Profile.
"""

from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from database import db
from database.models import Destination, User, TravelHistory
from services.route_service import RouteService
from recommendation.recommender import RecommendationEngine

plan_bp = Blueprint("plan", __name__)


@plan_bp.route("/plan", methods=["GET", "POST"])
def plan_trip():
    """Interactive questionnaire collecting user travel preferences and history."""
    all_destinations = Destination.query.order_by(Destination.name).all()
    city_names = [d.name for d in all_destinations]

    if request.method == "POST":
        visited = request.form.getlist("visited_destinations")
        interests = request.form.getlist("interests")
        budget = request.form.get("budget", "5000_10000")
        duration = request.form.get("duration", "2_3_days")
        companion = request.form.get("companion", "Friends")
        distance = request.form.get("distance", "any")
        transport = request.form.get("transport", "train")
        current_city = request.form.get("current_city", "Delhi")

        if not interests:
            # Default to Nature and Mountains if user didn't select
            interests = ["Mountains", "Nature"]

        # Save to session
        preferences = {
            "visited_destinations": visited,
            "interests": interests,
            "budget": budget,
            "duration": duration,
            "companion": companion,
            "distance": distance,
            "transport": transport,
            "current_city": current_city
        }
        session["plan_preferences"] = preferences
        session["visited_destinations"] = visited

        # If user is logged in, save to User model and TravelHistory table
        user_id = session.get("user_id")
        if user_id:
            user = User.query.get(user_id)
            if user:
                user.budget = budget
                user.trip_duration = duration
                user.travel_companion = companion
                user.transport_preference = transport
                user.preferred_distance = distance
                user.set_categories(interests)

                # Save travel history records
                for v_city in visited:
                    dest = Destination.query.filter(Destination.name.ilike(v_city)).first()
                    existing_history = TravelHistory.query.filter_by(
                        user_id=user.id, destination_name=v_city
                    ).first()
                    if not existing_history:
                        th = TravelHistory(
                            user_id=user.id,
                            destination_id=dest.id if dest else None,
                            destination_name=v_city
                        )
                        db.session.add(th)
                db.session.commit()

        flash("Your travel profile has been updated! Here are your tailored destination recommendations.", "success")
        return redirect(url_for("plan.recommendations"))

    # Load previously stored preferences if present
    saved_prefs = session.get("plan_preferences", {})
    return render_template(
        "plan.html",
        city_names=city_names,
        saved_prefs=saved_prefs
    )


@plan_bp.route("/recommendations")
def recommendations():
    """Display recommended destinations ranked by transparent content-based scoring."""
    prefs = session.get("plan_preferences")
    if not prefs:
        flash("Please complete the travel questionnaire first to view personalized recommendations.", "info")
        return redirect(url_for("plan.plan_trip"))

    all_destinations = Destination.query.all()
    graph = RouteService.get_or_build_graph()
    recommender = RecommendationEngine(graph=graph)

    recommended_results = recommender.recommend(
        destinations=all_destinations,
        preferred_categories=prefs.get("interests", ["Mountains", "Nature"]),
        budget_key=prefs.get("budget", "5000_10000"),
        duration_key=prefs.get("duration", "2_3_days"),
        travel_companion=prefs.get("companion", "Friends"),
        visited_destinations=prefs.get("visited_destinations", []),
        preferred_distance=prefs.get("distance", "any"),
        current_city=prefs.get("current_city", "Delhi"),
        top_k=9
    )

    budget_label_map = {
        "under_3000": "Under ₹3,000",
        "3000_5000": "₹3,000 - ₹5,000",
        "5000_10000": "₹5,000 - ₹10,000",
        "10000_20000": "₹10,000 - ₹20,000",
        "above_20000": "₹20,000+"
    }

    duration_label_map = {
        "1_day": "1 Day",
        "2_3_days": "2 - 3 Days",
        "4_5_days": "4 - 5 Days",
        "6_7_days": "6 - 7 Days",
        "above_7_days": "7+ Days"
    }

    return render_template(
        "recommendations.html",
        recommendations=recommended_results,
        prefs=prefs,
        budget_label=budget_label_map.get(prefs.get("budget"), "Custom"),
        duration_label=duration_label_map.get(prefs.get("duration"), "Custom")
    )


@plan_bp.route("/profile")
def profile():
    """User profile overview displaying travel history and current travel settings."""
    user = None
    user_id = session.get("user_id")
    if user_id:
        user = User.query.get(user_id)

    visited = session.get("visited_destinations", [])
    prefs = session.get("plan_preferences", {})

    all_cities = [d.name for d in Destination.query.order_by(Destination.name).all()]

    return render_template(
        "profile.html",
        user=user,
        visited=visited,
        prefs=prefs,
        all_cities=all_cities,
        is_guest=session.get("is_guest", True)
    )
