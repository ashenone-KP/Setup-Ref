"""Registration, login and logout.

These are deliberately excluded from the documented use cases (per the brief)
but are still needed for the system to function and enforce roles.
"""
from flask import (Blueprint, flash, redirect, render_template, request,
                   url_for)
from flask_login import current_user, login_required, login_user, logout_user

from ..extensions import db
from ..models import ROLE_STAFF, ROLE_STUDENT, User

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("main.dashboard"))

    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        role = request.form.get("role", ROLE_STUDENT)

        errors = []
        if not name:
            errors.append("Name is required.")
        if not email:
            errors.append("Email is required.")
        if len(password) < 6:
            errors.append("Password must be at least 6 characters.")
        if role not in (ROLE_STAFF, ROLE_STUDENT):
            errors.append("Please choose a valid account type.")
        if email and User.query.filter_by(email=email).first():
            errors.append("An account with that email already exists.")

        if errors:
            for message in errors:
                flash(message, "error")
            return render_template(
                "auth/register.html", name=name, email=email, role=role
            )

        user = User(name=name, email=email, role=role)
        user.set_password(password)
        if role == ROLE_STAFF:
            user.title = request.form.get("title", "").strip()
            user.bio = request.form.get("bio", "").strip()
        db.session.add(user)
        db.session.commit()

        login_user(user)
        flash(f"Welcome, {user.name}! Your account has been created.", "success")
        return redirect(url_for("main.dashboard"))

    return render_template("auth/register.html")


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("main.dashboard"))

    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        user = User.query.filter_by(email=email).first()
        if user is None or not user.check_password(password):
            flash("Invalid email or password.", "error")
            return render_template("auth/login.html", email=email)

        login_user(user)
        flash("Logged in successfully.", "success")
        next_page = request.args.get("next")
        return redirect(next_page or url_for("main.dashboard"))

    return render_template("auth/login.html")


@auth_bp.route("/logout")
@login_required
def logout():
    logout_user()
    flash("You have been logged out.", "success")
    return redirect(url_for("main.index"))
