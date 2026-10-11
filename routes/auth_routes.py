"""
Authentication Routes: User registration, login, guest session, and logout.
"""

from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from database import db
from database.models import User

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    """Register a new user account."""
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "")
        confirm_password = request.form.get("confirm_password", "")

        if not username or not password:
            flash("Username and password are required.", "danger")
            return render_template("register.html", username=username, email=email)

        if len(password) < 4:
            flash("Password must be at least 4 characters long.", "danger")
            return render_template("register.html", username=username, email=email)

        if password != confirm_password:
            flash("Passwords do not match.", "danger")
            return render_template("register.html", username=username, email=email)

        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            flash("Username is already taken. Please choose another.", "warning")
            return render_template("register.html", username=username, email=email)

        user = User(username=username, email=email or None)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()

        # Log user in
        session["user_id"] = user.id
        session["username"] = user.username
        session["is_guest"] = False
        flash(f"Welcome to Travel Planner, {user.username}! Your account has been created.", "success")
        return redirect(url_for("plan.plan_trip"))

    return render_template("register.html")


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    """User login or quick guest access."""
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")

        user = User.query.filter_by(username=username).first()
        if not user or not user.check_password(password):
            flash("Invalid username or password.", "danger")
            return render_template("login.html", username=username)

        session["user_id"] = user.id
        session["username"] = user.username
        session["is_guest"] = False
        flash(f"Welcome back, {user.username}!", "success")

        # Redirect to plan or recommendations
        next_page = request.args.get("next")
        return redirect(next_page or url_for("plan.plan_trip"))

    return render_template("login.html")


@auth_bp.route("/guest", methods=["POST", "GET"])
def guest_login():
    """Continue immediately as a Guest traveler without registration."""
    session["user_id"] = None
    session["username"] = "Guest Explorer"
    session["is_guest"] = True
    flash("Continuing as Guest. You can plan trips, view Dijkstra routes, and generate itineraries!", "info")
    return redirect(url_for("plan.plan_trip"))


@auth_bp.route("/logout")
def logout():
    """Log out current user or guest."""
    session.clear()
    flash("You have been logged out successfully.", "info")
    return redirect(url_for("main.index"))
