import enum
from datetime import datetime
from typing import TYPE_CHECKING

import sqlalchemy as sa
from flask import abort
from flask_jwt_extended import current_user
from sqlalchemy import ForeignKey, UniqueConstraint
from sqlalchemy.dialects.postgresql import ENUM
from sqlalchemy.orm import Mapped, mapped_column, relationship

from threaddit import db
from threaddit.moderations.models import UserRole
from threaddit.notifications.models import Notifications, NotifType

if TYPE_CHECKING:
    from threaddit.comments.models import Comments  # noqa: ALL
    from threaddit.posts.models import Posts
    from threaddit.reports.schemas import NewReportType, ReportResolveType, ReportTypeAdd
    from threaddit.threads.models import Thread
    from threaddit.users.models import User


class ReportType(db.Model):
    __tablename__ = "report_types"
    __table_args__ = (UniqueConstraint("thread_id", "name", name="unique_report_type"),)
    id: Mapped[int] = mapped_column(primary_key=True)
    thread_id: Mapped[int] = mapped_column(ForeignKey("threads.id"), index=True)
    name: Mapped[str] = mapped_column(nullable=False)
    description: Mapped[str | None] = mapped_column(nullable=True)
    reports: Mapped[list["Reports"]] = relationship(back_populates="report_type")

    # noinspection PyTypeChecker
    def __init__(self, name: str, description: str | None = None):
        self.name = name
        self.description = description

    @staticmethod
    def add_types(thread: "Thread", body: list["ReportTypeAdd"]):
        report_types = []
        for r_type in body:
            new_type = ReportType(r_type["name"], r_type["description"])
            new_type.thread_id = thread.id
            report_types.append(new_type)
        db.session.add_all(report_types)
        return report_types

    def delete(self):
        db.session.delete(self)


class ReportStatus(enum.Enum):
    PENDING = "PENDING"
    RESOLVED = "RESOLVED"
    REJECTED = "REJECTED"


class ReportAction(enum.Enum):
    LOCKED = "LOCKED"
    UNLOCKED = "UNLOCKED"
    REMOVED = "REMOVED"
    SKIPPED = "SKIPPED"


