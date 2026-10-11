import os
import json
from database import db
from database.models import Destination, RouteEdge, TouristPlace, Restaurant, Review

def seed_database(app, force=False):
    """
    Populate SQLite database from seed_data.json if tables are empty or force=True.
    """
    with app.app_context():
        if not force and Destination.query.count() > 0:
            # Already seeded
            return False

        seed_file = os.path.join(os.path.dirname(__file__), "..", "data", "seed_data.json")
        if not os.path.exists(seed_file):
            print(f"Warning: Seed file not found at {seed_file}")
            return False

        with open(seed_file, "r", encoding="utf-8") as f:
            data = json.load(f)

        if force:
            # Clear existing data in reverse dependency order
            Review.query.delete()
            Restaurant.query.delete()
            TouristPlace.query.delete()
            RouteEdge.query.delete()
            Destination.query.delete()
            db.session.commit()

        # 1. Seed Destinations
        dest_id_map = {}
        for dest in data.get("destinations", []):
            d = Destination(
                id=dest.get("id"),
                name=dest["name"],
                tagline=dest.get("tagline", ""),
                description=dest["description"],
                category=dest["category"],
                secondary_categories=json.dumps(dest.get("secondary_categories", [])),
                rating=dest.get("rating", 4.0),
                avg_cost_min=dest.get("avg_cost_min", 3000),
                avg_cost_max=dest.get("avg_cost_max", 7000),
                recommended_days=dest.get("recommended_days", 2),
                best_time=dest.get("best_time", "All year"),
                latitude=dest["latitude"],
                longitude=dest["longitude"],
                image_url=dest.get("image_url", ""),
                suitable_companions=json.dumps(dest.get("suitable_companions", []))
            )
            db.session.add(d)
            dest_id_map[dest["name"]] = dest.get("id")
        db.session.commit()

        # 2. Seed Route Edges (store bidirectional edges for consistency)
        seen_edges = set()
        for r in data.get("routes", []):
            src = r["source"]
            dst = r["destination"]
            dist = float(r["distance"])

            edge_key = tuple(sorted([src, dst]))
            if edge_key not in seen_edges:
                seen_edges.add(edge_key)
                db.session.add(RouteEdge(source=src, destination=dst, distance=dist))
                # Add reverse edge for explicit bidirectionality in DB
                db.session.add(RouteEdge(source=dst, destination=src, distance=dist))
        db.session.commit()

        # 3. Seed Tourist Places
        for p in data.get("tourist_places", []):
            tp = TouristPlace(
                destination_id=p["destination_id"],
                name=p["name"],
                category=p.get("category", "General"),
                description=p["description"],
                rating=p.get("rating", 4.0),
                entry_cost=p.get("entry_cost", 0.0),
                visit_duration=p.get("visit_duration", 2.0),
                best_time_of_day=p.get("best_time_of_day", "Morning")
            )
            db.session.add(tp)
        db.session.commit()

        # 4. Seed Restaurants
        for rest in data.get("restaurants", []):
            rst = Restaurant(
                destination_id=rest["destination_id"],
                name=rest["name"],
                cuisine=rest.get("cuisine", "Multi-Cuisine"),
                rating=rest.get("rating", 4.0),
                avg_cost_per_person=rest.get("avg_cost_per_person", 300.0),
                location=rest.get("location", ""),
                popular_dishes=rest.get("popular_dishes", "")
            )
            db.session.add(rst)
        db.session.commit()

        # 5. Seed Reviews
        for rev in data.get("reviews", []):
            r = Review(
                destination_id=rev["destination_id"],
                rating=rev.get("rating", 5),
                review_text=rev["review_text"],
                author_name=rev.get("author_name", "Traveler"),
                travel_date=rev.get("travel_date", "Recent")
            )
            db.session.add(r)
        db.session.commit()

        print(f"Successfully seeded database with {len(dest_id_map)} destinations and related data.")
        return True


if __name__ == "__main__":
    from flask import Flask
    from config import Config
    app = Flask(__name__)
    app.config.from_object(Config)
    db.init_app(app)
    from database.database import init_db
    init_db(app)
    seed_database(app, force=True)
