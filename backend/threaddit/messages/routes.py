from threaddit.messages.models import Messages
from flask import Blueprint, jsonify, request
from threaddit import db
from sqlalchemy import and_
from threaddit.users.models import User
from flask_login import login_required, current_user

messages = Blueprint("messages", __name__, url_prefix="/api")


@messages.route("/messages", methods=["POST"])
def new_message():
    form_data = request.json
    if form_data["content"]:
        receiver_id = User.query.filter_by(username=form_data["receiver"]).first().id
        new_message = Messages(
            sender_id=current_user.id,
            receiver_id=receiver_id,
            content=form_data["content"],
        )
        db.session.add(new_message)
        db.session.commit()
        return jsonify(new_message.as_dict()), 200
    else:
        return jsonify({"message": "Content is required"}), 400


@messages.route("/messages/inbox")
@login_required
def get_inbox():
    return jsonify(Messages.get_inbox(current_user.id)), 200


@messages.route("/messages/all/<user_name>")
@login_required
def get_messages(user_name):
    user_id = User.query.filter_by(username=user_name).first().id
    messages = Messages.query.filter(
        and_(Messages.receiver_id == user_id, Messages.sender_id == current_user.id)
        | and_(Messages.sender_id == user_id, Messages.receiver_id == current_user.id)
    ).order_by(Messages.created_at)
    for m in messages:
        if m.receiver_id == current_user.id and m.seen == False:
            m.seen = True
            m.seen_at = db.func.now()
    db.session.commit()
    return jsonify([m.as_dict() for m in messages.all()]), 200
