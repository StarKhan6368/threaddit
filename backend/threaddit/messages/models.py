from threaddit import db, app
import base64, os
from sqlalchemy import case, func, select


class Messages(db.Model):
    __tablename__ = "messages"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    sender_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    receiver_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    content = db.Column(db.Text, nullable=False)
    seen = db.Column(db.Boolean, default=False)
    seen_at = db.Column(db.DateTime(timezone=True))
    created_at = db.Column(
        db.DateTime(timezone=True), nullable=False, default=db.func.now()
    )
    user_sender = db.relationship(
        "User", back_populates="sender", primaryjoin="Messages.sender_id == User.id"
    )
    user_receiver = db.relationship(
        "User",
        back_populates="receiver",
        primaryjoin="Messages.receiver_id == User.id",
    )

    def __init__(self, sender_id, receiver_id, content):
        self.sender_id = sender_id
        self.receiver_id = receiver_id
        self.content = content

    def as_dict(self):
        if self.user_sender.avatar and not str(self.user_sender.avatar).startswith(
            "http"
        ):
            data = open(
                f"{app.config['UPLOAD_FOLDER']}/{self.user_sender.avatar}", "rb"
            ).read()
            user_sender_avatar = (
                f"data:image/jpeg;base64,{base64.b64encode(data).decode('utf-8')}"
            )
        else:
            user_sender_avatar = self.user_sender.avatar
        if self.user_receiver.avatar and not str(self.user_receiver.avatar).startswith(
            "http"
        ):
            data = open(
                f"{app.config['UPLOAD_FOLDER']}/{self.user_receiver.avatar}", "rb"
            ).read()
            user_receiver_avatar = (
                f"data:image/jpeg;base64,{base64.b64encode(data).decode('utf-8')}"
            )
        else:
            user_receiver_avatar = self.user_receiver.avatar
        return {
            "message_id": self.id,
            "sender": {
                "name": self.user_sender.username,
                "avatar": user_sender_avatar,
            },
            "receiver": {
                "name": self.user_receiver.username,
                "avatar": user_receiver_avatar,
            },
            "content": self.content,
            "created_at": self.created_at,
            "seen": self.seen,
            "seen_at": self.seen_at,
        }

    def get_inbox(user_id):
        my_case = case(
            (Messages.sender_id == user_id, Messages.receiver_id),
            else_=Messages.sender_id,
        ).label("contact_id")
        my_max = func.max(Messages.id).label("latest_id")
        my_subquery = (
            db.session.query(my_case, my_max)
            .filter((Messages.sender_id == user_id) | (Messages.receiver_id == user_id))
            .group_by("contact_id")
            .subquery()
        )
        messages = (
            Messages.query.join(my_subquery, my_subquery.c.latest_id == Messages.id)
            .order_by(Messages.created_at.desc())
            .all()
        )
        messages_list = []
        for message in messages:
            sender = (
                message.user_receiver
                if message.sender_id == user_id
                else message.user_sender
            )
            if sender.avatar and not str(sender.avatar).startswith("http"):
                data = open(
                    f"{app.config['UPLOAD_FOLDER']}/{sender.avatar}", "rb"
                ).read()
                sender_avatar = (
                    f"data:image/jpeg;base64,{base64.b64encode(data).decode('utf-8')}"
                )
            else:
                sender_avatar = sender.avatar
            messages_list.append(
                message.as_dict()
                | {
                    "latest_from_user": message.sender_id == user_id,
                    "sender": {
                        "name": sender.username,
                        "avatar": sender_avatar,
                    },
                }
            )
        return messages_list
