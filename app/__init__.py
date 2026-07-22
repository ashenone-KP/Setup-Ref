"""Application factory for the Supervisor-Matching system.

Using a factory (rather than a module-level app) lets the test suite build a
fresh app with a disposable database, and keeps configuration in one place.
"""
import os

from flask import Flask, render_template

from .config import Config
from .extensions import db, login_manager


def create_app(config_class=Config):
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object(config_class)

    # Ensure the instance folder exists, then default the database to a file
    # inside it if one was not supplied via config/environment.
    os.makedirs(app.instance_path, exist_ok=True)
    if not app.config.get("SQLALCHEMY_DATABASE_URI"):
        app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + os.path.join(
            app.instance_path, "supervisor_match.db"
        )

    db.init_app(app)
    login_manager.init_app(app)

    # Import models so SQLAlchemy is aware of them before create_all().
    from . import models  # noqa: F401

    # Register blueprints.
    from .blueprints.auth import auth_bp
    from .blueprints.main import main_bp
    from .blueprints.staff import staff_bp
    from .blueprints.student import student_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(staff_bp)
    app.register_blueprint(student_bp)

    register_error_handlers(app)

    with app.app_context():
        db.create_all()

    return app


def register_error_handlers(app):
    @app.errorhandler(403)
    def forbidden(_error):
        return render_template("errors/403.html"), 403

    @app.errorhandler(404)
    def not_found(_error):
        return render_template("errors/404.html"), 404
