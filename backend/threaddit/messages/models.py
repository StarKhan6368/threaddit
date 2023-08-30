from threaddit import db
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
        return {
            "message_id": self.id,
            "sender": {
                "name": self.user_sender.username,
                "avatar": self.user_sender.avatar,
            },
            "receiver": {
                "name": self.user_receiver.username,
                "avatar": self.user_receiver.avatar,
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
            messages_list.append(
                message.as_dict()
                | {
                    "latest_from_user": message.sender_id == user_id,
                    "sender": {
                        "name": sender.username,
                        "avatar": sender.avatar,
                    },
                }
            )
        return messages_list
