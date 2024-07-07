import os
import pathlib

import dotenv
from apiflask import APIFlask, fields
from flask_cors import CORS
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy_searchable import make_searchable

api = APIFlask(__name__, title="Threaddit API", version="1.0", docs_path="/openapi", spec_path="/openapi.yaml")
dotenv.load_dotenv()

# OpenAPI Generator Configuration
api.openapi_version = "3.1.0"
api.servers = [
    {"description": "Development", "url": "http://localhost:5000"},
    {"description": "Production", "url": "https://threaddit.onrender.com"},
]
api.info = {
    "description": "API Specifications for Threaddit Backend",
    "contact": {"name": "StarKhan", "email": "starkhan6368@gmail.com", "url": "https://github.com/starkhan6368"},
    "license": {"name": "GNU General Public License v3.0", "url": "https://www.gnu.org/licenses/gpl-3.0.html"},
}
api.tags = [
    {"name": "Health", "description": "Health Operations"},
]
api.config["SPEC_FORMAT"] = "yaml"
api.config["LOCAL_SPEC_PATH"] = pathlib.Path(api.root_path) / "../schemas/openapi.yaml"
api.config["SYNC_LOCAL_SPEC"] = True
api.config["AUTO_OPERATION_ID"] = True

# Database Configuration
api.config["SQLALCHEMY_DATABASE_URI"] = os.environ["SQLALCHEMY_DATABASE_URI"]

CORS(api)
db = SQLAlchemy(api)
migrate = Migrate(api, db)
make_searchable(db.Model.metadata)


@api.get("/api/status")
@api.doc(tags=["Health"])
@api.output({"status": fields.String(description="The status of the server", default="ok")}, schema_name="Status")
def server_status() -> dict[str, str]:
    """Get Server Status.

    Returns the status of the server.

    """
    return {"status": "ok"}


# Import and Register Blueprints
from threaddit.comment.routes import comments  # noqa: E402
from threaddit.media.routes import media  # noqa: E402
from threaddit.post.routes import posts  # noqa: E402
from threaddit.thread.routes import threads  # noqa: E402
from threaddit.user.routes import users  # noqa: E402
from threaddit.vote.routes import votes  # noqa: E402

api.register_blueprint(comments)
api.register_blueprint(media)
api.register_blueprint(posts)
api.register_blueprint(threads)
api.register_blueprint(users)
api.register_blueprint(votes)

# SqlAlchemy Searchable Configuration
db.configure_mappers()
