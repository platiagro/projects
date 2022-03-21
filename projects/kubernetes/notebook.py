# -*- coding: utf-8 -*-
"""Kubeflow notebook server utility functions."""
import asyncio
import http
import json
import os
import tarfile
import time
import warnings
from ast import literal_eval
from tempfile import NamedTemporaryFile, TemporaryFile

from kubernetes import client
from kubernetes.client.rest import ApiException
from kubernetes.stream import stream

from projects.controllers.utils import uuid_alpha
from projects.exceptions import InternalServerError
from projects.kfp.monitorings import (
    create_monitoring_task_config_map,
    delete_monitoring_task_config_map,
)
from projects.kubernetes.kube_config import load_kube_config

JUPYTER_WORKSPACE = "/home/jovyan/tasks"
MONITORING_TAG = "MONITORING"
NOTEBOOK_GROUP = "kubeflow.org"
NOTEBOOK_NAME = "server"
NOTEBOOK_NAMESPACE = "anonymous"
NOTEBOOK_POD_NAME = "server-0"
NOTEBOOK_CONTAINER_NAME = "server"
NOTEBOOK_WAITING_MSG = "Waiting for notebook server to be ready..."
MAX_RETRY = 5


class ApiClientForJsonPatch(client.ApiClient):
    def call_api(
        self,
        resource_path,
        method,
        path_params=None,
        query_params=None,
        header_params=None,
        body=None,
        post_params=None,
        files=None,
        response_type=None,
        auth_settings=None,
        async_req=None,
        _return_http_data_only=None,
        collection_formats=None,
        _preload_content=True,
        _request_timeout=None,
    ):
        header_params["Content-Type"] = self.select_header_content_type(
            ["application/json-patch+json"]
        )
        return super().call_api(
            resource_path,
            method,
            path_params,
            query_params,
            header_params,
            body,
            post_params,
            files,
            response_type,
            auth_settings,
            async_req,
            _return_http_data_only,
            collection_formats,
            _preload_content,
            _request_timeout,
        )


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
                        "storage": "1Gi",
                    },
                },
            },
        }
        v1.create_namespaced_persistent_volume_claim(
            namespace=NOTEBOOK_NAMESPACE,
            body=body,
        )

    except ApiException as e:
        body = literal_eval(e.body)
        message = body["message"]
        raise InternalServerError(
            code="CannotCreatePersistentVolumeClaim",
            message=f"Error while trying to create persistent volume claim: {message}",
        )

    try:
        notebook = custom_api.get_namespaced_custom_object(
            group=NOTEBOOK_GROUP,
            version="v1",
            namespace=NOTEBOOK_NAMESPACE,
            plural="notebooks",
            name=NOTEBOOK_NAME,
            _request_timeout=5,
        )

        # Prevents the creation of duplicate mountPath
        pod_vols = enumerate(
            notebook["spec"]["template"]["spec"]["containers"][0]["volumeMounts"]
        )
        vol_index = next((i for i, v in pod_vols if v["mountPath"] == mount_path), -1)
        if vol_index > -1:
            warnings.warn(
                f"Notebook server already has a task at: {mount_path}. Skipping the mount of volume {name}"
            )
            return

    except ApiException as e:
        if e.status == 404:
            warnings.warn(
                f"Notebook server does not exist. Skipping the mount of volume {name}"
            )
            return
        body = literal_eval(e.body)
        message = body["message"]
        raise InternalServerError(
            code="CannotPatchNotebookServer",
            message=f"Error while trying to patch notebook server: {message}",
        )

    try:
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
                pod_is_running = pod.status.phase == "Running"
                containers_are_running = all(
                    [c.ready for c in pod.status.container_statuses]
                )
                # TODO Check if the volume is mounted
                volume_is_mounted = True

                if pod_is_running and containers_are_running and volume_is_mounted:
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
        raise InternalServerError(
            code="CannotPatchNotebookServer",
            message=f"Error while trying to patch notebook server: {message}",
        )


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
        notebook = custom_api.get_namespaced_custom_object(
            group=NOTEBOOK_GROUP,
            version="v1",
            namespace=NOTEBOOK_NAMESPACE,
            plural="notebooks",
            name=NOTEBOOK_NAME,
            _request_timeout=5,
        )
    except ApiException as e:
        if e.status == 404:
            warnings.warn(
                f"Notebook server does not exist. Skipping update volume mount path {name}"
            )
            return
        body = literal_eval(e.body)
        message = body["message"]
        raise InternalServerError(
            code="CannotPatchNotebookServer",
            message=f"Error while trying to patch notebook server: {message}",
        )

    try:
        pod_vols = enumerate(notebook["spec"]["template"]["spec"]["volumes"])
        vol_index = next((i for i, v in pod_vols if v["name"] == f"{name}"), -1)
        if vol_index == -1:
            warnings.warn(f"Volume mount path not found: {name}")
            return

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
                if (
                    pod.status.phase == "Running"
                    and all([c.ready for c in pod.status.container_statuses])
                    and any(
                        [
                            vm
                            for vm in pod_volume_mounts
                            if vm.mount_path == f"{mount_path}"
                        ]
                    )
                ):
                    warnings.warn(
                        f"Updated volume mount path {name} in notebook server!"
                    )
                    break
            except ApiException:
                pass
            finally:
                warnings.warn(NOTEBOOK_WAITING_MSG)
                time.sleep(5)

    except ApiException as e:
        body = literal_eval(e.body)
        message = body["message"]
        raise InternalServerError(
            code="CannotPatchNotebookServer",
            message=f"Error while trying to patch notebook server: {message}",
        )


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
        notebook = custom_api.get_namespaced_custom_object(
            group=NOTEBOOK_GROUP,
            version="v1",
            namespace=NOTEBOOK_NAMESPACE,
            plural="notebooks",
            name=NOTEBOOK_NAME,
            _request_timeout=5,
        )
    except ApiException as e:
        if e.status == 404:
            warnings.warn(
                f"Notebook server does not exist. Skipping removing volume mount path {name}"
            )
            return
        body = literal_eval(e.body)
        message = body["message"]
        raise InternalServerError(
            code="CannotPatchNotebookServer",
            message=f"Error while trying to patch notebook server: {message}",
        )

    try:
        pod_vols = enumerate(notebook["spec"]["template"]["spec"]["volumes"])
        vol_index = next((i for i, v in pod_vols if v["name"] == f"{name}"), -1)
        if vol_index == -1:
            warnings.warn(f"Volume mount path not found: {name}")
            return

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
                if (
                    pod.status.phase == "Running"
                    and all([c.ready for c in pod.status.container_statuses])
                    and not [v for v in pod.spec.volumes if v.name == f"{name}"]
                ):
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
        raise InternalServerError(
            code="CannotPatchNotebookServer",
            message=f"Error while trying to patch notebook server: {message}",
        )


