# -*- coding: utf-8 -*-
"""Utility functions."""
import time

from ast import literal_eval
from kubernetes import client
from kubernetes.client.rest import ApiException
from kubernetes import stream

from projects.exceptions import InternalServerError
from projects.kfp import KF_PIPELINES_NAMESPACE
from projects.kubernetes.kube_config import load_kube_config

IGNORABLE_MESSAGES_KEYTEXTS = ["ContainerCreating",
                               "PodInitializing"]
IGNORABLE_STATUSES_REASONS = ["Evicted", "OutOfpods"]


def search_for_pod_info(details, operator_id):
    """
    Get operator pod info, such as: name, status and message error (if failed).

    Parameters
    ----------
    details : dict
        Workflow manifest from pipeline runtime.
    operator_id : str

    Returns
    -------
    dict
        Pod informations.
    """
    info = {}

    try:
        if "nodes" in details["status"]:
            for node in [*details["status"]["nodes"].values()]:
                if node["displayName"] == operator_id:
                    info = {"name": node["id"], "status": node["phase"], "message": node["message"]}
    except KeyError:
        pass

    return info


def get_container_logs(pod, container):
    """
    Returns latest logs of the specified container.

    Parameters
    ----------
    pod : str
    container : str

    Returns
    -------
    str
        Container's logs.

    Raises
    ------
    InternalServerError
        While trying to query Kubernetes API.
    """
    load_kube_config()
    core_api = client.CoreV1Api()
    try:
        logs = core_api.read_namespaced_pod_log(
            name=pod.metadata.name,
            namespace=KF_PIPELINES_NAMESPACE,
            container=container.name,
            pretty="true",
            tail_lines=512,
            timestamps=True,
        )
        return logs
    except ApiException as e:
        body = literal_eval(e.body)
        message = body["message"]

        if pod.status.reason in IGNORABLE_STATUSES_REASONS:
            return None

        for ignorable_messages in IGNORABLE_MESSAGES_KEYTEXTS:
            if ignorable_messages in message:
                return None

        raise InternalServerError(f"Error while trying to retrive container's log: {message}")


def volume_exists(name, namespace):
    """
    Returns whether a persistent volume exists.

    Parameters
    ----------
    name : str
    namespace : str

    Returns
    -------
    bool
    """
    load_kube_config()
    v1 = client.CoreV1Api()
    try:
        volume = v1.read_namespaced_persistent_volume_claim(name=name, namespace=namespace)
        if volume.status.phase == "Bound":
            return True
        else:
            return False
    except ApiException:
        return False


def get_volume_from_pod(volume_name, namespace, experiment_id):
    """
    Get volume content zipped on base64.

    Parameters
    ----------
        volume_name: str
        namespace: str
        experiment_id: str

    Returns
    -------
    str
        Volume content in base64.
    """
    load_kube_config()
    api_instance = client.CoreV1Api()

    pod_name = f"download-{experiment_id}"

    pod_manifest = {
        "apiVersion": "v1",
        "kind": "Pod",
        "metadata": {
            "name": pod_name
        },
        "spec": {
            "containers": [{
                "image": "alpine",
                "name": "main",
                "command": ["/bin/sh"],
                "args": [
                    "-c",
                    "while true;do date;sleep 5; done;apk add zip"
                ],
                "volumeMounts": [{
                    "mountPath": "/tmp/data",
                    "name": "vol-tmp-data"
                }]
              }],
            "volumes": [{
                "name": "vol-tmp-data",
                "persistentVolumeClaim": {
                    "claimName": volume_name
                }
            }]
        }
    }
    try:
        api_instance.create_namespaced_pod(body=pod_manifest,
                                           namespace=namespace)
    except ApiException as e:
        # status 409: AlreadyExists
        if e.status != 409:
            body = literal_eval(e.body)
            message = body["message"]
            raise InternalServerError(message)

    while True:
        resp = api_instance.read_namespaced_pod(name=pod_name,
                                                namespace=namespace)
        if resp.status.phase != "Pending":
            break
        time.sleep(1)

    exec_command = ["/bin/sh", "-c",
                    "apk add zip -q && zip -q -r - /tmp/data | base64"]

    container_stream = stream.stream(
        api_instance.connect_get_namespaced_pod_exec,
        name=pod_name,
        namespace=namespace,
        command=exec_command,
        container="main",
        stderr=True,
        stdin=False,
        stdout=True,
        tty=False,
        _preload_content=False,
    )

    zip_file_content = ""

    while container_stream.is_open():
        container_stream.update(timeout=10)
        if container_stream.peek_stdout():
            zip_file_content += container_stream.read_stdout()
    container_stream.close()

    api_instance.delete_namespaced_pod(name=pod_name,
                                       namespace=namespace)

    # the stdout string contains \n character, we must remove
    clean_zip_file_content = zip_file_content.replace("\n", "")
    return clean_zip_file_content
