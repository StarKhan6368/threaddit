from datetime import timedelta

import cloudinary
import sqlalchemy as sa
from flask import Flask, jsonify
from flask_jwt_extended import JWTManager
from flask_marshmallow import Marshmallow
from flask_sqlalchemy import SQLAlchemy
from marshmallow import ValidationError
from werkzeug.exceptions import HTTPException

from threaddit.config import (
    CLOUDINARY_API_KEY,
    CLOUDINARY_API_SECRET,
    CLOUDINARY_NAME,
    DATABASE_URI,
    SECRET_KEY,
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
app.config["JWT_SECRET_KEY"] = SECRET_KEY
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(hours=1)
app.config["JWT_REFRESH_TOKEN_EXPIRES"] = timedelta(days=30)
app.config["IMAGE_EXTENSIONS"] = [".jpg", ".jpeg", ".png", ".gif", ".webp", ".heic", ".heif"]
app.config["VIDEO_EXTENSIONS"] = [".mp4", ".webm", ".ogg", ".avi", ".mov", ".wmv", ".mpg", ".mpeg", ".flv", ".mkv"]
db = SQLAlchemy(app)
ma = Marshmallow(app)
jwt = JWTManager(app)


@app.route("/", defaults={"path": ""})
@app.route("/<path:_>")
def catch_all(_):
    return app.send_static_file("index.html")


@app.errorhandler(ValidationError)
def handle_validation_error(error: "ValidationError"):
    """
    Error Handler for Marshmallow Validation Errors
    """
    return jsonify(error.messages), 400


@app.errorhandler(HTTPException)
def handle_http_exception(error: "HTTPException"):
    """
    Error Handler for HTTP Exceptions
    """
    return jsonify(error.description), error.code


# Import and register custom converters
from threaddit.comments.converters import CommentConverter  # noqa: E402
from threaddit.messages.converters import MessageConverter  # noqa: E402
from threaddit.posts.converters import PostConverter  # noqa: E402
from threaddit.threads.converters import ThreadConverter  # noqa: E402
from threaddit.users.converters import UserConverter  # noqa: E402

app.url_map.converters["comment_id"] = CommentConverter
app.url_map.converters["message_id"] = MessageConverter
app.url_map.converters["post_id"] = PostConverter
app.url_map.converters["thread_id"] = ThreadConverter
app.url_map.converters["user_name"] = UserConverter

# Declaring models before initiating Schemas
import threaddit.auth.models  # noqa: E402
import threaddit.comments.models  # noqa: E402
import threaddit.media.models  # noqa: E402
import threaddit.messages.models  # noqa: E402
import threaddit.moderations.models  # noqa: E402
import threaddit.notifications.models  # noqa: E402
import threaddit.posts.models  # noqa: E402
import threaddit.reactions.models  # noqa: E402
import threaddit.saves.models  # noqa: E402
import threaddit.threads.models  # noqa: E402
import threaddit.users.models  # noqa: E402


@jwt.token_in_blocklist_loader
def check_if_token_revoked(_, jwt_payload: dict):
    jti = jwt_payload["jti"]
    token: "threaddit.auth.models.TokenBlockList | None" = db.session.execute(
        sa.select(threaddit.auth.models.TokenBlockList).filter_by(jti=jti)
    ).scalar_one_or_none()
    return token is not None


@jwt.expired_token_loader
def my_expired_token_callback(_, __):
    return jsonify({"error": "Expired Token", "message": "The token has expired"}), 401


# Import and register all blueprints
from threaddit.comments.routes import comments  # noqa: E402
from threaddit.messages.routes import messages  # noqa: E402
from threaddit.moderations.routes import moderations  # noqa: E402
from threaddit.posts.routes import posts  # noqa: E402
from threaddit.reactions.routes import reactions  # noqa: E402
from threaddit.saves.routes import saves  # noqa: E402
from threaddit.threads.routes import threads  # noqa: E402
from threaddit.users.routes import users  # noqa: E402f

app.register_blueprint(comments)
app.register_blueprint(messages)
app.register_blueprint(moderations)
app.register_blueprint(posts)
app.register_blueprint(reactions)
app.register_blueprint(saves)
app.register_blueprint(threads)
app.register_blueprint(users)
