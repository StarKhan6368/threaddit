from flask import Flask, jsonify, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from marshmallow import ValidationError
import os
import cloudinary
from flask_login import LoginManager
from threaddit.config import (
    DATABASE_URI,
    SECRET_KEY,
    CLOUDINARY_API_SECRET,
    CLOUDINARY_API_KEY,
    CLOUDINARY_NAME,
)

app = Flask(
    __name__,
    static_folder="../../frontend/threaddit/dist",
    static_url_path="/",
)
cloudinary.config(
    cloud_name=CLOUDINARY_NAME,
    api_key=CLOUDINARY_API_KEY,
    api_secret=CLOUDINARY_API_SECRET,
)
app.config["CLOUDINARY_NAME"] = CLOUDINARY_NAME
app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URI
app.config["SECRET_KEY"] = SECRET_KEY
db = SQLAlchemy(app)
login_manager = LoginManager(app)
ma = Marshmallow(app)


@login_manager.unauthorized_handler
def callback():
    return jsonify({"message": "Unauthorized"}), 401


@app.route("/", defaults={"path": ""})
@app.route("/<path:path>")
def catch_all(path):
    return app.send_static_file("index.html")


@app.errorhandler(ValidationError)
def handle_marshmallow_validation(err):
    return jsonify({"errors": err.messages}), 400


@app.errorhandler(404)
def not_found(e):
    return app.send_static_file("index.html")


# flake8: noqa
from threaddit.users.routes import user
from threaddit.subthreads.routes import threads
from threaddit.posts.routes import posts
from threaddit.comments.routes import comments
from threaddit.reactions.routes import reactions
from threaddit.messages.routes import messages

app.register_blueprint(user)
app.register_blueprint(threads)
app.register_blueprint(posts)
app.register_blueprint(comments)
app.register_blueprint(reactions)
app.register_blueprint(messages)
