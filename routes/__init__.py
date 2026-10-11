"""Flask Route Blueprints package."""
from routes.main_routes import main_bp
from routes.auth_routes import auth_bp
from routes.plan_routes import plan_bp
from routes.api_routes import api_bp

__all__ = ["main_bp", "auth_bp", "plan_bp", "api_bp"]
