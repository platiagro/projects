# -*- coding: utf-8 -*-
from io import BytesIO
from json import dumps, loads
from unittest import TestCase

import requests
from minio.error import BucketAlreadyOwnedByYou

from projects.api.main import app
from projects.controllers.tasks import get_tasks_by_tag
from projects.controllers.utils import uuid_alpha
from projects.database import engine
from projects.jupyter import JUPYTER_ENDPOINT, COOKIES, HEADERS
from projects.object_storage import BUCKET_NAME, MINIO_CLIENT

TASK_ID = str(uuid_alpha())
NAME = "foo"
DESCRIPTION = "long foo"
COMMANDS = ["CMD"]
COMMANDS_JSON = dumps(COMMANDS)
IMAGE = "platiagro/platiagro-notebook-image-test:0.1.0"
TAGS = ["PREDICTOR"]
TAGS_JSON = dumps(TAGS)
EXPERIMENT_NOTEBOOK_PATH = f"minio://{BUCKET_NAME}/tasks/{TASK_ID}/Experiment.ipynb"
DEPLOYMENT_NOTEBOOK_PATH = f"minio://{BUCKET_NAME}/tasks/{TASK_ID}/Deployment.ipynb"
IS_DEFAULT = False
PARAMETERS = [{"default": True, "name": "shuffle", "type": "boolean"}]
CREATED_AT = "2000-01-01 00:00:00"
CREATED_AT_ISO = "2000-01-01T00:00:00"
UPDATED_AT = "2000-01-01 00:00:00"
UPDATED_AT_ISO = "2000-01-01T00:00:00"
SAMPLE_NOTEBOOK = '{"cells":[{"cell_type":"code","execution_count":null,"metadata":{"tags":["parameters"]},"outputs":[],"source":["shuffle = True #@param {type: \\"boolean\\"}"]}],"metadata":{"kernelspec":{"display_name":"Python 3","language":"python","name":"python3"},"language_info":{"codemirror_mode":{"name":"ipython","version":3},"file_extension":".py","mimetype":"text/x-python","name":"python","nbconvert_exporter":"python","pygments_lexer":"ipython3","version":"3.6.9"}},"nbformat":4,"nbformat_minor":4}'

TASK_ID_2 = str(uuid_alpha())
EXPERIMENT_NOTEBOOK_PATH_2 = f"minio://{BUCKET_NAME}/tasks/{TASK_ID_2}/Experiment.ipynb"
DEPLOYMENT_NOTEBOOK_PATH_2 = f"minio://{BUCKET_NAME}/tasks/{TASK_ID_2}/Deployment.ipynb"


