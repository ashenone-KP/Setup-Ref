"""Database models for the Supervisor-Matching system.

Entities:
    User               - a staff member or a student (role field)
    AreaOfInterest     - a research/teaching area owned by a staff member
    ProjectIdea        - a project a staff member proposes
    Interest           - a topic a student is interested in (drives matching)
    SupervisionRequest - a student's request to be supervised by a staff member
    Bookmark           - a student saving a staff member or project idea
"""
from datetime import datetime

from flask_login import UserMixin
from werkzeug.security import check_password_hash, generate_password_hash

from .extensions import db, login_manager

ROLE_STAFF = "staff"
ROLE_STUDENT = "student"


class User(UserMixin, db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), nullable=False)  # ROLE_STAFF or ROLE_STUDENT

    # Staff-only profile fields (left null for students).
    title = db.Column(db.String(120))            # e.g. "Dr", "Senior Lecturer"
    bio = db.Column(db.Text)
    capacity = db.Column(db.Integer, default=4)  # max students this staff will supervise

    # Staff-owned collections.
    areas = db.relationship(
        "AreaOfInterest", backref="staff",
        cascade="all, delete-orphan", lazy=True,
    )
    project_ideas = db.relationship(
        "ProjectIdea", backref="staff",
        cascade="all, delete-orphan", lazy=True,
    )
    # Student-owned collections.
    interests = db.relationship(
        "Interest", backref="student",
        cascade="all, delete-orphan", lazy=True,
    )
    sent_requests = db.relationship(
        "SupervisionRequest",
        foreign_keys="SupervisionRequest.student_id",
        backref="student", cascade="all, delete-orphan", lazy=True,
    )
    received_requests = db.relationship(
        "SupervisionRequest",
        foreign_keys="SupervisionRequest.staff_id",
        backref="staff", cascade="all, delete-orphan", lazy=True,
    )
    bookmarks = db.relationship(
        "Bookmark",
        foreign_keys="Bookmark.student_id",
        backref="student", cascade="all, delete-orphan", lazy=True,
    )

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    @property
    def is_staff(self):
        return self.role == ROLE_STAFF

    @property
    def is_student(self):
        return self.role == ROLE_STUDENT

    def accepted_count(self):
        """How many supervision requests this staff member has accepted."""
        return SupervisionRequest.query.filter_by(
            staff_id=self.id, status="accepted"
        ).count()

    def has_capacity(self):
        """True while the staff member can still accept more students."""
        return self.accepted_count() < (self.capacity or 0)

    def __repr__(self):
        return f"<User {self.id} {self.role} {self.email}>"


class AreaOfInterest(db.Model):
    __tablename__ = "areas_of_interest"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    staff_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)


class ProjectIdea(db.Model):
    __tablename__ = "project_ideas"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    area_name = db.Column(db.String(120))                 # optional topic tag
    status = db.Column(db.String(20), default="open")     # "open" or "taken"
    staff_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)


class Interest(db.Model):
    __tablename__ = "interests"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    student_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)


class SupervisionRequest(db.Model):
    __tablename__ = "supervision_requests"

    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    staff_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    project_idea_id = db.Column(db.Integer, db.ForeignKey("project_ideas.id"))
    message = db.Column(db.Text)
    status = db.Column(db.String(20), default="pending")  # pending/accepted/declined
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    project_idea = db.relationship("ProjectIdea")


class Bookmark(db.Model):
    __tablename__ = "bookmarks"

    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    staff_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    project_idea_id = db.Column(db.Integer, db.ForeignKey("project_ideas.id"))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    staff = db.relationship("User", foreign_keys=[staff_id])
    project_idea = db.relationship("ProjectIdea")


@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))
