from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from threaddit import db

if TYPE_CHECKING:
    from threaddit.users.models import User


class TokenBlockList(db.Model):
    __tablename__ = "token_blocklist"
    id: Mapped[int] = mapped_column(primary_key=True)
    jti: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    type: Mapped[str] = mapped_column(String(16), nullable=False)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    created_at: Mapped[datetime] = mapped_column(nullable=False, default=db.func.now())
    user: Mapped["User"] = relationship(back_populates="blacklist_tokens")

    # noinspection PyTypeChecker
    def __init__(self, jti: str, token_type: str, user_id: int):
        self.jti = jti
        self.type = token_type
        self.user_id = user_id

    @staticmethod
    def add(jti: str, ttype: str, user: "User"):
        token = TokenBlockList(jti, ttype, user.id)
        db.session.add(token)
