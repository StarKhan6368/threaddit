from functools import wraps

from flask import abort
from flask_jwt_extended import current_user


def roles_accepted(*roles):
    """
    Doesn't Implicitly call jwt_required decorator,
    User Must have at least one of the roles mentioned.
    :param roles: roles to require
    """

    def wrapper(func):
        @wraps(func)
        def decorated(*args, **kwargs):
            user_roles = current_user.rolenames
            if not any(role in user_roles for role in roles):
                abort(403, "Unauthorized")
            return func(*args, **kwargs)

        return decorated

    return wrapper
