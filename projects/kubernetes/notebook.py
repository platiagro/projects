# -*- coding: utf-8 -*-
"""Kubeflow notebook server utility functions."""
import tarfile
import time
import warnings
from tempfile import TemporaryFile

from ast import literal_eval
from kubernetes import client
from kubernetes.client.rest import ApiException
from kubernetes.stream import stream
from werkzeug.exceptions import InternalServerError

from projects.kubernetes.kube_config import load_kube_config

NOTEBOOK_NAME = "server"
NOTEBOOK_NAMESPACE = "anonymous"
NOTEBOOK_POD_NAME = "server-0"
NOTEBOOK_CONAINER_NAME = "server"


def create_persistent_volume_claim(name, mount_path):
    """
    Creates a persistent volume claim and mounts it in the default notebook server.
    Parameters
    ----------
    name : str
    mount_path : str
    """
    load_kube_config()

    v1 = client.CoreV1Api()
    custom_api = client.CustomObjectsApi()

    try:
        body = {
            "metadata": {
                "name": f"vol-{name}",
            },
            "spec": {
                "accessModes": [
                    "ReadWriteOnce",
                ],
                "resources": {
                    "requests": {
                        "storage": "10Gi",
                    },
                }
            },
        }
        v1.create_namespaced_persistent_volume_claim(
            namespace=NOTEBOOK_NAMESPACE,
            body=body,
        )

        body = [
            {
                "op": "add",
                "path": "/spec/template/spec/volumes/-",
                "value": {
                    "name": name,
                    "persistentVolumeClaim": {
                        "claimName": f"vol-{name}",
                    },
                },
            },
            {
                "op": "add",
                "path": "/spec/template/spec/containers/0/volumeMounts/-",
                "value": {
                    "mountPath": mount_path,
                    "name": name,
                },
            },
        ]

        custom_api.patch_namespaced_custom_object(
            group="kubeflow.org",
            version="v1",
            namespace=NOTEBOOK_NAMESPACE,
            plural="notebooks",
            name=NOTEBOOK_NAME,
            body=body,
        )

        api_instance = client.CoreV1Api()
        # Wait for the pod to be ready and have all containers running
        while True:
            try:
                pod = api_instance.read_namespaced_pod(
                    name=NOTEBOOK_POD_NAME,
                    namespace=NOTEBOOK_NAMESPACE,
                    _request_timeout=5,
                )

                if pod.status.phase == "Running" \
                   and all([c.state.running for c in pod.status.container_statuses]) \
                   and any([v for v in pod.spec.volumes if v.name == f"{name}"]):
                    print(f"Mounted volume vol-{name} in notebook server!", flush=True)
                    break
            except ApiException:
                pass
            finally:
                warnings.warn(f"Waiting for notebook server to be ready...")
                time.sleep(5)

    except ApiException as e:
        body = literal_eval(e.body)
        message = body["message"]
        raise InternalServerError(f"Error while trying to patch notebook server: {message}")


def copy_file_to_pod(filepath, destination_path):
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


def copy_files_in_pod(source_path, destination_path):
    """
    Copies files from inside a pod.

    Parameters
    ----------
    source_path : str
    destination_path : str
    """
    print(f"Copying {source_path} to {destination_path}...", flush=True)
    load_kube_config()
    api_instance = client.CoreV1Api()

    # The following command zip the contents of path
    exec_command = ["cp", "-R", source_path, destination_path]

    container_stream = stream(
        api_instance.connect_get_namespaced_pod_exec,
        name=NOTEBOOK_POD_NAME,
        namespace=NOTEBOOK_NAMESPACE,
        command=exec_command,
        container=NOTEBOOK_CONAINER_NAME,
        stderr=True,
        stdin=False,
        stdout=True,
        tty=False,
        _preload_content=False,
    )

    while container_stream.is_open():
        container_stream.update(timeout=10)
        if container_stream.peek_stdout():
            print("STDOUT: %s" % container_stream.read_stdout(), flush=True)
        if container_stream.peek_stderr():
            print("STDERR: %s" % container_stream.read_stderr(), flush=True)
    container_stream.close()

    print(f"Copied {source_path} to {destination_path}!", flush=True)


def set_notebook_metadata(notebook_path, task_id):
    """
    Sets metadata values in notebook file.

    Parameters
    ----------
    notebook_path : str
    task_id : str
    """
    print(f"Setting metadata in {notebook_path}...", flush=True)
    load_kube_config()
    api_instance = client.CoreV1Api()

    # The following command sets task_id in the metadata of a notebook
    python_script = (
        f"import json; "
        f"f = open('{notebook_path}'); "
        f"n = json.load(f); "
        f"n['metadata']['task_id'] = '{task_id}'; "
        f"f.close(); "
        f"f = open('{notebook_path}', 'w') ;"
        f"json.dump(n, f); "
        f"f.close()"
    )
    exec_command = [
        "python",
        "-c",
        python_script,
    ]

    container_stream = stream(
        api_instance.connect_get_namespaced_pod_exec,
        name=NOTEBOOK_POD_NAME,
        namespace=NOTEBOOK_NAMESPACE,
        command=exec_command,
        container=NOTEBOOK_CONAINER_NAME,
        stderr=True,
        stdin=False,
        stdout=True,
        tty=False,
        _preload_content=False,
    )

    while container_stream.is_open():
        container_stream.update(timeout=10)
        if container_stream.peek_stdout():
            print("STDOUT: %s" % container_stream.read_stdout(), flush=True)
        if container_stream.peek_stderr():
            print("STDERR: %s" % container_stream.read_stderr(), flush=True)
    container_stream.close()

    print(f"Setting metadata in {notebook_path}...", flush=True)