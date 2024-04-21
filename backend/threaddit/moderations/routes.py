from typing import TYPE_CHECKING

import sqlalchemy as sa
from flask import Blueprint, abort, jsonify, request
from flask_jwt_extended import current_user, jwt_required

from threaddit import db
from threaddit.auth.decorators import admin_mod, roles_accepted
from threaddit.moderations.models import ModAdminInv, RoleType, UserRole
from threaddit.moderations.schemas import ModAdminInvSchema, ResLockSchema, ResLockType, UserRoleSchema
from threaddit.notifications.models import Notifications, NotifType

if TYPE_CHECKING:
    from threaddit.comments.models import Comments
    from threaddit.posts.models import Posts
    from threaddit.threads.models import Thread
    from threaddit.users.models import User

moderations = Blueprint("moderation", __name__)
user_roles_schema = UserRoleSchema(many=True)
inv_schema = ModAdminInvSchema()
invs_schema = ModAdminInvSchema(many=True)
res_lock_schema = ResLockSchema()


@moderations.route("/users/<user_name:user>/invites/grantee", methods=["GET"])
@moderations.route("/me/invites/grantee", methods=["GET"])
def user_grantee_invites_get(user: "User"):
    invs = db.session.scalars(sa.select(ModAdminInv).where(ModAdminInv.grantee_id == user.id)).all()
    return invs_schema.dump(invs), 200


@moderations.route("/users/<user_name:user>/invites/granter", methods=["GET"])
@moderations.route("/me/invites/granter", methods=["GET"])
def user_granter_invites_get(user: "User"):
    invs = db.session.scalars(sa.select(ModAdminInv).where(ModAdminInv.granter_id == user.id)).all()
    return invs_schema.dump(invs), 200


@moderations.route("/users/<user_name:user>/roles/grantee", methods=["GET"])
@moderations.route("/me/roles", methods=["GET"])
def user_grantee_roles_get(user: "User"):
    roles = db.session.scalars(sa.select(UserRole).where(UserRole.grantee_id == user.id)).all()
    return user_roles_schema.dump(roles), 200


@moderations.route("/users/<user_name:user>/roles/granter", methods=["GET"])
@moderations.route("/me/roles/granter", methods=["GET"])
def user_granter_roles_get(user: "User"):
    roles = db.session.scalars(sa.select(UserRole).where(UserRole.granter_id == user.id)).all()
    return user_roles_schema.dump(roles), 200


@moderations.route("/threads/<thread_id:thread>/moderators/invites", methods=["GET"])
def thread_moderator_invites_get(thread: "Thread"):
    invs = db.session.scalars(sa.select(ModAdminInv).where(ModAdminInv.thread_id == thread.id)).all()
    return invs_schema.dump(invs), 200


@moderations.route("/moderators/invitations", methods=["GET"])
def admin_invites_get():
    invs = db.session.scalars(sa.select(ModAdminInv).where(ModAdminInv.role_type == RoleType.ADMIN)).all()
    return invs_schema.dump(invs), 200


@moderations.route("/threads/<thread_id:thread>/moderators", methods=["GET"])
def thread_moderators_get(thread: "Thread"):
    modlist = db.session.scalars(
        sa.select(UserRole).where(UserRole.thread_id == thread.id, UserRole.role_type == RoleType.MODERATOR)
    ).all()
    return user_roles_schema.dump(modlist), 200


@moderations.route("/threads/<thread_id:thread>/moderators/<user_name:user>", methods=["POST"])
@jwt_required()
@admin_mod()
def thread_moderator_inv(thread: "Thread", user: "User"):
    user_role = db.session.scalar(
        sa.select(UserRole).where(
            UserRole.grantee_id == user.id, UserRole.thread_id == thread.id, UserRole.role_type == RoleType.MODERATOR
        )
    )
    if user_role:
        return abort(400, {"message": "User already moderator"})
    inv = ModAdminInv.invite(user, user, RoleType.MODERATOR, thread=thread)
    db.session.commit()
    return inv_schema.dump(inv), 200


@moderations.route("/threads/<thread_id:thread>/moderators/<user_name:user>", methods=["DELETE"])
@jwt_required()
@admin_mod()
def thread_moderator_del(thread: "Thread", user: "User"):
    user_role = db.session.scalar(
        sa.select(UserRole).where(
            UserRole.grantee_id == user.id, UserRole.thread_id == thread.id, UserRole.role_id == RoleType.MODERATOR
        )
    )
    user_role.delete(current_user)
    db.session.commit()
    return jsonify(message="Moderator removed"), 200


@moderations.route("/moderators/admins", methods=["GET"])
@jwt_required()
@roles_accepted("ADMIN", "OWNER")
def admins_get():
    admins = db.session.scalars(sa.select(UserRole).where(UserRole.role_id == RoleType.ADMIN)).all()
    return user_roles_schema.dump(admins), 200


@moderations.route("/moderators/admins/<user_name:user>", methods=["POST"])
@jwt_required()
@roles_accepted("ADMIN")
def admin_inv(user: "User"):
    user_role = db.session.scalar(
        sa.select(UserRole).where(UserRole.grantee_id == user.id, UserRole.role_id == RoleType.ADMIN)
    )
    if user_role:
        return abort(400, {"message": "User already admin"})
    inv = ModAdminInv.invite(current_user, user, RoleType.ADMIN, thread=None)
    db.session.commit()
    return inv_schema.dump(inv), 200


@moderations.route("/threads/<thread_id:thread>/moderators/invitations/<inv_id:inv>/accept", methods=["POST"])
@jwt_required()
def moderator_inv_accept(thread: "Thread", inv: "ModAdminInv"):
    if current_user.id != inv.grantee_id or thread.id != inv.thread_id:
        return abort(403, {"message": "Unauthorized"})
    inv.accept()
    db.session.commit()
    return inv_schema.dump(inv), 200