def handle_task_creation(
    task,
    task_id,
    experiment_notebook_path=None,
    deployment_notebook_path=None,
    copy_name=None,
):
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
    create_persistent_volume_claim(
        name=f"vol-task-{task_id}", mount_path=f"{JUPYTER_WORKSPACE}/{task.name}"
    )

    experiment_path = None
    deployment_path = None

    if experiment_notebook_path:
        experiment_path = f"{task.name}/{experiment_notebook_path}"

    if deployment_notebook_path:
        deployment_path = f"{task.name}/{deployment_notebook_path}"

    if copy_name:
        # the dot (.) at the end ensures that the contents of a folder is copied
        # and not the folder itself
        source_path = f"{JUPYTER_WORKSPACE}/{copy_name}/."
        destination_path = f"{JUPYTER_WORKSPACE}/{task.name}/"
        copy_files_in_pod(source_path, destination_path)
    else:
        if task.experiment_notebook and task.deployment_notebook:
            experiment_path = f"{task.name}/Experiment.ipynb"
            with NamedTemporaryFile("w", delete=False) as f1:
                json.dump(task.experiment_notebook, f1)

            filepath1 = f1.name

            deployment_path = f"{task.name}/Deployment.ipynb"
            with NamedTemporaryFile("w", delete=False) as f2:
                json.dump(task.deployment_notebook, f2)

            filepath2 = f2.name

            copy_files_to_pod([filepath1, filepath2], [experiment_path, deployment_path])
            os.remove(filepath1)
            os.remove(filepath2)
        
        elif task.experiment_notebook and not task.deployment_notebook:
            experiment_path = f"{task.name}/Experiment.ipynb"
            # copies experiment notebook file to pod
            with NamedTemporaryFile("w", delete=False) as f:
                json.dump(task.experiment_notebook, f)

            filepath = f.name
            copy_file_to_pod(filepath, experiment_path)
            os.remove(filepath)

        elif task.deployment_notebook and not task.experiment_notebook:
            deployment_path = f"{task.name}/Deployment.ipynb"
            # copies deployment notebook file to pod
            with NamedTemporaryFile("w", delete=False) as f:
                json.dump(task.deployment_notebook, f)

            filepath = f.name
            copy_file_to_pod(filepath, deployment_path)
            os.remove(filepath)

    # create ConfigMap for monitoring tasks
    if MONITORING_TAG in task.tags:
        experiment_notebook_content = get_file_from_pod(experiment_path)
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

    if experiment_path:
        loop.run_until_complete(
            set_notebook_metadata(
                notebook_path=experiment_path,
                task_id=task_id,
                experiment_id=experiment_id,
                operator_id=operator_id,
            )
        )

    if deployment_path:
        loop.run_until_complete(
            set_notebook_metadata(
                notebook_path=deployment_path,
                task_id=task_id,
                experiment_id=experiment_id,
                operator_id=operator_id,
            )
        )


