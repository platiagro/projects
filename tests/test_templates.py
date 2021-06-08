# -*- coding: utf-8 -*-
from json import dumps
from unittest import TestCase

from fastapi.testclient import TestClient

from projects.api.main import app
from projects.controllers.utils import uuid_alpha
from projects.database import engine

TEST_CLIENT = TestClient(app)

EXPERIMENT_ID = str(uuid_alpha())
DEPLOYMENT_ID = str(uuid_alpha())
OPERATOR_ID = str(uuid_alpha())
OPERATOR_ID_2 = str(uuid_alpha())
PROJECT_ID = str(uuid_alpha())
TASK_ID = str(uuid_alpha())
TASK_ID_2 = str(uuid_alpha())
TEMPLATE_ID = str(uuid_alpha())
NAME = "foo"
PARAMETERS = {"coef": 0.1}
OPERATORS = [{"taskId": TASK_ID}]
DESCRIPTION = "long foo"
IMAGE = "platiagro/platiagro-experiment-image:0.2.0"
TAGS = ["PREDICTOR"]
TAGS_JSON = dumps(TAGS)
TASKS_JSON = dumps([TASK_ID])
PARAMETERS_JSON = dumps(PARAMETERS)
POSITION_X = 0.3
POSITION_Y = 0.5
STATUS = "Pending"
URL = None
TASKS = [
    {
        "dependencies": [],
        "position_x": 0.0,
        "position_y": 0.0,
        "task_id": TASK_ID,
        "uuid": OPERATOR_ID,
    },
    {
        "dependencies": [OPERATOR_ID],
        "position_x": 200.0,
        "position_y": 0.0,
        "task_id": TASK_ID_2,
        "uuid": OPERATOR_ID_2,
    },
]
TASKS_JSON = dumps([
    {
        "uuid": OPERATOR_ID,
        "position_x": 0.0,
        "position_y": 0.0,
        "task_id": TASK_ID,
        "dependencies": []
    },
    {
        "uuid": OPERATOR_ID_2,
        "position_x": 200.0,
        "position_y": 0.0,
        "task_id": TASK_ID_2,
        "dependencies": [OPERATOR_ID]
    },
])
CREATED_AT = "2000-01-01 00:00:00"
CREATED_AT_ISO = "2000-01-01T00:00:00"
UPDATED_AT = "2000-01-01 00:00:00"
UPDATED_AT_ISO = "2000-01-01T00:00:00"

DEPENDENCIES_EMPTY = []
DEPENDENCIES_EMPTY_JSON = dumps(DEPENDENCIES_EMPTY)


