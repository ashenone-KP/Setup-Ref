"""Student-facing views: browse/search staff, supervisor detail, supervision
requests, bookmarks, interests and recommendations.

Covers the 'Search & Filter Staff by Area of Interest' and 'Send Supervision
Request' use cases.
"""
from flask import (Blueprint, abort, flash, redirect, render_template, request,
                   url_for)
from flask_login import current_user, login_required
from sqlalchemy import or_

from ..data.areas import UNIVERSITY_AREAS
from ..decorators import student_required
from ..extensions import db
from ..models import (ROLE_STAFF, Bookmark, Interest, SupervisionRequest, User)
from ..services.matching import recommend_supervisors

student_bp = Blueprint("student", __name__, url_prefix="/student")


# --- helpers ----------------------------------------------------------------

def _bookmarked_staff_ids():
    return {b.staff_id for b in current_user.bookmarks if b.staff_id is not None}


def _pending_staff_ids():
    return {r.staff_id for r in current_user.sent_requests if r.status == "pending"}


def _accepted_request():
    """The student's accepted request, if they already have a supervisor."""
    return next((r for r in current_user.sent_requests if r.status == "accepted"), None)


def _get_staff_or_404(staff_id):
    return User.query.filter_by(id=staff_id, role=ROLE_STAFF).first_or_404()


# --- browse & detail --------------------------------------------------------

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
            or_(User.name.ilike(like), User.title.ilike(like), User.bio.ilike(like))
        )
    staff = staff_query.order_by(User.name).all()

    # Narrow by subject: keep staff who have that subject among their areas.
    if area:
        needle = area.lower()
        staff = [s for s in staff if any(needle in a.name.lower() for a in s.areas)]

    return render_template(
        "student/browse.html",
        staff=staff, q=query_text, area=area, subjects=UNIVERSITY_AREAS,
        bookmarked_ids=_bookmarked_staff_ids(),
        pending_ids=_pending_staff_ids(),
        accepted=_accepted_request(),
    )


@student_bp.route("/staff/<int:staff_id>")
@login_required
@student_required
def view_staff(staff_id):
    staff = _get_staff_or_404(staff_id)
    return render_template(
        "student/profile.html", staff=staff,
        is_bookmarked=staff.id in _bookmarked_staff_ids(),
        has_pending=staff.id in _pending_staff_ids(),
        accepted=_accepted_request(),
    )


# --- supervision requests ---------------------------------------------------

@student_bp.route("/staff/<int:staff_id>/request", methods=["POST"])
@login_required
@student_required
def send_request(staff_id):
    staff = _get_staff_or_404(staff_id)
    fallback = request.referrer or url_for("student.browse")

    if _accepted_request() is not None:
        flash("You already have a confirmed supervisor.", "error")
        return redirect(fallback)
    if SupervisionRequest.query.filter_by(
        student_id=current_user.id, staff_id=staff.id, status="pending"
    ).first():
        flash("You already have a pending request with this supervisor.", "error")
        return redirect(fallback)

    project_idea_id = request.form.get("project_idea_id") or None
    if project_idea_id:
        try:
            project_idea_id = int(project_idea_id)
        except (TypeError, ValueError):
            project_idea_id = None
        # Only accept an idea that actually belongs to this staff member.
        if project_idea_id and not any(i.id == project_idea_id for i in staff.project_ideas):
            project_idea_id = None

    db.session.add(SupervisionRequest(
        student_id=current_user.id, staff_id=staff.id,
        project_idea_id=project_idea_id,
        message=request.form.get("message", "").strip(), status="pending",
    ))
    db.session.commit()
    flash(f"Supervision request sent to {staff.name}.", "success")
    return redirect(url_for("student.my_requests"))


@student_bp.route("/requests")
@login_required
@student_required
def my_requests():
    reqs = (SupervisionRequest.query
            .filter_by(student_id=current_user.id)
            .order_by(SupervisionRequest.created_at.desc()).all())
    return render_template("student/requests.html", requests=reqs)


