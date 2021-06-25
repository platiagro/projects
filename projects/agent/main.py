# -*- coding: utf-8 -*-
"""Persistence agent."""
import argparse
import concurrent.futures
import logging
import os
import sys

from kubernetes import client
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

from projects.agent.logger import DEFAULT_LOG_LEVEL
from projects.agent.watchers.deployment import watch_seldon_deployments
from projects.agent.watchers.workflow import watch_workflows
from projects.kubernetes.kube_config import load_kube_config

DB_HOST = os.getenv("MYSQL_DB_HOST", "mysql.platiagro")
DB_NAME = os.getenv("MYSQL_DB_NAME", "platiagro")
DB_USER = os.getenv("MYSQL_DB_USER", "root")
DB_PASS = os.getenv("MYSQL_DB_PASSWORD", "")
DB_URL = f"mysql+pymysql://{DB_USER}:{DB_PASS}@{DB_HOST}/{DB_NAME}"


engine = create_engine(DB_URL,
                       pool_size=5,
                       pool_recycle=300,
                       max_overflow=10)
session = scoped_session(sessionmaker(autocommit=False,
                                      autoflush=False,
                                      bind=engine))


def run(log_level):
    """
    Watches kubernetes events and saves relevant data.
    """
    load_kube_config()
    api = client.CustomObjectsApi()

    # This env variable is responsible for stopping all running
    # watchers when an exception is caught on any thread.
    os.environ["STOP_THREADS"] = "0"

    logging.basicConfig(level=log_level)

    watchers = [watch_workflows, watch_seldon_deployments]

    # We decided to use a ThreadPoolExecutor to concurrently run our watchers.
    # This is necessary because we couldn't easily catch watchers exceptions
    # with Python threading library, with this change, we are able to catch
    # exceptions in any of the watchers and immediatly terminate all threads.
    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = [executor.submit(watcher, api, session) for watcher in watchers]

        for future in concurrent.futures.as_completed(futures):
            try:
                future.result()
            except Exception as e:
                os.environ["STOP_THREADS"] = "1"
                logging.error(f"Exception caught: {e}")
                executor.shutdown()


def parse_args(args):
    """Takes argv and parses API options."""
    parser = argparse.ArgumentParser(
        description="Persistence Agent"
    )
    parser.add_argument(
        "--debug", action="count", help="Enable debug"
    )

    parser.add_argument(
        "--log-level",
        nargs="?",
        choices=["NOTSET", "DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
        default=DEFAULT_LOG_LEVEL,
        const=DEFAULT_LOG_LEVEL,
        help="Sets log level to logging"
    )

    return parser.parse_args(args)


if __name__ == "__main__":
    args = parse_args(sys.argv[1:])

    log_level = args.log_level

    if args.debug:
        engine.echo = True

    run(log_level=log_level)
