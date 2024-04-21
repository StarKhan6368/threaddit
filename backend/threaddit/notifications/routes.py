from datetime import UTC, datetime

import sqlalchemy as sa
from flask import Blueprint, abort, jsonify
from flask_jwt_extended import current_user, jwt_required

from threaddit import db
from threaddit.notifications.models import Notifications
from threaddit.notifications.schemas import NotificationSchema

notifications = Blueprint("notifications", __name__)
notifs_schema = NotificationSchema(many=True)


@notifications.route("/me/notifications", methods=["GET"])
@jwt_required()
def user_notification_get():
    notif_list = db.session.scalars(sa.select(Notifications).where(Notifications.user_id == current_user.id)).all()
    return notifs_schema.dump(notif_list), 200


@notifications.route("/me/notifications/unread", methods=["GET"])
@jwt_required()
def user_notification_unread_get():
    notif_list = db.session.scalars(
        sa.select(Notifications).where(
            sa.and_(Notifications.user_id == current_user.id, Notifications.seen_at.is_(None))
        )
    ).all()
    return notifs_schema.dump(notif_list), 200


@notifications.route("/me/notifications", methods=["PATCH"])
@jwt_required()
def user_notifs_read():
    stmt = db.session.execute(
        sa.update(Notifications)
        .where(Notifications.user_id == current_user.id, Notifications.seen_at.is_(None))
        .values(seen_at=datetime.now(tz=UTC))
        .returning(Notifications)
    )
    notif_list = db.session.scalars(stmt).all()
    db.session.commit()
    return notifs_schema.dump(notif_list), 200


@notifications.route("/me/notifications/<notif_id:notification>", methods=["PATCH"])
@jwt_required()
def user_notif_read(notification: "Notifications"):
    if notification.user_id != current_user.id:
        return abort(403, {"message": "Unauthorized"})
    notification.read()
    db.session.commit()
    return notifs_schema.dump([notification]), 200


@notifications.route("/me/notifications", methods=["DELETE"])
@jwt_required()
def user_notifs_del():
    db.session.execute(sa.delete(Notifications).where(Notifications.user_id == current_user.id))
    db.session.commit()
    return jsonify(message="Successfully Deleted All Read Notifications"), 200


@notifications.route("/me/notifications/read", methods=["DELETE"])
@jwt_required()
def user_notifs_read_del():
    db.session.execute(
        sa.delete(Notifications).where(Notifications.user_id == current_user.id, Notifications.seen_at.is_not(None))
    )
    db.session.commit()
    return jsonify(message="Successfully Deleted All Read Notifications"), 200


@notifications.route("/me/notifications/<notif_id:notification>", methods=["DELETE"])
@jwt_required()
def user_notif_del(notification: "Notifications"):
    if notification.user_id != current_user.id:
        return abort(403, {"message": "Unauthorized"})
    notification.delete()
    db.session.commit()
    return notifs_schema.dump([notification]), 200
