# -*- coding: utf-8 -*-
"""Deployments Logs controller."""
import re

from io import StringIO

from projects import models
from projects.kubernetes.seldon import list_deployment_pods
from projects.kubernetes.utils import get_pod_log

EXCLUDE_CONTAINERS = ['istio-proxy']
TIME_STAMP_PATTERN = r'\d{4}-\d{2}-\d{2}(:?\s|T)\d{2}:\d{2}:\d{2}(:?.|,)\d+Z?\s?'
LOG_MESSAGE_PATTERN = r'[a-zA-Z0-9\u00C0-\u00D6\u00D8-\u00f6\u00f8-\u00ff\"\'.\-@_,!#$%^&*()\[\]<>?\/|}{~:]{1,}'
LOG_LEVEL_PATTERN = r'(?<![\\w\\d])INFO(?![\\w\\d])|(?<![\\w\\d])WARNING(?![\\w\\d])|(?<![\\w\\d])WARN(?![\\w\\d])|(?<![\\w\\d])ERROR(?![\\w\\d])'


class LogController:
    def __init__(self, session):
        self.session = session

    def list_logs(self, project_id: str, deployment_id: str, run_id: str):
        """
        Lists logs from a deployment run.

        Parameters
        ----------
        project_id : str
        deployment_id : str
        run_id : str

        Returns
        -------
        list
            A list of all logs from a run.
        """
        deployment_pods = list_deployment_pods(deployment_id)
        response = []

        tasks = self.session.query(models.Task) \
            .all()
        tasks = dict((t.uuid, t.name) for t in tasks)

        for pod in deployment_pods:
            for container in pod.spec.containers:
                if container.name not in EXCLUDE_CONTAINERS:
                    pod_log = get_pod_log(pod, container)

                    if not pod_log:
                        operator_info = {"status": "Creating"}
                        response.append(operator_info)
                        continue

                    # retrieves the tasks linked to the operator
                    # using "metadata.annotations"
                    task_id = pod.metadata.annotations.get(container.name)

                    operator_info = {}
                    operator_info["containerName"] = tasks.get(task_id, task_id)
                    operator_info["logs"] = self.log_parser(pod_log)
                    operator_info.update({"status": "Completed"})
                    response.append(operator_info)

        return response

    def log_parser(self, raw_log):
        """
        Transform raw log text into human-readable logs.

        Parameters
        ----------
        raw_log : str
            The raw log content.

        Returns
        -------
        dict
            Detailed logs with level, Time Stamp and message from pod container.
        """
        logs = []
        buf = StringIO(raw_log)
        line = buf.readline()

        while line:
            line = line.replace('\n', '')

            timestamp = re.search(TIME_STAMP_PATTERN, line).group()
            line = re.sub(timestamp, '', line)

            level = re.findall(LOG_LEVEL_PATTERN, line)
            level = ' '.join([str(x) for x in level])
            line = line.replace(level, '')

            line = re.sub(r'( [-:*]{1})', '', line)
            message = re.findall(LOG_MESSAGE_PATTERN, line)
            message = ' '.join([str(x) for x in message])
            message = re.sub(TIME_STAMP_PATTERN, '', message).strip()

            log = {}
            log['timestamp'] = timestamp
            log['level'] = level
            log['message'] = message
            logs.append(log)
            line = buf.readline()

        return logs