def update_task_config_map(task_name, task_id, experiment_notebook_path):
    """
    Update ConfigMap for task notebooks.

    Parameters
    ----------
    task_name : projects.schemas.task.TaskCreate
    task_id : str
    experiment_notebook_path : str
    """
    # update ConfigMap of monitoring task
    delete_monitoring_task_config_map(task_id)
    experiment_path = f"{task_name}/{experiment_notebook_path}"
    experiment_notebook_content = get_file_from_pod(experiment_path)
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
    notebook_path = f"{JUPYTER_WORKSPACE}/{filepath}"

    warnings.warn(f"Fetching {notebook_path} from pod...")
    load_kube_config()
    api_instance = client.CoreV1Api()

    exec_command = ["cat", notebook_path]

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
            warnings.warn("File content fetched.")
    container_stream.close()

    return file_content


def get_files_from_task(task_name):
    """
    Get all files inside a task folder in a notebook server.

    Parameters
    ----------
     task_name: str

    Returns
    -------
    str
        File content.
    """

    warnings.warn(f"Zipping contents of task: '{task_name}'")
    load_kube_config()
    api_instance = client.CoreV1Api()

    python_script = (
        f"import os; "
        f"os.chdir('{JUPYTER_WORKSPACE}/{task_name}'); "
        f"os.system('zip -q -r - * | base64'); "
    )
    exec_command = ["python", "-c", python_script]

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

    zip_file_content = ""

    while container_stream.is_open():
        container_stream.update(timeout=10)
        if container_stream.peek_stdout():
            zip_file_content = container_stream.read_stdout()
            warnings.warn("File content fetched.")
    container_stream.close()

    # the stdout string contains \n character, we must remove
    clean_zip_file_content = zip_file_content.replace("\n", "")
    return clean_zip_file_content


def log_stdout_stderr(container_stream):
    """
    Catch and log container stdout and stderr.

    Parameters
    ----------
    container_stream: kubernetes.stream.ws_client.WSClient
    """
    if container_stream.peek_stdout():
        warnings.warn("STDOUT: %s" % container_stream.read_stdout())
    if container_stream.peek_stderr():
        warnings.warn("STDERR: %s" % container_stream.read_stderr())


