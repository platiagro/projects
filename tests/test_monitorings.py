# -*- coding: utf-8 -*-
from json import dumps
from unittest import TestCase

from projects.api.main import app
from projects.controllers.utils import uuid_alpha
from projects.database import engine
from projects.object_storage import BUCKET_NAME

DEPLOYMENT_ID = str(uuid_alpha())
EXPERIMENT_ID = str(uuid_alpha())
MONITORING_ID = str(uuid_alpha())
PROJECT_ID = str(uuid_alpha())
TASK_ID = str(uuid_alpha())
TASK_ID_2 = str(uuid_alpha())
NAME = "foo"
DESCRIPTION = "long foo"
IMAGE = "platiagro/platiagro-experiment-image:0.2.0"
PARAMETERS_JSON =  dumps({"default": True, "name": "shuffle", "type": "boolean"})
TAGS_JSON = dumps(["PREDICTOR"])
EXPERIMENT_NOTEBOOK_PATH = f"minio://{BUCKET_NAME}/tasks/{TASK_ID}/Experiment.ipynb"
DEPLOYMENT_NOTEBOOK_PATH = f"minio://{BUCKET_NAME}/tasks/{TASK_ID}/Deployment.ipynb"
POSITION = 0
CREATED_AT = "2000-01-01 00:00:00"
CREATED_AT_ISO = "2000-01-01T00:00:00"
UPDATED_AT = "2000-01-01 00:00:00"
UPDATED_AT_ISO = "2000-01-01T00:00:00"


