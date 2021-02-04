# -*- coding: utf-8 -*-
"""Persistence agent."""
import argparse
import logging
import os
import re
import sys
import uuid

from kubernetes import client, watch
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

from projects.kfp import KF_PIPELINES_NAMESPACE
from projects.kubernetes.kube_config import load_kube_config
from projects import models

DB_HOST = os.getenv("MYSQL_DB_HOST", "mysql.platiagro")
DB_NAME = os.getenv("MYSQL_DB_NAME", "platiagro")
DB_USER = os.getenv("MYSQL_DB_USER", "root")
DB_PASS = os.getenv("MYSQL_DB_PASSWORD", "")
DB_URL = f"mysql+pymysql://{DB_USER}:{DB_PASS}@{DB_HOST}/{DB_NAME}"
engine = create_engine(DB_URL,
                       pool_size=32,
                       pool_recycle=300,
                       max_overflow=64)
session = scoped_session(sessionmaker(autocommit=False,
                                      autoflush=False,
                                      bind=engine))


def run():
    """
    Watches kubernetes events and saves relevant data.
    """
    load_kube_config()
    api = client.CustomObjectsApi()
    w = watch.Watch()

    stream = w.stream(
        api.list_namespaced_custom_object,
        group="argoproj.io",
        version="v1alpha1",
        namespace=KF_PIPELINES_NAMESPACE,
        plural="workflows",
    )

    for workflow_manifest in stream:
        logging.info("Event: %s %s " % (workflow_manifest["type"], workflow_manifest["object"]["metadata"]["name"],))

        # First, we set the status for operators that are unlisted in object.status.nodes.
        # Obs: the workflow manifest contains only the nodes that are ready to run (whose dependencies succeeded)

        # if the workflow is pending/running, then unlisted_operators_status = "Pending"
        # if the workflow succeeded/failed, then unlisted_operators_status = "Unset/Setted Up"
        if workflow_manifest["object"]["status"].get("phase") in {"Pending", "Running"}:
            unlisted_operators_status = "Pending"
        else:
            unlisted_operators_status = "Unset"

        match = re.search(r"(experiment|deployment)-(.*)-\w+", workflow_manifest["object"]["metadata"]["name"])
        if match:
            key = match.group(1)
            id_ = match.group(2)
            session.query(models.Operator) \
                .filter_by(**{f"{key}_id": id_}) \
                .update({"status": unlisted_operators_status})

        # Then, we set the status for operators that are listed in object.status.nodes
        for node in workflow_manifest["object"]["status"].get("nodes", {}).values():
            try:
                operator_id = uuid.UUID(node["displayName"])
            except ValueError:
                continue

            # if workflow was interrupted, then status = "Terminated"
            if "message" in node and str(node["message"]) == "terminated":
                status = "Terminated"
            else:
                status = str(node["phase"])

            session.query(models.Operator) \
                .filter_by(uuid=operator_id) \
                .update({"status": status})

        session.commit()


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
