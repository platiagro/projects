# -*- coding: utf-8 -*-
"""WSGI server."""
import argparse
import sys

from flask import Flask, jsonify
from flask_cors import CORS
from werkzeug.exceptions import BadRequest, NotFound, MethodNotAllowed, \
    Forbidden, InternalServerError

from projects.api.comparisons import bp as comparisons_blueprint
from projects.api.deployments import bp as deployments_blueprint
from projects.api.deployments.runs import bp as deployments_runs_blueprint
from projects.api.deployments.runs.logs import bp as deployments_logs_blueprint
from projects.api.experiments import bp as experiments_blueprint
from projects.api.experiments.operators import bp as experiments_operators_blueprint
from projects.api.experiments.runs import bp as experiments_runs_blueprint
from projects.api.experiments.runs.datasets import bp as datasets_blueprint
from projects.api.experiments.runs.figures import bp as figures_blueprint
from projects.api.experiments.runs.logs import bp as experiments_logs_blueprint
from projects.api.experiments.runs.metrics import bp as metrics_blueprint
from projects.api.json_encoder import CustomJSONEncoder
from projects.api.projects import bp as projects_blueprint
from projects.api.tasks import bp as tasks_blueprint
from projects.api.tasks.parameters import bp as tasks_parameters_blueprint
from projects.api.templates import bp as templates_blueprint
from projects.database import db_session, init_db
from projects.initializer import init_artifacts, init_tasks

app = Flask(__name__)
app.json_encoder = CustomJSONEncoder
app.register_blueprint(
    projects_blueprint,
    url_prefix="/projects",
)
app.register_blueprint(
    comparisons_blueprint,
    url_prefix="/projects/<project_id>/comparisons",
)
app.register_blueprint(
    experiments_blueprint,
    url_prefix="/projects/<project_id>/experiments",
)
app.register_blueprint(
    experiments_operators_blueprint,
    url_prefix="/projects/<project_id>/experiments/<experiment_id>/operators",
)
app.register_blueprint(
    experiments_runs_blueprint,
    url_prefix="/projects/<project_id>/experiments/<experiment_id>/runs",
)
app.register_blueprint(
    datasets_blueprint,
    url_prefix="/projects/<project_id>/experiments/<experiment_id>/runs/<run_id>/operators/<operator_id>/datasets",
)
app.register_blueprint(
    figures_blueprint,
    url_prefix="/projects/<project_id>/experiments/<experiment_id>/runs/<run_id>/operators/<operator_id>/figures",
)
app.register_blueprint(
    experiments_logs_blueprint,
    url_prefix="/projects/<project_id>/experiments/<experiment_id>/runs/<run_id>/operators/<operator_id>/logs",
)
app.register_blueprint(
    metrics_blueprint,
    url_prefix="/projects/<project_id>/experiments/<experiment_id>/runs/<run_id>/operators/<operator_id>/metrics",
)
app.register_blueprint(
    deployments_blueprint,
    url_prefix="/projects/<project_id>/deployments",
)
app.register_blueprint(
    deployments_runs_blueprint,
    url_prefix="/projects/<project_id>/deployments/<deployment_id>/runs",
)
app.register_blueprint(
    deployments_logs_blueprint,
    url_prefix="/projects/<project_id>/deployments/<deployment_id>/runs/<run_id>/logs",
)
app.register_blueprint(
    tasks_blueprint,
    url_prefix="/tasks",
)
app.register_blueprint(
    tasks_parameters_blueprint,
    url_prefix="/tasks/<task_id>/parameters",
)
app.register_blueprint(
    templates_blueprint,
    url_prefix="/templates",
)


@app.teardown_appcontext
def shutdown_session(exception=None):
    db_session.remove()


@app.route("/", methods=["GET"])
def ping():
    """
    Handles GET requests to /.
    """
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
        "--tasks-config", help="Path to tasks config file."
    )
    parser.add_argument(
        "--artifacts-config", help="Path to artifacts config file."
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

    # Install tasks from config file
    if args.tasks_config:
        init_tasks(args.tasks_config)

    # Install artifacts from config file
    if args.artifacts_config:
        init_artifacts(args.artifacts_config)

    app.run(host="0.0.0.0", port=args.port, debug=args.debug)
