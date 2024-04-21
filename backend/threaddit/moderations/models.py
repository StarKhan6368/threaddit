import enum
from datetime import UTC, datetime, timedelta
from typing import TYPE_CHECKING

from flask import abort
from sqlalchemy.dialects.postgresql import ENUM
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.schema import ForeignKey

from threaddit import db
from threaddit.notifications.models import Notifications, NotifType

if TYPE_CHECKING:
    from threaddit.threads.models import Thread
    from threaddit.users.models import User


class RoleType(enum.Enum):
    OWNER = "OWNER"
    MODERATOR = "MODERATOR"
    ADMIN = "ADMIN"


class UserRole(db.Model):
    __tablename__ = "user_roles"
    id: Mapped[int] = mapped_column(primary_key=True)
    grantee_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False, unique=True)
    granter_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    role_type: Mapped["RoleType"] = mapped_column(ENUM(RoleType, name="role_type"), nullable=False)
    thread_id: Mapped[int | None] = mapped_column(ForeignKey("threads.id"), unique=True, nullable=True)
    created_at: Mapped[datetime] = mapped_column(nullable=False, default=db.func.now())
    grantee: Mapped["User"] = relationship(back_populates="roles_accepted", foreign_keys=[grantee_id])
    granter: Mapped["User"] = relationship(back_populates="roles_granted", foreign_keys=[granter_id])
    thread: Mapped["Thread"] = relationship(back_populates="user_role")

    # noinspection PyTypeChecker
    def __init__(self, granter_id: int, grantee_id: int, role_type: "RoleType", thread_id: int | None = None):
        self.granter_id = granter_id
        self.grantee_id = grantee_id
        self.role_type = role_type
        self.thread_id = thread_id

    @staticmethod
    def add(granter: "User", grantee: "User", role_type: "RoleType", thread: "Thread|None" = None):
        if role_type == RoleType.MODERATOR and not thread:
            return abort(500, {"message": "Thread not found"})
        user_role = UserRole(
            granter_id=granter.id, grantee_id=grantee.id, role_type=role_type, thread_id=thread.id if thread else None
        )
        db.session.add(user_role)
        Notifications.notify(
            notif_type=NotifType.MODERATOR_ADDED if role_type == RoleType.MODERATOR else NotifType.ADMIN_ADDED,
            user=grantee,
            title=(
                f"You are now a {'moderator' if role_type == RoleType.MODERATOR else 'admin'} of "
                f"{thread.name if thread else 'threadit'}"
            ),
            sub_title=f"Use your powers wisely, {grantee.username}",
            content=f"Granted by {granter.username}",
            res_id=thread.id if thread else None,
            res_media_id=thread.logo_id if thread else None,
        )
        return user_role

    def delete(self, revoker: "User"):
        db.session.delete(self)
        message = f"You are no longer {self.role.name} of {self.thread.name if self.role_id == 1 else 'threadit'}"
        Notifications.notify(
            notif_type=NotifType.MODERATOR_REMOVED if self.role_id == 1 else NotifType.ADMIN_REMOVED,
            user=self.grantee_id,
            title=message,
            sub_title=None,
            content=f"Revoked by {revoker.username}",
            res_id=self.thread_id if self.role_type == RoleType.MODERATOR else None,
            res_media_id=self.thread.logo_id if self.role_type == RoleType.MODERATOR else None,
        )


class InvStatus(enum.Enum):
    PENDING = "PENDING"
    ACCEPTED = "ACCEPTED"
    REJECTED = "REJECTED"


