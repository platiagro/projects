# -*- coding: utf-8 -*-
"""WSGI server."""
import argparse
import sys

from flask import Flask, jsonify
from flask_cors import CORS
from werkzeug.exceptions import BadRequest, NotFound, MethodNotAllowed, \
    InternalServerError

from .components import bp as components_blueprint
from ..database import db_session, init_db
from .experiments import bp as experiments_blueprint
from .experiments_components import bp as experiments_components_blueprint
from .json_encoder import CustomJSONEncoder
from .projects import bp as projects_blueprint
from ..samples import init_components

app = Flask(__name__)
app.json_encoder = CustomJSONEncoder
app.register_blueprint(projects_blueprint, url_prefix="/projects")
app.register_blueprint(experiments_blueprint,
    url_prefix="/projects/<project_id>/experiments")
app.register_blueprint(components_blueprint, url_prefix="/components")
app.register_blueprint(experiments_components_blueprint,
    url_prefix="/projects/<project_id>/experiments/<experiment_id>/components")


@app.teardown_appcontext
def shutdown_session(exception=None):
    db_session.remove()


@app.route("/", methods=["GET"])
def ping():
    """Handles GET requests to /."""
    return "pong"


@app.errorhandler(BadRequest)
@app.errorhandler(NotFound)
@app.errorhandler(MethodNotAllowed)
@app.errorhandler(InternalServerError)
def handle_errors(e):
    """Handles exceptions raised by the API."""
    return jsonify({"message": e.description}), e.code


def parse_args(args):
    """Takes argv and parses API options."""
    parser = argparse.ArgumentParser(
        description="Projects API"
    )
    parser.add_argument(
        "--port", type=int, default=8080, help="Port for HTTP server (default: 8080)"
    )
    parser.add_argument("--enable-cors", action="count")
    parser.add_argument(
        "--debug", action="count", help="Enable debug"
    )
    parser.add_argument(
        "--init-db", action="count", help="Create database and tables before the HTTP server starts"
    )
    parser.add_argument(
        "--samples-config", help="Path to sample components config file."
    )
    return parser.parse_args(args)


if __name__ == "__main__":
    args = parse_args(sys.argv[1:])

    # Enable CORS if required
    if args.enable_cors:
        CORS(app)

    # Initializes DB if required
    if args.init_db:
        init_db()

    # Install sample components if required
    if args.samples_config:
        init_components(args.samples_config)

    app.run(host="0.0.0.0", port=args.port, debug=args.debug)
