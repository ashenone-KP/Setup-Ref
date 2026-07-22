"""Student-facing views: browse and search staff, and view a profile.

Covers the 'Search & Filter Staff by Area of Interest' use case. The search
combines a free-text query (name/title/bio) with an optional area filter.
"""
from flask import Blueprint, render_template, request
from flask_login import login_required
from sqlalchemy import or_

from ..decorators import student_required
from ..extensions import db
from ..models import ROLE_STAFF, AreaOfInterest, User

student_bp = Blueprint("student", __name__, url_prefix="/student")


@student_bp.route("/browse")
@login_required
@student_required
def browse():
    query_text = request.args.get("q", "").strip()
    area = request.args.get("area", "").strip()

    staff_query = User.query.filter_by(role=ROLE_STAFF)
    if query_text:
        like = f"%{query_text}%"
        staff_query = staff_query.filter(
            or_(
                User.name.ilike(like),
                User.title.ilike(like),
                User.bio.ilike(like),
            )
        )
    staff = staff_query.order_by(User.name).all()

    # Area filter is applied in Python so a staff member matches if *any* of
    # their areas contains the search term (case-insensitive).
    if area:
        needle = area.lower()
        staff = [s for s in staff if any(needle in a.name.lower() for a in s.areas)]

    all_areas = sorted(
        {a.name for a in AreaOfInterest.query.all()}, key=str.lower
    )
    return render_template(
        "student/browse.html",
        staff=staff, q=query_text, area=area, all_areas=all_areas,
    )


@student_bp.route("/staff/<int:staff_id>")
@login_required
@student_required
def view_staff(staff_id):
    staff = User.query.filter_by(id=staff_id, role=ROLE_STAFF).first_or_404()
    return render_template("student/profile.html", staff=staff)
