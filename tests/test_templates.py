# -*- coding: utf-8 -*-
from json import dumps
from unittest import TestCase

from projects.api.main import app
from projects.controllers.utils import uuid_alpha
from projects.database import engine
from projects.object_storage import BUCKET_NAME

TEMPLATE_ID = str(uuid_alpha())
NAME = "foo"
TASK_ID = str(uuid_alpha())
PROJECT_ID = str(uuid_alpha())
EXPERIMENT_ID = str(uuid_alpha())
OPERATOR_ID = str(uuid_alpha())
POSITION = 0
PARAMETERS = {"coef": 0.1}
OPERATORS = [{"taskId": TASK_ID}]
DESCRIPTION = "long foo"
IMAGE = "platiagro/platiagro-notebook-image-test:0.2.0"
COMMANDS = ["CMD"]
COMMANDS_JSON = dumps(COMMANDS)
ARGUMENTS = ["ARG"]
ARGUMENTS_JSON = dumps(ARGUMENTS)
TAGS = ["PREDICTOR"]
TAGS_JSON = dumps(TAGS)
TASKS_JSON = dumps([TASK_ID])
PARAMETERS_JSON = dumps(PARAMETERS)
EXPERIMENT_NOTEBOOK_PATH = f"minio://{BUCKET_NAME}/tasks/{TASK_ID}/Experiment.ipynb"
DEPLOYMENT_NOTEBOOK_PATH = f"minio://{BUCKET_NAME}/tasks/{TASK_ID}/Deployment.ipynb"
CREATED_AT = "2000-01-01 00:00:00"
CREATED_AT_ISO = "2000-01-01T00:00:00"
UPDATED_AT = "2000-01-01 00:00:00"
UPDATED_AT_ISO = "2000-01-01T00:00:00"


