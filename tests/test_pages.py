"""Page-render and remaining-branch tests that raise coverage toward the
'all units tested' band (auth/main redirects, staff profile & idea edit/delete,
student page renders, request with a named project idea)."""
from app.extensions import db
from app.models import (ROLE_STAFF, ROLE_STUDENT, AreaOfInterest, ProjectIdea,
                        SupervisionRequest, User)

from tests.conftest import create_user, login


# --- auth ------------------------------------------------------------------

def test_login_success_lands_on_dashboard(client):
    create_user(role=ROLE_STUDENT, email="s@example.com", password="password123")
    resp = client.post("/login", data={"email": "s@example.com", "password": "password123"},
                       follow_redirects=True)
    assert resp.status_code == 200
    assert b"Find a supervisor" in resp.data


def test_logout_ends_session(client):
    user = create_user(role=ROLE_STUDENT, email="s@example.com")
    login(client, user)
    client.get("/logout")
    # Protected page now redirects to login.
    assert client.get("/student/browse").status_code == 302


def test_register_redirects_when_logged_in(client):
    user = create_user(role=ROLE_STUDENT, email="s@example.com")
    login(client, user)
    assert client.get("/register").status_code == 302


# --- main (role-based redirects) -------------------------------------------

def test_index_redirects_when_logged_in(client):
    user = create_user(role=ROLE_STUDENT, email="s@example.com")
    login(client, user)
    assert client.get("/").status_code == 302


def test_dashboard_redirects_by_role(client):
    staff = create_user(role=ROLE_STAFF, email="staff@example.com")
    login(client, staff)
    r = client.get("/dashboard")
    assert r.status_code == 302 and "/staff/dashboard" in r.headers["Location"]

    student = create_user(role=ROLE_STUDENT, email="stud@example.com")
    login(client, student)
    r = client.get("/dashboard")
    assert r.status_code == 302 and "/student/browse" in r.headers["Location"]


# --- staff pages & idea edit/delete ----------------------------------------

def test_staff_dashboard_and_requests_render(client):
    staff = create_user(role=ROLE_STAFF, email="staff@example.com")
    login(client, staff)
    assert client.get("/staff/dashboard").status_code == 200
    assert client.get("/staff/requests").status_code == 200


def test_staff_profile_get_and_update(client):
    staff = create_user(role=ROLE_STAFF, email="staff@example.com")
    login(client, staff)
    assert client.get("/staff/profile").status_code == 200
    client.post("/staff/profile", data={"name": "Dr New", "title": "Dr",
                                        "bio": "Bio", "capacity": "3"})
    updated = db.session.get(User, staff.id)
    assert updated.name == "Dr New" and updated.capacity == 3


def test_edit_and_delete_project_idea(client):
    staff = create_user(role=ROLE_STAFF, email="staff@example.com")
    idea = ProjectIdea(title="Old", description="d", staff_id=staff.id, status="open")
    db.session.add(idea)
    db.session.commit()
    login(client, staff)
    client.post(f"/staff/ideas/{idea.id}/edit",
                data={"title": "New title", "description": "nd", "status": "taken"})
    edited = db.session.get(ProjectIdea, idea.id)
    assert edited.title == "New title" and edited.status == "taken"
    client.post(f"/staff/ideas/{idea.id}/delete")
    assert db.session.get(ProjectIdea, idea.id) is None


def test_cannot_edit_another_staffs_idea(client):
    owner = create_user(role=ROLE_STAFF, email="owner@example.com")
    other = create_user(role=ROLE_STAFF, email="other@example.com")
    idea = ProjectIdea(title="X", description="d", staff_id=owner.id)
    db.session.add(idea)
    db.session.commit()
    login(client, other)
    assert client.post(f"/staff/ideas/{idea.id}/edit",
                       data={"title": "H", "description": "h"}).status_code == 404


# --- student pages & request with a named idea -----------------------------

def test_student_pages_render(client):
    staff = create_user(role=ROLE_STAFF, email="staff@example.com", name="Prof A")
    db.session.add(AreaOfInterest(name="Web", staff_id=staff.id))
    db.session.commit()
    student = create_user(role=ROLE_STUDENT, email="stud@example.com")
    login(client, student)
    assert client.get(f"/student/staff/{staff.id}").status_code == 200
    assert client.get("/student/saved").status_code == 200
    assert client.get("/student/interests").status_code == 200
    assert client.get("/student/requests").status_code == 200


def test_send_request_with_valid_project_idea(client):
    staff = create_user(role=ROLE_STAFF, email="staff@example.com")
    idea = ProjectIdea(title="Proj", description="d", staff_id=staff.id, status="open")
    db.session.add(idea)
    db.session.commit()
    student = create_user(role=ROLE_STUDENT, email="stud@example.com")
    login(client, student)
    client.post(f"/student/staff/{staff.id}/request",
                data={"message": "hi", "project_idea_id": str(idea.id)})
    req = SupervisionRequest.query.filter_by(student_id=student.id, staff_id=staff.id).first()
    assert req is not None and req.project_idea_id == idea.id