@moderations.route("/threads/<thread_id:thread>/moderators/invitations/<inv_id:inv>/reject", methods=["POST"])
@jwt_required()
def moderator_inv_reject(thread: "Thread", inv: "ModAdminInv"):
    if current_user.id != inv.grantee_id or thread.id != inv.thread_id:
        return abort(403, {"message": "Unauthorized"})
    inv.reject()
    db.session.commit()
    return inv_schema.dump(inv), 200


@moderations.route("/moderators/admins/<inv_id:inv>/accept", methods=["POST"])
@jwt_required()
def admin_inv_accept(inv: "ModAdminInv"):
    if current_user.id != inv.grantee_id or inv.role_type != RoleType.ADMIN:
        return abort(403, {"message": "Unauthorized"})
    inv.accept()
    db.session.commit()
    return inv_schema.dump(inv), 200


@moderations.route("/moderators/admins/<inv_id:inv>/reject", methods=["POST"])
@jwt_required()
def admin_inv_reject(inv: "ModAdminInv"):
    if current_user.id != inv.grantee_id or inv.role_type != RoleType.ADMIN:
        return abort(403, {"message": "Unauthorized"})
    inv.reject()
    db.session.commit()
    return inv_schema.dump(inv), 200


@moderations.route("/moderators/admins/<user_name:user>", methods=["DELETE"])
@jwt_required()
@roles_accepted("admin")
def admin_del(user: "User"):
    user_role = db.session.scalar(
        sa.select(UserRole).where(UserRole.grantee_id == user.id, UserRole.role_id == RoleType.ADMIN)
    )
    if user_role:
        user_role.delete(current_user)
        db.session.commit()
        return jsonify(message="Admin removed"), 200
    return abort(403, {"message": "Unauthorized"})


@moderations.route("/threads/<thread_id:thread>/lock", methods=["POST"])
@jwt_required()
@admin_mod()
def thread_lock(thread: "Thread"):
    thread.is_locked = True
    db.session.commit()
    return jsonify(message="Thread locked"), 200


@moderations.route("/threads/<thread_id:thread>/unlock", methods=["POST"])
@jwt_required()
@admin_mod()
def thread_unlock(thread: "Thread"):
    thread.is_locked = False
    db.session.commit()
    return jsonify(message="Thread unlocked"), 200


# noinspection DuplicatedCode
@moderations.route("/threads/<thread_id:thread>/posts/<post_id:post>/lock", methods=["POST"])
@jwt_required()
@admin_mod()
def post_lock(thread: "Thread", post: "Posts"):
    post.validate_post(thread)
    body: "ResLockType" = res_lock_schema.load(request.json | {"thread_id": thread.id})
    post.is_locked = True
    Notifications.notify(
        notif_type=NotifType.POST_LOCKED,
        user=post.user,
        title=f"Your post on {thread.name} has been locked by {current_user.username}",
        sub_title=post.title,
        content=f"Reason: {body['report_type_id'].name}\n Comment: {body['mod_comment'] or 'None'}",
        res_id=post.id,
        res_media_id=None,
    )
    db.session.commit()
    return jsonify(message="Post locked"), 200


# noinspection PyUnusedLocal
@moderations.route("/threads/<thread_id:thread>/posts/<post_id:post>/unlock", methods=["POST"])
@jwt_required()
@admin_mod()
def post_unlock(thread: "Thread", post: "Posts"):
    post.validate_post(thread)
    post.is_locked = False
    Notifications.notify(
        notif_type=NotifType.POST_UNLOCKED,
        user=post.user,
        title=f"Your post on {thread.name} has been unlocked by {current_user.username}",
        sub_title=post.title,
        content=None,
        res_id=post.id,
        res_media_id=None,
    )
    db.session.commit()
    return jsonify(message="Post unlocked"), 200


# noinspection DuplicatedCode
@moderations.route(
    "/threads/<thread_id:thread>/posts/<post_id:post>/comments/<comment_id:comment>/lock", methods=["POST"]
)
@jwt_required()
@admin_mod()
def comment_lock(thread: "Thread", post: "Posts", comment: "Comments"):
    comment.validate_comment(thread, post)
    body: "ResLockType" = res_lock_schema.load(request.json | {"thread_id": thread.id})
    comment.is_locked = True
    Notifications.notify(
        notif_type=NotifType.COMMENT_LOCKED,
        user=post.user,
        title=f"Your comment on {thread.name} has been locked",
        sub_title=comment.content,
        content=f"Reason: {body['report_type_id'].name}\n Comment: {body['mod_comment'] or 'None'}",
        res_id=post.id,
        res_media_id=None,
    )
    db.session.commit()
    return jsonify(message="Post locked"), 200


# noinspection PyUnusedLocal
@moderations.route(
    "/threads/<thread_id:thread>/posts/<post_id:post>/comments/<comment_id:comment>/unlock", methods=["POST"]
)
@jwt_required()
@admin_mod()
def comment_unlock(thread: "Thread", post: "Posts", comment: "Comments"):
    comment.validate_comment(thread, post)
    comment.is_locked = False
    Notifications.notify(
        notif_type=NotifType.COMMENT_UNLOCKED,
        user=comment.user,
        title=f"Your comment on {thread.name} has been unlocked by {current_user.username}",
        sub_title=post.title,
        content=comment.content,
        res_id=post.id,
        res_media_id=None,
    )
    db.session.commit()
    return jsonify(message="Post unlocked"), 200
