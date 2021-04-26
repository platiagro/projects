# -*- coding: utf-8 -*-
"""Persistence agent."""
import argparse
import os
import sys
import threading

from kubernetes import client
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

from projects.agent.watch_deployments import watch_seldon_deployments
from projects.agent.watch_workflows import watch_workflows
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


def run():
    """
    Watches kubernetes events and saves relevant data.
    """
    load_kube_config()
    api = client.CustomObjectsApi()

    workflows_thread = threading.Thread(target=watch_workflows, args=(api, session))
    sdeps_thread = threading.Thread(target=watch_seldon_deployments, args=(api, session))

    workflows_thread.start()
    sdeps_thread.start()


def parse_args(args):
    """Takes argv and parses API options."""
    parser = argparse.ArgumentParser(
        description="Persistence Agent"
    )
    parser.add_argument(
        "--debug", action="count", help="Enable debug"
    )
    return parser.parse_args(args)


if __name__ == "__main__":
    args = parse_args(sys.argv[1:])

    if args.debug:
        engine.echo = True

    run()
