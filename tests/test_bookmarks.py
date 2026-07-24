"""Tests for student bookmarks."""
from app.models import ROLE_STAFF, ROLE_STUDENT, Bookmark

from tests.conftest import create_user, login


def test_toggle_bookmark_adds_and_removes(client):
    staff = create_user(role=ROLE_STAFF, email="staff@example.com")
    student = create_user(role=ROLE_STUDENT, email="stud@example.com")
    login(client, student)
    client.post(f"/student/staff/{staff.id}/bookmark")
    assert Bookmark.query.count() == 1
    client.post(f"/student/staff/{staff.id}/bookmark")
    assert Bookmark.query.count() == 0


def test_saved_lists_bookmarks(client):
    staff = create_user(role=ROLE_STAFF, email="staff@example.com", name="Prof X")
    student = create_user(role=ROLE_STUDENT, email="stud@example.com")
    login(client, student)
    client.post(f"/student/staff/{staff.id}/bookmark")
    resp = client.get("/student/saved")
    assert b"Prof X" in resp.data


def test_staff_cannot_bookmark(client):
    s1 = create_user(role=ROLE_STAFF, email="s1@example.com")
    s2 = create_user(role=ROLE_STAFF, email="s2@example.com")
    login(client, s1)
    resp = client.post(f"/student/staff/{s2.id}/bookmark")
    assert resp.status_code == 403
    assert Bookmark.query.count() == 0
