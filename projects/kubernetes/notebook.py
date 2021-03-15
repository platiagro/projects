# -*- coding: utf-8 -*-
"""Kubeflow notebook server utility functions."""
import asyncio
import json
import os
import tarfile
import time
import warnings

from tempfile import NamedTemporaryFile, TemporaryFile

from ast import literal_eval
from kubernetes import client
from kubernetes.client.rest import ApiException
from kubernetes.stream import stream

from projects.controllers.utils import uuid_alpha
from projects.exceptions import InternalServerError
from projects.kfp.monitorings import create_monitoring_task_config_map, \
    delete_monitoring_task_config_map
from projects.kubernetes.kube_config import load_kube_config

JUPYTER_WORKSPACE = "/home/jovyan/tasks"
MONITORING_TAG = "MONITORING"
NOTEBOOK_GROUP = "kubeflow.org"
NOTEBOOK_NAME = "server"
NOTEBOOK_NAMESPACE = "anonymous"
NOTEBOOK_POD_NAME = "server-0"
NOTEBOOK_CONTAINER_NAME = "server"
NOTEBOOK_WAITING_MSG = "Waiting for notebook server to be ready..."


class ApiClientForJsonPatch(client.ApiClient):
    def call_api(self, resource_path, method,
                 path_params=None, query_params=None, header_params=None,
                 body=None, post_params=None, files=None,
                 response_type=None, auth_settings=None, async_req=None,
                 _return_http_data_only=None, collection_formats=None,
                 _preload_content=True, _request_timeout=None):
        header_params["Content-Type"] = self.select_header_content_type(["application/json-patch+json"])
        return super().call_api(resource_path, method, path_params, query_params, header_params, body,
                                post_params, files, response_type, auth_settings, async_req, _return_http_data_only,
                                collection_formats, _preload_content, _request_timeout)


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
    custom_api = client.CustomObjectsApi(api_client=ApiClientForJsonPatch())

    try:
        body = {
            "metadata": {
                "name": name,
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
                        "claimName": name,
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
            group=NOTEBOOK_GROUP,
            version="v1",
            namespace=NOTEBOOK_NAMESPACE,
            plural="notebooks",
            name=NOTEBOOK_NAME,
            body=body,
        )

        # Wait for the pod to be ready and have all containers running
        while True:
            try:
                pod = v1.read_namespaced_pod(
                    name=NOTEBOOK_POD_NAME,
                    namespace=NOTEBOOK_NAMESPACE,
                    _request_timeout=5,
                )

                if pod.status.phase == "Running" \
                   and all([c.state.running for c in pod.status.container_statuses]) \
                   and any([v for v in pod.spec.volumes if v.name == f"{name}"]):
                    warnings.warn(f"Mounted volume {name} in notebook server!")
                    break
            except ApiException:
                pass
            finally:
                warnings.warn(NOTEBOOK_WAITING_MSG)
                time.sleep(5)

    except ApiException as e:
        body = literal_eval(e.body)
        message = body["message"]
        raise InternalServerError(f"Error while trying to patch notebook server: {message}")


def update_persistent_volume_claim(name, mount_path):
    """
    Update a persistent volume mount in the default notebook server.

    Parameters
    ----------
    name : str
    mount_path : str
    """
    load_kube_config()
    v1 = client.CoreV1Api()
    custom_api = client.CustomObjectsApi(api_client=ApiClientForJsonPatch())

    try:
        pod = v1.read_namespaced_pod(
            name=NOTEBOOK_POD_NAME,
            namespace=NOTEBOOK_NAMESPACE,
            _request_timeout=5,
        )
        pod_vols = enumerate(pod.spec.volumes)
        vol_index = next((i for i, v in pod_vols if v.name == f"{name}"), -1)
        if vol_index == -1:
            raise InternalServerError(f"Not found volume: {name}")

        body = [
            {
                "op": "replace",
                "path": f"/spec/template/spec/containers/0/volumeMounts/{vol_index}/mountPath",
                "value": mount_path,
            },
        ]

        custom_api.patch_namespaced_custom_object(
            group=NOTEBOOK_GROUP,
            version="v1",
            namespace=NOTEBOOK_NAMESPACE,
            plural="notebooks",
            name=NOTEBOOK_NAME,
            body=body,
        )

        # Wait for the pod to be ready and have all containers running
        while True:
            try:
                pod = v1.read_namespaced_pod(
                    name=NOTEBOOK_POD_NAME,
                    namespace=NOTEBOOK_NAMESPACE,
                    _request_timeout=5,
                )
                pod_volume_mounts = pod.spec.containers[0].volume_mounts
                if pod.status.phase == "Running" \
                   and all([c.state.running for c in pod.status.container_statuses]) \
                   and any([vm for vm in pod_volume_mounts if vm.mount_path == f"{mount_path}"]):
                    warnings.warn(f"Updated volume mount path {name} in notebook server!")
                    break
            except ApiException:
                pass
            finally:
                warnings.warn(NOTEBOOK_WAITING_MSG)
                time.sleep(5)

    except ApiException as e:
        body = literal_eval(e.body)
        message = body["message"]
        raise InternalServerError(f"Error while trying to patch notebook server: {message}")


def remove_persistent_volume_claim(name, mount_path):
    """
    Remove a persistent volume claim in the default notebook server.
    Parameters
    ----------
    name : str
    mount_path : str
    """
    load_kube_config()
    v1 = client.CoreV1Api()
    custom_api = client.CustomObjectsApi(api_client=ApiClientForJsonPatch())

    try:
        pod = v1.read_namespaced_pod(
            name=NOTEBOOK_POD_NAME,
            namespace=NOTEBOOK_NAMESPACE,
            _request_timeout=5,
        )
        pod_vols = enumerate(pod.spec.volumes)
        vol_index = next((i for i, v in pod_vols if v.name == f"{name}"), -1)
        if vol_index == -1:
            raise InternalServerError(f"Not found volume: {name}")

        v1.delete_namespaced_persistent_volume_claim(
            name=name,
            namespace=NOTEBOOK_NAMESPACE,
        )

        body = [
            {
                "op": "remove",
                "path": f"/spec/template/spec/volumes/{vol_index}",
            },
            {
                "op": "remove",
                "path": f"/spec/template/spec/containers/0/volumeMounts/{vol_index}",
            },
        ]

        custom_api.patch_namespaced_custom_object(
            group=NOTEBOOK_GROUP,
            version="v1",
            namespace=NOTEBOOK_NAMESPACE,
            plural="notebooks",
            name=NOTEBOOK_NAME,
            body=body,
        )

        # Wait for the pod to be ready and have all containers running
        while True:
            try:
                pod = v1.read_namespaced_pod(
                    name=NOTEBOOK_POD_NAME,
                    namespace=NOTEBOOK_NAMESPACE,
                    _request_timeout=5,
                )
                if pod.status.phase == "Running" \
                   and all([c.state.running for c in pod.status.container_statuses]) \
                   and not [v for v in pod.spec.volumes if v.name == f"{name}"]:
                    warnings.warn(f"Removed volume {name} in notebook server!")
                    break
            except ApiException:
                pass
            finally:
                warnings.warn(NOTEBOOK_WAITING_MSG)
                time.sleep(5)

    except ApiException as e:
        body = literal_eval(e.body)
        message = body["message"]
        raise InternalServerError(f"Error while trying to patch notebook server: {message}")


def handle_task_creation(task,
                         task_id,
                         experiment_notebook_path=None,
                         deployment_notebook_path=None,
                         copy_name=None):
    """
    Creates Kubernetes resources and set metadata for notebook objects.

    Parameters
    ----------
    task : projects.schemas.task.TaskCreate
    task_id : str
    experiment_notebook_path : str
    deployment_notebook_path : str
    copy_name : str
        Name of the template to be copied from. Default to None.
    """
    # mounts a volume for the task in the notebook server
    create_persistent_volume_claim(name=f"vol-task-{task_id}",
                                   mount_path=f"{JUPYTER_WORKSPACE}/{task.name}")

    if copy_name:
        source_path = f"{JUPYTER_WORKSPACE}/{copy_name}/."
        destination_path = f"{JUPYTER_WORKSPACE}/{task.name}/"
        experiment_path = f"{task.name}/{experiment_notebook_path}"
        deployment_path = f"{task.name}/{deployment_notebook_path}"
        copy_files_in_pod(source_path, destination_path)
    else:
        # copies experiment notebook file to pod
        with NamedTemporaryFile("w", delete=False) as f:
            json.dump(task.experiment_notebook, f)

        filepath = f.name
        experiment_path = f"{task.name}/{experiment_notebook_path}"
        copy_file_to_pod(filepath, experiment_path)
        os.remove(filepath)

        # copies deployment notebook file to pod
        with NamedTemporaryFile("w", delete=False) as f:
            json.dump(task.deployment_notebook, f)

        filepath = f.name
        deployment_path = f"{task.name}/{deployment_notebook_path}"
        copy_file_to_pod(filepath, deployment_path)
        os.remove(filepath)

    # create ConfigMap for monitoring tasks
    if MONITORING_TAG in task.tags:
        experiment_notebook_content = get_file_from_pod(experiment_notebook_path)
        create_monitoring_task_config_map(task_id, experiment_notebook_content)

    # The new task must have its own task_id, experiment_id and operator_id.
    # Notice these values are ignored when a notebook is run in a pipeline.
    # They are only used by JupyterLab interface.
    experiment_id = uuid_alpha()
    operator_id = uuid_alpha()

    # creates a new event loop,
    # to execute metadata functions concurrently
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    loop.run_until_complete(
        set_notebook_metadata(
            notebook_path=experiment_path,
            task_id=task_id,
            experiment_id=experiment_id,
            operator_id=operator_id,
        )
    )

    loop.run_until_complete(
        set_notebook_metadata(
            notebook_path=deployment_path,
            task_id=task_id,
            experiment_id=experiment_id,
            operator_id=operator_id,
        )
    )


def update_task_config_map(task,
                           task_id,
                           experiment_notebook_path):
    """
    Update ConfigMap for task notebooks.

    Parameters
    ----------
    task : projects.schemas.task.TaskCreate
    task_id : str
    experiment_notebook_path : str
    """
    # update ConfigMap of monitoring task
    delete_monitoring_task_config_map(task_id)
    experiment_notebook_content = get_file_from_pod(experiment_notebook_path)
    create_monitoring_task_config_map(task_id, experiment_notebook_content)


def get_file_from_pod(filepath):
    """
    Get the content of a file from a pod in notebook server.

    Parameters
    ----------
    filepath : str

    Returns
    -------
    str
        File content.
    """
    warnings.warn(f"Fetching {filepath} from pod...")
    load_kube_config()
    api_instance = client.CoreV1Api()

    exec_command = ["cat", filepath]

    container_stream = stream(
        api_instance.connect_get_namespaced_pod_exec,
        name=NOTEBOOK_POD_NAME,
        namespace=NOTEBOOK_NAMESPACE,
        command=exec_command,
        container=NOTEBOOK_CONTAINER_NAME,
        stderr=True,
        stdin=False,
        stdout=True,
        tty=False,
        _preload_content=False,
    )

    file_content = ""

    while container_stream.is_open():
        container_stream.update(timeout=10)
        if container_stream.peek_stdout():
            file_content = container_stream.read_stdout()
            warnings.warn(f"File content fetched.")
    container_stream.close()

    return file_content


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
    warnings.warn(f"Copying '{filepath}' to '{destination_path}'...")
    load_kube_config()
    api_instance = client.CoreV1Api()

    # The following command extracts the contents of STDIN to /home/jovyan/tasks
    exec_command = ["tar", "xvf", "-", "-C", "/home/jovyan/tasks"]

    container_stream = stream(
        api_instance.connect_get_namespaced_pod_exec,
        name=NOTEBOOK_POD_NAME,
        namespace=NOTEBOOK_NAMESPACE,
        command=exec_command,
        container=NOTEBOOK_CONTAINER_NAME,
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
                warnings.warn("STDOUT: %s" % container_stream.read_stdout())
            if container_stream.peek_stderr():
                warnings.warn("STDERR: %s" % container_stream.read_stderr())
            if data:
                container_stream.write_stdin(data)
                data = tar_buffer.read(1000000)
            else:
                break
        container_stream.close()

    warnings.warn(f"Copied '{filepath}' to '{destination_path}'!")


def copy_files_in_pod(source_path, destination_path):
    """
    Copies files from inside a pod.

    Parameters
    ----------
    source_path : str
    destination_path : str
    """
    warnings.warn(f"Copying '{source_path}' to '{destination_path}'...")
    load_kube_config()
    api_instance = client.CoreV1Api()

    # The following command zip the contents of path
    exec_command = ["cp", "-a", source_path, destination_path]

    container_stream = stream(
        api_instance.connect_get_namespaced_pod_exec,
        name=NOTEBOOK_POD_NAME,
        namespace=NOTEBOOK_NAMESPACE,
        command=exec_command,
        container=NOTEBOOK_CONTAINER_NAME,
        stderr=True,
        stdin=False,
        stdout=True,
        tty=False,
        _preload_content=False,
    )

    while container_stream.is_open():
        container_stream.update(timeout=10)
        if container_stream.peek_stdout():
            warnings.warn("STDOUT: %s" % container_stream.read_stdout())
        if container_stream.peek_stderr():
            warnings.warn("STDERR: %s" % container_stream.read_stderr())
    container_stream.close()

    warnings.warn(f"Copied '{source_path}' to '{destination_path}'!")


async def set_notebook_metadata(notebook_path, task_id, experiment_id, operator_id):
    """
    Sets metadata values in notebook file.

    Parameters
    ----------
    notebook_path : str
    task_id : str
    experiment_id : str
    operator_id : str
    """
    if notebook_path is None:
        return

    warnings.warn(f"Setting metadata in {notebook_path}...")
    load_kube_config()
    api_instance = client.CoreV1Api()

    # The following command sets task_id in the metadata of a notebook
    python_script = (
        f"import json; "
        f"f = open('{JUPYTER_WORKSPACE}/{notebook_path}'); "
        f"n = json.load(f); "
        f"n['metadata']['task_id'] = '{task_id}'; "
        f"n['metadata']['experiment_id'] = '{experiment_id}'; "
        f"n['metadata']['operator_id'] = '{operator_id}'; "
        f"f.close(); "
        f"f = open('{JUPYTER_WORKSPACE}/{notebook_path}', 'w'); "
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
        container=NOTEBOOK_CONTAINER_NAME,
        stderr=True,
        stdin=False,
        stdout=True,
        tty=False,
        _preload_content=False,
    )

    while container_stream.is_open():
        container_stream.update(timeout=10)
        if container_stream.peek_stdout():
            warnings.warn("STDOUT: %s" % container_stream.read_stdout())
        if container_stream.peek_stderr():
            warnings.warn("STDERR: %s" % container_stream.read_stderr())
    container_stream.close()

    warnings.warn(f"Setting metadata in {notebook_path}...")


def get_notebook_state():
    """
    Get notebook server state.

    Returns
    -------
    bool

    Raises
    ------
    ApiException
    """
    load_kube_config()
    v1 = client.CoreV1Api()
    try:
        pod = v1.read_namespaced_pod(
            name=NOTEBOOK_POD_NAME,
            namespace=NOTEBOOK_NAMESPACE,
            _request_timeout=5,
        )
        if pod.status.phase == "Running" \
           and all([c.state.running for c in pod.status.container_statuses]):
            return True
        return False
    except ApiException as e:
        body = literal_eval(e.body)
        message = body["message"]
        raise InternalServerError(f"Error while trying to get notebook server state: {message}")
