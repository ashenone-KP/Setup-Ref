"""Populate the database with demo data.

Run with `python seed.py`. Useful for the demo video and manual testing.
Wipes and recreates all tables, then adds staff (with areas and project
ideas) and a couple of students with interests.
"""
from app import create_app
from app.extensions import db
from app.models import (AreaOfInterest, Interest, ProjectIdea, ROLE_STAFF,
                        ROLE_STUDENT, User)

STAFF = [
    {
        "name": "Claudia Iacob", "title": "Dr", "email": "claudia@uni.ac.uk",
        "bio": "Human-computer interaction and software engineering education.",
        "capacity": 5,
        "areas": ["Human-computer interaction", "Software engineering", "Requirements engineering"],
        "ideas": [
            ("Usability of student-facing university tools",
             "Evaluate and redesign a university web tool using HCI methods.",
             "Human-computer interaction"),
            ("A recommender for module choices",
             "Build and test a recommender that suggests optional modules.",
             "Software engineering"),
        ],
    },
    {
        "name": "David Okafor", "title": "Dr", "email": "david@uni.ac.uk",
        "bio": "Graph theory and algorithms for large networks.",
        "capacity": 3,
        "areas": ["Graph theory", "Algorithms", "Data analysis"],
        "ideas": [
            ("Community detection in social graphs",
             "Implement and compare community-detection algorithms on real data.",
             "Graph theory"),
        ],
    },
    {
        "name": "Priya Nair", "title": "Prof", "email": "priya@uni.ac.uk",
        "bio": "Software maintenance, testing and program analysis.",
        "capacity": 4,
        "areas": ["Software maintenance", "Software testing", "Data analysis"],
        "ideas": [
            ("Automated test generation for legacy code",
             "Explore tools that generate unit tests for an untested codebase.",
             "Software testing"),
            ("Mining bug reports for maintenance insights",
             "Analyse an open-source issue tracker to find maintenance patterns.",
             "Software maintenance"),
        ],
    },
]

STUDENTS = [
    {"name": "Sam Taylor", "email": "sam@uni.ac.uk",
     "interests": ["Software testing", "Data analysis"]},
    {"name": "Mia Chen", "email": "mia@uni.ac.uk",
     "interests": ["Graph theory", "Algorithms"]},
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
        print("Seeded:", User.query.count(), "users,",
              AreaOfInterest.query.count(), "areas,",
              ProjectIdea.query.count(), "project ideas.")
        print("All demo accounts use the password: password123")


if __name__ == "__main__":
    seed()
