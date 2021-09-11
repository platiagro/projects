# -*- coding: utf-8 -*-
"""ASGI server."""
import argparse
import os
import sys

import uvicorn
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse, PlainTextResponse, Response

from projects import __version__, api
from projects.exceptions import (
    BadRequest,
    Forbidden,
    InternalServerError,
    NotFound,
    ServiceUnavailable,
)

app = FastAPI(
    title="PlatIAgro Projects",
    description="These are the docs for PlatIAgro Projects API. The endpoints below are usually accessed by the PlatIAgro Web-UI",
    version=__version__,
)
app.include_router(api.projects.router)
app.include_router(api.comparisons.router)
app.include_router(api.experiments.router)
app.include_router(api.experiment_data.router)
app.include_router(api.experiment_operators.router)
app.include_router(api.experiment_runs.router)
app.include_router(api.datasets.router)
app.include_router(api.figures.router)
app.include_router(api.experiment_logs.router)
app.include_router(api.metrics.router)
app.include_router(api.results.router)
app.include_router(api.operator_parameters.router)
app.include_router(api.deployments.router)
app.include_router(api.deployment_operators.router)
app.include_router(api.deployment_runs.router)
app.include_router(api.deployment_logs.router)
app.include_router(api.monitorings.router)
app.include_router(api.monitoring_figures.router)
app.include_router(api.predictions.router)
app.include_router(api.tasks.router)
app.include_router(api.parameters.router)
app.include_router(api.templates.router)
app.include_router(api.responses.router)
app.include_router(api.healthcheck.router)


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
@app.exception_handler(ServiceUnavailable)
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
        response.headers[
            "Access-Control-Allow-Methods"
        ] = "POST, GET, DELETE, PATCH, OPTIONS"
        response.headers["Access-Control-Allow-Headers"] = "Authorization, Content-Type"
        return response

    @app.middleware("http")
    async def add_cors_header(request: Request, call_next):
        """
        Sets CORS headers.
        """
        response = await call_next(request)
        response.headers["Access-Control-Allow-Origin"] = "*"
        response.headers[
            "Access-Control-Allow-Methods"
        ] = "POST, GET, DELETE, PATCH, OPTIONS"
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
        "--host",
        type=str,
        default="127.0.0.1",
        help="Host for HTTP server (default: 127.0.0.1)",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8080,
        help="Port for HTTP server (default: 8080)",
    )
    return parser.parse_args(args)


if __name__ == "__main__":
    args = parse_args(sys.argv[1:])

    uvicorn.run(app, host=args.host, port=args.port)
