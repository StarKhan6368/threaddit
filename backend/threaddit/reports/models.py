import enum
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey
from sqlalchemy.dialects.postgresql import ENUM
from sqlalchemy.orm import Mapped, mapped_column, relationship

from threaddit import db

if TYPE_CHECKING:
    from threaddit.users.models import User


class ReportType(db.Model):
    __tablename__ = "report_types"
    id: Mapped[int] = mapped_column(primary_key=True)
    thread_id: Mapped[int] = mapped_column(ForeignKey("threads.id"), index=True)
    name: Mapped[str] = mapped_column(nullable=False)
    description: Mapped[str | None] = mapped_column(nullable=True)

    # noinspection PyTypeChecker
    def __init__(self, name: str, description: str | None = None):
        self.name = name
        self.description = description


class ReportStatus(enum.Enum):
    PENDING = "PENDING"
    RESOLVED = "RESOLVED"
    REJECTED = "REJECTED"


class Reports(db.Model):
    __tablename__ = "reports"
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    content: Mapped[str] = mapped_column(nullable=False)
    report_type_id: Mapped[int] = mapped_column(ForeignKey("report_types.id"))
    created_at: Mapped[datetime] = mapped_column(default=db.func.now(), nullable=False)
    status: Mapped[ReportStatus] = mapped_column(
        ENUM(ReportStatus="report_status_enum"), nullable=False, default=ReportStatus.PENDING
    )
    mod_comment: Mapped[str | None] = mapped_column(nullable=True)
    user: Mapped["User"] = relationship(back_populates="reports")
    report_type: Mapped["ReportType"] = relationship(back_populates="reports")

    # noinspection PyTypeChecker
    def __init__(self, user_id: int, report_type_id: int):
        self.user_id = user_id
        self.report_type_id = report_type_id
