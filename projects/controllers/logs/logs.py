# -*- coding: utf-8 -*-
"""Logs controller."""
import io
import re
import dateutil.parser
from typing import List, Optional

from projects.kfp.runs import get_latest_run_id
from projects.kubernetes.argo import list_workflow_pods
from projects.kubernetes.utils import get_container_logs
from projects.schemas.log import Log, LogList

EXCLUDE_CONTAINERS = ["istio-proxy", "wait"]
LOG_PATTERN = re.compile(r"(.*?)\s(INFO|WARN|WARNING|ERROR|DEBUG)?\s*(.*)")


class LogController:
    def __init__(self):
        pass

    def list_logs(self, project_id: str, run_id: str, experiment_id: Optional[str] = None, deployment_id: Optional[str] = None):
        """
        Lists logs from a run.

        Parameters
        ----------
        project_id : str
        run_id : str
            The run_id. If `run_id=latest`, then returns logs from the latest run_id.
        experiment_id : str or None
        deployment_id : str or None

        Returns
        -------
        dict
            A dict of logs from a run.
        """
        if run_id == "latest":
            run_id = get_latest_run_id(experiment_id or deployment_id)

        # BUG: workflows and pods are deleted after 1 day due to a
        # "Garbage Collector" feature of Argo workflows/Kubeflow Pipelines.
        # The link below provide useful information on how to configure log
        # persistence and where to set the Time-to-live (TTL) for workflows:
        # https://github.com/kubeflow/pipelines/issues/844#issuecomment-559841627
        # We can make use of these configurations and fix this bug later.
        pods = list_workflow_pods(run_id=run_id)

        # Retrieves logs from all containers in all pods (that were not deleted)
        logs = self.pods_to_logs(pods)

        return LogList(
            logs=logs,
            total=len(logs),
        )

    def pods_to_logs(self, pods: List):
        """
        Transform raw log text into human-readable logs.

        Parameters
        ----------
        pods : list
            A list of pod details.

        Returns
        -------
        list
            Detailed logs with level, title, date and message from a container.
        """
        logs = []
        for pod in pods:
            for container in pod.spec.containers:
                if container.name not in EXCLUDE_CONTAINERS:
                    raw_logs = get_container_logs(pod, container)

                    if container.env is None:
                        task_name = pod.metadata.name
                    else:
                        task_name = next((e.value for e in container.env if e.name == "TASK_NAME"), pod.metadata.name)

                    created_at = pod.metadata.creation_timestamp

                    if raw_logs:
                        logs.extend(
                            self.split_messages(raw_logs, task_name),
                        )
                    else:
                        logs.append(
                            Log(
                                level="INFO",
                                title=task_name,
                                message="Container is creating...",
                                created_at=created_at,
                            ),
                        )

        return logs

    def split_messages(self, raw_logs: str, task_name: str):
        """
        Splits raw log text into a list of log schemas.

        Parameters
        ----------
        raw_logs : str
        task_name : str

        Returns
        -------
        list
            Detailed logs with level, Time Stamp and message from pod container.
        """
        logs = []
        buffer = io.StringIO(raw_logs)

        message_lines = []
        created_at = None
        level = "INFO"

        line = buffer.readline()
        while line:
            line = line.strip("\n")
            # Captures the beginning of a log message (until 1st space char)
            # and tries to parse a datetime and a level from this message.
            match = LOG_PATTERN.match(line)
            if match:
                # Appends the previous lines of log
                if len(message_lines) > 0:
                    logs.append(
                        Log(
                            level=level,
                            title=task_name,
                            message="\n".join(message_lines),
                            created_at=created_at,
                        ),
                    )
                    message_lines = []

                date_str = match.group(1)
                level = match.group(2) or "INFO"
                line = match.group(3)

                try:
                    created_at = dateutil.parser.isoparse(date_str)
                except (ValueError, OverflowError):
                    pass

            message_lines.append(line)
            line = buffer.readline()

        if len(message_lines) > 0:
            logs.append(
                Log(
                    level=level,
                    title=task_name,
                    message="\n".join(message_lines),
                    created_at=created_at,
                ),
            )

        return logs
