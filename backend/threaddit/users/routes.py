import sqlalchemy as sa
from flask import Blueprint, abort, jsonify, request
from flask_jwt_extended import (
    create_access_token,
    create_refresh_token,
    current_user,
    get_jwt,
    get_jwt_identity,
    jwt_required,
)

from threaddit import db
from threaddit.auth.models import TokenBlockList
from threaddit.users.models import User
from threaddit.users.schemas import (
    LoginSchema,
    LoginType,
    RegisterSchema,
    RegisterType,
    UserFormSchema,
    UserFormType,
    UserSchema,
)

users = Blueprint("users", __name__, url_prefix="/users")
login_schema = LoginSchema()
register_schema = RegisterSchema()
user_patch_schema = UserFormSchema()
user_schema = UserSchema()
users_schema = UserSchema(many=True)


@users.route("/login", methods=["POST"])
def user_login():
    body: "LoginType" = login_schema.load(request.json)
    user = db.session.scalar(sa.select(User).where(User.email == body["email"]))
    if not user or not user.check_password(body["password"]):
        return abort(401, "Invalid credentials")
    additional_claims = {"user_name": user.username, "email": user.email}
    access_token = create_access_token(identity=user.id, additional_claims=additional_claims)
    refresh_token = create_refresh_token(identity=user.id)
    return jsonify(
        user=user_schema.dump(user), token={"access_token": access_token, "refresh_token": refresh_token}
    ), 200


@users.route("/refresh", methods=["POST"])
@jwt_required(refresh=True)
def user_refresh():
    identity = get_jwt_identity()
    additional_claims = {"user_name": current_user.username, "email": current_user.email}
    access_token = create_access_token(identity=identity, additional_claims=additional_claims, fresh=False)
    return jsonify(access_token=access_token), 200


@users.route("/logout", methods=["DELETE"])
@jwt_required(verify_type=False)
def user_logout():
    token: dict = get_jwt()
    TokenBlockList.add(token["jti"], token["type"], current_user)
    db.session.commit()
    return jsonify(message="Logged out"), 200


@users.route("/register", methods=["POST"])
def user_register():
    body: "RegisterType" = register_schema.load(request.json)
    check_name = db.session.scalar(sa.select(User).where(User.username == body["user_name"]))
    if check_name:
        abort(400, {"user_name": f"User with username {body['user_name']} already exists"})
    check_mail = db.session.scalar(sa.select(User).where(User.email == body["email"]))
    if check_mail:
        abort(400, {"email": f"User with email {body['email']} already registered"})
    user = User.add(username=body["user_name"], email=body["email"], password_hash=body["password"])
    db.session.commit()
    return user_schema.dump(user), 200


@users.route("/me", methods=["GET"])
@jwt_required()
def user_me():
    return user_schema.dump(current_user), 200


@users.route("/me", methods=["PATCH"])
@jwt_required()
def user_patch():
    form: "UserFormType" = user_patch_schema.load(request.form | request.files)
    current_user.update(form)
    db.session.commit()
    return user_schema.dump(current_user), 200


@users.route("/search/<user_name>", methods=["GET"])
def users_search(user_name: str):
    users_list = db.session.scalars(sa.select(User).where(User.username.ilike(f"%{user_name}%"))).all()
    return users_schema.dump(users_list), 200


@users.route("/<user_name:user>", methods=["GET"])
def user_get(user: "User"):
    return user_schema.dump(user), 200
