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
IMAGE = "platiagro/platiagro-experiment-image:0.2.0"
COMMANDS = ["CMD"]
COMMANDS_JSON = dumps(COMMANDS)
ARGUMENTS = ["ARG"]
ARGUMENTS_JSON = dumps(ARGUMENTS)
TAGS = ["PREDICTOR"]
TAGS_JSON = dumps(TAGS)
EXPERIMENT_NOTEBOOK_PATH = "Experiment.ipynb"
DEPLOYMENT_NOTEBOOK_PATH = "Deployment.ipynb"
IS_DEFAULT = False
PARAMETERS = [{"default": True, "name": "shuffle", "type": "boolean"}]
CREATED_AT = "2000-01-01 00:00:00"
CREATED_AT_ISO = "2000-01-01T00:00:00"
UPDATED_AT = "2000-01-01 00:00:00"
UPDATED_AT_ISO = "2000-01-01T00:00:00"
SAMPLE_NOTEBOOK = '{"cells":[{"cell_type":"code","execution_count":null,"metadata":{"tags":["parameters"]},"outputs":[],"source":["shuffle = True #@param {type: \\"boolean\\"}"]}],"metadata":{"kernelspec":{"display_name":"Python 3","language":"python","name":"python3"},"language_info":{"codemirror_mode":{"name":"ipython","version":3},"file_extension":".py","mimetype":"text/x-python","name":"python","nbconvert_exporter":"python","pygments_lexer":"ipython3","version":"3.6.9"}},"nbformat":4,"nbformat_minor":4}'

TASK_ID_2 = str(uuid_alpha())


