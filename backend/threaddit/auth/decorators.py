from functools import wraps

from flask import abort
from flask_jwt_extended import current_user

from threaddit.moderations.models import RoleType


def roles_accepted(*roles):
    """
    Doesn't Implicitly call jwt_required decorator,
    User Must have at least one of the roles mentioned.
    :param roles: roles to require
    """

    def wrapper(func):
        @wraps(func)
        def decorated(*args, **kwargs):
            accepted_roles = [RoleType(role) for role in roles]
            if not any(role in current_user.rolenames for role in accepted_roles):
                return abort(403, {"message": "Unauthorized"})
            return func(*args, **kwargs)

        return decorated

    return wrapper


def admin_mod():
    """
    Doesn't Implicitly call jwt_required decorator, must at least have thread converter in route
    Checks if user is admin or moderator in thread
    """

    def wrapper(func):
        @wraps(func)
        def decorated(*args, **kwargs):
            thread = kwargs.get("thread")
            if not current_user.is_admin and not current_user.moderator_in(thread):
                return abort(403, {"message": "Unauthorized"})
            return func(*args, **kwargs)

        return decorated

    return wrapper


def admin_mod_author():
    """
    Doesn't Implicitly call jwt_required decorator, route must at least have thread converter
    Checks if current user created comment -> post -> thread in order whichever exist first
    Then checks if user is admin or moderator in thread
    """

    def wrapper(func):
        @wraps(func)
        def decorated(*args, **kwargs):
            thread = kwargs.get("thread")
            if kwargs.get("comment"):
                creator_id = kwargs.get("comment").user_id
            elif kwargs.get("post"):
                creator_id = kwargs.get("post").user_id
            else:
                creator_id = thread.created_by
            if creator_id:
                if creator_id != current_user.id:
                    return abort(403, {"message": "Unauthorized"})
            elif not current_user.is_admin or not current_user.moderator_in(thread):
                return abort(403, {"message": "Unauthorized"})
            return func(*args, **kwargs)

        return decorated

    return wrapper
