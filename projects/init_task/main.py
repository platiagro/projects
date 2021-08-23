# -*- coding: utf-8 -*-
"""
Task initialization Job.
"""
import argparse
import distutils.dir_util
import json
import logging
import os
import pkgutil
import sys
import warnings
from typing import Optional

EXAMPLE_DEPLOYMENT_NOTEBOOK = pkgutil.get_data("projects", "config/Deployment.ipynb")
EXAMPLE_EXPERIMENT_NOTEBOOK = pkgutil.get_data("projects", "config/Experiment.ipynb")


def run(
    task_id: str,
    source: str,
    destination: str,
    experiment_notebook: Optional[str] = None,
    deployment_notebook: Optional[str] = None,
):
    """
    A job that initializes the contents of a task.

    It either copies the contents of another task, or adds sample
    Jupyter Notebooks of an Experiment and a Deployment.

    Parameters
    ----------
    task_id : str
    source : str
    destination : str
    experiment_notebook: str or None
    deployment_notebook: str or None
    """
    logging.info("Initializing Task.")
    logging.info(f"task_id = {task_id}")
    logging.info(f"source = {source}")
    logging.info(f"destination = {destination}")
    logging.info(f"experiment_notebook = {experiment_notebook}")
    logging.info(f"deployment_notebook = {deployment_notebook}")

    experiment_notebook_path = os.path.join(destination, "Experiment.ipynb")
    deployment_notebook_path = os.path.join(destination, "Deployment.ipynb")

    if source is not None and os.path.exists(source):
        logging.info("Copying contents from source task to new task.")
        distutils.dir_util.copy_tree(source, destination)
    else:
        logging.info("Copying notebooks to new task.")

        try:
            experiment_notebook = json.loads(experiment_notebook)
        except (TypeError, ValueError, json.decoder.JSONDecodeError):
            experiment_notebook = json.loads(EXAMPLE_EXPERIMENT_NOTEBOOK)

        try:
            deployment_notebook = json.loads(deployment_notebook)
        except (TypeError, ValueError, json.decoder.JSONDecodeError):
            deployment_notebook = json.loads(EXAMPLE_DEPLOYMENT_NOTEBOOK)

        with open(experiment_notebook_path, "w") as f:
            json.dump(experiment_notebook, f)

        with open(deployment_notebook_path, "w") as f:
            json.dump(deployment_notebook, f)

    if os.path.exists(experiment_notebook_path):
        set_notebook_metadata(experiment_notebook_path, task_id)

    if os.path.exists(deployment_notebook_path):
        set_notebook_metadata(deployment_notebook_path, task_id)

    logging.info("Done!")


def set_notebook_metadata(source: str, task_id: str):
    """
    Sets task_id in the metadata of a notebook file.

    Parameters
    ----------
    source : str
    task_id : str
    """
    logging.info(f"Adding metadata in the notebook {source}.")

    try:
        with open(source, "r") as f:
            notebook = json.load(f)
            notebook["metadata"]["task_id"] = task_id

        with open(source, "w") as f:
            json.dump(notebook, f)

    except (TypeError, ValueError, json.decoder.JSONDecodeError):
        warnings.warn("Could not set metadata in the notebook. Maybe the notebook is not a valid JSON.")


def parse_args(args):
    """Takes argv and parses API options."""
    parser = argparse.ArgumentParser(
        description="Task Initialization Job",
    )
    parser.add_argument(
        "--task-id", type=str, help="Task id",
    )
    parser.add_argument(
        "--source", type=str, help="Source directory",
    )
    parser.add_argument(
        "--destination", type=str, help="Destination directory",
    )
    parser.add_argument(
        "--experiment-notebook", type=str, help="Experiment notebook",
    )
    parser.add_argument(
        "--deployment-notebook", type=str, help="Deployment notebook",
    )
    parser.add_argument(
        "--log-level",
        nargs="?",
        choices=["NOTSET", "DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
        default="INFO",
        const="INFO",
        help="Log level",
    )

    return parser.parse_args(args)


if __name__ == "__main__":
    args = parse_args(sys.argv[1:])

    logging.basicConfig(level=args.log_level)

    run(
        task_id=args.task_id,
        source=args.source,
        destination=args.destination,
        experiment_notebook=args.experiment_notebook,
        deployment_notebook=args.deployment_notebook,
    )
