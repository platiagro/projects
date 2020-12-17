# -*- coding: utf-8 -*-
"""Deployments Logs controller."""
import json
import re

from io import StringIO

from kubernetes import client
from kubernetes.client.rest import ApiException
from werkzeug.exceptions import NotFound, InternalServerError

from projects.controllers.utils import raise_if_project_does_not_exist, \
    raise_if_deployment_does_not_exist
from projects.kfp import KF_PIPELINES_NAMESPACE
from projects.kubernetes.kube_config import load_kube_config
from projects.kubernetes.seldon import list_deployment_pods
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

    load_kube_config()
    core_api = client.CoreV1Api()

    try:
        response = []
        deployment_pods = list_deployment_pods(deployment_id)

        for pod in deployment_pods:
            for container in pod.spec.containers:
                if container.name not in EXCLUDE_CONTAINERS:
                    # Equivalent to
                    # `kubectl -n KF_PIPELINES_NAMESPACE logs pod.metada.name -c container.name`
                    pod_log = core_api.read_namespaced_pod_log(
                        name=pod.metadata.name,
                        namespace=KF_PIPELINES_NAMESPACE,
                        container=container.name,
                        pretty='true',
                        tail_lines=512,
                        timestamps=True
                    )

                    logs = log_parser(pod_log)

                    # get task name
                    # TODO: deixar o nome da task visivel no arquivo yaml deste container

                    operator = Operator.query.get(container.name)
                    if operator:
                        task = Task.query.get(operator.task_id)
                        if task:
                            name = task.name

                    resp = {}
                    resp['containerName'] = container.name if not operator else name
                    resp['logs'] = logs
                    response.append(resp)
        return response
    except ApiException as e:
        body = json.loads(e.body)
        error_message = body['message']
        if 'not found' in error_message:
            raise NotFound('The specified deployment does not exist')
        raise InternalServerError('{}'.format(error_message))


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

        log = {}
        log['timestamp'] = timestamp
        log['level'] = level
        log['message'] = message
        logs.append(log)
        line = buf.readline()

    return logs
