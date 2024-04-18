from typing import TYPE_CHECKING

import sqlalchemy as sa
from flask import Blueprint, abort, jsonify
from flask_jwt_extended import current_user, jwt_required

from threaddit import db
from threaddit.auth.decorators import roles_accepted
from threaddit.moderations.models import UserRole
from threaddit.users.models import User
from threaddit.users.schemas import UserLinkSchema

if TYPE_CHECKING:
    from threaddit.threads.models import Thread

moderations = Blueprint("moderation", __name__)
users_link_schema = UserLinkSchema(many=True)


@moderations.route("/threads/<thread_id:thread>/moderators", methods=["GET"])
def get_moderators(thread: "Thread"):
    modlist = db.session.scalars(
        sa.select(User).join(UserRole).where(UserRole.thread_id == thread.id, UserRole.role_id == 1)
    ).all()
    return users_link_schema.dump(modlist), 200


@moderations.route("/threads/<thread_id:thread>/moderators/<user_name:user>", methods=["POST"])
@jwt_required()
@roles_accepted("admin", "mod")
def new_mod(thread: "Thread", user: "User"):
    user_role = db.session.scalar(
        sa.select(UserRole).where(UserRole.user_id == user.id, UserRole.thread_id == thread.id, UserRole.role_id == 1)
    )
    if current_user.is_admin or current_user.moderator_in(thread):
        if user_role:
            return abort(400, {"message": "User already moderator"})
        UserRole.add_moderator(user, thread)
        db.session.commit()
        return jsonify(message="Moderator added"), 200
    return abort(403, {"message": "Unauthorized"})


@moderations.route("/threads/<thread_id:thread>/moderators/<user_name:user>", methods=["DELETE"])
@jwt_required()
@roles_accepted("admin", "mod")
def delete_mod(thread: "Thread", user: "User"):
    user_role = db.session.scalar(
        sa.select(UserRole).where(UserRole.user_id == user.id, UserRole.thread_id == thread.id, UserRole.role_id == 1)
    )
    if (current_user.is_admin or current_user.moderator_in(thread)) and user_role:
        user_role.delete()
        db.session.commit()
        return jsonify(message="Moderator removed"), 200
    return abort(403, {"message": "Unauthorized"})


@moderations.route("/moderators/admins", methods=["GET"])
@jwt_required()
@roles_accepted("admin")
def get_admins():
    admins = db.session.scalars(sa.select(User).join(UserRole).where(UserRole.role_id == 2))  # noqa: PLR2004
    return users_link_schema.dump(admins), 200


@moderations.route("/moderators/admins/<user_name:user>", methods=["POST"])
@jwt_required()
@roles_accepted("admin")
def admin_add(user: "User"):
    user_role = db.session.scalar(sa.select(UserRole).where(UserRole.user_id == user.id, UserRole.role_id == 2))  # noqa: PLR2004
    if current_user.is_admin:
        if user_role:
            return abort(400, {"message": "User already admin"})
        UserRole.add_admin(user)
        db.session.commit()
        return jsonify(message="Admin added"), 200
    return abort(403, {"message": "Unauthorized"})


@moderations.route("/moderators/admins/<user_name:user>", methods=["DELETE"])
@jwt_required()
@roles_accepted("admin")
def admin_remove(user: "User"):
    user_role = db.session.scalar(sa.select(UserRole).where(UserRole.user_id == user.id, UserRole.role_id == 2))  # noqa: PLR2004
    if current_user.is_admin and user_role:
        user_role.delete()
        db.session.commit()
        return jsonify(message="Admin removed"), 200
    return abort(403, {"message": "Unauthorized"})
