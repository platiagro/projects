# -*- coding: utf-8 -*-
"""ASGI server."""
import argparse
import os
import sys

import uvicorn
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse, PlainTextResponse, Response

from projects import __version__
from projects.api import comparisons, deployments, experiments, monitorings, \
    predictions, projects, tasks, templates
from projects.api.deployments import operators as deployment_operators, \
    runs as deployment_runs, responses
from projects.api.deployments.runs import logs as deployment_logs
from projects.api.experiments import operators as experiment_operators, \
    runs as experiment_runs
from projects.api.experiments.runs import datasets, figures, \
    logs as experiment_logs, metrics, results
from projects.api.experiments.operators import parameters as operator_parameters
from projects.api.tasks import parameters
from projects.database import init_db
from projects.exceptions import BadRequest, Forbidden, NotFound, \
    InternalServerError
from projects.api.monitorings import figures as monitoring_figures

init_db()

app = FastAPI(
    title="PlatIAgro Projects",
    description="These are the docs for PlatIAgro Projects API. The endpoints below are usually accessed by the PlatIAgro Web-UI",
    version=__version__,
)
app.include_router(projects.router)
app.include_router(comparisons.router)
app.include_router(experiments.router)
app.include_router(experiment_operators.router)
app.include_router(experiment_runs.router)
app.include_router(datasets.router)
app.include_router(figures.router)
app.include_router(experiment_logs.router)
app.include_router(metrics.router)
app.include_router(results.router)
app.include_router(operator_parameters.router)
app.include_router(deployments.router)
app.include_router(deployment_operators.router)
app.include_router(deployment_runs.router)
app.include_router(deployment_logs.router)
app.include_router(monitorings.router)
app.include_router(monitoring_figures.router)
app.include_router(predictions.router)
app.include_router(tasks.router)
app.include_router(parameters.router)
app.include_router(templates.router)
app.include_router(responses.router)


@app.get("/", response_class=PlainTextResponse)
async def ping():
    """
    Handles GET requests to /.
    """
    return "pong"


@app.exception_handler(BadRequest)
@app.exception_handler(NotFound)
@app.exception_handler(InternalServerError)
@app.exception_handler(Forbidden)
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


def enable_cors():
    """
    Enables CORS preflight requests.
    """
    @app.options("/{rest_of_path:path}")
    async def preflight_handler(request: Request, rest_of_path: str) -> Response:
        """
        Handles CORS preflight requests.
        """
        response = Response()
        response.headers["Access-Control-Allow-Origin"] = "*"
        response.headers["Access-Control-Allow-Methods"] = "POST, GET, DELETE, PATCH, OPTIONS"
        response.headers["Access-Control-Allow-Headers"] = "Authorization, Content-Type"
        return response

    @app.middleware("http")
    async def add_cors_header(request: Request, call_next):
        """
        Sets CORS headers.
        """
        response = await call_next(request)
        response.headers["Access-Control-Allow-Origin"] = "*"
        response.headers["Access-Control-Allow-Methods"] = "POST, GET, DELETE, PATCH, OPTIONS"
        response.headers["Access-Control-Allow-Headers"] = "Authorization, Content-Type"
        return response


if os.getenv("ENABLE_CORS"):
    enable_cors()


def parse_args(args):
    """Takes argv and parses API options."""
    parser = argparse.ArgumentParser(
        description="Projects API",
    )
    parser.add_argument(
        "--host", type=str, default="127.0.0.1", help="Host for HTTP server (default: 127.0.0.1)",
    )
    parser.add_argument(
        "--port", type=int, default=8080, help="Port for HTTP server (default: 8080)",
    )
    return parser.parse_args(args)


if __name__ == "__main__":
    args = parse_args(sys.argv[1:])

    uvicorn.run(app, host=args.host, port=args.port)
