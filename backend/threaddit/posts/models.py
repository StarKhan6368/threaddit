from datetime import UTC, datetime
from typing import TYPE_CHECKING

from sqlalchemy import UniqueConstraint
from sqlalchemy.ext.associationproxy import AssociationProxy, association_proxy
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.schema import ForeignKey

from threaddit import db
from threaddit.media.models import Media, OpType

if TYPE_CHECKING:
    from threaddit.comments.models import Comments
    from threaddit.media.schemas import MediaFormType
    from threaddit.posts.schemas import PostFormType
    from threaddit.reactions.models import Reactions
    from threaddit.threads.models import Thread
    from threaddit.users.models import User


class Posts(db.Model):
    __tablename__ = "posts"
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    thread_id: Mapped[int] = mapped_column(ForeignKey("threads.id"))
    title: Mapped[str] = mapped_column(nullable=False)
    content: Mapped[str | None] = mapped_column()
    created_at: Mapped[datetime] = mapped_column(nullable=False, default=db.func.now())
    edited_at: Mapped[datetime] = mapped_column(nullable=True)
    upvotes: Mapped[int] = mapped_column(default=0)
    downvotes: Mapped[int] = mapped_column(default=0)
    comment_count: Mapped[int] = mapped_column(default=0)
    saved_count: Mapped[int] = mapped_column(default=0)
    media: AssociationProxy["Media"] = association_proxy("post_media_association", "media")
    post_media_association: Mapped[list["PostMediaMapping"]] = relationship(order_by="PostMediaMapping.media_order")
    user: Mapped["User"] = relationship(back_populates="posts")
    thread: Mapped["Thread"] = relationship(back_populates="post")
    comment: Mapped[list["Comments"]] = relationship(back_populates="post")
    reaction: Mapped[list["Reactions"]] = relationship(back_populates="post")

    @hybrid_property
    def karma(self) -> int:
        return self.upvotes - self.downvotes

    @classmethod
    @karma.expression
    def karma(cls) -> int:
        return cls.upvotes - cls.downvotes

    @hybrid_property
    def vote_ratio(self):
        return self.upvotes / (self.upvotes + self.downvotes)

    @classmethod
    @vote_ratio.expression
    def vote_ratio(cls):
        return cls.upvotes / (cls.upvotes + cls.downvotes)

    @classmethod
    def add(cls, form: "PostFormType", user: "User", thread: "Thread"):
        new_post = Posts(
            user_id=user.id,
            thread_id=thread.id,
            title=form["title"],
            content=form["content"],
        )
        db.session.add(new_post)
        for media_form in form["media_list"]:
            new_media = Media.add(f"posts/{new_post.id}", media_form)
            PostMediaMapping.add(post=new_post, media=new_media, form=media_form)
        thread.post_count += 1
        user.post_count += 1
        return new_post

    def update(self, form: "PostFormType"):
        for media_form in self._parse_media_list(form["media_list"]):
            if not media_form["media_id"] and media_form["operation"] == OpType.ADD:
                new_media = Media.add(f"posts/{self.id}", media_form)
                PostMediaMapping.add(post=self, media=new_media, form=media_form)
            else:
                self._handle_media(media_form)
        self.content = form["content"] or self.content
        self.title = form["title"] or self.title
        # noinspection PyTypeChecker
        self.edited_at = datetime.now(tz=UTC)

    def delete(self):
        for media in self.media:
            media.remove()
        self.thread.post_count -= 1
        self.user.post_count -= 1
        for comment in self.comment:
            comment.remove(post_delete=True)
        db.session.delete(self)

    def _parse_media_list(self, media_list: list["MediaFormType"]):
        post_medias = {media.id: media for media in self.media}
        for media_form in media_list:
            if not media_form["media_id"]:
                continue
            media_id = media_form["media_id"].id
            if media_id and media_id in post_medias:
                post_medias.pop(media_id)
        media_list.extend([{"media_id": media, "operation": OpType.DELETE} for media in post_medias.values()])
        return media_list

    def _handle_media(self, form: "MediaFormType"):
        media: "Media" = form["media_id"]
        match form["operation"]:
            case OpType.UPDATE:
                media.update(f"posts/{self.thread_id}/{self.user_id}/{self.id}", form=form)
                media.post_media_association.media_order = form["index"]
            case OpType.DELETE:
                media.delete()
            case OpType.SKIP:
                media.post_media_association.media_order = form["index"]

    # noinspection PyTypeChecker
    def __init__(self, user_id: int, thread_id: int, title: str, content: str | None = None):
        self.user_id = user_id
        self.thread_id = thread_id
        self.title = title
        self.content = content


class PostMediaMapping(db.Model):
    __tableargs__ = UniqueConstraint("post_id", "media_id", name="post_media_mappings_post_id_media_id_key")
    __tablename__ = "post_media_mappings"
    post_id: Mapped[int] = mapped_column(ForeignKey("posts.id"), primary_key=True)
    media_id: Mapped[int] = mapped_column(ForeignKey("media.id"), primary_key=True)
    media_order: Mapped[int] = mapped_column(nullable=False)

    # noinspection PyTypeChecker
    def __init__(self, post: "Posts", media: "Media", media_order: int):
        self.post = post
        self.media = media
        self.media_order = media_order

    @classmethod
    def add(cls, post: "Posts", media: "Media", form: "MediaFormType"):
        db.session.add(PostMediaMapping(post=post, media=media, media_order=form["index"]))
