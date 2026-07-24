"""Tests for the student browse/search-and-filter view."""
from app.extensions import db
from app.models import ROLE_STAFF, ROLE_STUDENT, AreaOfInterest

from tests.conftest import create_user, login


def _make_staff(email, name, areas, bio=""):
    staff = create_user(role=ROLE_STAFF, email=email, name=name, bio=bio)
    for area in areas:
        db.session.add(AreaOfInterest(name=area, staff_id=staff.id))
    db.session.commit()
    return staff


def test_browse_lists_all_staff(client):
    _make_staff("a@example.com", "Ada Lovelace", ["Algorithms"])
    _make_staff("b@example.com", "Alan Turing", ["Computation"])
    student = create_user(role=ROLE_STUDENT, email="stud@example.com")
    login(client, student)

    resp = client.get("/student/browse")
    assert b"Ada Lovelace" in resp.data
    assert b"Alan Turing" in resp.data


def test_browse_text_search_filters_by_name(client):
    _make_staff("a@example.com", "Ada Lovelace", ["Algorithms"])
    _make_staff("b@example.com", "Alan Turing", ["Computation"])
    student = create_user(role=ROLE_STUDENT, email="stud@example.com")
    login(client, student)

    resp = client.get("/student/browse?q=Turing")
    assert b"Alan Turing" in resp.data
    assert b"Ada Lovelace" not in resp.data


def test_browse_area_filter(client):
    _make_staff("a@example.com", "Ada Lovelace", ["Graph theory"])
    _make_staff("b@example.com", "Alan Turing", ["Software testing"])
    student = create_user(role=ROLE_STUDENT, email="stud@example.com")
    login(client, student)

    resp = client.get("/student/browse?area=Graph theory")
    assert b"Ada Lovelace" in resp.data
    assert b"Alan Turing" not in resp.data


def test_staff_cannot_access_student_browse(client):
    staff = create_user(role=ROLE_STAFF, email="staff@example.com")
    login(client, staff)
    resp = client.get("/student/browse")
    assert resp.status_code == 403


def test_browse_card_shows_topic_count_and_slots(client):
    _make_staff("a@example.com", "Ada Lovelace", ["Algorithms", "Web"])
    student = create_user(role=ROLE_STUDENT, email="stud@example.com")
    login(client, student)
    body = client.get("/student/browse").data.decode()
    assert "2 topics" in body       # topic count from the staff's areas
    assert "slot" in body           # open-slots pill (capacity 4, 0 accepted)
