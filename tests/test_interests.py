"""Tests for student interests and the recommendations route."""
from app.extensions import db
from app.models import ROLE_STAFF, ROLE_STUDENT, AreaOfInterest, Interest

from tests.conftest import create_user, login


def test_add_valid_interest(client):
    student = create_user(role=ROLE_STUDENT, email="stud@example.com")
    login(client, student)
    client.post("/student/interests/add", data={"name": "Algorithms"})
    assert Interest.query.count() == 1


def test_reject_interest_not_in_list(client):
    student = create_user(role=ROLE_STUDENT, email="stud@example.com")
    login(client, student)
    client.post("/student/interests/add", data={"name": "Underwater Basket Weaving"})
    assert Interest.query.count() == 0


def test_delete_interest(client):
    student = create_user(role=ROLE_STUDENT, email="stud@example.com")
    login(client, student)
    client.post("/student/interests/add", data={"name": "Web"})
    interest = Interest.query.first()
    client.post(f"/student/interests/{interest.id}/delete")
    assert Interest.query.count() == 0


def test_recommended_ranks_by_overlap(client):
    match = create_user(role=ROLE_STAFF, email="match@example.com", name="Match Staff")
    db.session.add_all([AreaOfInterest(name="Algorithms", staff_id=match.id),
                        AreaOfInterest(name="Web", staff_id=match.id)])
    nomatch = create_user(role=ROLE_STAFF, email="no@example.com", name="Nomatch Staff")
    db.session.add(AreaOfInterest(name="Sport", staff_id=nomatch.id))
    student = create_user(role=ROLE_STUDENT, email="stud@example.com")
    db.session.add_all([Interest(name="Algorithms", student_id=student.id),
                        Interest(name="Web", student_id=student.id)])
    db.session.commit()
    login(client, student)
    resp = client.get("/student/recommended")
    assert b"Match Staff" in resp.data
    assert b"Nomatch Staff" not in resp.data


def test_recommended_prompts_without_interests(client):
    student = create_user(role=ROLE_STUDENT, email="stud@example.com")
    login(client, student)
    resp = client.get("/student/recommended")
    assert b"interests" in resp.data.lower()
