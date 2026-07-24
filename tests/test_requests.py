"""Tests for supervision requests: sending, guards, accept/decline, capacity."""
from app.extensions import db
from app.models import (ROLE_STAFF, ROLE_STUDENT, ProjectIdea,
                        SupervisionRequest, User)

from tests.conftest import create_user, login


def _staff(email="staff@example.com", capacity=2):
    return create_user(role=ROLE_STAFF, email=email, capacity=capacity)


def _student(email="stud@example.com"):
    return create_user(role=ROLE_STUDENT, email=email)


def test_student_can_send_request(client):
    staff = _staff()
    student = _student()
    login(client, student)
    client.post(f"/student/staff/{staff.id}/request", data={"message": "hi"})
    req = SupervisionRequest.query.one()
    assert req.status == "pending"
    assert req.student_id == student.id and req.staff_id == staff.id


def test_duplicate_pending_blocked(client):
    staff = _staff()
    student = _student()
    login(client, student)
    client.post(f"/student/staff/{staff.id}/request", data={"message": "a"})
    client.post(f"/student/staff/{staff.id}/request", data={"message": "b"})
    assert SupervisionRequest.query.count() == 1


def test_cannot_request_after_accepted(client):
    s1, s2 = _staff("s1@example.com"), _staff("s2@example.com")
    student = _student()
    db.session.add(SupervisionRequest(student_id=student.id, staff_id=s1.id, status="accepted"))
    db.session.commit()
    login(client, student)
    client.post(f"/student/staff/{s2.id}/request", data={"message": "x"})
    assert SupervisionRequest.query.filter_by(staff_id=s2.id).count() == 0


def test_accept_respects_capacity(client):
    staff = _staff(capacity=1)
    a, b = _student("a@example.com"), _student("b@example.com")
    r1 = SupervisionRequest(student_id=a.id, staff_id=staff.id, status="pending")
    r2 = SupervisionRequest(student_id=b.id, staff_id=staff.id, status="pending")
    db.session.add_all([r1, r2])
    db.session.commit()
    login(client, staff)
    client.post(f"/staff/requests/{r1.id}/accept")
    assert db.session.get(SupervisionRequest, r1.id).status == "accepted"
    # Now full — the second accept must be rejected.
    client.post(f"/staff/requests/{r2.id}/accept")
    assert db.session.get(SupervisionRequest, r2.id).status == "pending"


def test_decline(client):
    staff = _staff()
    student = _student()
    r = SupervisionRequest(student_id=student.id, staff_id=staff.id, status="pending")
    db.session.add(r)
    db.session.commit()
    login(client, staff)
    client.post(f"/staff/requests/{r.id}/decline")
    assert db.session.get(SupervisionRequest, r.id).status == "declined"


def test_accept_marks_named_idea_taken(client):
    staff = _staff()
    student = _student()
    idea = ProjectIdea(title="T", description="D", staff_id=staff.id, status="open")
    db.session.add(idea)
    db.session.commit()
    r = SupervisionRequest(student_id=student.id, staff_id=staff.id,
                           project_idea_id=idea.id, status="pending")
    db.session.add(r)
    db.session.commit()
    login(client, staff)
    client.post(f"/staff/requests/{r.id}/accept")
    assert db.session.get(ProjectIdea, idea.id).status == "taken"


def test_staff_cannot_accept_others_request(client):
    owner, other = _staff("owner@example.com"), _staff("other@example.com")
    student = _student()
    r = SupervisionRequest(student_id=student.id, staff_id=owner.id, status="pending")
    db.session.add(r)
    db.session.commit()
    login(client, other)
    resp = client.post(f"/staff/requests/{r.id}/accept")
    assert resp.status_code == 404
    assert db.session.get(SupervisionRequest, r.id).status == "pending"


def test_student_sees_own_requests(client):
    staff = create_user(role=ROLE_STAFF, email="staff@example.com", name="Prof Who")
    student = _student()
    db.session.add(SupervisionRequest(student_id=student.id, staff_id=staff.id,
                                      status="pending", message="hello"))
    db.session.commit()
    login(client, student)
    resp = client.get("/student/requests")
    assert b"Prof Who" in resp.data