class TestTasks(TestCase):
    def setUp(self):
        self.maxDiff = None
        conn = engine.connect()
        text = (
            f"INSERT INTO tasks (uuid, name, description, commands, image, tags, experiment_notebook_path, deployment_notebook_path, is_default, created_at, updated_at) "
            f"VALUES ('{TASK_ID}', '{NAME}', '{DESCRIPTION}', '{COMMANDS_JSON}', '{IMAGE}', '{TAGS_JSON}', '{EXPERIMENT_NOTEBOOK_PATH}', '{DEPLOYMENT_NOTEBOOK_PATH}', 0, '{CREATED_AT}', '{UPDATED_AT}')"
        )
        conn.execute(text)
        text = (
            f"INSERT INTO tasks (uuid, name, description, commands, image, tags, experiment_notebook_path, deployment_notebook_path, is_default, created_at, updated_at) "
            f"VALUES ('{TASK_ID_2}', 'foo 2', '{DESCRIPTION}', '{COMMANDS_JSON}', '{IMAGE}', '{TAGS_JSON}', '{EXPERIMENT_NOTEBOOK_PATH_2}', '{DEPLOYMENT_NOTEBOOK_PATH_2}', 0, '{CREATED_AT}', '{UPDATED_AT}')"
        )
        conn.execute(text)
        conn.close()

        try:
            MINIO_CLIENT.make_bucket(BUCKET_NAME)
        except BucketAlreadyOwnedByYou:
            pass

        file = BytesIO(SAMPLE_NOTEBOOK.encode("utf-8"))
        MINIO_CLIENT.put_object(
            bucket_name=BUCKET_NAME,
            object_name=EXPERIMENT_NOTEBOOK_PATH[len(f"minio://{BUCKET_NAME}/"):],
            data=file,
            length=file.getbuffer().nbytes,
        )

        file = BytesIO(b'{"cells":[{"cell_type":"code","execution_count":null,"metadata":{},"outputs":[],"source":[]}],"metadata":{"kernelspec":{"display_name":"Python 3","language":"python","name":"python3"},"language_info":{"codemirror_mode":{"name":"ipython","version":3},"file_extension":".py","mimetype":"text/x-python","name":"python","nbconvert_exporter":"python","pygments_lexer":"ipython3","version":"3.6.9"}},"nbformat":4,"nbformat_minor":4}')
        MINIO_CLIENT.put_object(
            bucket_name=BUCKET_NAME,
            object_name=DEPLOYMENT_NOTEBOOK_PATH[len(f"minio://{BUCKET_NAME}/"):],
            data=file,
            length=file.getbuffer().nbytes,
        )

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
            url=f"{JUPYTER_ENDPOINT}/api/contents/tasks/{TASK_ID}",
            data=dumps({"type": "directory", "content": None}),
        )

        session.put(
            url=f"{JUPYTER_ENDPOINT}/api/contents/tasks/{TASK_ID}/Deployment.ipynb",
            data=dumps({"type": "notebook", "content": loads(SAMPLE_NOTEBOOK)}),
        )

        session.put(
            url=f"{JUPYTER_ENDPOINT}/api/contents/tasks/{TASK_ID}/Experiment.ipynb",
            data=dumps({"type": "notebook", "content": loads(SAMPLE_NOTEBOOK)}),
        )

    def tearDown(self):
        prefix = f"tasks/{TASK_ID}"
        for obj in MINIO_CLIENT.list_objects(BUCKET_NAME, prefix=prefix, recursive=True):
            MINIO_CLIENT.remove_object(BUCKET_NAME, obj.object_name)

        conn = engine.connect()
        text = f"DELETE FROM tasks WHERE 1 = 1"
        conn.execute(text)
        conn.close()

    def test_list_tasks(self):
        with app.test_client() as c:
            rv = c.get("/tasks")
            result = rv.get_json()
            self.assertIsInstance(result["tasks"], list)
            self.assertIsInstance(result["total"], int)

            rv = c.get("/tasks?order=uuid asc")
            result = rv.get_json()
            self.assertIsInstance(result["tasks"], list)
            self.assertIsInstance(result["total"], int)

            rv = c.get("/tasks?page=1&order=uuid asc")
            result = rv.get_json()
            self.assertIsInstance(result["tasks"], list)
            self.assertIsInstance(result["total"], int)

            rv = c.get(f"/tasks?name={NAME}&page=1&order=uuid asc")
            result = rv.get_json()
            self.assertIsInstance(result["tasks"], list)
            self.assertIsInstance(result["total"], int)

            rv = c.get(f"/tasks?name={NAME}&page=1&page_size=10&order=name desc")
            result = rv.get_json()
            self.assertIsInstance(result["tasks"], list)
            self.assertIsInstance(result["total"], int)

    def test_create_task(self):
        with app.test_client() as c:
            # when name is missing
            # should raise bad request
            rv = c.post("/tasks", json={})
            result = rv.get_json()
            expected = {"message": "name is required"}
            self.assertDictEqual(expected, result)
            self.assertEqual(rv.status_code, 400)

            # when invalid tag is sent
            # should raise bad request
            rv = c.post("/tasks", json={
                "name": "test",
                "description": "long test",
                "tags": ["UNK"],
                "copyFrom": TASK_ID,
            })
            result = rv.get_json()
            self.assertEqual(rv.status_code, 400)

            # task name already exists
            rv = c.post("/tasks", json={
                "name": "foo",
            })
            result = rv.get_json()
            expected = {"message": "a task with that name already exists"}
            self.assertDictEqual(expected, result)
            self.assertEqual(rv.status_code, 400)

            # when copyFrom and experimentNotebook/deploymentNotebook are sent
            # should raise bad request
            rv = c.post("/tasks", json={
                "name": "test",
                "description": "long test",
                "tags": TAGS,
                "copyFrom": TASK_ID,
                "experimentNotebook": loads(SAMPLE_NOTEBOOK),
                "deploymentNotebook": loads(SAMPLE_NOTEBOOK),
            })
            result = rv.get_json()
            expected = {"message": "Either provide notebooks or a task to copy from"}
            self.assertDictEqual(expected, result)
            self.assertEqual(rv.status_code, 400)

            # when copyFrom uuid does not exist
            # should raise bad request
            rv = c.post("/tasks", json={
                "name": "test copyFrom uuid does not exist ",
                "description": "long test",
                "tags": TAGS,
                "copyFrom": "unk",
            })
            result = rv.get_json()
            expected = {"message": "Source task does not exist"}
            self.assertDictEqual(expected, result)
            self.assertEqual(rv.status_code, 400)

            # when neither copyFrom nor experimentNotebook/deploymentNotebook are sent
            # should create a task using an empty template notebook
            rv = c.post("/tasks", json={
                "name": "test create a task using an empty template notebook",
                "description": "long test",
            })
            result = rv.get_json()
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
                "commands",
                "image",
                "experimentNotebookPath",
                "deploymentNotebookPath",
                "createdAt",
                "updatedAt",
            ]
            for attr in machine_generated:
                self.assertIn(attr, result)
                del result[attr]
            self.assertDictEqual(expected, result)

            # when copyFrom is sent
            # should create a task copying notebooks from copyFrom
            rv = c.post("/tasks", json={
                "name": "test copy",
                "description": "long test",
                "tags": TAGS,
                "copyFrom": TASK_ID,
            })
            result = rv.get_json()
            expected = {
                "name": "test copy",
                "description": "long test",
                "tags": TAGS,
                "isDefault": IS_DEFAULT,
                "parameters": PARAMETERS,
            }
            machine_generated = [
                "uuid",
                "commands",
                "image",
                "experimentNotebookPath",
                "deploymentNotebookPath",
                "createdAt",
                "updatedAt",
            ]
            for attr in machine_generated:
                self.assertIn(attr, result)
                del result[attr]
            self.assertDictEqual(expected, result)

            # when experimentNotebook and deploymentNotebook are sent
            # should create a task using their values as source
            rv = c.post("/tasks", json={
                "name": "test",
                "description": "long test",
                "tags": TAGS,
                "experimentNotebook": loads(SAMPLE_NOTEBOOK),
                "deploymentNotebook": loads(SAMPLE_NOTEBOOK),
            })
            result = rv.get_json()
            expected = {
                "name": "test",
                "description": "long test",
                "tags": TAGS,
                "isDefault": IS_DEFAULT,
                "parameters": PARAMETERS,
            }
            machine_generated = [
                "uuid",
                "commands",
                "image",
                "experimentNotebookPath",
                "deploymentNotebookPath",
                "createdAt",
                "updatedAt",
            ]
            for attr in machine_generated:
                self.assertIn(attr, result)
                del result[attr]
            self.assertDictEqual(expected, result)

            # when image and commands are sent
            # should create a task using their values as source
            rv = c.post("/tasks", json={
                "name": "test tasks with image and command",
                "description": "long test",
                "commands": COMMANDS,
                "image": IMAGE,
                "tags": TAGS
            })
            result = rv.get_json()
            expected = {
                "name": "test tasks with image and command",
                "description": "long test",
                "commands": COMMANDS,
                "image": IMAGE,
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

            # when image is invalid should receive bad request
            rv = c.post("/tasks", json={
                "name": "test invalid image name",
                "image": "invalid name",
            })
            result = rv.get_json()
            expected = {"message": "invalid docker image name"}
            self.assertDictEqual(expected, result)
            self.assertEqual(rv.status_code, 400)

    def test_get_task(self):
        with app.test_client() as c:
            rv = c.get("/tasks/foo")
            result = rv.get_json()
            expected = {"message": "The specified task does not exist"}
            self.assertDictEqual(expected, result)
            self.assertEqual(rv.status_code, 404)

            rv = c.get(f"/tasks/{TASK_ID}")
            result = rv.get_json()
            expected = {
                "uuid": TASK_ID,
                "name": "foo",
                "description": DESCRIPTION,
                "commands": COMMANDS,
                "image": IMAGE,
                "tags": TAGS,
                "experimentNotebookPath": EXPERIMENT_NOTEBOOK_PATH,
                "deploymentNotebookPath": DEPLOYMENT_NOTEBOOK_PATH,
                "isDefault": IS_DEFAULT,
                "parameters": PARAMETERS,
                "createdAt": CREATED_AT_ISO,
                "updatedAt": UPDATED_AT_ISO,
            }
            self.assertDictEqual(expected, result)

    def test_update_task(self):
        with app.test_client() as c:
            # task none
            rv = c.patch("/tasks/foo", json={})
            result = rv.get_json()
            expected = {"message": "The specified task does not exist"}
            self.assertDictEqual(expected, result)
            self.assertEqual(rv.status_code, 404)

            # task name already exists
            rv = c.patch(f"/tasks/{TASK_ID}", json={
                "name": "foo 2",
            })
            result = rv.get_json()
            expected = {"message": "a task with that name already exists"}
            self.assertDictEqual(expected, result)
            self.assertEqual(rv.status_code, 400)

            # invalid tags
            rv = c.patch(f"/tasks/{TASK_ID}", json={
                "tags": ["UNK"],
            })
            result = rv.get_json()
            self.assertEqual(rv.status_code, 400)

            # invalid key
            rv = c.patch(f"/tasks/{TASK_ID}", json={
                "unk": "bar",
            })
            result = rv.get_json()
            self.assertEqual(rv.status_code, 400)

            # update task using the same name
            rv = c.patch(f"/tasks/{TASK_ID}", json={
                "name": "foo",
            })
            result = rv.get_json()
            self.assertEqual(rv.status_code, 200)

            # update task name
            rv = c.patch(f"/tasks/{TASK_ID}", json={
                "name": "bar",
            })
            result = rv.get_json()
            expected = {
                "uuid": TASK_ID,
                "name": "bar",
                "description": DESCRIPTION,
                "commands": COMMANDS,
                "image": IMAGE,
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

            # update task tags
            rv = c.patch(f"/tasks/{TASK_ID}", json={
                "tags": ["FEATURE_ENGINEERING"],
            })
            result = rv.get_json()
            expected = {
                "uuid": TASK_ID,
                "name": "bar",
                "description": DESCRIPTION,
                "commands": COMMANDS,
                "image": IMAGE,
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

            # update task experiment notebook
            rv = c.patch(f"/tasks/{TASK_ID}", json={
                "experimentNotebook": loads(SAMPLE_NOTEBOOK),
            })
            result = rv.get_json()
            expected = {
                "uuid": TASK_ID,
                "name": "bar",
                "description": DESCRIPTION,
                "commands": COMMANDS,
                "image": IMAGE,
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

            # update task deployment notebook
            rv = c.patch(f"/tasks/{TASK_ID}", json={
                "deploymentNotebook": loads(SAMPLE_NOTEBOOK),
            })
            result = rv.get_json()
            expected = {
                "uuid": TASK_ID,
                "name": "bar",
                "description": DESCRIPTION,
                "commands": COMMANDS,
                "image": IMAGE,
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

    def test_delete_task(self):
        with app.test_client() as c:
            # task is none
            rv = c.delete("/tasks/unk")
            result = rv.get_json()
            expected = {"message": "The specified task does not exist"}
            self.assertDictEqual(expected, result)
            self.assertEqual(rv.status_code, 404)

            # jupyter file is not none
            rv = c.delete(f"/tasks/{TASK_ID}")
            result = rv.get_json()
            expected = {"message": "Task deleted"}
            self.assertDictEqual(expected, result)

            # jupyter file is none
            rv = c.delete(f"/tasks/{TASK_ID_2}")
            result = rv.get_json()
            expected = {"message": "Task deleted"}
            self.assertDictEqual(expected, result)

    def test_get_tasks_by_tag(self):
        task = get_tasks_by_tag("PREDICTOR")
        self.assertIsInstance(task, list)
