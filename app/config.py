"""Application configuration objects.

Separate config classes keep runtime and test settings apart so the test
suite always runs against a disposable in-memory database.
"""
import os

from sqlalchemy.pool import StaticPool


class Config:
    """Base configuration used when the app runs normally."""

    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret-change-me")
    # Left as None so the app factory can default it to a file inside the
    # Flask instance folder. Set DATABASE_URL to override (e.g. Postgres).
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL")
    SQLALCHEMY_TRACK_MODIFICATIONS = False


class TestConfig(Config):
    """Configuration used by the pytest suite.

    Uses a single shared in-memory SQLite connection (StaticPool) so tables
    created in a test remain visible for the whole test.
    """

    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite://"
    SQLALCHEMY_ENGINE_OPTIONS = {
        "connect_args": {"check_same_thread": False},
        "poolclass": StaticPool,
    }
    SECRET_KEY = "test-secret"
    WTF_CSRF_ENABLED = False