class TestTasks(TestCase):
    def setUp(self):
        self.maxDiff = None
        conn = engine.connect()
        text = (
            f"INSERT INTO tasks (uuid, name, description, image, commands, arguments, tags, parameters, experiment_notebook_path, deployment_notebook_path, is_default, created_at, updated_at) "
            f"VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
        )
        conn.execute(text, (TASK_ID, NAME, DESCRIPTION, IMAGE, COMMANDS_JSON, ARGUMENTS_JSON, TAGS_JSON,
                            dumps([]), EXPERIMENT_NOTEBOOK_PATH, DEPLOYMENT_NOTEBOOK_PATH, 0, CREATED_AT, UPDATED_AT,))

        text = (
            f"INSERT INTO tasks (uuid, name, description, image, commands, arguments, tags, parameters, experiment_notebook_path, deployment_notebook_path, is_default, created_at, updated_at) "
            f"VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
        )
        conn.execute(text, (TASK_ID_2, 'foo 2', DESCRIPTION, IMAGE, COMMANDS_JSON, ARGUMENTS_JSON, TAGS_JSON,
                            dumps([]), EXPERIMENT_NOTEBOOK_PATH, DEPLOYMENT_NOTEBOOK_PATH, 0, CREATED_AT, UPDATED_AT,))
        conn.close()

        try:
            MINIO_CLIENT.make_bucket(BUCKET_NAME)
        except BucketAlreadyOwnedByYou:
            pass

        session = requests.Session()
        session.cookies.update(COOKIES)
        session.headers.update(HEADERS)
        session.hooks = {
            "response": lambda r, *args, **kwargs: r.raise_for_status(),
        }

        session.put(
            url=f"{JUPYTER_ENDPOINT}/api/contents/tasks",
            data=dumps({"type": "directory", "content": None}),
        )

        session.put(
            url=f"{JUPYTER_ENDPOINT}/api/contents/tasks/{NAME}",
            data=dumps({"type": "directory", "content": None}),
        )

        session.put(
            url=f"{JUPYTER_ENDPOINT}/api/contents/tasks/{NAME}/Deployment.ipynb",
            data=dumps({"type": "notebook", "content": loads(SAMPLE_NOTEBOOK)}),
        )

        session.put(
            url=f"{JUPYTER_ENDPOINT}/api/contents/tasks/{NAME}/Experiment.ipynb",
            data=dumps({"type": "notebook", "content": loads(SAMPLE_NOTEBOOK)}),
        )

    def tearDown(self):
        prefix = f"tasks/{NAME}"
        for obj in MINIO_CLIENT.list_objects(BUCKET_NAME, prefix=prefix, recursive=True):
            MINIO_CLIENT.remove_object(BUCKET_NAME, obj.object_name)

        session = requests.Session()
        session.cookies.update(COOKIES)
        session.headers.update(HEADERS)
        session.hooks = {
            "response": lambda r, *args, **kwargs: r.raise_for_status(),
        }

        r = session.get(
            url=f"{JUPYTER_ENDPOINT}/api/contents/tasks",
        )
        contents = r.json()["content"]
        for content in contents:
            session.delete(
                url=f"{JUPYTER_ENDPOINT}/api/contents/{content['path']}/Experiment.ipynb",
            )
            session.delete(
                url=f"{JUPYTER_ENDPOINT}/api/contents/{content['path']}/Deployment.ipynb",
            )
            session.delete(
                url=f"{JUPYTER_ENDPOINT}/api/contents/{content['path']}",
            )

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
        # when name is missing
        # should raise bad request
        rv = TEST_CLIENT.post("/tasks", json={})
        result = rv.json()
        self.assertEqual(rv.status_code, 400)
        expected = {"message": "name is required"}
        self.assertDictEqual(expected, result)

        # when invalid tag is sent
        # should raise bad request
        rv = TEST_CLIENT.post("/tasks", json={
            "name": "test",
            "description": "long test",
            "tags": ["UNK"],
            "copyFrom": TASK_ID,
        })
        result = rv.json()
        self.assertEqual(rv.status_code, 400)

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
        expected = {"message": "Source task does not exist"}
        self.assertDictEqual(expected, result)
        self.assertEqual(rv.status_code, 400)

        # when neither copyFrom nor experimentNotebook/deploymentNotebook are sent
        # should create a task using an empty template notebook
        rv = TEST_CLIENT.post("/tasks", json={
            "name": "test create a task using an empty template notebook",
            "description": "long test",
        })
        result = rv.json()
        expected = {
            "name": "test create a task using an empty template notebook",
            "description": "long test",
            "tags": ["DEFAULT"],
            "isDefault": IS_DEFAULT,
            "parameters": [
                {"default": "", "name": "dataset", "type": "string"},
            ],
        }
        # uuid, commands, experiment_notebook_path, deployment_notebook_path, created_at, updated_at
        # are machine-generated we assert they exist, but we don't assert their values
        machine_generated = [
            "uuid",
            "image",
            "commands",
            "arguments",
            "experimentNotebookPath",
            "deploymentNotebookPath",
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
            "tags": TAGS,
            "copyFrom": TASK_ID,
        })
        result = rv.json()
        expected = {
            "name": "test copy",
            "description": "long test",
            "tags": TAGS,
            "isDefault": IS_DEFAULT,
            "parameters": PARAMETERS,
        }
        machine_generated = [
            "uuid",
            "image",
            "commands",
            "arguments",
            "experimentNotebookPath",
            "deploymentNotebookPath",
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
            "name": "test",
            "description": "long test",
            "tags": TAGS,
            "experimentNotebook": loads(SAMPLE_NOTEBOOK),
            "deploymentNotebook": loads(SAMPLE_NOTEBOOK),
        })
        result = rv.json()
        expected = {
            "name": "test",
            "description": "long test",
            "tags": TAGS,
            "isDefault": IS_DEFAULT,
            "parameters": PARAMETERS,
        }
        machine_generated = [
            "uuid",
            "image",
            "commands",
            "arguments",
            "experimentNotebookPath",
            "deploymentNotebookPath",
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
            "tags": TAGS
        })
        result = rv.json()
        expected = {
            "name": "test tasks with image and command",
            "description": "long test",
            "image": IMAGE,
            "commands": COMMANDS,
            "arguments": ARGUMENTS,
            "tags": TAGS,
            "isDefault": IS_DEFAULT,
            "parameters": [
                {"default": "", "name": "dataset", "type": "string"},
            ],
        }
        machine_generated = [
            "uuid",
            "experimentNotebookPath",
            "deploymentNotebookPath",
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
            "tags": ["DATASETS"],
            "image": IMAGE,
        })
        result = rv.json()
        expected = {
            "name": "test fake dataset task",
            "description": None,
            "tags": ["DATASETS"],
            "isDefault": IS_DEFAULT,
            "parameters": [],
            "experimentNotebookPath": None,
            "deploymentNotebookPath": None,
            "image": IMAGE,
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

    def test_create_task_name_none(self):
        rv = TEST_CLIENT.post("/tasks", json={
            "description": "test without the name",
            "tags": TAGS,
            "copyFrom": TASK_ID,
        })
        result = rv.json()
        expected = {
            "description": "test without the name",
            "tags": TAGS,
            "isDefault": IS_DEFAULT,
            "parameters": PARAMETERS,
        }
        machine_generated = [
            "uuid",
            "image",
            "commands",
            "arguments",
            "experimentNotebookPath",
            "deploymentNotebookPath",
            "createdAt",
            "updatedAt",
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
            "image": IMAGE,
            "commands": COMMANDS,
            "arguments": ARGUMENTS,
            "tags": TAGS,
            "experimentNotebookPath": EXPERIMENT_NOTEBOOK_PATH,
            "deploymentNotebookPath": DEPLOYMENT_NOTEBOOK_PATH,
            "isDefault": IS_DEFAULT,
            "parameters": PARAMETERS,
            "createdAt": CREATED_AT_ISO,
            "updatedAt": UPDATED_AT_ISO,
        }
        self.assertDictEqual(expected, result)
        self.assertEqual(rv.status_code, 200)

    def test_update_task(self):
        # task none
        rv = TEST_CLIENT.patch("/tasks/foo", json={})
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
        self.assertEqual(rv.status_code, 400)

        # invalid key
        rv = TEST_CLIENT.patch(f"/tasks/{TASK_ID}", json={
            "unk": "bar",
        })
        result = rv.json()
        self.assertEqual(rv.status_code, 400)

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
            "image": IMAGE,
            "commands": COMMANDS,
            "arguments": ARGUMENTS,
            "tags": TAGS,
            "experimentNotebookPath": EXPERIMENT_NOTEBOOK_PATH,
            "deploymentNotebookPath": DEPLOYMENT_NOTEBOOK_PATH,
            "isDefault": IS_DEFAULT,
            "parameters": PARAMETERS,
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
            "image": IMAGE,
            "commands": COMMANDS,
            "arguments": ARGUMENTS,
            "tags": ["FEATURE_ENGINEERING"],
            "experimentNotebookPath": EXPERIMENT_NOTEBOOK_PATH,
            "deploymentNotebookPath": DEPLOYMENT_NOTEBOOK_PATH,
            "isDefault": IS_DEFAULT,
            "parameters": PARAMETERS,
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
            "image": IMAGE,
            "commands": COMMANDS,
            "arguments": ARGUMENTS,
            "tags": ["FEATURE_ENGINEERING"],
            "experimentNotebookPath": EXPERIMENT_NOTEBOOK_PATH,
            "deploymentNotebookPath": DEPLOYMENT_NOTEBOOK_PATH,
            "isDefault": IS_DEFAULT,
            "parameters": PARAMETERS,
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
            "image": IMAGE,
            "commands": COMMANDS,
            "arguments": ARGUMENTS,
            "tags": ["FEATURE_ENGINEERING"],
            "experimentNotebookPath": EXPERIMENT_NOTEBOOK_PATH,
            "deploymentNotebookPath": DEPLOYMENT_NOTEBOOK_PATH,
            "isDefault": IS_DEFAULT,
            "parameters": PARAMETERS,
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

        # jupyter file is not none
        rv = TEST_CLIENT.delete(f"/tasks/{TASK_ID}")
        result = rv.json()
        expected = {"message": "Task deleted"}
        self.assertDictEqual(expected, result)
        self.assertEqual(rv.status_code, 200)

        # jupyter file is none
        rv = TEST_CLIENT.delete(f"/tasks/{TASK_ID_2}")
        result = rv.json()
        expected = {"message": "Task deleted"}
        self.assertDictEqual(expected, result)
        self.assertEqual(rv.status_code, 200)
