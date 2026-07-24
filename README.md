# SupervisorMatch

A web application that helps final-year students find a project supervisor.
Staff publish their **areas of interest** and **project ideas**; students
**browse and search** staff, get **recommended supervisors**, **bookmark**
favourites, and send **supervision requests**.

Built for the M30819 *Software Engineering Theory and Practice* referral
(individual submission).

## Tech stack

- **Python 3.12** / **Flask** (application factory + blueprints)
- **Flask-SQLAlchemy** (ORM) with **SQLite**
- **Flask-Login** (authentication & role-based access)
- **pytest** + **pytest-cov** (automated tests)
- Server-rendered **Jinja2** templates + plain CSS

## Architecture (MVC / 3-tier)

| Layer | Responsibility | Where |
|-------|----------------|-------|
| Presentation (View) | HTML pages, styling | `app/templates`, `app/static` |
| Application (Controller) | Request handling, routing, access control | `app/blueprints`, `app/decorators.py` |
| Domain logic (Service) | Reusable business logic (e.g. matching) | `app/services` |
| Data (Model) | Entities & persistence | `app/models.py` |

## Setup

```bash
python -m venv .venv
.venv\Scripts\activate        # Windows
pip install -r requirements.txt
python seed.py                # optional: load demo data
python run.py                 # http://127.0.0.1:5000
```

Demo accounts (after `seed.py`) all use the password `password123`, e.g.
`claudia@uni.ac.uk` (staff) and `sam@uni.ac.uk` (student).

## Tests

```bash
python -m pytest                              # run all tests
python -m pytest --cov=app --cov-report=term  # with coverage
```

## Design & attribution

The visual design (layout, component styling, dashboard shell) is adapted from a
Figma Community template built with [shadcn/ui](https://ui.shadcn.com/) (MIT licence),
re-implemented in plain CSS and themed with the University of Portsmouth brand
colours (deep purple `#350034`, azure `#00A0FF`). The original template is kept for
reference under `docs/design/reference/`.

## Project links

- Demo video: _add link here_
- Test plan: `docs/test-plan.md` (to be added)

## Status

Implemented: accounts & roles, staff area/project-idea management, student
browse/search & filter, supervisor matching service, UoP-themed UI.
Next: supervision requests, bookmarks, recommendation page.
