# -*- coding: utf-8 -*-
"""Deployments Logs controller."""
import io
import json
import re

from kubernetes import client
from kubernetes.client.rest import ApiException
from werkzeug.exceptions import BadRequest, NotFound

from projects.controllers.utils import raise_if_project_does_not_exist, \
    raise_if_deployment_does_not_exist
from projects.kfp import KF_PIPELINES_NAMESPACE
from projects.kubernetes.kube_config import load_kube_config
from projects.models import Operator, Task


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

    timestamp_with_tz = r'\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}.\d+Z'
    timestamp_without_tz = r'\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2},\d+'
    timestamp_regex = timestamp_with_tz + '|' + timestamp_without_tz

    log_level = ['INFO', 'WARN', 'ERROR']
    log_level_regex = r'(?<![\w\d]){}(?![\w\d])'
    full_log_level_regex = ''

    for level in log_level:
        if full_log_level_regex:
            full_log_level_regex += '|' + log_level_regex.format(level)
        else:
            full_log_level_regex = log_level_regex.format(level)

    log_message_regex = r'[a-zA-Z0-9\"\'.\-@_!#$%^&*()<>?\/|}{~:]{1,}'

    load_kube_config()
    custom_api = client.CustomObjectsApi()
    core_api = client.CoreV1Api()

    try:
        api_response = custom_api.get_namespaced_custom_object(
            'machinelearning.seldon.io',
            'v1',
            KF_PIPELINES_NAMESPACE,
            'seldondeployments',
            deployment_id,
        )

        response = []
        for deployment_name in api_response['status']['deploymentStatus'].keys():
            api_response = core_api.list_namespaced_pod(
                KF_PIPELINES_NAMESPACE,
                label_selector=f'app={deployment_name}'
            )
            for i in api_response.items:
                pod_name = i.metadata.name
                api_response = core_api.read_namespaced_pod(
                    pod_name,
                    KF_PIPELINES_NAMESPACE,
                )
                for container in api_response.spec.containers:
                    name = container.name
                    if name != 'istio-proxy' and name != 'seldon-container-engine':
                        pod_log = core_api.read_namespaced_pod_log(
                            pod_name,
                            KF_PIPELINES_NAMESPACE,
                            container=name,
                            pretty='true',
                            tail_lines=512,
                            timestamps=True)

                        logs = []
                        buf = io.StringIO(pod_log)
                        line = buf.readline()
                        while line:
                            line = line.replace('\n', '')

                            timestamp = re.findall(timestamp_regex, line)
                            timestamp = ' '.join([str(x) for x in timestamp])
                            line = line.replace(timestamp, '')

                            level = re.findall(full_log_level_regex, line)
                            level = ' '.join([str(x) for x in level])
                            line = line.replace(level, '')

                            line = re.sub(r'( [-:*]{1})', '', line)
                            message = re.findall(log_message_regex, line)
                            message = ' '.join([str(x) for x in message])

                            log = {}
                            log['timestamp'] = timestamp
                            log['level'] = level
                            log['message'] = message
                            logs.append(log)
                            line = buf.readline()

                        # get task name
                        operator = Operator.query.get(name)
                        if operator:
                            task = Task.query.get(operator.task_id)
                            if task:
                                name = task.name

                        resp = {}
                        resp['containerName'] = name
                        resp['logs'] = logs
                        response.append(resp)
        return response
    except ApiException as e:
        body = json.loads(e.body)
        error_message = body['message']
        if 'not found' in error_message:
            raise NotFound('The specified deployment does not exist')
        raise BadRequest('{}'.format(error_message))