@student_bp.route("/requests/<int:req_id>/cancel", methods=["POST"])
@login_required
@student_required
def cancel_request(req_id):
    req = _own_request_or_404(req_id)
    if req.status != "pending":
        flash("Only pending requests can be cancelled.", "error")
    else:
        db.session.delete(req)
        db.session.commit()
        flash("Request cancelled.", "success")
    return redirect(url_for("student.my_requests"))


@student_bp.route("/requests/<int:req_id>/edit", methods=["POST"])
@login_required
@student_required
def edit_request(req_id):
    req = _own_request_or_404(req_id)
    if req.status != "pending":
        flash("Only pending requests can be edited.", "error")
        return redirect(url_for("student.my_requests"))

    project_idea_id = request.form.get("project_idea_id") or None
    if project_idea_id:
        try:
            project_idea_id = int(project_idea_id)
        except (TypeError, ValueError):
            project_idea_id = None
        if project_idea_id and not any(i.id == project_idea_id for i in req.staff.project_ideas):
            project_idea_id = None

    req.message = request.form.get("message", "").strip()
    req.project_idea_id = project_idea_id
    db.session.commit()
    flash("Request updated.", "success")
    return redirect(url_for("student.my_requests"))


def _own_request_or_404(req_id):
    req = db.session.get(SupervisionRequest, req_id)
    if req is None or req.student_id != current_user.id:
        abort(404)
    return req


# --- bookmarks --------------------------------------------------------------

@student_bp.route("/staff/<int:staff_id>/bookmark", methods=["POST"])
@login_required
@student_required
def toggle_bookmark(staff_id):
    staff = _get_staff_or_404(staff_id)
    existing = Bookmark.query.filter_by(
        student_id=current_user.id, staff_id=staff.id
    ).first()
    if existing:
        db.session.delete(existing)
        db.session.commit()
        flash("Removed from saved.", "success")
    else:
        db.session.add(Bookmark(student_id=current_user.id, staff_id=staff.id))
        db.session.commit()
        flash(f"Saved {staff.name}.", "success")
    return redirect(request.referrer or url_for("student.browse"))


@student_bp.route("/saved")
@login_required
@student_required
def saved():
    ids = [b.staff_id for b in current_user.bookmarks if b.staff_id is not None]
    staff = (User.query.filter(User.id.in_(ids)).order_by(User.name).all()
             if ids else [])
    return render_template(
        "student/saved.html", staff=staff,
        bookmarked_ids=set(ids), pending_ids=_pending_staff_ids(),
        accepted=_accepted_request(),
    )


# --- interests & recommendations -------------------------------------------

@student_bp.route("/interests")
@login_required
@student_required
def interests():
    taken = {i.name for i in current_user.interests}
    available = [a for a in UNIVERSITY_AREAS if a not in taken]
    return render_template(
        "student/interests.html",
        interests=current_user.interests, available=available,
    )


@student_bp.route("/interests/add", methods=["POST"])
@login_required
@student_required
def add_interest():
    name = request.form.get("name", "").strip()
    if name not in UNIVERSITY_AREAS:
        flash("Please choose an interest from the list.", "error")
    elif any(i.name.lower() == name.lower() for i in current_user.interests):
        flash("That interest is already on your list.", "error")
    else:
        db.session.add(Interest(name=name, student_id=current_user.id))
        db.session.commit()
        flash("Interest added.", "success")
    return redirect(url_for("student.interests"))


@student_bp.route("/interests/<int:interest_id>/delete", methods=["POST"])
@login_required
@student_required
def delete_interest(interest_id):
    interest = db.session.get(Interest, interest_id)
    if interest is None or interest.student_id != current_user.id:
        abort(404)
    db.session.delete(interest)
    db.session.commit()
    flash("Interest removed.", "success")
    return redirect(url_for("student.interests"))


@student_bp.route("/recommended")
@login_required
@student_required
def recommended():
    staff_list = User.query.filter_by(role=ROLE_STAFF).all()
    ranked = recommend_supervisors(current_user, staff_list)
    return render_template(
        "student/recommended.html", ranked=ranked,
        has_interests=len(current_user.interests) > 0,
        bookmarked_ids=_bookmarked_staff_ids(),
        pending_ids=_pending_staff_ids(),
        accepted=_accepted_request(),
    )
