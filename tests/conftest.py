"""Shared pytest fixtures and helpers.

Builds a fresh app on a disposable in-memory database for every test, and
provides helpers to create users and log a user into the test client.
"""
import pytest

from app import create_app
from app.config import TestConfig
from app.extensions import db
from app.models import ROLE_STAFF, ROLE_STUDENT, User


@pytest.fixture
def app():
    app = create_app(TestConfig)
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    return app.test_client()


def create_user(role=ROLE_STUDENT, email=None, password="password123",
                name="Test User", **kwargs):
    """Create and persist a user, returning it."""
    email = email or f"{role}@example.com"
    user = User(name=name, email=email, role=role, **kwargs)
    user.set_password(password)
    db.session.add(user)
    db.session.commit()
    return user


def login(client, user):
    """Log a user into the test client without going through the form.

    The app fixture keeps one application context open for the whole test,
    and Flask-Login caches the resolved user on ``g``. Clearing that cache
    lets a test switch between users (e.g. student then staff) correctly.
    """
    from flask import g

    with client.session_transaction() as session:
        session["_user_id"] = str(user.id)
        session["_fresh"] = True
    g.pop("_login_user", None)
