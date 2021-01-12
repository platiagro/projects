# -*- coding: utf-8 -*-
"""Utility functions."""
import tarfile
from ast import literal_eval
from tempfile import TemporaryFile

from kubernetes import client
from kubernetes.client.rest import ApiException
from kubernetes.stream import stream
from werkzeug.exceptions import InternalServerError

from projects.kfp import KF_PIPELINES_NAMESPACE
from projects.kubernetes.kube_config import load_kube_config

NOTEBOOK_NAME = "server"
NOTEBOOK_NAMESPACE = "anonymous"
NOTEBOOK_POD_NAME = "server-0"
NOTEBOOK_CONAINER_NAME = "server"


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


def get_pod_log(pod, container):
    """
    Read log of the specified Pod.

    Parameters
    ----------
    pod : kubernetes.client.models.v1_pod.V1Pod
    container : kubernetes.client.models.v1_container.V1Container

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
        pod_log = core_api.read_namespaced_pod_log(
                        name=pod.metadata.name,
                        namespace=KF_PIPELINES_NAMESPACE,
                        container=container.name,
                        pretty='true',
                        tail_lines=512,
                        timestamps=True
                    )

        return pod_log
    except ApiException as e:
        body = literal_eval(e.body)
        message = body['message']

        if 'ContainerCreating' in message:
            return []
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


def copy_file_inside_pod(filepath, destination_path):
    """
    Copies a local file to a pod in notebook server.
    Based on this example:
    https://github.com/prafull01/Kubernetes-Utilities/blob/master/kubectl_cp_as_python_client.py

    Parameters
    ----------
    filepath : str
    destination_path : str
    """
    print(f"Copying {filepath} to {destination_path}...", flush=True)
    load_kube_config()
    api_instance = client.CoreV1Api()

    # The following command extracts the contents of STDIN to /home/jovyan/
    exec_command = ["tar", "xvf", "-", "-C", f"/home/jovyan"]

    container_stream = stream(
        api_instance.connect_get_namespaced_pod_exec,
        name=NOTEBOOK_POD_NAME,
        namespace=NOTEBOOK_NAMESPACE,
        command=exec_command,
        container=NOTEBOOK_CONAINER_NAME,
        stderr=True,
        stdin=True,
        stdout=True,
        tty=False,
        _preload_content=False,
    )

    with TemporaryFile() as tar_buffer:
        # Prepares an uncompressed tarfile that will be written to STDIN
        with tarfile.open(fileobj=tar_buffer, mode="w") as tar:
            tar.add(filepath, arcname=destination_path)

        # Rewinds to beggining of tarfile
        tar_buffer.seek(0)

        # WARNING:
        # Attempts to write the entire tarfile caused connection errors for large files
        # The loop below reads/writes small chunks to prevent these errors
        data = tar_buffer.read(1000000)
        while container_stream.is_open():
            container_stream.update(timeout=10)
            if container_stream.peek_stdout():
                print("STDOUT: %s" % container_stream.read_stdout(), flush=True)
            if container_stream.peek_stderr():
                print("STDERR: %s" % container_stream.read_stderr(), flush=True)
            if data:
                container_stream.write_stdin(data)
                data = tar_buffer.read(1000000)
            else:
                break
        container_stream.close()

    print(f"Copied {filepath} to {destination_path}!", flush=True)
