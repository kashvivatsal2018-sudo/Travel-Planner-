import json
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from database import db


class User(db.Model):
    """User model for authenticated accounts and persistent travel preferences."""
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=True)
    password_hash = db.Column(db.String(256), nullable=False)
    budget = db.Column(db.String(50), nullable=True)
    trip_duration = db.Column(db.String(50), nullable=True)
    travel_companion = db.Column(db.String(50), nullable=True)
    transport_preference = db.Column(db.String(50), nullable=True)
    preferred_categories = db.Column(db.Text, nullable=True, default="[]")  # JSON string
    preferred_distance = db.Column(db.String(50), nullable=True, default="Any")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    travel_histories = db.relationship("TravelHistory", backref="user", lazy=True, cascade="all, delete-orphan")

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def get_categories(self):
        try:
            return json.loads(self.preferred_categories or "[]")
        except Exception:
            return []

    def set_categories(self, categories_list):
        self.preferred_categories = json.dumps(categories_list)


class Destination(db.Model):
    """Tourist destination city node in the graph and recommendation catalog."""
    __tablename__ = "destinations"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    tagline = db.Column(db.String(255), nullable=True)
    description = db.Column(db.Text, nullable=False)
    category = db.Column(db.String(50), nullable=False)  # Primary: Mountains, Nature, etc.
    secondary_categories = db.Column(db.Text, nullable=True, default="[]")  # JSON list
    rating = db.Column(db.Float, nullable=False, default=4.0)
    avg_cost_min = db.Column(db.Integer, nullable=False, default=3000)
    avg_cost_max = db.Column(db.Integer, nullable=False, default=7000)
    recommended_days = db.Column(db.Integer, nullable=False, default=2)
    best_time = db.Column(db.String(100), nullable=False)
    latitude = db.Column(db.Float, nullable=False)
    longitude = db.Column(db.Float, nullable=False)
    image_url = db.Column(db.String(500), nullable=True)
    suitable_companions = db.Column(db.Text, nullable=True, default="[]")  # JSON list

    # Relationships
    tourist_places = db.relationship("TouristPlace", backref="destination", lazy=True, cascade="all, delete-orphan")
    restaurants = db.relationship("Restaurant", backref="destination", lazy=True, cascade="all, delete-orphan")
    reviews = db.relationship("Review", backref="destination", lazy=True, cascade="all, delete-orphan")

    def get_secondary_categories(self):
        try:
            return json.loads(self.secondary_categories or "[]")
        except Exception:
            return []

    def get_all_categories(self):
        cats = [self.category]
        cats.extend(self.get_secondary_categories())
        return list(set(cats))

    def get_suitable_companions(self):
        try:
            return json.loads(self.suitable_companions or "[]")
        except Exception:
            return []

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "tagline": self.tagline,
            "description": self.description,
            "category": self.category,
            "secondary_categories": self.get_secondary_categories(),
            "all_categories": self.get_all_categories(),
            "rating": self.rating,
            "avg_cost_min": self.avg_cost_min,
            "avg_cost_max": self.avg_cost_max,
            "recommended_days": self.recommended_days,
            "best_time": self.best_time,
            "latitude": self.latitude,
            "longitude": self.longitude,
            "image_url": self.image_url,
            "suitable_companions": self.get_suitable_companions(),
            "places_count": len(self.tourist_places),
            "restaurants_count": len(self.restaurants)
        }


class TravelHistory(db.Model):
    """Log of previous destinations visited by users or guests."""
    __tablename__ = "travel_history"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)
    session_key = db.Column(db.String(100), nullable=True)  # For guest sessions
    destination_id = db.Column(db.Integer, db.ForeignKey("destinations.id"), nullable=True)
    destination_name = db.Column(db.String(100), nullable=False)
    visited_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationship to Destination
    destination_rel = db.relationship("Destination", foreign_keys=[destination_id], lazy=True)


class RouteEdge(db.Model):
    """Road network edges connecting cities in the weighted graph."""
    __tablename__ = "routes"

    id = db.Column(db.Integer, primary_key=True)
    source = db.Column(db.String(100), nullable=False)
    destination = db.Column(db.String(100), nullable=False)
    distance = db.Column(db.Float, nullable=False)  # in Kilometers

    def to_dict(self):
        return {
            "id": self.id,
            "source": self.source,
            "destination": self.destination,
            "distance": self.distance
        }


class TouristPlace(db.Model):
    """Attractions and points of interest for destinations."""
    __tablename__ = "tourist_places"

    id = db.Column(db.Integer, primary_key=True)
    destination_id = db.Column(db.Integer, db.ForeignKey("destinations.id"), nullable=False)
    name = db.Column(db.String(150), nullable=False)
    category = db.Column(db.String(50), nullable=False)  # Nature, Viewpoint, Religious, etc.
    description = db.Column(db.Text, nullable=False)
    rating = db.Column(db.Float, nullable=False, default=4.0)
    entry_cost = db.Column(db.Float, nullable=False, default=0.0)
    visit_duration = db.Column(db.Float, nullable=False, default=2.0)  # in Hours
    best_time_of_day = db.Column(db.String(50), nullable=False, default="Morning")

    def to_dict(self):
        return {
            "id": self.id,
            "destination_id": self.destination_id,
            "name": self.name,
            "category": self.category,
            "description": self.description,
            "rating": self.rating,
            "entry_cost": self.entry_cost,
            "visit_duration": self.visit_duration,
            "best_time_of_day": self.best_time_of_day
        }


class Restaurant(db.Model):
    """Recommended local eateries, cafes, and dining spots."""
    __tablename__ = "restaurants"

    id = db.Column(db.Integer, primary_key=True)
    destination_id = db.Column(db.Integer, db.ForeignKey("destinations.id"), nullable=False)
    name = db.Column(db.String(150), nullable=False)
    cuisine = db.Column(db.String(100), nullable=False)
    rating = db.Column(db.Float, nullable=False, default=4.0)
    avg_cost_per_person = db.Column(db.Float, nullable=False, default=300.0)
    location = db.Column(db.String(150), nullable=False)
    popular_dishes = db.Column(db.String(255), nullable=True)

    def to_dict(self):
        return {
            "id": self.id,
            "destination_id": self.destination_id,
            "name": self.name,
            "cuisine": self.cuisine,
            "rating": self.rating,
            "avg_cost_per_person": self.avg_cost_per_person,
            "location": self.location,
            "popular_dishes": self.popular_dishes
        }


class Review(db.Model):
    """Sample destination reviews for academic demonstration."""
    __tablename__ = "reviews"

    id = db.Column(db.Integer, primary_key=True)
    destination_id = db.Column(db.Integer, db.ForeignKey("destinations.id"), nullable=False)
    rating = db.Column(db.Integer, nullable=False, default=5)
    review_text = db.Column(db.Text, nullable=False)
    author_name = db.Column(db.String(100), nullable=False, default="Traveler")
    travel_date = db.Column(db.String(50), nullable=True)

    def to_dict(self):
        return {
            "id": self.id,
            "destination_id": self.destination_id,
            "rating": self.rating,
            "review_text": self.review_text,
            "author_name": self.author_name,
            "travel_date": self.travel_date
        }
