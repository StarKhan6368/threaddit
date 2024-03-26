from flask import Flask, jsonify
from flask_login.utils import login_required
from flask_sqlalchemy import SQLAlchemy
from marshmallow import ValidationError
import cloudinary
from flask_login import LoginManager
from sqlalchemy import text
from threaddit.auth.decorators import auth_role
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


@login_manager.unauthorized_handler
def callback():
    return jsonify({"message": "Unauthorized"}), 401


@app.route("/", defaults={"path": ""})
@app.route("/<path:path>")
def catch_all(path):
    return app.send_static_file("index.html")


@app.route("/api/recalculate")
@login_required
@auth_role(["admin"])
def recalculate():
    try:
        with open("threaddit/recalculate.sql", "r") as f:
            sql = text(f.read())
        db.session.execute(sql)
        db.session.commit()
        return jsonify({"message": "Recalculated"}), 200
    except Exception as e:
        print(e)
        return jsonify({"message": "Failed"}), 400


@app.errorhandler(ValidationError)
def handle_marshmallow_validation(err):
    return jsonify({"errors": err.messages}), 400


@app.errorhandler(404)
def not_found(e):
    return app.send_static_file("index.html")


from threaddit.users.routes import user  # noqa
from threaddit.subthreads.routes import threads  # noqa
from threaddit.posts.routes import posts  # noqa
from threaddit.comments.routes import comments  # noqa
from threaddit.reactions.routes import reactions  # noqa
from threaddit.messages.routes import messages  # noqa

app.register_blueprint(user)
app.register_blueprint(threads)
app.register_blueprint(posts)
app.register_blueprint(comments)
app.register_blueprint(reactions)
app.register_blueprint(messages)
