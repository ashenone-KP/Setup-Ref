"""Flask extension instances.

Kept in their own module so both the app factory and the models can import
them without creating circular imports.
"""
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()
login_manager = LoginManager()
login_manager.login_view = "auth.login"
login_manager.login_message_category = "error"