class TestMonitorings(TestCase):
    def setUp(self):
        self.maxDiff = None
        conn = engine.connect()
        text = (
            f"INSERT INTO tasks (uuid, name, description, image, commands, arguments, tags, experiment_notebook_path, deployment_notebook_path, is_default, parameters, created_at, updated_at) "
            f"VALUES ('{TASK_ID}', '{NAME}', '{DESCRIPTION}', '{IMAGE}', null, null, '{TAGS_JSON}', '{EXPERIMENT_NOTEBOOK_PATH}', '{DEPLOYMENT_NOTEBOOK_PATH}', 0, '{PARAMETERS_JSON}', '{CREATED_AT}', '{UPDATED_AT}')"
        )
        conn.execute(text)

        text = (
            f"INSERT INTO tasks (uuid, name, description, image, commands, arguments, tags, experiment_notebook_path, deployment_notebook_path, is_default, parameters, created_at, updated_at) "
            f"VALUES ('{TASK_ID_2}', '{NAME}', '{DESCRIPTION}', '{IMAGE}', null, null, '{TAGS_JSON}', '{EXPERIMENT_NOTEBOOK_PATH}', '{DEPLOYMENT_NOTEBOOK_PATH}', 0, '{PARAMETERS_JSON}', '{CREATED_AT}', '{UPDATED_AT}')"
        )
        conn.execute(text)

        text = (
            f"INSERT INTO projects (uuid, name, created_at, updated_at) "
            f"VALUES ('{PROJECT_ID}', '{NAME}', '{CREATED_AT}', '{UPDATED_AT}')"
        )
        conn.execute(text)

        text = (
            f"INSERT INTO experiments (uuid, name, project_id, position, is_active, created_at, updated_at) "
            f"VALUES ('{EXPERIMENT_ID}', '{NAME}', '{PROJECT_ID}', '{POSITION}', 1, '{CREATED_AT}', '{UPDATED_AT}')"
        )
        conn.execute(text)

        text = (
            f"INSERT INTO deployments (uuid, name, project_id, experiment_id, position, is_active, created_at, updated_at) "
            f"VALUES ('{DEPLOYMENT_ID}', '{NAME}', '{PROJECT_ID}', '{EXPERIMENT_ID}', '{POSITION}', 1, '{CREATED_AT}', '{UPDATED_AT}')"
        )
        conn.execute(text)

        text = (
            f"INSERT INTO monitoring (uuid, deployment_id, task_id, created_at) "
            f"VALUES ('{MONITORING_ID}', '{DEPLOYMENT_ID}', '{TASK_ID}', '{CREATED_AT}')"
        )
        conn.execute(text)

        conn.close()

    def tearDown(self):
        conn = engine.connect()

        text = f"DELETE FROM monitoring WHERE deployment_id = '{DEPLOYMENT_ID}'"
        conn.execute(text)

        text = f"DELETE FROM deployments WHERE project_id = '{PROJECT_ID}'"
        conn.execute(text)

        text = f"DELETE FROM experiments WHERE project_id in ('{PROJECT_ID}')"
        conn.execute(text)

        text = f"DELETE FROM projects WHERE uuid = '{PROJECT_ID}'"
        conn.execute(text)

        text = f"DELETE FROM tasks WHERE uuid = '{TASK_ID}'"
        conn.execute(text)

        text = f"DELETE FROM tasks WHERE uuid = '{TASK_ID_2}'"
        conn.execute(text)
        conn.close()

    def test_list_monitorings(self):
        with app.test_client() as c:
            rv = c.get("/projects/unk/deployments/unk/monitorings")
            result = rv.get_json()
            expected = {"message": "The specified project does not exist"}
            self.assertDictEqual(expected, result)
            self.assertEqual(rv.status_code, 404)

            rv = c.get(f"/projects/{PROJECT_ID}/deployments/unk/monitorings")
            result = rv.get_json()
            expected = {"message": "The specified deployment does not exist"}
            self.assertDictEqual(expected, result)
            self.assertEqual(rv.status_code, 404)

            rv = c.get(f"/projects/{PROJECT_ID}/deployments/{DEPLOYMENT_ID}/monitorings")
            result = rv.get_json()
            self.assertIsInstance(result, list)

    def test_create_monitoring(self):
        with app.test_client() as c:
            rv = c.post("/projects/unk/deployments/unk/monitorings", json={})
            result = rv.get_json()
            expected = {"message": "The specified project does not exist"}
            self.assertDictEqual(expected, result)
            self.assertEqual(rv.status_code, 404)

            rv = c.post(f"/projects/{PROJECT_ID}/deployments/unk/monitorings", json={})
            result = rv.get_json()
            expected = {"message": "The specified deployment does not exist"}
            self.assertDictEqual(expected, result)
            self.assertEqual(rv.status_code, 404)

            rv = c.post(
                f"/projects/{PROJECT_ID}/deployments/{DEPLOYMENT_ID}/monitorings",
                json={
                    "taskId": "unk",
                }
            )
            result = rv.get_json()
            expected = {"message": "The specified task does not exist"}
            self.assertDictEqual(expected, result)
            self.assertEqual(rv.status_code, 404)

            rv = c.post(
                f"/projects/{PROJECT_ID}/deployments/{DEPLOYMENT_ID}/monitorings",
                json={
                    "taskId": TASK_ID_2,
                }
            )
            result = rv.get_json()
            expected = {
                "deploymentId": DEPLOYMENT_ID,
                "taskId": TASK_ID_2,
            }
            machine_generated = ["uuid", "createdAt"]
            for attr in machine_generated:
                self.assertIn(attr, result)
                del result[attr]
            self.assertDictEqual(expected, result)

    def test_delete_monitoring(self):
        with app.test_client() as c:
            rv = c.delete(f"/projects/unk/deployments/unk/monitorings/unk")
            result = rv.get_json()
            expected = {"message": "The specified project does not exist"}
            self.assertDictEqual(expected, result)
            self.assertEqual(rv.status_code, 404)

            rv = c.delete(f"/projects/{PROJECT_ID}/deployments/unk/monitorings/unk")
            result = rv.get_json()
            expected = {"message": "The specified deployment does not exist"}
            self.assertDictEqual(expected, result)
            self.assertEqual(rv.status_code, 404)

            rv = c.delete(f"/projects/{PROJECT_ID}/deployments/{DEPLOYMENT_ID}/monitorings/unk")
            result = rv.get_json()
            expected = {"message": "The specified monitoring does not exist"}
            self.assertDictEqual(expected, result)
            self.assertEqual(rv.status_code, 404)

            rv = c.delete(f"/projects/{PROJECT_ID}/deployments/{DEPLOYMENT_ID}/monitorings/{MONITORING_ID}")
            result = rv.get_json()
            expected = {"message": "Monitoring deleted"}
            self.assertDictEqual(expected, result)
