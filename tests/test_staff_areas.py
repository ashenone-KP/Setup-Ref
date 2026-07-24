"""Tests for staff area-of-interest and project-idea management, plus role
access control."""
from app.models import ROLE_STAFF, ROLE_STUDENT, AreaOfInterest, ProjectIdea

from tests.conftest import create_user, login


def test_staff_can_add_area(client):
    staff = create_user(role=ROLE_STAFF, email="s1@example.com")
    login(client, staff)
    client.post("/staff/areas/add", data={"name": "Algorithms"})
    assert AreaOfInterest.query.filter_by(staff_id=staff.id).count() == 1


def test_add_area_rejects_value_not_in_list(client):
    staff = create_user(role=ROLE_STAFF, email="s2@example.com")
    login(client, staff)
    # Not one of the official subject areas.
    client.post("/staff/areas/add", data={"name": "Underwater Basket Weaving"})
    assert AreaOfInterest.query.count() == 0


def test_add_area_rejects_duplicate(client):
    staff = create_user(role=ROLE_STAFF, email="s3@example.com")
    login(client, staff)
    client.post("/staff/areas/add", data={"name": "Data Analytics"})
    client.post("/staff/areas/add", data={"name": "Data Analytics"})
    assert AreaOfInterest.query.count() == 1


def test_staff_can_delete_area(client):
    staff = create_user(role=ROLE_STAFF, email="s4@example.com")
    login(client, staff)
    client.post("/staff/areas/add", data={"name": "Web"})
    area = AreaOfInterest.query.first()
    client.post(f"/staff/areas/{area.id}/delete")
    assert AreaOfInterest.query.count() == 0


def test_staff_cannot_delete_another_staffs_area(client):
    owner = create_user(role=ROLE_STAFF, email="owner@example.com")
    other = create_user(role=ROLE_STAFF, email="other@example.com")
    login(client, owner)
    client.post("/staff/areas/add", data={"name": "Cyber Security / Security"})
    area = AreaOfInterest.query.first()
    # Log in as the other staff member and try to delete the first one's area.
    login(client, other)
    resp = client.post(f"/staff/areas/{area.id}/delete")
    assert resp.status_code == 404
    assert AreaOfInterest.query.count() == 1


def test_add_project_idea_requires_title_and_description(client):
    staff = create_user(role=ROLE_STAFF, email="s5@example.com")
    login(client, staff)
    client.post("/staff/ideas/add", data={"title": "Only a title", "description": ""})
    assert ProjectIdea.query.count() == 0
    client.post("/staff/ideas/add",
                data={"title": "Good idea", "description": "A real description."})
    assert ProjectIdea.query.count() == 1


def test_student_cannot_access_staff_area(client):
    student = create_user(role=ROLE_STUDENT, email="stud@example.com")
    login(client, student)
    resp = client.post("/staff/areas/add", data={"name": "Nope"})
    assert resp.status_code == 403
    assert AreaOfInterest.query.count() == 0
