from app.services.matching import normalise, overlap_score, recommend_supervisors

from tests.conftest import create_user, login  # noqa: F401  (login unused but handy)
from app.models import ROLE_STAFF, ROLE_STUDENT, AreaOfInterest, Interest
from app.extensions import db


def test_normalise_lowers_and_strips():
    assert normalise("  Graph Theory ") == "graph theory"


def test_overlap_score_no_overlap():
    score, shared = overlap_score(["a", "b"], ["c", "d"])
    assert score == 0
    assert shared == []


def test_overlap_score_partial_overlap():
    score, shared = overlap_score(["Graph theory", "Algorithms"], ["algorithms"])
    assert score == 1
    assert shared == ["algorithms"]


def test_overlap_score_ignores_case_and_blanks():
    score, shared = overlap_score(["Data Analysis", "  ", ""], ["data analysis"])
    assert score == 1
    assert shared == ["data analysis"]


def _staff_with_areas(email, area_names):
    staff = create_user(role=ROLE_STAFF, email=email)
    for name in area_names:
        db.session.add(AreaOfInterest(name=name, staff_id=staff.id))
    db.session.commit()
    return staff


def test_recommend_ranks_by_overlap(app):
    student = create_user(role=ROLE_STUDENT, email="stud@example.com")
    for interest in ["Graph theory", "Algorithms", "Data analysis"]:
        db.session.add(Interest(name=interest, student_id=student.id))
    db.session.commit()

    best = _staff_with_areas("best@example.com", ["Graph theory", "Algorithms"])
    some = _staff_with_areas("some@example.com", ["Data analysis"])
    none = _staff_with_areas("none@example.com", ["Networking"])

    ranked = recommend_supervisors(student, [some, none, best])
    # 'none' is excluded (score 0); 'best' ranks above 'some'.
    assert [s.email for s, _, _ in ranked] == ["best@example.com", "some@example.com"]
    assert ranked[0][1] == 2
