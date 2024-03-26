import uuid
from datetime import datetime

import cloudinary.uploader as uploader
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.schema import ForeignKey
from typing_extensions import TYPE_CHECKING

from threaddit import app, db

if TYPE_CHECKING:
    from threaddit.models import UserRole
    from threaddit.posts.models import Posts
    from threaddit.users.models import User


class Subthread(db.Model):
    __tablename__ = "subthreads"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(unique=True, nullable=False)
    description: Mapped[str | None] = mapped_column()
    created_at: Mapped[datetime] = mapped_column(nullable=False, default=db.func.now())
    logo: Mapped[str | None] = mapped_column()
    created_by: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    post_count: Mapped[int] = mapped_column(default=0, nullable=False)
    comment_count: Mapped[int] = mapped_column(default=0, nullable=False)
    subscriber_count: Mapped[int] = mapped_column(default=0, nullable=False)
    user: Mapped["User"] = relationship(back_populates="subthread")
    user_role: Mapped[list["UserRole"]] = relationship(back_populates="subthread")
    subscription: Mapped[list["Subscription"]] = relationship(back_populates="subthread")
    post: Mapped[list["Posts"]] = relationship(back_populates="subthread")

    @classmethod
    def add(cls, form_data, image, created_by):
        name = form_data.get("name") if form_data.get("name").startswith("t/") else f"t/{form_data.get('name')}"
        new_sub = Subthread(
            name=name,
            description=form_data.get("description"),
            created_by=created_by,
        )
        new_sub.handle_logo(form_data.get("content_type"), image, form_data.get("content_url"))
        db.session.add(new_sub)
        db.session.commit()
        return new_sub

    def patch(self, form_data, image):
        self.handle_logo(form_data.get("content_type"), image, form_data.get("content_url"))
        self.description = form_data.get("description", self.description)
        db.session.commit()

    def remove(self):
        db.session.delete(self)
        db.session.commit()

    def handle_logo(self, content_type, image=None, url: None | str = None):
        if content_type == "image" and image:
            self.delete_logo()
            image_data = uploader.upload(image, public_id=f"{uuid.uuid4().hex}_{image.filename.rsplit('.')[0]}")
            url = f"https://res.cloudinary.com/{app.config['CLOUDINARY_NAME']}/image/upload/f_auto,q_auto/{image_data.get('public_id')}"
            self.logo = url
        elif content_type == "url" and url:
            self.logo = url

    def delete_logo(self):
        if self.logo and self.logo.startswith(f"https://res.cloudinary.com/{app.config['CLOUDINARY_NAME']}"):
            res = uploader.destroy(self.logo.split("/")[-1])
            print(f"Cloudinary Image Destory Response for {self.name}: ", res)

    def as_dict(self, cur_user_id: int | None = None):
        data = {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "created_at": self.created_at,
            "logo": self.logo,
            "PostsCount": self.post_count,
            "CommentsCount": self.comment_count,
            "created_by": self.user.username if self.user else None,
            "subscriberCount": self.subscriber_count,
            "modList": [r.user.username for r in self.user_role if r.role.slug == "mod"],
        }
        if cur_user_id:
            data["has_subscribed"] = bool(
                Subscription.query.filter_by(user_id=cur_user_id, subthread_id=self.id).first()
            )
        return data

    def __init__(self, name: str, created_by: int, description: str | None = None, logo: str | None = None):
        self.name = name
        self.description = description
        self.logo = logo
        self.created_by = created_by


class Subscription(db.Model):
    __tablename__ = "subscriptions"
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    subthread_id: Mapped[int] = mapped_column(ForeignKey("subthreads.id"))
    user: Mapped["User"] = relationship(back_populates="subscription")
    subthread: Mapped["Subthread"] = relationship(back_populates="subscription")

    @classmethod
    def add(cls, thread_id: int, user_id: int, subthread: "Subthread"):
        new_sub = Subscription(user_id=user_id, subthread_id=thread_id)
        db.session.add(new_sub)
        subthread.subscriber_count += 1
        db.session.commit()

    def remove(self):
        self.subthread.subscriber_count -= 1
        db.session.delete(self)
        db.session.commit()

    def __init__(self, user_id: int, subthread_id: int):
        self.user_id = user_id
        self.subthread_id = subthread_id
