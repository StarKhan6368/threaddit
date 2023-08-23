from flask import Flask, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from flask_login import LoginManager
from flask_migrate import Migrate
from threaddit.config import POSTGRES_USER, POSTGRES_PASSWORD, SECRET_KEY

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@localhost/threaddit_test"
app.config["SECRET_KEY"] = SECRET_KEY
db = SQLAlchemy(app)
login_manager = LoginManager(app)
ma = Marshmallow(app)
migrate = Migrate(app, db)


@login_manager.unauthorized_handler
def callback():
    return jsonify({"message": "Unauthorized"}), 401


@app.route("/")
def index():
    return "Hello World!"


from threaddit.users.routes import user
from threaddit.subthreads.routes import subthread
app.register_blueprint(user)
app.register_blueprint(subthread)
