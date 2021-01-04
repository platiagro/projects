# -*- coding: utf-8 -*-
"""Deployments Logs controller."""
import re
from io import StringIO

from projects.controllers.utils import raise_if_project_does_not_exist, \
    raise_if_deployment_does_not_exist

from projects.kubernetes.seldon import list_deployment_pods
from projects.kubernetes.utils import get_pod_log
from projects.models import Operator, Task

EXCLUDE_CONTAINERS = ['istio-proxy', 'seldon-container-engine']
TIME_STAMP_PATTERN = r'\d{4}-\d{2}-\d{2}(:?\s|T)\d{2}:\d{2}:\d{2}(:?.|,)\d+Z?\s?'
LOG_MESSAGE_PATTERN = r'[a-zA-Z0-9\"\'.\-@_!#$%^&*()<>?\/|}{~:]{1,}'
LOG_LEVEL_PATTERN = r'(?<![\\w\\d])INFO(?![\\w\\d])|(?<![\\w\\d])WARN(?![\\w\\d])|(?<![\\w\\d])ERROR(?![\\w\\d])'


def list_logs(project_id, deployment_id, run_id):
    """
    Lists logs from a deployment run.

    Parameters
    ----------
    project_id : str
    deployment_id : str
    run_id : str

    Returns
    -------
    dict
        A list of all logs from a run.

    Raises
    ------
    NotFound
        When any of project_id or deployment_id does not exist.
    """
    raise_if_project_does_not_exist(project_id)
    raise_if_deployment_does_not_exist(deployment_id)

    deployment_pods = list_deployment_pods(deployment_id)
    log = {'status': 'Starting'}

    if not deployment_pods:
        log.update({'status': 'Creating'})

    for pod in deployment_pods:
        for container in pod.spec.containers:
            if container.name not in EXCLUDE_CONTAINERS:
                pod_log = get_pod_log(pod, container)

                if not pod_log:
                    log.update({'status': 'Creating'})
                    return log

                log['containerName'] = get_operator_name(container.name)
                log['logs'] = log_parser(pod_log)
                log['status'] = 'Completed'
                log = [log]
    return log


def log_parser(raw_log):
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
        message = re.sub(TIME_STAMP_PATTERN, '', message)

        log = {}
        log['timestamp'] = timestamp
        log['level'] = level
        log['message'] = message
        logs.append(log)
        line = buf.readline()

    return logs


def get_operator_name(container_name):
    """
    Get task name from a container.

    Parameters
    ----------
    container_name : str

    Returns
    -------
    str
        The task name.

    Notes
    -----
    If the container is not linked to any operator, it returns the name of the container.
    """
    # get task name
    # TODO: deixar o nome da task visivel no arquivo yaml deste container
    operator = Operator.query.get(container_name)

    if operator:
        task = Task.query.get(operator.task_id)
        if task:
            return task.name

    return container_name
