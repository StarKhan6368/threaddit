from flask import Blueprint, jsonify, request
from flask_login import current_user, login_required
from sqlalchemy import and_

from threaddit import db
from threaddit.messages.models import MessageSchema, Messages
from threaddit.users.models import User

messages = Blueprint("messages", __name__, url_prefix="/api")


@messages.route("/messages", methods=["POST"])
def new_message():
    if form_data := request.json:
        receiver_id = User.query.filter_by(username=form_data["receiver"]).first()
        if receiver_id:
            MessageSchema().load(form_data)
            message = Messages.add(current_user.id, receiver_id.id, form_data["content"])
            return jsonify(message.as_dict()), 200
        return jsonify({"message": "User not found"}), 404
    return jsonify({"message": "Content is required"}), 400


@messages.route("/messages/<message_id>", methods=["PATCH"])
def update_message(message_id):
    if form_data := request.json:
        message = Messages.query.filter_by(id=message_id).first()
        if message:
            MessageSchema().load(form_data)
            message.patch(form_data.get("content", message.content))
            return jsonify(message.as_dict()), 200
        return jsonify({"message": "Message not found"}), 404
    return jsonify({"message": "Content is required"}), 400


@messages.route("/messages/<message_id>", methods=["DELETE"])
def delete_message(message_id):
    message = Messages.query.filter_by(id=message_id).first()
    if message:
        message.remove()
        return jsonify({"message": "Message deleted"}), 200
    return jsonify({"message": "Message not found"}), 404


@messages.route("/messages/inbox")
@login_required
def get_inbox():
    return jsonify(Messages.get_inbox(current_user.id)), 200


@messages.route("/messages/all/<user_name>")
@login_required
def get_messages(user_name):
    user_id = User.query.filter_by(username=user_name).first()
    if user_id:
        messages = Messages.query.filter(
            and_(Messages.receiver_id == user_id.id, Messages.sender_id == current_user.id)
            | and_(Messages.sender_id == user_id.id, Messages.receiver_id == current_user.id)
        ).order_by(Messages.created_at)
        for m in messages:
            if m.receiver_id == current_user.id and not m.seen:
                m.seen = True
                m.seen_at = db.func.now()
        db.session.commit()
        return jsonify([m.as_dict() for m in messages.all()]), 200
    return jsonify({"message": "User not found"}), 404
