from functools import wraps

from flask import abort
from flask_login import current_user

from app.models import Permission, Group


def permission_required(permission):
    """Restrict a view to users with the given permission."""

    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.can(permission):
                abort(403)
            return f(*args, **kwargs)

        return decorated_function

    return decorator


def admin_required(f):
    return permission_required(Permission.ADMINISTER)(f)


# TODO: add handling for non-existant groups
def group_required(groups):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            authorised = False
            for g in groups:
                group = Group.query.filter_by(name=g).first()
                if current_user in group.users:
                    authorised = True
            if not authorised:
                abort(403)
            return func(*args, **kwargs)
        return wrapper
    return decorator
