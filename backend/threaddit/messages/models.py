from datetime import datetime

from marshmallow import Schema, fields, validate, validates
from marshmallow.exceptions import ValidationError
from sqlalchemy import case, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.schema import ForeignKey

from threaddit import db
from threaddit.users.models import User


class Messages(db.Model):
    __tablename__ = "messages"
    id: Mapped[int] = mapped_column(primary_key=True)
    sender_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    receiver_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    content: Mapped[str] = mapped_column()
    seen: Mapped[bool] = mapped_column(default=False)
    is_edited: Mapped[bool] = mapped_column(default=False)
    seen_at: Mapped[datetime | None] = mapped_column()
    created_at: Mapped[datetime] = mapped_column(nullable=False, default=db.func.now())
    user_sender: Mapped["User"] = relationship(back_populates="sender", primaryjoin="Messages.sender_id == User.id")
    user_receiver: Mapped["User"] = relationship(
        back_populates="receiver", primaryjoin="Messages.receiver_id == User.id"
    )

    @classmethod
    def add(cls, sender_id: int, receiver_id: int, content: str):
        new_message = Messages(
            sender_id=sender_id,
            receiver_id=receiver_id,
            content=content,
        )
        db.session.add(new_message)
        db.session.commit()
        return new_message

    def patch(self, content):
        if content == self.content:
            return
        self.content = content
        self.is_edited = True
        db.session.commit()

    def remove(self):
        db.session.delete(self)
        db.session.commit()

    def __init__(self, sender_id, receiver_id, content):
        self.sender_id = sender_id
        self.receiver_id = receiver_id
        self.content = content

    def as_dict(self):
        return {
            "message_id": self.id,
            "sender": {
                "username": self.user_sender.username,
                "avatar": self.user_sender.avatar,
            },
            "receiver": {
                "username": self.user_receiver.username,
                "avatar": self.user_receiver.avatar,
            },
            "content": self.content,
            "created_at": self.created_at,
            "seen": self.seen,
            "seen_at": self.seen_at,
        }

    @classmethod
    def get_inbox(cls, user_id):
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
            sender = message.user_receiver if message.sender_id == user_id else message.user_sender
            messages_list.append(
                message.as_dict()
                | {
                    "latest_from_user": message.sender_id == user_id,
                    "sender": {
                        "username": sender.username,
                        "avatar": sender.avatar,
                    },
                }
            )
        return messages_list


class MessageSchema(Schema):
    content = fields.Str(required=True, validate=validate.Length(min=1))
    receiver_id = fields.Int(required=True)

    @validates("receiver_id")
    def valid_receiver_id(self, value):
        if not User.query.filter_by(id=value).first():
            raise ValidationError("Receiver not found")

    @validates("content")
    def valid_content(self, value):
        if not value.strip():
            raise ValidationError("Content is required")
