# -*- coding: utf-8 -*-
from json import loads
import unittest
import unittest.mock as mock

from fastapi.testclient import TestClient

from projects import models
from projects.api.main import app
from projects.database import session_scope
from projects.kfp.tasks import make_task_creation_job

import tests.util as util

app.dependency_overrides[session_scope] = util.override_session_scope
TEST_CLIENT = TestClient(app)

HOST_URL = "http://ml-pipeline.kubeflow:8888"


class TestTasks(unittest.TestCase):
    maxDiff = None

    def setUp(self):
        """
        Sets up the test before running it.
        """
        util.create_mocks()

    def tearDown(self):
        """
        Deconstructs the test after running it.
        """
        util.delete_mocks()

    def test_list_tasks_no_args(self):
        """
        Should return an empty list.
        """
        rv = TEST_CLIENT.get("/tasks")
        result = rv.json()

        expected = util.MOCK_TASK_LIST
        self.assertEqual(result, expected)
        self.assertEqual(rv.status_code, 200)

    def test_list_tasks_filter_name(self):
        """
        Should return a list of tasks sorted by name descending.
        """
        rv = TEST_CLIENT.get("/tasks?name=task")
        result = rv.json()

        expected = util.MOCK_TASK_LIST
        self.assertEqual(result, expected)
        self.assertEqual(rv.status_code, 200)

    def test_list_tasks_order_name_asc(self):
        """
        Should return a list of tasks sorted by name descending.
        """
        rv = TEST_CLIENT.get("/tasks?order=name asc")
        result = rv.json()

        expected = util.MOCK_TASK_LIST
        self.assertEqual(result, expected)
        self.assertEqual(rv.status_code, 200)

    def test_list_tasks_order_name_desc(self):
        """
        Should return a list of tasks sorted by name descending.
        """
        rv = TEST_CLIENT.get("/tasks?order=name desc")
        result = rv.json()

        expected = util.MOCK_TASK_LIST_SORTED_BY_NAME_DESC
        self.assertEqual(result, expected)
        self.assertEqual(rv.status_code, 200)

    def test_list_tasks_invalid_order_argument(self):
        """
        Should return a http error 400 and a message 'invalid order argument'.
        """
        rv = TEST_CLIENT.get("/tasks?order=name unk")
        result = rv.json()

        expected = {
            "message": "Invalid order argument",
            "code": "InvalidOrderBy",
        }
        self.assertDictEqual(expected, result)
        self.assertEqual(rv.status_code, 400)

    def test_list_tasks_page_size_1(self):
        """
        Should return a list of tasks with one element.
        """
        rv = TEST_CLIENT.get("/tasks?page_size=1")
        result = rv.json()

        expected = {"tasks": [util.MOCK_TASK_1], "total": 1}
        self.assertEqual(result, expected)
        self.assertEqual(rv.status_code, 200)

    def test_list_tasks_page_size_1_page_3(self):
        """
        Should return a list of tasks with one element.
        """
        rv = TEST_CLIENT.get("/tasks?page_size=1&page=3")
        result = rv.json()

        expected = {"tasks": [util.MOCK_TASK_3], "total": 1}
        self.assertEqual(result, expected)
        self.assertEqual(rv.status_code, 200)

    @mock.patch(
        "kfp.Client",
        return_value=util.MOCK_KFP_CLIENT,
    )
    def test_create_task_empty_request_body_success(
        self,
        mock_kfp_client,
    ):
        """
        Should create task successfully.
        """
        rv = TEST_CLIENT.post("/tasks", json={})
        self.assertEqual(rv.status_code, 200)

        mock_kfp_client.assert_any_call(host=HOST_URL)

    def test_create_task_given_name_already_exists_error(self):
        """
        Should return http status 400 and a message 'a task with given name already exists'.
        """
        rv = TEST_CLIENT.post("/tasks", json={"name": util.MOCK_TASK_NAME_1})
        result = rv.json()

        expected = {
            "message": "a task with that name already exists",
            "code": "TaskNameExists",
        }
        self.assertDictEqual(expected, result)
        self.assertEqual(rv.status_code, 400)

    def test_create_task_notebook_or_task_id_error(self):
        """
        Should return http status 400 and a message 'Either provide notebooks or a task to copy from'.
        """
        task_id = util.MOCK_UUID_1
        experiment_notebook = {
            "cells": [],
            "metadata": {},
            "nbformat": 4,
            "nbformat_minor": 4,
        }
        rv = TEST_CLIENT.post(
            "/tasks",
            json={
                "copyFrom": task_id,
                "experimentNotebook": experiment_notebook,
            },
        )
        result = rv.json()

        expected = {
            "message": "Either provide notebooks or a task to copy from",
            "code": "MissingRequiredNotebookOrTaskId",
        }
        self.assertDictEqual(expected, result)
        self.assertEqual(rv.status_code, 400)

    def test_create_task_invalid_task_id_error(self):
        """
        Should return http status 400 and a message 'source task does not exist'.
        """
        task_id = "unk"
        rv = TEST_CLIENT.post(
            "/tasks",
            json={
                "copyFrom": task_id,
            },
        )
        result = rv.json()

        expected = {
            "message": "source task does not exist",
            "code": "InvalidTaskId",
        }
        self.assertDictEqual(expected, result)
        self.assertEqual(rv.status_code, 400)

    def test_create_task_invalid_docker_image_error(self):
        """
        Should return http status 400 and a message 'invalid docker image name'.
        """
        docker_image = "unk"
        rv = TEST_CLIENT.post(
            "/tasks",
            json={
                "image": docker_image,
            },
        )
        result = rv.json()

        expected = {
            "message": "invalid docker image name",
            "code": "InvalidDockerImageName",
        }
        self.assertDictEqual(expected, result)
        self.assertEqual(rv.status_code, 400)

    @mock.patch(
        "kfp.Client",
        return_value=util.MOCK_KFP_CLIENT,
    )
    def test_create_task_without_name_success(
        self,
        mock_kfp_client,
    ):
        """
        Should create and return a task successfully. A task name is auto generated.
        """
        task_category = "DEFAULT"

        rv = TEST_CLIENT.post("/tasks", json={"category": task_category})
        result = rv.json()

        expected = {
            "arguments": None,
            "category": "DEFAULT",
            "commands": None,
            "cpuLimit": "2000m",
            "cpuRequest": "100m",
            "createdAt": mock.ANY,
            "dataIn": None,
            "dataOut": None,
            "description": None,
            "docs": None,
            "hasNotebook": True,
            "image": models.task.TASK_DEFAULT_EXPERIMENT_IMAGE,
            "memoryLimit": models.task.TASK_DEFAULT_MEMORY_LIMIT,
            "memoryRequest": models.task.TASK_DEFAULT_MEMORY_REQUEST,
            "name": "Tarefa em branco - 1",
            "parameters": [],
            "readinessProbeInitialDelaySeconds": models.task.TASK_DEFAULT_READINESS_INITIAL_DELAY_SECONDS,
            "tags": ["DEFAULT"],
            "updatedAt": mock.ANY,
            "uuid": mock.ANY,
        }
        self.assertEqual(result, expected)
        self.assertEqual(rv.status_code, 200)

        mock_kfp_client.assert_any_call(host=HOST_URL)

    @mock.patch(
        "kfp.Client",
        return_value=util.MOCK_KFP_CLIENT,
    )
    def test_task_creation_job_function(
        self,
        mock_kfp_client,
    ):
        make_task_creation_job

    @mock.patch(
        "kfp.Client",
        return_value=util.MOCK_KFP_CLIENT,
    )
    def test_create_task_with_name_success(
        self,
        mock_kfp_client,
    ):
        """
        Should create and return a task successfully.
        """
        task_name = "task-6"
        task_category = "DEFAULT"

        rv = TEST_CLIENT.post(
            "/tasks", json={"name": task_name, "category": task_category}
        )
        result = rv.json()

        expected = {
            "arguments": None,
            "category": "DEFAULT",
            "commands": None,
            "cpuLimit": models.task.TASK_DEFAULT_CPU_LIMIT,
            "cpuRequest": models.task.TASK_DEFAULT_CPU_REQUEST,
            "createdAt": mock.ANY,
            "dataIn": None,
            "dataOut": None,
            "description": None,
            "docs": None,
            "hasNotebook": True,
            "image": models.task.TASK_DEFAULT_EXPERIMENT_IMAGE,
            "memoryLimit": models.task.TASK_DEFAULT_MEMORY_LIMIT,
            "memoryRequest": models.task.TASK_DEFAULT_MEMORY_REQUEST,
            "name": task_name,
            "parameters": [],
            "readinessProbeInitialDelaySeconds": models.task.TASK_DEFAULT_READINESS_INITIAL_DELAY_SECONDS,
            "tags": ["DEFAULT"],
            "updatedAt": mock.ANY,
            "uuid": mock.ANY,
        }
        self.assertEqual(result, expected)
        self.assertEqual(rv.status_code, 200)

    #  mock_kfp_client.assert_any_call(host=HOST_URL)

    @mock.patch(
        "kfp.Client",
        return_value=util.MOCK_KFP_CLIENT,
    )
    def test_create_task_copy_from_success(
        self,
        mock_kfp_client,
    ):
        """
        Should create and return a task successfully. A task name is auto generated.
        """
        task_id = util.MOCK_UUID_1

        rv = TEST_CLIENT.post("/tasks", json={"copyFrom": task_id})
        result = rv.json()

        expected = {
            "arguments": None,
            "category": "DEFAULT",
            "commands": None,
            "cpuLimit": models.task.TASK_DEFAULT_CPU_LIMIT,
            "cpuRequest": models.task.TASK_DEFAULT_CPU_REQUEST,
            "createdAt": mock.ANY,
            "dataIn": None,
            "dataOut": None,
            "description": None,
            "docs": None,
            "hasNotebook": True,
            "image": models.task.TASK_DEFAULT_EXPERIMENT_IMAGE,
            "memoryLimit": models.task.TASK_DEFAULT_MEMORY_LIMIT,
            "memoryRequest": models.task.TASK_DEFAULT_MEMORY_REQUEST,
            "name": f"{util.MOCK_TASK_NAME_1} - Cópia - 1",
            "parameters": [],
            "readinessProbeInitialDelaySeconds": models.task.TASK_DEFAULT_READINESS_INITIAL_DELAY_SECONDS,
            "tags": ["DEFAULT"],
            "updatedAt": mock.ANY,
            "uuid": mock.ANY,
        }
        self.assertEqual(result, expected)
        self.assertEqual(rv.status_code, 200)

        mock_kfp_client.assert_any_call(host=HOST_URL)

    @mock.patch(
        "kfp.Client",
        return_value=util.MOCK_KFP_CLIENT,
    )
    def test_create_task_with_notebook_success(
        self,
        mock_kfp_client,
    ):
        """
        Should create and return a task successfully.
        """
        rv = TEST_CLIENT.post(
            "/tasks",
            json={
                "experimentNotebook": util.MOCK_NOTEBOOK,
                "deploymentNotebook": util.MOCK_NOTEBOOK,
            },
        )
        result = rv.json()

        expected = {
            "arguments": None,
            "category": "DEFAULT",
            "commands": None,
            "cpuLimit": models.task.TASK_DEFAULT_CPU_LIMIT,
            "cpuRequest": models.task.TASK_DEFAULT_CPU_REQUEST,
            "createdAt": mock.ANY,
            "dataIn": None,
            "dataOut": None,
            "description": None,
            "docs": None,
            "hasNotebook": True,
            "image": models.task.TASK_DEFAULT_EXPERIMENT_IMAGE,
            "memoryLimit": models.task.TASK_DEFAULT_MEMORY_LIMIT,
            "memoryRequest": models.task.TASK_DEFAULT_MEMORY_REQUEST,
            "name": "Tarefa em branco - 1",
            "parameters": [],
            "readinessProbeInitialDelaySeconds": models.task.TASK_DEFAULT_READINESS_INITIAL_DELAY_SECONDS,
            "tags": ["DEFAULT"],
            "updatedAt": mock.ANY,
            "uuid": mock.ANY,
        }
        self.assertEqual(result, expected)
        self.assertEqual(rv.status_code, 200)

        mock_kfp_client.assert_any_call(host=HOST_URL)

    def test_get_task_not_found(self):
        """
        Should return a http error 404 and a message 'specified task does not exist'.
        """
        task_id = "foo"

        rv = TEST_CLIENT.get(f"/tasks/{task_id}")
        result = rv.json()

        expected = {
            "message": "The specified task does not exist",
            "code": "TaskNotFound",
        }
        self.assertDictEqual(expected, result)
        self.assertEqual(rv.status_code, 404)

    def test_get_task_success(self):
        """
        Should return a task successfully.
        """
        task_id = util.MOCK_UUID_1

        rv = TEST_CLIENT.get(f"/tasks/{task_id}")
        result = rv.json()

        expected = util.MOCK_TASK_1
        self.assertEqual(result, expected)
        self.assertEqual(rv.status_code, 200)

    def test_update_task(self):
        """
        Should return a http error 404 and a message 'The specified task does not exist'.
        """
        rv = TEST_CLIENT.patch(
            "/tasks/foo",
            json={
                "name": "foo 2",
            },
        )
        result = rv.json()
        expected = {
            "message": "The specified task does not exist",
            "code": "TaskNotFound",
        }
        self.assertDictEqual(expected, result)
        self.assertEqual(rv.status_code, 404)

    def test_update_task_exists(self):
        """
        Should return a http error 400 and a message 'The task with that name already exists'.
        """
        task_id = util.MOCK_UUID_4

        rv = TEST_CLIENT.patch(
            f"/tasks/{task_id}",
            json={
                "name": "task-5",
            },
        )
        result = rv.json()
        expected = {
            "message": "a task with that name already exists",
            "code": "TaskNameExists",
        }
        self.assertDictEqual(expected, result)
        self.assertEqual(rv.status_code, 400)

    def test_update_task_invalid_category_error(self):
        """
        Should return a http error 400 and a message 'Invalid category. Choose any of {valid_str}'.
        """
        task_id = util.MOCK_UUID_4
        category = "unk"

        rv = TEST_CLIENT.patch(
            f"/tasks/{task_id}",
            json={
                "category": category,
            },
        )
        result = rv.json()
        valid_str = "DEFAULT,DATASETS,DESCRIPTIVE_STATISTICS,FEATURE_ENGINEERING,PREDICTOR,COMPUTER_VISION,NLP,MONITORING"
        expected = {
            "message": f"Invalid category. Choose any of {valid_str}",
            "code": "InvalidCategory",
        }
        self.assertDictEqual(expected, result)
        self.assertEqual(rv.status_code, 400)

    def test_update_task_unk_tags(self):
        """
        Should return a successfully updated task.
        """
        task_id = util.MOCK_UUID_5

        rv = TEST_CLIENT.patch(
            f"/tasks/{task_id}",
            json={
                "tags": ["UNK"],
            },
        )
        result = rv.json()
        expected = {
            "arguments": None,
            "category": "MONITORING",
            "commands": None,
            "cpuLimit": "2000m",
            "cpuRequest": "100m",
            "createdAt": mock.ANY,
            "dataIn": None,
            "dataOut": None,
            "description": None,
            "docs": None,
            "hasNotebook": False,
            "image": "platiagro/platiagro-experiment-image:0.3.0",
            "memoryLimit": "10Gi",
            "memoryRequest": "2Gi",
            "name": "task-5",
            "parameters": [],
            "readinessProbeInitialDelaySeconds": 60,
            "tags": ["UNK"],
            "updatedAt": mock.ANY,
            "uuid": "uuid-5",
        }
        self.assertDictEqual(expected, result)
        self.assertEqual(rv.status_code, 200)

    @mock.patch(
        "kubernetes.client.CoreV1Api",
        return_value=util.MOCK_CORE_V1_API,
    )
    @mock.patch(
        "kubernetes.client.CustomObjectsApi",
        return_value=util.MOCK_CUSTOM_OBJECTS_API,
    )
    @mock.patch(
        "kubernetes.config.load_kube_config",
    )
    def test_update_task_name(
        self,
        mock_config_load,
        mock_custom_objects_api,
        mock_core_v1_api,
    ):
        """
        Should return a successfully updated task.
        """
        task_id = util.MOCK_UUID_5
        rv = TEST_CLIENT.patch(
            f"/tasks/{task_id}",
            json={
                "name": "name foo",
            },
        )
        result = rv.json()
        expected = {
            "arguments": None,
            "category": "MONITORING",
            "commands": None,
            "cpuLimit": "2000m",
            "cpuRequest": "100m",
            "createdAt": mock.ANY,
            "dataIn": None,
            "dataOut": None,
            "description": None,
            "docs": None,
            "hasNotebook": False,
            "image": "platiagro/platiagro-experiment-image:0.3.0",
            "memoryLimit": "10Gi",
            "memoryRequest": "2Gi",
            "name": "name foo",
            "parameters": [],
            "readinessProbeInitialDelaySeconds": 60,
            "tags": [],
            "updatedAt": mock.ANY,
            "uuid": "uuid-5",
        }
        self.assertDictEqual(expected, result)
        self.assertEqual(rv.status_code, 200)

        mock_core_v1_api.assert_any_call()
        mock_custom_objects_api.assert_any_call(api_client=mock.ANY)
        mock_config_load.assert_any_call()

    def test_update_task_tags(self):
        """
        Should return a successfully updated task.
        """
        task_id = util.MOCK_UUID_5

        rv = TEST_CLIENT.patch(
            f"/tasks/{task_id}",
            json={
                "tags": ["FEATURE_ENGINEERING"],
            },
        )
        result = rv.json()
        expected = {
            "uuid": "uuid-5",
            "name": "task-5",
            "description": None,
            "commands": None,
            "cpuLimit": "2000m",
            "cpuRequest": "100m",
            "arguments": None,
            "category": "MONITORING",
            "tags": ["FEATURE_ENGINEERING"],
            "dataIn": None,
            "dataOut": None,
            "docs": None,
            "hasNotebook": False,
            "image": "platiagro/platiagro-experiment-image:0.3.0",
            "memoryLimit": "10Gi",
            "memoryRequest": "2Gi",
            "parameters": [],
            "readinessProbeInitialDelaySeconds": 60,
            "createdAt": mock.ANY,
        }
        machine_generated = ["updatedAt"]
        for attr in machine_generated:
            self.assertIn(attr, result)
            del result[attr]
        self.assertDictEqual(expected, result)
        self.assertEqual(rv.status_code, 200)

    @mock.patch(
        "kubernetes.client.CoreV1Api",
        return_value=util.MOCK_CORE_V1_API,
    )
    @mock.patch(
        "kubernetes.config.load_kube_config",
    )
    def test_update_task_experiment_notebook(
        self,
        mock_config_load,
        mock_core_v1_api,
    ):
        """
        Should return a successfully updated task experiment notebook.
        """
        task_id = util.MOCK_UUID_5

        rv = TEST_CLIENT.patch(
            f"/tasks/{task_id}",
            json={
                "experimentNotebook": loads(util.SAMPLE_NOTEBOOK),
            },
        )
        result = rv.json()
        expected = {
            "uuid": "uuid-5",
            "name": "task-5",
            "description": None,
            "commands": None,
            "arguments": None,
            "cpuLimit": "2000m",
            "cpuRequest": "100m",
            "category": "MONITORING",
            "tags": [],
            "dataIn": None,
            "dataOut": None,
            "docs": None,
            "hasNotebook": True,
            "image": "platiagro/platiagro-experiment-image:0.3.0",
            "memoryLimit": "10Gi",
            "memoryRequest": "2Gi",
            "parameters": [],
            "readinessProbeInitialDelaySeconds": 60,
            "createdAt": mock.ANY,
        }
        machine_generated = ["updatedAt"]
        for attr in machine_generated:
            self.assertIn(attr, result)
            del result[attr]
        self.assertDictEqual(expected, result)
        self.assertEqual(rv.status_code, 200)

        mock_core_v1_api.assert_any_call()
        mock_config_load.assert_any_call()

    @mock.patch(
        "kubernetes.client.CoreV1Api",
        return_value=util.MOCK_CORE_V1_API,
    )
    @mock.patch(
        "kubernetes.config.load_kube_config",
    )
    def test_update_task_deployment_notebook(self, mock_config_load, mock_core_v1_api):
        """
        Should return a successfully updated task deployment notebook.
        """
        task_id = util.MOCK_UUID_4

        rv = TEST_CLIENT.patch(
            f"/tasks/{task_id}",
            json={
                "deploymentNotebook": loads(util.SAMPLE_NOTEBOOK),
            },
        )
        result = rv.json()
        expected = {
            "uuid": "uuid-4",
            "name": "task-4",
            "description": None,
            "commands": None,
            "cpuLimit": "2000m",
            "cpuRequest": "100m",
            "arguments": None,
            "category": "DEFAULT",
            "tags": [],
            "dataIn": None,
            "dataOut": None,
            "docs": None,
            "hasNotebook": True,
            "image": "platiagro/platiagro-experiment-image:0.3.0",
            "memoryLimit": "10Gi",
            "memoryRequest": "2Gi",
            "parameters": [],
            "readinessProbeInitialDelaySeconds": 60,
            "createdAt": mock.ANY,
        }
        machine_generated = ["updatedAt"]
        for attr in machine_generated:
            self.assertIn(attr, result)
            del result[attr]
        self.assertDictEqual(expected, result)
        self.assertEqual(rv.status_code, 200)

        mock_core_v1_api.assert_any_call()
        mock_config_load.assert_any_call()

    def test_delete_task_not_found(self):
        """
        Should return a http error 404 and a message 'The specified task does not exist'.
        """
        task_id = "unk"

        rv = TEST_CLIENT.delete(f"/tasks/{task_id}")
        result = rv.json()

        expected = {
            "message": "The specified task does not exist",
            "code": "TaskNotFound",
        }
        self.assertDictEqual(expected, result)
        self.assertEqual(rv.status_code, 404)

    def test_delete_task_related_to_operator_error(self):
        """
        Should return a http error 403 and a message 'Task related to an operator'.
        """
        task_id = util.MOCK_UUID_1

        rv = TEST_CLIENT.delete(f"/tasks/{task_id}")
        result = rv.json()

        expected = {
            "message": "Task related to an operator",
            "code": "TaskProtectedFromDeletion",
        }
        self.assertDictEqual(expected, result)
        self.assertEqual(rv.status_code, 403)

    @mock.patch(
        "kubernetes.client.CoreV1Api",
        return_value=util.MOCK_CORE_V1_API,
    )
    @mock.patch(
        "kubernetes.client.CustomObjectsApi",
        return_value=util.MOCK_CUSTOM_OBJECTS_API,
    )
    @mock.patch(
        "kubernetes.config.load_kube_config",
    )
    def test_delete_task_success(
        self,
        mock_config_load,
        mock_custom_objects_api,
        mock_core_v1_api,
    ):
        """
        Should delete task successfully.
        """
        task_id = util.MOCK_UUID_4

        rv = TEST_CLIENT.delete(f"/tasks/{task_id}")
        result = rv.json()

        expected = {"message": "Task deleted"}
        self.assertDictEqual(expected, result)

        mock_core_v1_api.assert_any_call()
        mock_custom_objects_api.assert_any_call(api_client=mock.ANY)
        mock_config_load.assert_any_call()
