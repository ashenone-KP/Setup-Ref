"""Populate the database with demo data.

Run with `python seed.py`. Useful for the demo video and manual testing.
Wipes and recreates all tables, then adds staff (with areas and project
ideas) and a couple of students with interests.
"""
from app import create_app
from app.extensions import db
from app.models import (AreaOfInterest, Bookmark, Interest, ProjectIdea,
                        ROLE_STAFF, ROLE_STUDENT, SupervisionRequest, User)

STAFF = [
    {
        "name": "Claudia Iacob", "title": "Dr", "email": "claudia@uni.ac.uk",
        "bio": "Human-computer interaction and software engineering education.",
        "capacity": 5,
        "areas": ["HCI", "Software Engineering", "Systems Analysis"],
        "ideas": [
            ("Usability of student-facing university tools",
             "Evaluate and redesign a university web tool using HCI methods.",
             "HCI"),
            ("A recommender for module choices",
             "Build and test a recommender that suggests optional modules.",
             "Software Engineering"),
        ],
    },
    {
        "name": "David Okafor", "title": "Dr", "email": "david@uni.ac.uk",
        "bio": "Graph theory and algorithms for large networks.",
        "capacity": 3,
        "areas": ["Algorithms", "Computation / Maths", "Data Analytics"],
        "ideas": [
            ("Community detection in social graphs",
             "Implement and compare community-detection algorithms on real data.",
             "Algorithms"),
        ],
    },
    {
        "name": "Priya Nair", "title": "Prof", "email": "priya@uni.ac.uk",
        "bio": "Software maintenance, testing and program analysis.",
        "capacity": 4,
        "areas": ["Software Engineering", "Databases", "Cyber Security / Security"],
        "ideas": [
            ("Automated test generation for legacy code",
             "Explore tools that generate unit tests for an untested codebase.",
             "Software Engineering"),
            ("Mining bug reports for maintenance insights",
             "Analyse an open-source issue tracker to find maintenance patterns.",
             "Databases"),
        ],
    },
]

STUDENTS = [
    {"name": "Sam Taylor", "email": "sam@uni.ac.uk",
     "interests": ["Software Engineering", "Data Analytics"]},
    {"name": "Mia Chen", "email": "mia@uni.ac.uk",
     "interests": ["Algorithms", "Computation / Maths"]},
]


def seed():
    app = create_app()
    with app.app_context():
        db.drop_all()
        db.create_all()

        for spec in STAFF:
            staff = User(
                name=spec["name"], title=spec["title"], email=spec["email"],
                role=ROLE_STAFF, bio=spec["bio"], capacity=spec["capacity"],
            )
            staff.set_password("password123")
            db.session.add(staff)
            db.session.flush()  # assign staff.id
            for area in spec["areas"]:
                db.session.add(AreaOfInterest(name=area, staff_id=staff.id))
            for title, desc, tag in spec["ideas"]:
                db.session.add(ProjectIdea(
                    title=title, description=desc, area_name=tag, staff_id=staff.id
                ))

        for spec in STUDENTS:
            student = User(name=spec["name"], email=spec["email"], role=ROLE_STUDENT)
            student.set_password("password123")
            db.session.add(student)
            db.session.flush()
            for interest in spec["interests"]:
                db.session.add(Interest(name=interest, student_id=student.id))

        db.session.commit()

        # A couple of demo requests + bookmarks so the states look populated.
        by_email = {u.email: u for u in User.query.all()}
        sam = by_email["sam@uni.ac.uk"]
        mia = by_email["mia@uni.ac.uk"]
        db.session.add_all([
            SupervisionRequest(
                student_id=sam.id, staff_id=by_email["david@uni.ac.uk"].id,
                message="I'd love to work on graph algorithms.", status="pending"),
            SupervisionRequest(
                student_id=mia.id, staff_id=by_email["priya@uni.ac.uk"].id,
                message="Interested in a database-focused project.", status="pending"),
            Bookmark(student_id=sam.id, staff_id=by_email["claudia@uni.ac.uk"].id),
            Bookmark(student_id=mia.id, staff_id=by_email["david@uni.ac.uk"].id),
        ])
        db.session.commit()

        print("Seeded:", User.query.count(), "users,",
              AreaOfInterest.query.count(), "areas,",
              ProjectIdea.query.count(), "project ideas,",
              SupervisionRequest.query.count(), "requests,",
              Bookmark.query.count(), "bookmarks.")
        print("All demo accounts use the password: password123")


if __name__ == "__main__":
    seed()