class ModAdminInv(db.Model):
    __tablename__ = "mod_admin_inv"
    id: Mapped[int] = mapped_column(primary_key=True)
    granter_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    grantee_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    thread_id: Mapped[int | None] = mapped_column(ForeignKey("threads.id"), nullable=False)
    role_type: Mapped["RoleType"] = mapped_column(ENUM(RoleType, name="role_type"), nullable=False)
    status: Mapped["InvStatus"] = mapped_column(ENUM(InvStatus, name="inv_status"), nullable=False)
    invited_at: Mapped[datetime] = mapped_column(nullable=False, default=db.func.now())
    closed_at: Mapped[datetime | None] = mapped_column(nullable=True)
    grantee: Mapped["User"] = relationship(foreign_keys=[grantee_id])
    granter: Mapped["User"] = relationship(foreign_keys=[granter_id])
    thread: Mapped["Thread"] = relationship()

    # noinspection PyTypeChecker
    def __init__(self, granter_id: int, grantee_id: int, role_type: "RoleType", thread_id: int):
        self.granter_id = granter_id
        self.grantee_id = grantee_id
        self.role_type = role_type
        self.thread_id = thread_id

    @staticmethod
    def invite(granter: "User", grantee: "User", role_type: "RoleType", thread: "Thread|None" = None):
        if role_type == RoleType.MODERATOR and not thread:
            return abort(500, {"message": "Thread not found"})
        inv = ModAdminInv(
            granter_id=granter.id, grantee_id=grantee.id, thread_id=thread.id if thread else None, role_type=role_type
        )
        db.session.add(inv)
        Notifications.notify(
            notif_type=NotifType.MODERATOR_INVITED,
            user=grantee,
            title=(
                f"You have been invited to {'moderate' if inv.role_type == RoleType.MODERATOR else 'administrate'} "
                f"{inv.thread.name if inv.role_type == RoleType.MODERATOR else 'threadit'}"
            ),
            sub_title=f"Invited by {granter.username}",
            content="Invite will be valid for 24 hours",
            res_id=thread.id,
            res_media_id=thread.logo_id,
        )
        return inv

    # noinspection DuplicatedCode
    def accept(self):
        if datetime.now(tz=UTC) - self.invited_at > timedelta(days=1):
            Notifications.notify(
                notif_type=NotifType.MODINV_REJECTED
                if self.role_type == RoleType.MODERATOR
                else NotifType.ADMINV_REJECTED,
                user=self.granter_id,
                title=self._make_msg(expired=True),
                sub_title=f"Invitation Acceptation initiated by {self.grantee.username}",
                content=f"Invited at {self.invited_at}",
                res_id=self.thread_id,
                res_media_id=self.thread.logo_id,
            )
            return abort(403, {"message": "Invitation has expired"})
        if self.role_type == RoleType.MODERATOR:
            UserRole.add_moderator(granter=self.granter_id, user=self.grantee, thread=self.thread)
        elif self.role_type == RoleType.ADMIN:
            UserRole.add_admin(granter=self.granter_id, user=self.grantee)
        # noinspection PyTypeChecker
        self.status = InvStatus.ACCEPTED
        # noinspection PyTypeChecker
        self.closed_at = datetime.now(tz=UTC)
        Notifications.notify(
            notif_type=NotifType.MODINV_ACCEPTED if self.role_type == RoleType.MODERATOR else NotifType.ADMINV_ACCEPTED,
            user=self.granter_id,
            title=self._make_msg(expired=False),
            sub_title=f"Accepted by {self.grantee.username}",
            content=f"Accepted at {self.closed_at}",
            res_id=self.thread_id,
            res_media_id=self.thread.logo_id,
        )
        return self

    # noinspection DuplicatedCode
    def reject(self):
        # noinspection PyTypeChecker
        self.status = InvStatus.REJECTED
        # noinspection PyTypeChecker
        self.closed_at = datetime.now(tz=UTC)
        Notifications.notify(
            notif_type=NotifType.MODINV_REJECTED if self.role_type == RoleType.MODERATOR else NotifType.ADMINV_REJECTED,
            user=self.granter_id,
            title=self._make_msg(expired=False),
            sub_title=f"Rejected by {self.grantee.username}",
            content=f"Rejected at {self.closed_at}",
            res_id=self.thread_id,
            res_media_id=self.thread.logo_id,
        )

    def _make_msg(self, expired: bool) -> str:
        return (
            f"Your invitation to {'moderate' if self.role_type == RoleType.MODERATOR else 'administrate'} "
            f"{self.thread.name if self.role_type == RoleType.MODERATOR else 'threadit'} has been "
            f"{'accepted' if self.status == InvStatus.ACCEPTED else 'rejected' if not expired else 'expired'}"
        )
