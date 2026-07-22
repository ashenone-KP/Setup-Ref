"""Staff-facing views: profile, areas of interest, and project ideas.

Covers the 'Manage Area of Interest' and 'Manage Project Idea' use cases,
each implemented as full create/update/delete flows scoped to the logged-in
staff member's own profile.
"""
from flask import (Blueprint, abort, flash, redirect, render_template, request,
                   url_for)
from flask_login import current_user, login_required

from ..decorators import staff_required
from ..extensions import db
from ..models import AreaOfInterest, ProjectIdea

staff_bp = Blueprint("staff", __name__, url_prefix="/staff")


@staff_bp.route("/dashboard")
@login_required
@staff_required
def dashboard():
    return render_template(
        "staff/dashboard.html",
        areas=current_user.areas,
        ideas=current_user.project_ideas,
        pending=[r for r in current_user.received_requests if r.status == "pending"],
    )


@staff_bp.route("/profile", methods=["GET", "POST"])
@login_required
@staff_required
def profile():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        if name:
            current_user.name = name
        current_user.title = request.form.get("title", "").strip()
        current_user.bio = request.form.get("bio", "").strip()
        try:
            current_user.capacity = max(0, int(request.form.get("capacity", "4")))
        except (TypeError, ValueError):
            flash("Capacity must be a whole number.", "error")
            return render_template("staff/profile.html")
        db.session.commit()
        flash("Profile updated.", "success")
        return redirect(url_for("staff.dashboard"))

    return render_template("staff/profile.html")


# --- Areas of interest -------------------------------------------------------

@staff_bp.route("/areas/add", methods=["POST"])
@login_required
@staff_required
def add_area():
    name = request.form.get("name", "").strip()
    if not name:
        flash("An area of interest needs a name.", "error")
    elif any(a.name.lower() == name.lower() for a in current_user.areas):
        flash("That area is already on your profile.", "error")
    else:
        db.session.add(AreaOfInterest(name=name, staff_id=current_user.id))
        db.session.commit()
        flash("Area of interest added.", "success")
    return redirect(url_for("staff.dashboard"))


@staff_bp.route("/areas/<int:area_id>/edit", methods=["POST"])
@login_required
@staff_required
def edit_area(area_id):
    area = _own_area_or_404(area_id)
    name = request.form.get("name", "").strip()
    if not name:
        flash("An area of interest needs a name.", "error")
    else:
        area.name = name
        db.session.commit()
        flash("Area of interest updated.", "success")
    return redirect(url_for("staff.dashboard"))


@staff_bp.route("/areas/<int:area_id>/delete", methods=["POST"])
@login_required
@staff_required
def delete_area(area_id):
    area = _own_area_or_404(area_id)
    db.session.delete(area)
    db.session.commit()
    flash("Area of interest removed.", "success")
    return redirect(url_for("staff.dashboard"))


# --- Project ideas -----------------------------------------------------------

@staff_bp.route("/ideas/add", methods=["POST"])
@login_required
@staff_required
def add_idea():
    title = request.form.get("title", "").strip()
    description = request.form.get("description", "").strip()
    area_name = request.form.get("area_name", "").strip()
    if not title or not description:
        flash("A project idea needs both a title and a description.", "error")
    else:
        db.session.add(ProjectIdea(
            title=title, description=description,
            area_name=area_name or None, staff_id=current_user.id,
        ))
        db.session.commit()
        flash("Project idea added.", "success")
    return redirect(url_for("staff.dashboard"))


@staff_bp.route("/ideas/<int:idea_id>/edit", methods=["POST"])
@login_required
@staff_required
def edit_idea(idea_id):
    idea = _own_idea_or_404(idea_id)
    title = request.form.get("title", "").strip()
    description = request.form.get("description", "").strip()
    if not title or not description:
        flash("A project idea needs both a title and a description.", "error")
    else:
        idea.title = title
        idea.description = description
        idea.area_name = request.form.get("area_name", "").strip() or None
        idea.status = request.form.get("status", "open")
        db.session.commit()
        flash("Project idea updated.", "success")
    return redirect(url_for("staff.dashboard"))


@staff_bp.route("/ideas/<int:idea_id>/delete", methods=["POST"])
@login_required
@staff_required
def delete_idea(idea_id):
    idea = _own_idea_or_404(idea_id)
    db.session.delete(idea)
    db.session.commit()
    flash("Project idea removed.", "success")
    return redirect(url_for("staff.dashboard"))


# --- Helpers -----------------------------------------------------------------

def _own_area_or_404(area_id):
    area = db.session.get(AreaOfInterest, area_id)
    if area is None or area.staff_id != current_user.id:
        abort(404)
    return area


def _own_idea_or_404(idea_id):
    idea = db.session.get(ProjectIdea, idea_id)
    if idea is None or idea.staff_id != current_user.id:
        abort(404)
    return idea
