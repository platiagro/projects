# -*- coding: utf-8 -*-
"""ASGI server."""
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
from projects.api.experiments.operators.parameters import bp as operators_parameters_blueprint
from projects.api.experiments.runs import bp as experiments_runs_blueprint
from projects.api.experiments.runs.datasets import bp as datasets_blueprint
from projects.api.experiments.runs.figures import bp as figures_blueprint
from projects.api.experiments.runs.logs import bp as experiments_logs_blueprint
from projects.api.experiments.runs.metrics import bp as metrics_blueprint
from projects.api.json_encoder import CustomJSONEncoder
from projects.api.monitorings import bp as monitorings_blueprint
from projects.api.predictions import bp as predictions_blueprint
from projects.api.projects import bp as projects_blueprint
from projects.api.tasks import bp as tasks_blueprint
from projects.api.tasks.parameters import bp as tasks_parameters_blueprint
from projects.api.templates import bp as templates_blueprint
from projects.database import db_session, init_db

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
    operators_parameters_blueprint,
    url_prefix="/projects/<project_id>/experiments/<experiment_id>/operators/<operator_id>/parameters",
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
    monitorings_blueprint,
    url_prefix="/projects/<project_id>/deployments/<deployment_id>/monitorings"
)
app.register_blueprint(
    predictions_blueprint,
    url_prefix="/projects/<project_id>/deployments/<deployment_id>/predictions",
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


@app.exception_handler(BadRequest)
@app.exception_handler(NotFound)
@app.exception_handler(InternalServerError)
async def handle_errors(request: Request, exception: Exception):
    """
    Handles exceptions raised by the API.

    Parameters
    ----------
    exception : Exception

    Returns
    -------
    str
    """
    return JSONResponse(
        status_code=exception.code,
        content={"message": exception.message},
    )


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
    return parser.parse_args(args)


if __name__ == "__main__":
    args = parse_args(sys.argv[1:])

    # Enable CORS if required
    if args.enable_cors:
        app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

    # Initializes DB if required
    if args.init_db:
        init_db()

    if args.debug:
        engine.echo = True

    uvicorn.run(app, port=args.port, debug=args.debug)
