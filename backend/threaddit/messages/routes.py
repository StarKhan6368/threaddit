from datetime import UTC, datetime
from typing import TYPE_CHECKING

import sqlalchemy as sa
from flask import Blueprint, abort, jsonify, request
from flask_jwt_extended import current_user, jwt_required

from threaddit import db
from threaddit.messages.models import Messages
from threaddit.messages.schemas import MessageFormType, MessageSchema, NewMessageSchema

if TYPE_CHECKING:
    from threaddit.users.models import User

messages = Blueprint("messages", __name__)
new_message_schema = NewMessageSchema()
message_schema = MessageSchema()
messages_schema = MessageSchema(many=True)


@messages.route("/users/<user_name:receiver>/messages", methods=["POST"])
@jwt_required()
def message_add(receiver: "User"):
    if current_user.id != receiver.id:
        return abort(403, {"message": "Unauthorized"})
    form: "MessageFormType" = new_message_schema.load(request.form | request.files)
    message = Messages.add(current_user, receiver, form)
    return message_schema.dump(message), 201


@messages.route("/users/<user_name:user>/messages/<message_id:message>", methods=["PATCH"])
@jwt_required()
def message_update(user: "User", message: "Messages"):
    if current_user.id != user.id or current_user.id != message.sender_id:
        return abort(403, {"message": "Unauthorized"})
    form: "MessageFormType" = new_message_schema.load(request.form | request.files)
    message.patch(form)
    return message_schema.dump(message), 200


@messages.route("/users/<user_name:user>/messages/<message_id:message>", methods=["DELETE"])
@jwt_required()
def message_del(user: "User", message: "Messages"):
    if current_user.id != user.id or current_user.id != message.sender_id:
        return abort(403, {"message": "Unauthorized"})
    message.remove()
    return jsonify(message="Message deleted"), 200


@messages.route("/users/<user_name:user>/inbox")
@jwt_required()
def inbox_get(user: "User"):
    if current_user.id != user.id:
        return abort(403, {"message": "Unauthorized"})
    subquery = (
        sa.select(sa.func.max(Messages.id).label("latest_id"))
        .where(sa.or_(Messages.sender_id == user.id, Messages.receiver_id == user.id))
        .group_by(sa.case((Messages.sender_id == user.id, Messages.receiver_id), else_=Messages.sender_id))
    )
    messages_list = db.session.scalars(sa.select(Messages).where(Messages.id.in_(subquery))).all()
    return messages_schema.dump(messages_list), 200


@messages.route("/users/<user_name:sender>/messages/<user_name:receiver>", methods=["GET"])
@jwt_required()
def get_messages(sender: "User", receiver: "User"):
    if current_user.id != sender.id:
        return abort(403, {"message": "Unauthorized"})
    messages_list = db.session.scalars(
        sa.select(Messages)
        .where(
            sa.or_(
                sa.and_(Messages.sender_id == sender.id, Messages.receiver_id == receiver.id),
                sa.and_(Messages.sender_id == receiver.id, Messages.receiver_id == sender.id),
            )
        )
        .order_by(Messages.id.desc())
    ).all()
    for message in messages_list:
        if not message.seen_at and message.sender_id == receiver.id:
            message.seen_at = datetime.now(tz=UTC)
    return messages_schema.dump(messages_list), 200
