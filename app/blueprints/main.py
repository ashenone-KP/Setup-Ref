"""Landing page and role-based dashboard redirect."""
from flask import Blueprint, redirect, render_template, url_for
from flask_login import current_user, login_required

main_bp = Blueprint("main", __name__)


@main_bp.route("/")
def index():
    if current_user.is_authenticated:
        return redirect(url_for("main.dashboard"))
    return render_template("index.html")


@main_bp.route("/dashboard")
@login_required
def dashboard():
    """Send each role to its own home page."""
    if current_user.is_staff:
        return redirect(url_for("staff.dashboard"))
    return redirect(url_for("student.browse"))
