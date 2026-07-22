"""Role-based access decorators.

Stacked underneath @login_required so authentication is already guaranteed;
these only enforce that the logged-in user has the right role.
"""
from functools import wraps

from flask import abort
from flask_login import current_user


def staff_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_staff:
            abort(403)
        return view(*args, **kwargs)

    return wrapped


def student_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_student:
            abort(403)
        return view(*args, **kwargs)

    return wrapped
