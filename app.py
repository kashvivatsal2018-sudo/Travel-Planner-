"""
Travel Planner: Academic Full-Stack Web Application.
Main entry point and application factory.
"""

import os
from flask import Flask, render_template, session
from config import Config
from database import db
from database.database import init_db
from database.seed import seed_database
from routes import main_bp, auth_bp, plan_bp, api_bp


def create_app(config_class=Config):
    """Application factory for Flask Travel Planner."""
    app = Flask(
        __name__,
        template_folder="templates",
        static_folder="static"
    )
    app.config.from_object(config_class)

    # Initialize Database
    db.init_app(app)

    # Register Route Blueprints
    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(plan_bp)
    app.register_blueprint(api_bp)

    # Global Template Context Processor
    @app.context_processor
    def inject_user_context():
        return {
            "current_user_name": session.get("username", "Guest Explorer"),
            "is_logged_in": session.get("user_id") is not None,
            "is_guest": session.get("is_guest", True),
            "visited_count": len(session.get("visited_destinations", []))
        }

    # Error Handlers
    @app.errorhandler(404)
    def page_not_found(e):
        return render_template("404.html", error_message="The requested destination or page does not exist."), 404

    @app.errorhandler(500)
    def internal_server_error(e):
        return render_template("500.html", error_message="An unexpected server error occurred. Please try again."), 500

    # Initialize DB schema and seed data on startup
    with app.app_context():
        init_db(app)
        seed_database(app)

    return app


app = create_app()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5001))
    print(f"Starting Travel Planner Web Application on http://127.0.0.1:{port}")
    app.run(host="0.0.0.0", port=port, debug=True)
