from flask import Flask, jsonify, send_from_directory, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from marshmallow import ValidationError
import os
from flask_login import LoginManager
from threaddit.config import POSTGRES_USER, POSTGRES_PASSWORD, SECRET_KEY


upload_folder = os.path.join(os.path.dirname(__file__), "static/uploads")
app = Flask(__name__, static_folder="templates", static_url_path="/")
app.config[
    "SQLALCHEMY_DATABASE_URI"
] = f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@localhost/threaddit"
app.config["SECRET_KEY"] = SECRET_KEY
app.config["UPLOAD_FOLDER"] = upload_folder
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


@app.route("/api/send_image/<filename>")
def send_image(filename):
    return send_from_directory(app.config["UPLOAD_FOLDER"], filename)


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
