from sqlalchemy import func

from threaddit import db, login_manager
from flask_login import UserMixin
from threaddit import ma
from threaddit.models import Role, UserRole
from flask_marshmallow.fields import fields
from marshmallow.exceptions import ValidationError


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)


class User(db.Model, UserMixin):
    __tablename__: str = "users"
    id: int = db.Column(db.Integer, primary_key=True)
    username: str = db.Column(db.Text, unique=True, nullable=False)
    email: str = db.Column(db.Text, unique=True, nullable=False)
    password_hash: str = db.Column(db.Text, nullable=False)
    avatar: str = db.Column(db.Text)
    bio: str = db.Column(db.Text)
    registration_date = db.Column(db.DateTime(timezone=True), nullable=False, default=db.func.now())
    subthread = db.relationship("Subthread", back_populates="user")
    user_role = db.relationship("UserRole", back_populates="user")
    subscription = db.relationship("Subscription", back_populates="user")

    def __init__(self, username: str, email: str, password_hash: str):
        self.username = username
        self.email = email
        self.password_hash = password_hash

    def get_id(self):
        return self.id

    def __str__(self) -> str:
        return f"id: {self.id}, username: {self.username}, email: {self.email}, " \
               f"registration_date: {self.registration_date}"

    def add(self):
        db.session.add(self)
        db.session.commit()

    def patch(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    def has_role(self, role):
        return bool(
                    UserRole.query
                    .join(Role)
                    .filter(Role.slug == role)
                    .filter(UserRole.user_id == self.id)
                    .count() == 1
                    )

    @classmethod
    def get_all(cls):
        all_users: list[dict] = []
        for user in cls.query.all():
            all_users.append(user.as_dict(include_all=True))
        return all_users

    def as_dict(self, include_all=False) -> dict:
        return {
            "username": self.username,
            "email": self.email,
            "avatar": self.avatar,
            "bio": self.bio,
            "registrationDate": self.registration_date,
            "roles": [r.role.slug for r in self.user_role]
        } if not include_all else {"id": self.id, **self.as_dict()}


def username_validator(username: str):
    if db.session.query(User).filter(func.lower(User.username) == username.lower()).first():
        raise ValidationError("Username already exists")


def email_validator(email: str):
    if User.query.filter_by(email=email).first():
        raise ValidationError("Email already exists")


class UserLoginValidator(ma.SQLAlchemySchema):
    class Meta:
        model = User

    email = fields.Email(required=True)
    password = fields.Str(required=True, validate=[fields.validate.Length(min=8)])


class UserRegisterValidator(ma.SQLAlchemySchema):
    class Meta:
        model = User

    username = fields.Str(
        required=True,
        validate=[
            fields.validate.Length(
                min=4,
                max=15,
                error="Username must be between 1 and 50 characters"
            ),
            fields.validate.Regexp(
                "^[a-zA-Z][a-zA-Z0-9_]*$",
                error="Username must start with a letter, and contain only letters, numbers, and underscores.",
            ),
            username_validator
        ],
    )
    email = fields.Email(required=True, validate=[email_validator])
    password = fields.Str(required=True, validate=[fields.validate.Length(min=8)])


class UsersPatchValidator(ma.SQLAlchemySchema):
    class Meta:
        model = User

    username = fields.Str(validate=[fields.validate.Length(min=4, max=15), username_validator])
    avatar = fields.Str()
    bio = fields.Str()
