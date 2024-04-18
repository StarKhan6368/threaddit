from datetime import UTC, datetime
from typing import TYPE_CHECKING

from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.schema import ForeignKey

from threaddit import db
from threaddit.media.models import Media, OpType

if TYPE_CHECKING:
    from threaddit.messages.schemas import MessageFormType
    from threaddit.users.models import User


class Messages(db.Model):
    __tablename__ = "messages"
    id: Mapped[int] = mapped_column(primary_key=True)
    sender_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    receiver_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    content: Mapped[str] = mapped_column(nullable=False)
    media_id: Mapped[int | None] = mapped_column(ForeignKey("media.id"), nullable=True)
    is_deleted: Mapped[bool] = mapped_column(default=False, nullable=False)
    sent_at: Mapped[datetime] = mapped_column(default=db.func.now(), nullable=False)
    seen_at: Mapped[datetime | None] = mapped_column(default=db.func.now(), nullable=True)
    edited_at: Mapped[datetime | None] = mapped_column(default=db.func.now(), nullable=True)
    media: Mapped["Media"] = relationship()
    user_sender: Mapped["User"] = relationship(primaryjoin="Messages.sender_id == User.id")
    user_receiver: Mapped["User"] = relationship(primaryjoin="Messages.receiver_id == User.id")

    @classmethod
    def add(cls, sender: "User", receiver: "User", form: "MessageFormType"):
        new_message = Messages(
            sender_id=sender.id,
            receiver_id=receiver.id,
            content=form["content"],
        )
        if form["media"]:
            new_message.media = Media.add(f"/users/{sender.username}/messages/{new_message.id}", form=form)
        db.session.add(new_message)
        return new_message

    # noinspection DuplicatedCode
    def _handle_media(self, form: "MessageFormType"):
        if form["media_id"] and self.media_id == form["media_id"].id:
            match form["operation"]:
                case OpType.UPDATE:
                    self.media.update(f"users/{self.username}", form=form)
                case OpType.DELETE:
                    self.media.delete()
        elif not form["media_id"] and form["operation"] == OpType.ADD and not self.media_id:
            self.media = Media.add(f"users/{self.username}", form=form)

    def patch(self, form: "MessageFormType"):
        self.content = form["content"] or self.content
        if form["media"]:
            self._handle_media(form)
        # noinspection PyTypeChecker
        self.edited_at = datetime.now(tz=UTC)

    def remove(self):
        # noinspection PyTypeChecker
        self.is_deleted = True
        # noinspection PyTypeChecker
        self.content = "**deleted**"
        if self.media:
            self.media.delete()
        db.session.delete(self)

    # noinspection PyTypeChecker
    def __init__(self, sender_id: int, receiver_id: int, content: str):
        self.sender_id = sender_id
        self.receiver_id = receiver_id
        self.content = content