class TestTemplates(TestCase):
    def setUp(self):
        self.maxDiff = None
        conn = engine.connect()
        text = (
            f"INSERT INTO tasks (uuid, name, description, image, commands, arguments, tags, experiment_notebook_path, deployment_notebook_path, is_default, created_at, updated_at) "
            f"VALUES ('{TASK_ID}', '{NAME}', '{DESCRIPTION}', '{IMAGE}', '{COMMANDS_JSON}', '{ARGUMENTS_JSON}', '{TAGS_JSON}', '{EXPERIMENT_NOTEBOOK_PATH}', '{DEPLOYMENT_NOTEBOOK_PATH}', 0, '{CREATED_AT}', '{UPDATED_AT}')"
        )
        conn.execute(text)

        text = (
            f"INSERT INTO projects (uuid, name, created_at, updated_at) "
            f"VALUES ('{PROJECT_ID}', '{NAME}', '{CREATED_AT}', '{UPDATED_AT}')"
        )
        conn.execute(text)

        text = (
            f"INSERT INTO experiments (uuid, name, project_id, position, is_active, created_at, updated_at) VALUES "
            f"('{EXPERIMENT_ID}', '{NAME}', '{PROJECT_ID}', '{POSITION}', 1, '{CREATED_AT}', '{UPDATED_AT}')"
        )
        conn.execute(text)

        text = (
            f"INSERT INTO operators (uuid, experiment_id, task_id, parameters, created_at, updated_at) "
            f"VALUES ('{OPERATOR_ID}', '{EXPERIMENT_ID}', '{TASK_ID}', '{PARAMETERS_JSON}', '{CREATED_AT}', '{UPDATED_AT}')"
        )
        conn.execute(text)

        text = f"INSERT INTO templates (uuid, name, tasks, created_at, updated_at) VALUES ('{TEMPLATE_ID}', '{NAME}', '{TASKS_JSON}', '{CREATED_AT}', '{UPDATED_AT}')"
        conn.execute(text)
        conn.close()

    def tearDown(self):
        conn = engine.connect()
        text = f"DELETE FROM templates WHERE uuid = '{TEMPLATE_ID}'"
        conn.execute(text)

        text = f"DELETE FROM operators WHERE experiment_id = '{EXPERIMENT_ID}'"
        conn.execute(text)

        text = f"DELETE FROM experiments WHERE project_id = '{PROJECT_ID}'"
        conn.execute(text)

        text = f"DELETE FROM projects WHERE uuid = '{PROJECT_ID}'"
        conn.execute(text)

        text = f"DELETE FROM tasks WHERE uuid = '{TASK_ID}'"
        conn.execute(text)
        conn.close()

    def test_list_templates(self):
        with app.test_client() as c:
            rv = c.get("/templates")
            result = rv.get_json()
            self.assertIsInstance(result, list)

    def test_create_template(self):
        with app.test_client() as c:
            rv = c.post("/templates", json={})
            result = rv.get_json()
            expected = {"message": "name is required"}
            self.assertDictEqual(expected, result)
            self.assertEqual(rv.status_code, 400)

            rv = c.post("/templates", json={
                "name": "foo",
            })
            result = rv.get_json()
            expected = {"message": "experimentId is required"}
            self.assertDictEqual(expected, result)
            self.assertEqual(rv.status_code, 400)

            rv = c.post("/templates", json={
                "name": "foo",
                "experimentId": "UNK",
            })
            result = rv.get_json()
            expected = {"message": "The specified experiment does not exist"}
            self.assertDictEqual(expected, result)
            self.assertEqual(rv.status_code, 400)

            rv = c.post("/templates", json={
                "name": "foo",
                "experimentId": EXPERIMENT_ID,
            })
            result = rv.get_json()
            expected = {
                "name": "foo",
                "operators": OPERATORS,
            }
            # uuid, created_at, updated_at are machine-generated
            # we assert they exist, but we don't assert their values
            machine_generated = ["uuid", "createdAt", "updatedAt"]
            for attr in machine_generated:
                self.assertIn(attr, result)
                del result[attr]
            self.assertDictEqual(expected, result)

    def test_get_template(self):
        with app.test_client() as c:
            rv = c.get("/templates/foo")
            result = rv.get_json()
            expected = {"message": "The specified template does not exist"}
            self.assertDictEqual(expected, result)
            self.assertEqual(rv.status_code, 404)

            rv = c.get(f"/templates/{TEMPLATE_ID}")
            result = rv.get_json()
            expected = {
                "uuid": TEMPLATE_ID,
                "name": NAME,
                "operators": OPERATORS,
                "createdAt": CREATED_AT_ISO,
                "updatedAt": UPDATED_AT_ISO,
            }
            self.assertDictEqual(expected, result)

    def test_update_template(self):
        with app.test_client() as c:
            rv = c.patch("/templates/foo", json={})
            result = rv.get_json()
            expected = {"message": "The specified template does not exist"}
            self.assertDictEqual(expected, result)
            self.assertEqual(rv.status_code, 404)

            rv = c.patch(f"/templates/{TEMPLATE_ID}", json={
                "unk": "bar",
            })
            result = rv.get_json()
            self.assertEqual(rv.status_code, 400)

            rv = c.patch(f"/templates/{TEMPLATE_ID}", json={
                "name": "bar",
            })
            result = rv.get_json()
            expected = {
                "uuid": TEMPLATE_ID,
                "name": "bar",
                "operators": OPERATORS,
                "createdAt": CREATED_AT_ISO,
            }
            machine_generated = ["updatedAt"]
            for attr in machine_generated:
                self.assertIn(attr, result)
                del result[attr]
            self.assertDictEqual(expected, result)

    def test_delete_template(self):
        with app.test_client() as c:
            rv = c.delete("/templates/unk")
            result = rv.get_json()
            expected = {"message": "The specified template does not exist"}
            self.assertDictEqual(expected, result)
            self.assertEqual(rv.status_code, 404)

            rv = c.delete(f"/templates/{TEMPLATE_ID}")
            result = rv.get_json()
            expected = {"message": "Template deleted"}
            self.assertDictEqual(expected, result)
