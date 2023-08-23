from flask import Blueprint, request, jsonify
from marshmallow.exceptions import ValidationError
from threaddit.users.models import UserLoginValidator, UserRegisterValidator, User, UsersPatchValidator
from threaddit.config import SECRET_KEY
from threaddit.auth.decorators import auth_role
from bcrypt import hashpw, checkpw
from flask_login import login_user, logout_user, current_user, login_required

user = Blueprint('users', __name__, url_prefix="/api")


@user.route("/user/login", methods=["POST"])
def user_login():
    if current_user.is_authenticated:
        return jsonify({"message": "Already logged in"}), 409
    login_form = request.json
    UserLoginValidator().load(login_form)
    user_info = User.query.filter_by(email=login_form.get("email")).first()
    # if user_info and checkpw(login_form.get("password").encode(), user_info.password_hash.encode()): IN DEV MODE
    if user_info and login_form.get("password") == user_info.password_hash:
        login_user(user_info)
        return jsonify(user_info.as_dict()), 200
    return jsonify({"message": "Invalid credentials"}), 401


@user.route("/user/logout")
@login_required
def user_logout():
    logout_user()
    return jsonify({"message": "Successfully logged out"}), 200


@user.route("/user/register", methods=["POST"])
def user_register():
    if current_user.is_authenticated:
        return jsonify({"message": "Already logged in"}), 409
    register_form = request.json
    UserRegisterValidator().load(register_form)
    # new_user = User(register_form.get("username"), register_form.get("email"),
    #                 hashpw(register_form.get("password").encode(), SECRET_KEY).decode("utf-8")): IN DEV MODE
    new_user = User(register_form.get("username"), register_form.get("email"), register_form.get("password"))
    new_user.add()
    return jsonify(new_user.as_dict()), 201


@user.route("/user", methods=["PATCH"])
@login_required
def user_patch():
    UsersPatchValidator().load(request.json)
    current_user.patch(**request.json)
    return jsonify(current_user.as_dict()), 200


@user.route("/user", methods=["DELETE"])
@login_required
def user_delete():
    current_user.delete()
    logout_user()
    return jsonify({"message": "Successfully deleted"}), 200


@user.route("/user", methods=["GET"])
@login_required
def user_get():
    return jsonify(current_user.as_dict()), 200


@user.route("/user/<user_name>", methods=["GET"])
@auth_role(["admin", "sup-admin", "owner"])
def user_get_by_username(user_name):
    return jsonify(User.query.filter_by(username=user_name).first().as_dict(include_all=True)), 200


@user.route("/users", methods=["GET"])
@login_required
@auth_role(["admin", "sup-admin", "owner"])
def users_get():
    return jsonify(User.get_all()), 200


@user.errorhandler(ValidationError)
def handle_marshmallow_validation(err):
    return jsonify({"errors": err.messages}), 400
