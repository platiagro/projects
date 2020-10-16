# -*- coding: utf-8 -*-
"""WSGI server."""
import argparse
import sys

from flask import Flask, jsonify
from flask_cors import CORS
from werkzeug.exceptions import BadRequest, NotFound, MethodNotAllowed, \
    Forbidden, InternalServerError

from ..database import db_session, init_db
from .compare_results import bp as compare_results_blueprint
from .experiments import bp as experiments_blueprint
from .datasets import bp as datasets_blueprint
from .figures import bp as figures_blueprint
from .json_encoder import CustomJSONEncoder
from .operators import bp as operators_blueprint
from .parameters import bp as parameters_blueprint
from .projects import bp as projects_blueprint
from .metrics import bp as metrics_blueprint
from .tasks import bp as tasks_blueprint
from .templates import bp as templates_blueprint
from ..samples import init_tasks

app = Flask(__name__)
app.json_encoder = CustomJSONEncoder
app.register_blueprint(projects_blueprint, url_prefix="/projects")
app.register_blueprint(compare_results_blueprint, url_prefix="/projects/<project_id>/comparisons")
app.register_blueprint(experiments_blueprint, url_prefix="/projects/<project_id>/experiments")
app.register_blueprint(tasks_blueprint, url_prefix="/tasks")
app.register_blueprint(parameters_blueprint, url_prefix="/tasks/<task_id>/parameters")
app.register_blueprint(operators_blueprint,
                       url_prefix="/projects/<project_id>/experiments/<experiment_id>/operators")
app.register_blueprint(datasets_blueprint,
                       url_prefix="/projects/<project_id>/experiments/<experiment_id>/operators/<operator_id>/datasets")
app.register_blueprint(figures_blueprint,
                       url_prefix="/projects/<project_id>/experiments/<experiment_id>/operators/<operator_id>/figures")
app.register_blueprint(metrics_blueprint,
                       url_prefix="/projects/<project_id>/experiments/<experiment_id>/operators/<operator_id>/metrics")
app.register_blueprint(templates_blueprint, url_prefix="/templates")


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
@app.errorhandler(Forbidden)
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
        "--samples-config", help="Path to sample tasks config file."
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

    # Install sample tasks if required
    if args.samples_config:
        init_tasks(args.samples_config)

    app.run(host="0.0.0.0", port=args.port, debug=args.debug)