class TestTemplates(TestCase):
    def setUp(self):
        self.maxDiff = None
        conn = engine.connect()
        text = (
            f"INSERT INTO tasks (uuid, name, description, image, commands, arguments, tags, parameters, "
            f"experiment_notebook_path, deployment_notebook_path, cpu_limit, cpu_request, memory_limit, memory_request, "
            f"readiness_probe_initial_delay_seconds, is_default, created_at, updated_at) "
            f"VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
        )
        conn.execute(text, (TASK_ID, "name", "desc", "image", None, None, dumps(["TAGS"]), dumps([]),
                            "experiment_path", "deploy_path", "100m", "100m", "1Gi", "1Gi", 30, 0, CREATED_AT, UPDATED_AT,))

        text = (
            f"INSERT INTO tasks (uuid, name, description, image, commands, arguments, tags, parameters, "
            f"experiment_notebook_path, deployment_notebook_path, cpu_limit, cpu_request, memory_limit, memory_request, "
            f"readiness_probe_initial_delay_seconds, is_default, created_at, updated_at) "
            f"VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
        )
        conn.execute(text, (TASK_ID_2, "name", "desc", "image", None, None, dumps(["TAGS"]), dumps([]),
                            "experiment_path", "deploy_path", "100m", "100m", "1Gi", "1Gi", 30, 0, CREATED_AT, UPDATED_AT,))

        text = (
            f"INSERT INTO projects (uuid, name, created_at, updated_at) "
            f"VALUES (%s, %s, %s, %s)"
        )
        conn.execute(text, (PROJECT_ID, NAME, CREATED_AT, UPDATED_AT,))

        text = (
            f"INSERT INTO experiments (uuid, name, project_id, position, is_active, created_at, updated_at) VALUES "
            f"(%s, %s, %s, %s, %s, %s, %s)"
        )
        conn.execute(text, (EXPERIMENT_ID, NAME, PROJECT_ID, 0, 1, CREATED_AT, UPDATED_AT,))

        text = (
            f"INSERT INTO deployments (uuid, name, project_id, experiment_id, position, is_active, status, url, created_at, updated_at) "
            f"VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
        )
        conn.execute(text, (DEPLOYMENT_ID, NAME, PROJECT_ID, EXPERIMENT_ID, 0, 1, STATUS, URL, CREATED_AT, UPDATED_AT,))

        text = (
            f"INSERT INTO operators (uuid, name, status, status_message, experiment_id, task_id, parameters, position_x, position_y, dependencies, created_at, updated_at) "
            f"VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
        )
        conn.execute(text, (OPERATOR_ID, None, "Unset", None, EXPERIMENT_ID, TASK_ID, PARAMETERS_JSON, POSITION_X,
                            POSITION_Y, DEPENDENCIES_EMPTY_JSON, '2000-01-02 00:00:00', UPDATED_AT,))

        text = (
            f"INSERT INTO operators (uuid, name, status, status_message, deployment_id, task_id, parameters, position_x, position_y, dependencies, created_at, updated_at) "
            f"VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
        )
        conn.execute(text, (OPERATOR_ID_2, None, "Unset", None, DEPLOYMENT_ID, TASK_ID, PARAMETERS_JSON,
                            POSITION_X, POSITION_Y, DEPENDENCIES_EMPTY_JSON, CREATED_AT, UPDATED_AT,))

        text = (
            f"INSERT INTO templates (uuid, name, tasks, created_at, updated_at) "
            f"VALUES (%s, %s, %s, %s, %s)"
        )
        conn.execute(text, (TEMPLATE_ID, NAME, TASKS_JSON, CREATED_AT, UPDATED_AT,))
        conn.close()

    def tearDown(self):
        conn = engine.connect()
        text = f"DELETE FROM templates WHERE uuid = '{TEMPLATE_ID}'"
        conn.execute(text)

        conn = engine.connect()
        text = f"DELETE FROM templates WHERE name IN ('foo bar', 'foo bar foo', 'foo bar foo bar')"
        conn.execute(text)

        text = f"DELETE FROM operators WHERE deployment_id = '{DEPLOYMENT_ID}'"
        conn.execute(text)

        text = f"DELETE FROM operators WHERE experiment_id = '{EXPERIMENT_ID}'"
        conn.execute(text)

        text = f"DELETE FROM deployments WHERE project_id = '{PROJECT_ID}'"
        conn.execute(text)

        text = f"DELETE FROM experiments WHERE project_id = '{PROJECT_ID}'"
        conn.execute(text)

        text = f"DELETE FROM projects WHERE uuid = '{PROJECT_ID}'"
        conn.execute(text)

        text = f"DELETE FROM tasks WHERE uuid = '{TASK_ID_2}'"
        conn.execute(text)

        text = f"DELETE FROM tasks WHERE uuid = '{TASK_ID}'"
        conn.execute(text)
        conn.close()

    def test_list_templates(self):
        rv = TEST_CLIENT.get("/templates")
        result = rv.json()
        self.assertIsInstance(result["templates"], list)
        self.assertIsInstance(result["total"], int)
        self.assertEqual(rv.status_code, 200)

    def test_create_template(self):
        rv = TEST_CLIENT.post("/templates", json={})
        result = rv.json()
        self.assertEqual(rv.status_code, 422)

        rv = TEST_CLIENT.post("/templates", json={
            "name": "foo",
        })
        result = rv.json()
        expected = {"message": "experimentId or deploymentId needed to create template."}
        self.assertDictEqual(expected, result)
        self.assertEqual(rv.status_code, 400)

        rv = TEST_CLIENT.post("/templates", json={
            "name": "foo",
            "experimentId": "UNK",
        })
        result = rv.json()
        expected = {"message": "The specified experiment does not exist"}
        self.assertDictEqual(expected, result)
        self.assertEqual(rv.status_code, 400)

        rv = TEST_CLIENT.post("/templates", json={
            "name": "foo bar",
            "experimentId": EXPERIMENT_ID,
        })
        result = rv.json()
        expected = {
            "name": "foo bar",
            "tasks": [
                {
                    "dependencies": [],
                    "position_x": POSITION_X,
                    "position_y": POSITION_Y,
                    "task_id": TASK_ID,
                    "uuid": OPERATOR_ID
                }
            ],
        }
        # uuid, created_at, updated_at are machine-generated
        # we assert they exist, but we don't assert their values
        machine_generated = ["uuid", "createdAt", "updatedAt"]
        for attr in machine_generated:
            self.assertIn(attr, result)
            del result[attr]
        self.assertDictEqual(expected, result)

        rv = TEST_CLIENT.post("/templates", json={
            "name": "foo bar foo",
            "deploymentId": "UNK",
        })
        result = rv.json()
        expected = {"message": "The specified deployment does not exist"}
        self.assertDictEqual(expected, result)
        self.assertEqual(rv.status_code, 400)

        rv = TEST_CLIENT.post("/templates", json={
            "name": "foo bar foo bar",
            "deploymentId": DEPLOYMENT_ID,
        })
        result = rv.json()
        expected = {
            "name": "foo bar foo bar",
            "tasks": [
                {
                    "dependencies": [],
                    "position_x": POSITION_X,
                    "position_y": POSITION_Y,
                    "task_id": TASK_ID,
                    "uuid": OPERATOR_ID_2
                }
            ],
        }

        # uuid, created_at, updated_at are machine-generated
        # we assert they exist, but we don't assert their values
        machine_generated = ["uuid", "createdAt", "updatedAt"]
        for attr in machine_generated:
            self.assertIn(attr, result)
            del result[attr]
        self.assertDictEqual(expected, result)

    def test_get_template(self):
        rv = TEST_CLIENT.get("/templates/foo")
        result = rv.json()
        expected = {"message": "The specified template does not exist"}
        self.assertDictEqual(expected, result)
        self.assertEqual(rv.status_code, 404)

        rv = TEST_CLIENT.get(f"/templates/{TEMPLATE_ID}")
        result = rv.json()
        expected = {
            "uuid": TEMPLATE_ID,
            "name": NAME,
            "tasks": TASKS,
            "createdAt": CREATED_AT_ISO,
            "updatedAt": UPDATED_AT_ISO,
        }
        self.assertDictEqual(expected, result)

    def test_update_template(self):
        rv = TEST_CLIENT.patch("/templates/foo", json={})
        result = rv.json()
        expected = {"message": "The specified template does not exist"}
        self.assertDictEqual(expected, result)
        self.assertEqual(rv.status_code, 404)

        rv = TEST_CLIENT.patch(f"/templates/{TEMPLATE_ID}", json={
            "name": "bar",
        })
        result = rv.json()
        expected = {
            "uuid": TEMPLATE_ID,
            "name": "bar",
            "tasks": TASKS,
            "createdAt": CREATED_AT_ISO,
        }
        machine_generated = ["updatedAt"]
        for attr in machine_generated:
            self.assertIn(attr, result)
            del result[attr]
        self.assertDictEqual(expected, result)

    def test_delete_template(self):
        rv = TEST_CLIENT.delete("/templates/unk")
        result = rv.json()
        expected = {"message": "The specified template does not exist"}
        self.assertDictEqual(expected, result)
        self.assertEqual(rv.status_code, 404)

        rv = TEST_CLIENT.delete(f"/templates/{TEMPLATE_ID}")
        result = rv.json()
        expected = {"message": "Template deleted"}
        self.assertDictEqual(expected, result)

    def test_delete_multiple_templates(self):
        rv = TEST_CLIENT.post("/templates/deletetemplates", json=[])
        result = rv.json()
        expected = {"message": "inform at least one template"}
        self.assertDictEqual(expected, result)
        self.assertEqual(rv.status_code, 400)

        rv = TEST_CLIENT.post("/templates/deletetemplates", json=[TEMPLATE_ID])
        result = rv.json()
        expected = {"message": "Successfully removed templates"}
        self.assertDictEqual(expected, result)
        self.assertEqual(rv.status_code, 200)