class Reports(db.Model):
    __tablename__ = "reports"
    __tableargs__ = (UniqueConstraint("reporter_id", "post_id", "comment_id", name="unique_report"),)
    id: Mapped[int] = mapped_column(primary_key=True)
    reporter_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    post_id: Mapped[int] = mapped_column(ForeignKey("posts.id"))
    comment_id: Mapped[int | None] = mapped_column(ForeignKey("comments.id"), nullable=True)
    reporter_comment: Mapped[str] = mapped_column(nullable=False)
    report_type_id: Mapped[int] = mapped_column(ForeignKey("report_types.id"))
    created_at: Mapped[datetime] = mapped_column(default=db.func.now(), nullable=False)
    status: Mapped[ReportStatus] = mapped_column(
        ENUM(ReportStatus, name="report_status_enum"), nullable=False, default=ReportStatus.PENDING
    )
    action: Mapped[ReportAction | None] = mapped_column(ENUM(ReportAction, name="report_action_enum"), nullable=True)
    mod_comment: Mapped[str | None] = mapped_column(nullable=True)
    user: Mapped["User"] = relationship(back_populates="reports")
    report_type: Mapped["ReportType"] = relationship(back_populates="reports")

    # noinspection PyTypeChecker
    def __init__(self, user_id: int, post_id: int, content: str | None = None):
        self.reporter_id = user_id
        self.post_id = post_id
        self.reporter_comment = content

    @staticmethod
    def add(user: "User", thread: "Thread", post: "Posts", form: "NewReportType", comment: "Comments|None" = None):
        report = Reports(user_id=user.id, post_id=post.id, content=form["reporter_comment"])
        report.report_type = form["report_type"]
        if comment:
            comment.report_count += 1
            report.comment_id = comment.id
        else:
            post.report_count += 1
        db.session.add(report)
        report.notify_mods(thread, user, post, comment)
        return report

    def resolve(self, thread: "Thread", post: "Posts", body: "ReportResolveType", comment: "Comments|None" = None):
        if not self.action and body["action"] == ReportAction.UNLOCKED:
            return abort(400, {"message": "Already unlocked, Initial Resolve cannot unlock"})
        # noinspection PyTypeChecker
        self.status = body["resolution"]
        # noinspection PyTypeChecker
        self.mod_comment = body["mod_comment"]
        # noinspection PyTypeChecker
        self.action = body["action"]
        if comment:
            self._handle_res(body, comment)
        else:
            self._handle_res(body, post)
        self.notify_report(body, thread, post, comment)
        return self

    @staticmethod
    def _handle_res(body: "ReportResolveType", res: "Posts|Comments"):
        res.report_count -= 1
        match body["action"]:
            case ReportAction.LOCKED:
                res.is_locked = True
            case ReportAction.UNLOCKED:
                res.is_locked = False
            case ReportAction.REMOVED:
                res.is_removed = True
        if body["disable_reports"] is True:
            res.disable_reports = True

    @staticmethod
    def get_report(reporter: "User", thread: "Thread", post: "Posts", comment: "Comments|None" = None):
        if comment:
            comment.validate_comment(thread, post)
            if comment.disable_reports:
                return abort(403, {"message": "Reports disabled for this comment"})
        else:
            post.validate_post(thread)
            if post.disable_reports:
                return abort(403, {"message": "Reports disabled for this post"})
        comment_id = comment.id if comment else None
        return db.session.scalar(
            sa.select(Reports).where(
                Reports.reporter_id == reporter.id, Reports.post_id == post.id, Reports.comment_id == comment_id
            )
        )

    def notify_mods(self, thread: "Thread", user: "User", post: "Posts", comment: "Comments|None" = None):
        mods_list: list[int] = db.session.scalars(
            sa.select(UserRole.user_id).where(UserRole.thread_id == thread.id, UserRole.role_id == 1)
        ).all()
        Notifications.notify_bulk(
            notify_type=NotifType.COMMENT_REPORTED if comment else NotifType.POST_REPORTED,
            users=mods_list,
            title=f"New Report on {'comment' if comment else 'post'} by {user.username}",
            sub_title=comment.content if comment else post.title,
            content=self.report_type.name,
            res_id=self.id,
            res_media_id=user.avatar_id,
        )

    def notify_report(
        self,
        body: "ReportResolveType",
        thread: "Thread",
        post: "Posts",
        comment: "Comments|None" = None,
    ):
        n_type = NotifType.REPORT_RESOLVED if body["resolution"] == ReportStatus.RESOLVED else NotifType.REPORT_REJECTED
        action = body["action"]
        Notifications.notify(
            notif_type=n_type,
            user=self.reporter_id,
            title=(
                f"Your Report on {'comment' if comment else 'post'} has been "
                f"{body["resolution"].name.lower()} by moderator {current_user.username}"
            ),
            sub_title=f"The {'comment' if comment else 'post'} has been {action.name.lower()}",
            content=self.mod_comment,
            res_id=self.id,
            res_media_id=None,
        )
        if comment and action == ReportAction.REMOVED:
            Notifications.notify(
                notif_type=NotifType.COMMENT_REMOVED,
                user=comment.user_id,
                title=f"Your comment on {thread.name} has been removed by moderator {current_user.username}",
                sub_title=comment.content,
                content=self.report_type.name,
                res_id=post.id,
                res_media_id=None,
            )
        elif not comment and action != ReportAction.SKIPPED:
            Notifications.notify(
                notif_type=NotifType.POST_REMOVED if action == ReportAction.REMOVED else NotifType.POST_LOCKED,
                user=post.user_id,
                title=f"Your post on {thread.name} has been {action.name.lower()} by moderator {current_user.username}",
                sub_title=post.title,
                content=self.report_type.name,
                res_id=post.id,
                res_media_id=None,
            )
