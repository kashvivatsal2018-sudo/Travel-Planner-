import os
from database import db
from database.models import User, Destination, TravelHistory, RouteEdge, TouristPlace, Restaurant, Review


def init_db(app):
    """Initialize database tables with the Flask application context."""
    with app.app_context():
        # Ensure database directory exists
        db_path = app.config.get("SQLALCHEMY_DATABASE_URI", "")
        if "sqlite:///" in db_path:
            file_path = db_path.replace("sqlite:///", "")
            os.makedirs(os.path.dirname(os.path.abspath(file_path)), exist_ok=True)
            
        db.create_all()


def get_all_destinations():
    """Retrieve all destination records ordered by rating descending."""
    return Destination.query.order_by(Destination.rating.desc()).all()


def get_destination_by_id(dest_id):
    """Retrieve destination by primary key ID."""
    return Destination.query.get(dest_id)


def get_destination_by_name(name):
    """Retrieve destination by unique name case-insensitively."""
    return Destination.query.filter(Destination.name.ilike(name.strip())).first()


def get_all_routes():
    """Retrieve all route edges from database."""
    return RouteEdge.query.all()
