# -*- coding: utf-8 -*-
"""ASGI server."""
import argparse
import sys

import uvicorn
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, PlainTextResponse

from projects.api import comparisons, deployments, experiments, monitorings, \
    predictions, projects, tasks, templates
from projects.api.deployments import runs as deployment_runs
from projects.api.deployments.runs import logs as deployment_logs
from projects.api.experiments import operators, runs as experiment_runs
from projects.api.experiments.runs import datasets, figures, \
    logs as experiment_logs, metrics
from projects.api.tasks import parameters
from projects.database import engine, init_db
from projects.exceptions import BadRequest, NotFound, InternalServerError


app = FastAPI()
app.include_router(projects.router)
app.include_router(comparisons.router)
app.include_router(experiments.router)
app.include_router(operators.router)
app.include_router(experiment_runs.router)
app.include_router(datasets.router)
app.include_router(figures.router)
app.include_router(experiment_logs.router)
app.include_router(metrics.router)
app.include_router(deployments.router)
app.include_router(deployment_runs.router)
app.include_router(deployment_logs.router)
app.include_router(monitorings.router)
app.include_router(predictions.router)
app.include_router(tasks.router)
app.include_router(parameters.router)
app.include_router(templates.router)


@app.get("/", response_class=PlainTextResponse)
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
