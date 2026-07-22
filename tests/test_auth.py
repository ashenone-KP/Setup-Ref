"""Tests for registration and login (functional requirement: accounts/roles)."""
from app.models import ROLE_STAFF, User

from tests.conftest import create_user


def test_register_creates_student_and_logs_in(client):
    resp = client.post("/register", data={
        "name": "Alice Student", "email": "alice@example.com",
        "password": "secret123", "role": "student",
    }, follow_redirects=True)
    assert resp.status_code == 200
    user = User.query.filter_by(email="alice@example.com").first()
    assert user is not None
    assert user.is_student
    # Password is stored hashed, never in plain text.
    assert user.password_hash != "secret123"
    assert user.check_password("secret123")


def test_register_rejects_short_password(client):
    client.post("/register", data={
        "name": "Bob", "email": "bob@example.com",
        "password": "123", "role": "student",
    })
    assert User.query.filter_by(email="bob@example.com").first() is None


def test_register_rejects_duplicate_email(client):
    create_user(email="dupe@example.com")
    client.post("/register", data={
        "name": "Second", "email": "dupe@example.com",
        "password": "secret123", "role": "staff",
    })
    # Still only one account with that email.
    assert User.query.filter_by(email="dupe@example.com").count() == 1


def test_login_with_wrong_password_fails(client):
    create_user(email="carol@example.com", password="rightpass")
    resp = client.post("/login", data={
        "email": "carol@example.com", "password": "wrongpass",
    })
    assert b"Invalid email or password" in resp.data


def test_staff_registration_sets_role(client):
    client.post("/register", data={
        "name": "Dr Dan", "email": "dan@example.com",
        "password": "secret123", "role": "staff",
    })
    user = User.query.filter_by(email="dan@example.com").first()
    assert user.role == ROLE_STAFF