def handle_container_stream(container_stream, buffer=None):
    """
    Read container stream stdout and stderr and write the buffer, if given.

    Parameters
    ----------
    container_stream: kubernetes.stream.ws_client.WSClient
    tar_buffer: file-like
    """
    # WARNING:
    # Attempts to write the entire tarfile caused connection errors for large files
    # The loop below reads/writes small chunks to prevent these errors
    retry_count = 0
    while retry_count < MAX_RETRY:
        try:
            while container_stream.is_open():
                container_stream.update(timeout=10)
                log_stdout_stderr(container_stream)
                if buffer is not None:
                    data = buffer.read(1000000)
                    if data:
                        container_stream.write_stdin(data)
                        continue
                    break
            container_stream.close()
            break
        except ApiException as e:
            if e.status == http.HTTPStatus.INTERNAL_SERVER_ERROR:
                retry_count += 1
                continue
            warnings.warn("Kubernetes API Error: %s" % e.reason)


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
    while True:
        try:
            pod = api_instance.read_namespaced_pod(
                name=NOTEBOOK_POD_NAME,
                namespace=NOTEBOOK_NAMESPACE,
                _request_timeout=5,
            )
            if not pod.status.container_statuses:
                continue
            pod_is_running = pod.status.phase == "Running"
            containers_are_running = all(
                [c.ready for c in pod.status.container_statuses]
            )
            if pod_is_running and containers_are_running:
                break
        except ApiException:
            pass
    while True:
        try:
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
            break
        except ApiException:
            pass

    with TemporaryFile() as tar_buffer:
        # Prepares an uncompressed tarfile that will be written to STDIN
        with tarfile.open(fileobj=tar_buffer, mode="w") as tar:
            tar.add(filepath, arcname=destination_path)

        # Rewinds to beggining of tarfile
        tar_buffer.seek(0)

        handle_container_stream(container_stream=container_stream, buffer=tar_buffer)

    warnings.warn(f"Copied '{filepath}' to '{destination_path}'!")


def copy_files_to_pod(filepaths, destination_path):
    """
    Copies a local file to a pod in notebook server.
    Based on this example:
    https://github.com/prafull01/Kubernetes-Utilities/blob/master/kubectl_cp_as_python_client.py

    Parameters
    ----------
    filepath : str
    destination_path : str
    """
    warnings.warn(f"Copying '{filepaths[0]} and {filepaths[1]}' to '{destination_path}'...")
    load_kube_config()
    api_instance = client.CoreV1Api()

    # The following command extracts the contents of STDIN to /home/jovyan/tasks
    exec_command = ["tar", "xvf", "-", "-C", "/home/jovyan/tasks"]
    while True:
        try:
            pod = api_instance.read_namespaced_pod(
                name=NOTEBOOK_POD_NAME,
                namespace=NOTEBOOK_NAMESPACE,
                _request_timeout=5,
            )
            if not pod.status.container_statuses:
                continue
            pod_is_running = pod.status.phase == "Running"
            containers_are_running = all(
                [c.ready for c in pod.status.container_statuses]
            )
            if pod_is_running and containers_are_running:
                break
        except ApiException:
            pass
    while True:
        try:
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
            break
        except ApiException:
            pass

    with TemporaryFile() as tar_buffer:
        # Prepares an uncompressed tarfile that will be written to STDIN
        with tarfile.open(fileobj=tar_buffer, mode="w") as tar:
            tar.add(filepaths[0], arcname=destination_path[0])
            tar.add(filepaths[1], arcname=destination_path[1])

        # Rewinds to beggining of tarfile
        tar_buffer.seek(0)

        handle_container_stream(container_stream=container_stream, buffer=tar_buffer)

    warnings.warn(f"Copied '{filepaths[0]} and {filepaths[1]}' to '{destination_path[0]} and {destination_path[1]}'!")


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

    handle_container_stream(container_stream=container_stream)

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

    handle_container_stream(container_stream=container_stream)

    warnings.warn(f"Setting metadata in {notebook_path}...")
