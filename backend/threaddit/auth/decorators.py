from functools import wraps
from flask import jsonify
from flask_login import current_user


def auth_role(role):
    def wrapper(func):
        @wraps(func)
        def decorated(*args, **kwargs):
            roles = role if isinstance(role, list) else [role]
            if not any(current_user.has_role(r) for r in roles):
                return jsonify({"message": "Unauthorized"}), 401
            return func(*args, **kwargs)
        return decorated
    return wrapper
