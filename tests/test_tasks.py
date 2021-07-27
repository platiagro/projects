# -*- coding: utf-8 -*-
from json import dumps, loads
from unittest import TestCase

import requests
from fastapi.testclient import TestClient
from minio.error import BucketAlreadyOwnedByYou

from projects.api.main import app
from projects.controllers.utils import uuid_alpha
from projects.database import engine
from projects.jupyter import COOKIES, HEADERS, JUPYTER_ENDPOINT
from projects.object_storage import BUCKET_NAME, MINIO_CLIENT

TEST_CLIENT = TestClient(app)

TASK_ID = str(uuid_alpha())
NAME = "name foo"
DESCRIPTION = "long foo"
IMAGE = "platiagro/platiagro-experiment-image:0.3.0"
COMMANDS = ["CMD"]
COMMANDS_JSON = dumps(COMMANDS)
ARGUMENTS = ["ARG"]
ARGUMENTS_JSON = dumps(ARGUMENTS)
CATEGORY = "DEFAULT"
DATA_IN = ""
DATA_OUT = ""
DOCS = ""
TAGS = ["PREDICTOR"]
TAGS_JSON = dumps(TAGS)
EXPERIMENT_NOTEBOOK_PATH = None
DEPLOYMENT_NOTEBOOK_PATH = None
IS_DEFAULT = False
PARAMETERS = [{"default": True, "name": "shuffle", "type": "boolean"}]
CREATED_AT = "2000-01-01 00:00:00"
CREATED_AT_ISO = "2000-01-01T00:00:00"
UPDATED_AT = "2000-01-01 00:00:00"
UPDATED_AT_ISO = "2000-01-01T00:00:00"
SAMPLE_NOTEBOOK = '{"cells":[{"cell_type":"code","execution_count":null,"metadata":{"tags":["parameters"]},"outputs":[],"source":["shuffle = True #@param {type: \\"boolean\\"}"]}],"metadata":{"kernelspec":{"display_name":"Python 3","language":"python","name":"python3"},"language_info":{"codemirror_mode":{"name":"ipython","version":3},"file_extension":".py","mimetype":"text/x-python","name":"python","nbconvert_exporter":"python","pygments_lexer":"ipython3","version":"3.6.9"}},"nbformat":4,"nbformat_minor":4}'

TASK_ID_2 = str(uuid_alpha())

PROJECT_ID = str(uuid_alpha())

EXPERIMENT_ID = str(uuid_alpha())
POSITION = 0

OPERATOR_ID = str(uuid_alpha())
PARAMETERS = {"coef": 0.1}
PARAMETERS_JSON = dumps(PARAMETERS)
POSITION_X = 0
POSITION_Y = 0
DEPENDENCIES_OP_ID = [OPERATOR_ID]
DEPENDENCIES_OP_ID_JSON = dumps(DEPENDENCIES_OP_ID)

EMAILS_TO_SEND = ["fictional.receiver.1661430@protonmail.com"]
TENANT = "anonymous"


class TestTasks(TestCase):

    def setUp(self):
        self.maxDiff = None
        conn = engine.connect()
        text = (
            f"INSERT INTO tasks (uuid, name, description, image, commands, arguments, category, "
            f"tags, data_in, data_out, docs, parameters, experiment_notebook_path, "
            f"deployment_notebook_path, cpu_limit, cpu_request, memory_limit, memory_request, "
            f"readiness_probe_initial_delay_seconds, is_default, created_at, updated_at) "
            f"VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
        )
        conn.execute(text, (TASK_ID, NAME, DESCRIPTION, IMAGE, COMMANDS_JSON, ARGUMENTS_JSON, CATEGORY, TAGS_JSON, DATA_IN, DATA_OUT, DOCS, dumps([]),
                            EXPERIMENT_NOTEBOOK_PATH, DEPLOYMENT_NOTEBOOK_PATH, "100m", "100m", "1Gi", "1Gi", 300, 0, CREATED_AT, UPDATED_AT,))

        text = (
            f"INSERT INTO tasks (uuid, name, description, image, commands, arguments, category, "
            f"tags, data_in, data_out, docs, parameters, experiment_notebook_path, "
            f"deployment_notebook_path, cpu_limit, cpu_request, memory_limit, memory_request, "
            f"readiness_probe_initial_delay_seconds, is_default, created_at, updated_at) "
            f"VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
        )
        conn.execute(text, (TASK_ID_2, 'foo 2', DESCRIPTION, IMAGE, COMMANDS_JSON, ARGUMENTS_JSON, CATEGORY, TAGS_JSON, DATA_IN,
                            DATA_OUT, DOCS, dumps([]), EXPERIMENT_NOTEBOOK_PATH, DEPLOYMENT_NOTEBOOK_PATH, "100m", "100m", "1Gi",
                            "1Gi", 300, 0, CREATED_AT, UPDATED_AT,))

        text = (
            f"INSERT INTO projects (uuid, name, created_at, updated_at, tenant) "
            f"VALUES (%s, %s, %s, %s, %s)"
        )
        conn.execute(text, (PROJECT_ID, NAME, CREATED_AT, UPDATED_AT, TENANT,))

        text = (
            f"INSERT INTO experiments (uuid, name, project_id, position, is_active, created_at, updated_at) "
            f"VALUES (%s, %s, %s, %s, %s, %s, %s)"
        )
        conn.execute(text, (EXPERIMENT_ID, NAME, PROJECT_ID, POSITION, 1, CREATED_AT, UPDATED_AT,))

        text = (
            f"INSERT INTO operators (uuid, name, status, status_message, experiment_id, task_id, parameters, position_x, "
            f"position_y, dependencies, created_at, updated_at) "
            f"VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
        )
        conn.execute(text, (OPERATOR_ID, None, "Unset", None, EXPERIMENT_ID, TASK_ID, PARAMETERS_JSON, POSITION_X,
                            POSITION_Y, DEPENDENCIES_OP_ID_JSON, CREATED_AT, UPDATED_AT,))
        conn.close()

    def tearDown(self):
        conn = engine.connect()
        text = f"DELETE FROM operators WHERE uuid = '{OPERATOR_ID}'"
        conn.execute(text)

        conn = engine.connect()
        text = f"DELETE FROM experiments WHERE uuid = '{EXPERIMENT_ID}'"
        conn.execute(text)

        conn = engine.connect()
        text = f"DELETE FROM projects WHERE uuid = '{PROJECT_ID}'"
        conn.execute(text)

        conn = engine.connect()
        text = f"DELETE FROM tasks WHERE uuid in ('{TASK_ID}', '{TASK_ID_2}')"
        conn.execute(text)

        conn = engine.connect()
        text = "DELETE FROM tasks WHERE name LIKE '%%test%%'"
        conn.execute(text)

        conn.close()

    def test_list_tasks(self):
        rv = TEST_CLIENT.get("/tasks")
        result = rv.json()
        self.assertIsInstance(result["tasks"], list)
        self.assertIsInstance(result["total"], int)
        self.assertEqual(rv.status_code, 200)

        rv = TEST_CLIENT.get("/tasks?order=uuid asc")
        result = rv.json()
        self.assertIsInstance(result["tasks"], list)
        self.assertIsInstance(result["total"], int)
        self.assertEqual(rv.status_code, 200)

        rv = TEST_CLIENT.get("/tasks?order=uuid desc")
        result = rv.json()
        self.assertIsInstance(result["tasks"], list)
        self.assertIsInstance(result["total"], int)
        self.assertEqual(rv.status_code, 200)

        rv = TEST_CLIENT.get("/tasks?page=1&order=uuid asc")
        result = rv.json()
        self.assertIsInstance(result["tasks"], list)
        self.assertIsInstance(result["total"], int)
        self.assertEqual(rv.status_code, 200)

        rv = TEST_CLIENT.get(f"/tasks?name={NAME}&page=1&order=uuid asc")
        result = rv.json()
        self.assertIsInstance(result["tasks"], list)
        self.assertIsInstance(result["total"], int)
        self.assertEqual(rv.status_code, 200)

        rv = TEST_CLIENT.get(f"/tasks?name={NAME}&page=1&page_size=10&order=name desc")
        result = rv.json()
        self.assertIsInstance(result["tasks"], list)
        self.assertIsInstance(result["total"], int)
        self.assertEqual(rv.status_code, 200)

        rv = TEST_CLIENT.get(f"/tasks?order=foo")
        result = rv.json()
        expected = {"message": "Invalid order argument"}
        self.assertDictEqual(expected, result)
        self.assertEqual(rv.status_code, 400)

        rv = TEST_CLIENT.get(f"/tasks?order=foo bar")
        result = rv.json()
        expected = {"message": "Invalid order argument"}
        self.assertDictEqual(expected, result)
        self.assertEqual(rv.status_code, 400)

    def test_create_task(self):
        # when invalid tag is sent
        # should raise bad request
        rv = TEST_CLIENT.post("/tasks", json={
            "name": "test",
            "description": "long test",
            "category": CATEGORY,
            "tags": ["UNK"],
            "copyFrom": TASK_ID,
        })
        result = rv.json()
        self.assertEqual(rv.status_code, 200)

        # Passing the name null
        rv = TEST_CLIENT.post("/tasks", json={
            "description": "test with name null",
            "category": CATEGORY
        })
        result = rv.json()
        expected = {
            "name": "Tarefa em branco - 1",
            "description": "test with name null",
            "image": IMAGE,
            "category": CATEGORY,
            "cpuLimit": "2000m",
            "cpuRequest": "100m",
            "memoryLimit": "10Gi",
            "memoryRequest": "2Gi",
            "tags": [
                "DEFAULT"
            ],
            "dataIn": None,
            "dataOut": None,
            "docs": None,
        }
        machine_generated = [
            "uuid",
            "hasNotebook",
            "readinessProbeInitialDelaySeconds",
            "commands",
            "arguments",
            "parameters",
            "createdAt",
            "updatedAt",
        ]
        for attr in machine_generated:
            self.assertIn(attr, result)
            del result[attr]
        self.assertEqual(rv.status_code, 200)
        self.assertDictEqual(expected, result)

        rv = TEST_CLIENT.post("/tasks", json={
            "category": CATEGORY
        })
        result = rv.json()
        self.assertEqual(rv.status_code, 200)

        # task name already exists
        rv = TEST_CLIENT.post("/tasks", json={
            "name": "name foo",
        })
        result = rv.json()
        expected = {"message": "a task with that name already exists"}
        self.assertDictEqual(expected, result)
        self.assertEqual(rv.status_code, 400)

        # when copyFrom and experimentNotebook/deploymentNotebook are sent
        # should raise bad request
        rv = TEST_CLIENT.post("/tasks", json={
            "name": "test",
            "description": "long test",
            "tags": TAGS,
            "copyFrom": TASK_ID,
            "experimentNotebook": loads(SAMPLE_NOTEBOOK),
            "deploymentNotebook": loads(SAMPLE_NOTEBOOK),
        })
        result = rv.json()
        expected = {"message": "Either provide notebooks or a task to copy from"}
        self.assertDictEqual(expected, result)
        self.assertEqual(rv.status_code, 400)

        # when copyFrom uuid does not exist
        # should raise bad request
        rv = TEST_CLIENT.post("/tasks", json={
            "name": "test copyFrom uuid does not exist ",
            "description": "long test",
            "tags": TAGS,
            "copyFrom": "unk",
        })
        result = rv.json()
        expected = {"message": "source task does not exist"}
        self.assertDictEqual(expected, result)
        self.assertEqual(rv.status_code, 400)

        # when neither copyFrom nor experimentNotebook/deploymentNotebook are sent
        # should create a task using an empty template notebook
        rv = TEST_CLIENT.post("/tasks", json={
            "name": "test create a task using an empty template notebook",
            "description": "long test",
            "category": CATEGORY,
        })
        result = rv.json()
        expected = {
            "name": "test create a task using an empty template notebook",
            "description": "long test",
            "category": CATEGORY,
            "cpuLimit": "2000m",
            "cpuRequest": "100m",
            "tags": ["DEFAULT"],
            "dataIn": None,
            "dataOut": None,
            "docs": None,
            "hasNotebook": True,
            "image": IMAGE,
            "memoryLimit": "10Gi",
            "memoryRequest": "2Gi",
            "parameters": [],
            "readinessProbeInitialDelaySeconds": "60",
        }
        # uuid, commands, experiment_notebook_path, deployment_notebook_path, created_at, updated_at
        # are machine-generated we assert they exist, but we don't assert their values
        machine_generated = [
            "uuid",
            "commands",
            "arguments",
            "createdAt",
            "updatedAt",
        ]
        for attr in machine_generated:
            self.assertIn(attr, result)
            del result[attr]
        self.assertDictEqual(expected, result)
        self.assertEqual(rv.status_code, 200)

        # when copyFrom is sent
        # should create a task copying notebooks from copyFrom
        rv = TEST_CLIENT.post("/tasks", json={
            "name": "test copy",
            "description": "long test",
            "category": CATEGORY,
            "tags": TAGS,
            "copyFrom": TASK_ID,
        })
        result = rv.json()
        expected = {
            "name": "test copy",
            "description": "long test",
            "category": CATEGORY,
            "cpuLimit": "100m",
            "cpuRequest": "100m",
            "tags": TAGS,
            "dataIn": None,
            "dataOut": None,
            "docs": None,
            "hasNotebook": False,
            "image": IMAGE,
            "memoryLimit": "1Gi",
            "memoryRequest": "1Gi",
            "parameters": [],
            "readinessProbeInitialDelaySeconds": "60",
        }
        machine_generated = [
            "uuid",
            "commands",
            "arguments",
            "createdAt",
            "updatedAt",
        ]
        for attr in machine_generated:
            self.assertIn(attr, result)
            del result[attr]
        self.assertDictEqual(expected, result)
        self.assertEqual(rv.status_code, 200)

        # when experimentNotebook and deploymentNotebook are sent
        # should create a task using their values as source
        rv = TEST_CLIENT.post("/tasks", json={
            "name": "test 02",
            "description": "long test",
            "category": CATEGORY,
            "tags": TAGS,
            "experimentNotebook": loads(SAMPLE_NOTEBOOK),
            "deploymentNotebook": loads(SAMPLE_NOTEBOOK),
        })
        result = rv.json()
        expected = {
            "name": "test 02",
            "description": "long test",
            "category": CATEGORY,
            "cpuLimit": "2000m",
            "cpuRequest": "100m",
            "tags": TAGS,
            "dataIn": None,
            "dataOut": None,
            "docs": None,
            "hasNotebook": True,
            "image": IMAGE,
            "memoryLimit": "10Gi",
            "memoryRequest": "2Gi",
            "parameters": [],
            "readinessProbeInitialDelaySeconds": "60",
        }
        machine_generated = [
            "uuid",
            "commands",
            "arguments",
            "createdAt",
            "updatedAt",
        ]
        for attr in machine_generated:
            self.assertIn(attr, result)
            del result[attr]
        self.assertDictEqual(expected, result)
        self.assertEqual(rv.status_code, 200)

        # when image and commands are sent
        # should create a task using their values as source
        rv = TEST_CLIENT.post("/tasks", json={
            "name": "test tasks with image and command",
            "description": "long test",
            "image": IMAGE,
            "commands": COMMANDS,
            "arguments": ARGUMENTS,
            "category": CATEGORY,
            "tags": TAGS
        })
        result = rv.json()
        expected = {
            "name": "test tasks with image and command",
            "description": "long test",
            "commands": COMMANDS,
            "cpuLimit": "2000m",
            "cpuRequest": "100m",
            "arguments": ARGUMENTS,
            "category": CATEGORY,
            "tags": TAGS,
            "dataIn": None,
            "dataOut": None,
            "docs": None,
            "hasNotebook": False,
            "image": IMAGE,
            "memoryLimit": "10Gi",
            "memoryRequest": "2Gi",
            "parameters": [],
            "readinessProbeInitialDelaySeconds": "60",
        }
        machine_generated = [
            "uuid",
            "createdAt",
            "updatedAt",
        ]
        for attr in machine_generated:
            self.assertIn(attr, result)
            del result[attr]
        self.assertDictEqual(expected, result)
        self.assertEqual(rv.status_code, 200)

        # when image is invalid should receive bad request
        rv = TEST_CLIENT.post("/tasks", json={
            "name": "test invalid image name",
            "image": "invalid name",
        })
        result = rv.json()
        expected = {"message": "invalid docker image name"}
        self.assertDictEqual(expected, result)
        self.assertEqual(rv.status_code, 400)

        # dataset task that has null notebooks
        rv = TEST_CLIENT.post("/tasks", json={
            "name": "test fake dataset task",
            "category": CATEGORY,
            "tags": ["DATASETS"],
            "image": IMAGE,
        })
        result = rv.json()
        expected = {
            "name": "test fake dataset task",
            "description": None,
            "category": CATEGORY,
            "cpuLimit": "2000m",
            "cpuRequest": "100m",
            "tags": ["DATASETS"],
            "dataIn": None,
            "dataOut": None,
            "docs": None,
            "hasNotebook": False,
            "image": IMAGE,
            "memoryLimit": "10Gi",
            "memoryRequest": "2Gi",
            "parameters": [],
            "readinessProbeInitialDelaySeconds": "60",
        }
        machine_generated = [
            "uuid",
            "createdAt",
            "updatedAt",
            "commands",
            "arguments",
        ]
        for attr in machine_generated:
            self.assertIn(attr, result)
            del result[attr]
        self.assertDictEqual(expected, result)
        self.assertEqual(rv.status_code, 200)

    def test_get_task(self):
        rv = TEST_CLIENT.get("/tasks/foo")
        result = rv.json()
        expected = {"message": "The specified task does not exist"}
        self.assertDictEqual(expected, result)
        self.assertEqual(rv.status_code, 404)

        rv = TEST_CLIENT.get(f"/tasks/{TASK_ID}")
        result = rv.json()
        expected = {
            "uuid": TASK_ID,
            "name": "name foo",
            "description": DESCRIPTION,
            "commands": COMMANDS,
            "cpuLimit": "100m",
            "cpuRequest": "100m",
            "arguments": ARGUMENTS,
            "category": CATEGORY,
            "tags": TAGS,
            "dataIn": DATA_IN,
            "dataOut": DATA_OUT,
            "docs": DOCS,
            "hasNotebook": False,
            "image": IMAGE,
            "memoryLimit": "1Gi",
            "memoryRequest": "1Gi",
            "parameters": [],
            "readinessProbeInitialDelaySeconds": "300",
            "createdAt": CREATED_AT_ISO,
            "updatedAt": UPDATED_AT_ISO,
        }
        self.assertDictEqual(expected, result)
        self.assertEqual(rv.status_code, 200)

    def test_update_task(self):
        # task none
        rv = TEST_CLIENT.patch("/tasks/foo", json={
            "name": "foo 2",
        })
        result = rv.json()
        expected = {"message": "The specified task does not exist"}
        self.assertDictEqual(expected, result)
        self.assertEqual(rv.status_code, 404)

        # task name already exists
        rv = TEST_CLIENT.patch(f"/tasks/{TASK_ID}", json={
            "name": "foo 2",
        })
        result = rv.json()
        expected = {"message": "a task with that name already exists"}
        self.assertDictEqual(expected, result)
        self.assertEqual(rv.status_code, 400)

        # invalid tags
        rv = TEST_CLIENT.patch(f"/tasks/{TASK_ID}", json={
            "tags": ["UNK"],
        })
        result = rv.json()
        self.assertEqual(rv.status_code, 200)

        # update task using the same name
        rv = TEST_CLIENT.patch(f"/tasks/{TASK_ID}", json={
            "name": "name foo",
        })
        result = rv.json()
        self.assertEqual(rv.status_code, 200)

        # update task name
        rv = TEST_CLIENT.patch(f"/tasks/{TASK_ID}", json={
            "name": "new name foo",
        })
        result = rv.json()
        expected = {
            "uuid": TASK_ID,
            "name": "new name foo",
            "description": DESCRIPTION,
            "commands": COMMANDS,
            "cpuLimit": "100m",
            "cpuRequest": "100m",
            "arguments": ARGUMENTS,
            "category": CATEGORY,
            "tags": ["UNK"],
            "dataIn": DATA_IN,
            "dataOut": DATA_OUT,
            "docs": DOCS,
            "hasNotebook": False,
            "image": IMAGE,
            "memoryLimit": "1Gi",
            "memoryRequest": "1Gi",
            "parameters": [],
            "readinessProbeInitialDelaySeconds": "300",
            "createdAt": CREATED_AT_ISO,
        }
        machine_generated = ["updatedAt"]
        for attr in machine_generated:
            self.assertIn(attr, result)
            del result[attr]
        self.assertDictEqual(expected, result)
        self.assertEqual(rv.status_code, 200)

        # update task tags
        rv = TEST_CLIENT.patch(f"/tasks/{TASK_ID}", json={
            "tags": ["FEATURE_ENGINEERING"],
        })
        result = rv.json()
        expected = {
            "uuid": TASK_ID,
            "name": "new name foo",
            "description": DESCRIPTION,
            "commands": COMMANDS,
            "cpuLimit": "100m",
            "cpuRequest": "100m",
            "arguments": ARGUMENTS,
            "category": CATEGORY,
            "tags": ["FEATURE_ENGINEERING"],
            "dataIn": DATA_IN,
            "dataOut": DATA_OUT,
            "docs": DOCS,
            "hasNotebook": False,
            "image": IMAGE,
            "memoryLimit": "1Gi",
            "memoryRequest": "1Gi",
            "parameters": [],
            "readinessProbeInitialDelaySeconds": "300",
            "createdAt": CREATED_AT_ISO,
        }
        machine_generated = ["updatedAt"]
        for attr in machine_generated:
            self.assertIn(attr, result)
            del result[attr]
        self.assertDictEqual(expected, result)
        self.assertEqual(rv.status_code, 200)

        # update task experiment notebook
        rv = TEST_CLIENT.patch(f"/tasks/{TASK_ID}", json={
            "experimentNotebook": loads(SAMPLE_NOTEBOOK),
        })
        result = rv.json()
        expected = {
            "uuid": TASK_ID,
            "name": "new name foo",
            "description": DESCRIPTION,
            "commands": COMMANDS,
            "arguments": ARGUMENTS,
            "cpuLimit": "100m",
            "cpuRequest": "100m",
            "category": CATEGORY,
            "tags": ["FEATURE_ENGINEERING"],
            "dataIn": DATA_IN,
            "dataOut": DATA_OUT,
            "docs": DOCS,
            "hasNotebook": True,
            "image": IMAGE,
            "memoryLimit": "1Gi",
            "memoryRequest": "1Gi",
            "parameters": [],
            "readinessProbeInitialDelaySeconds": "300",
            "createdAt": CREATED_AT_ISO,
        }
        machine_generated = ["updatedAt"]
        for attr in machine_generated:
            self.assertIn(attr, result)
            del result[attr]
        self.assertDictEqual(expected, result)
        self.assertEqual(rv.status_code, 200)

        # update task deployment notebook
        rv = TEST_CLIENT.patch(f"/tasks/{TASK_ID}", json={
            "deploymentNotebook": loads(SAMPLE_NOTEBOOK),
        })
        result = rv.json()
        expected = {
            "uuid": TASK_ID,
            "name": "new name foo",
            "description": DESCRIPTION,
            "commands": COMMANDS,
            "cpuLimit": "100m",
            "cpuRequest": "100m",
            "arguments": ARGUMENTS,
            "category": CATEGORY,
            "tags": ["FEATURE_ENGINEERING"],
            "dataIn": DATA_IN,
            "dataOut": DATA_OUT,
            "docs": DOCS,
            "hasNotebook": True,
            "image": IMAGE,
            "memoryLimit": "1Gi",
            "memoryRequest": "1Gi",
            "parameters": [],
            "readinessProbeInitialDelaySeconds": "300",
            "createdAt": CREATED_AT_ISO,
        }
        machine_generated = ["updatedAt"]
        for attr in machine_generated:
            self.assertIn(attr, result)
            del result[attr]
        self.assertDictEqual(expected, result)
        self.assertEqual(rv.status_code, 200)

    def test_delete_task(self):
        # task is none
        rv = TEST_CLIENT.delete("/tasks/unk")
        result = rv.json()
        expected = {"message": "The specified task does not exist"}
        self.assertDictEqual(expected, result)
        self.assertEqual(rv.status_code, 404)

        # task is related to an operator
        rv = TEST_CLIENT.delete(f"/tasks/{TASK_ID}")
        result = rv.json()
        expected = {"message": "Task related to an operator"}
        self.assertDictEqual(expected, result)
        self.assertEqual(rv.status_code, 403)

        # jupyter file is none
        rv = TEST_CLIENT.delete(f"/tasks/{TASK_ID_2}")
        result = rv.json()
        expected = {"message": "Task deleted"}
        self.assertDictEqual(expected, result)
        self.assertEqual(rv.status_code, 200)

    def test_send_email(self):

        # valid request
        rv = TEST_CLIENT.post(f"/tasks/{TASK_ID}/emails", json={
             "emails": EMAILS_TO_SEND
         })
        result = rv.json()
        expected = {"message": "email has been sent"}
        self.assertDictEqual(expected, result)
        self.assertEqual(rv.status_code, 200)

        # string is not an email
        rv = TEST_CLIENT.post(f"/tasks/{TASK_ID}/emails", json={
             "emails":["notEmailString",]
         })
        result = rv.json()
        self.assertEqual(rv.status_code, 422)

        # task does not exist
        rv = TEST_CLIENT.post(f"/tasks/foo/emails", json={
             "emails": EMAILS_TO_SEND
         })
        result = rv.json()
        expected = {"message": "The specified task does not exist"}
        self.assertDictEqual(expected, result)
        self.assertEqual(rv.status_code, 404)
