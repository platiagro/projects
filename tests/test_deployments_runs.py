# -*- coding: utf-8 -*-
from json import dumps
from os import remove
from unittest import TestCase

from fastapi.testclient import TestClient

from projects.api.main import app
from projects.controllers.utils import uuid_alpha
from projects.database import engine
from projects.kfp import kfp_client

TEST_CLIENT = TestClient(app)

DEPLOYMENT_ID = str(uuid_alpha())
DEPLOYMENT_ID_2 = str(uuid_alpha())
NAME = "foo-bar"
PROJECT_ID = str(uuid_alpha())
CREATED_AT = "2000-01-01 00:00:00"
UPDATED_AT = "2000-01-01 00:00:00"
EXPERIMENT_ID = str(uuid_alpha())
POSITION = 0
STATUS = "Pending"
URL = None
OPERATOR_ID = str(uuid_alpha())
OPERATOR_ID_2 = str(uuid_alpha())
TASK_ID = str(uuid_alpha())
TASK_ID_2 = str(uuid_alpha())
PARAMETERS_JSON = dumps({"coef": 0.1})
DEP_EMPTY_JSON = dumps([])
IMAGE = "platiagro/platiagro-experiment-image:0.2.0"
TAGS_JSON = dumps(["PREDICTOR"])
DEPLOY_NOTEBOOK_PATH = "Deployment.ipynb"
EX_NOTEBOOK_PATH = "Experiment.ipynb"


class TestDeploymentsRuns(TestCase):

    def setUp(self):
        self.maxDiff = None

        with open("tests/resources/mocked_deployment.yaml", "r") as file:
            content = file.read()

        content = content.replace("$deploymentId", DEPLOYMENT_ID)
        with open("tests/resources/mocked.yaml", "w") as file:
            file.write(content)

        kfp_experiment = kfp_client().create_experiment(name=DEPLOYMENT_ID)
        kfp_client().run_pipeline(
            experiment_id=kfp_experiment.id,
            job_name=DEPLOYMENT_ID,
            pipeline_package_path="tests/resources/mocked.yaml",
        )

        conn = engine.connect()
        text = (
            f"INSERT INTO tasks (uuid, name, description, image, commands, arguments, tags, parameters, "
            f"experiment_notebook_path, deployment_notebook_path, cpu_limit, cpu_request, memory_limit, memory_request, "
            f"readiness_probe_initial_delay_seconds, is_default, created_at, updated_at) "
            f"VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
        )
        conn.execute(text, (TASK_ID, "name", "desc", IMAGE, None, None, TAGS_JSON, dumps([]),
                            EX_NOTEBOOK_PATH, DEPLOY_NOTEBOOK_PATH, "100m", "100m", "1Gi", "1Gi", 300, 0, CREATED_AT, UPDATED_AT,))

        text = (
            f"INSERT INTO tasks (uuid, name, description, image, commands, arguments, tags, parameters, "
            f"experiment_notebook_path, deployment_notebook_path, cpu_limit, cpu_request, memory_limit, memory_request, "
            f"readiness_probe_initial_delay_seconds, is_default, created_at, updated_at) "
            f"VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
        )
        conn.execute(text, (TASK_ID_2, "name", "desc", IMAGE, None, None, TAGS_JSON, dumps([]),
                            EX_NOTEBOOK_PATH, None, "100m", "100m", "1Gi", "1Gi", 300, 0, CREATED_AT, UPDATED_AT,))

        text = (
            f"INSERT INTO projects (uuid, name, created_at, updated_at) "
            f"VALUES (%s, %s, %s, %s)"
        )
        conn.execute(text, (PROJECT_ID, NAME, CREATED_AT, UPDATED_AT,))

        text = (
            f"INSERT INTO experiments (uuid, name, project_id, position, is_active, created_at, updated_at) "
            f"VALUES (%s, %s, %s, %s, %s, %s, %s)"
        )
        conn.execute(text, (EXPERIMENT_ID, NAME, PROJECT_ID, POSITION, 1, CREATED_AT, UPDATED_AT,))

        text = (
            f"INSERT INTO deployments (uuid, name, project_id, experiment_id, position, is_active, status, url, created_at, updated_at) "
            f"VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
        )
        conn.execute(text, (DEPLOYMENT_ID, NAME, PROJECT_ID, EXPERIMENT_ID, POSITION, 1, STATUS, URL, CREATED_AT, UPDATED_AT,))

        text = (
            f"INSERT INTO deployments (uuid, name, project_id, experiment_id, position, is_active, status, url, created_at, updated_at) "
            f"VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
        )
        conn.execute(text, (DEPLOYMENT_ID_2, NAME, PROJECT_ID, EXPERIMENT_ID, POSITION, 1, STATUS, URL, CREATED_AT, UPDATED_AT,))

        text = (
            f"INSERT INTO operators (uuid, name, status, status_message, experiment_id, deployment_id, task_id, parameters, dependencies, created_at, updated_at) "
            f"VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
        )
        conn.execute(text, (OPERATOR_ID, None, "Unset", None, EXPERIMENT_ID, DEPLOYMENT_ID,
                     TASK_ID_2, PARAMETERS_JSON, DEP_EMPTY_JSON, CREATED_AT, UPDATED_AT,))

        text = (
            f"INSERT INTO operators (uuid, name, status, status_message, experiment_id, deployment_id, task_id, parameters, dependencies, created_at, updated_at) "
            f"VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
        )
        conn.execute(text, (OPERATOR_ID_2, None, "Unset", None, EXPERIMENT_ID, DEPLOYMENT_ID,
                     TASK_ID, PARAMETERS_JSON, dumps([OPERATOR_ID]), CREATED_AT, UPDATED_AT,))
        conn.close()

    def tearDown(self):
        conn = engine.connect()

        text = f"DELETE FROM operators WHERE experiment_id in" \
               f"(SELECT uuid FROM experiments where project_id = '{PROJECT_ID}')"
        conn.execute(text)

        text = f"DELETE FROM deployments WHERE project_id = '{PROJECT_ID}'"
        conn.execute(text)

        text = f"DELETE FROM experiments WHERE project_id = '{PROJECT_ID}'"
        conn.execute(text)

        text = f"DELETE FROM projects WHERE uuid = '{PROJECT_ID}'"
        conn.execute(text)

        text = f"DELETE FROM tasks WHERE uuid IN ('{TASK_ID}', '{TASK_ID_2}')"
        conn.execute(text)

        conn.close()

        remove("tests/resources/mocked.yaml")

    def test_list_runs(self):
        rv = TEST_CLIENT.get(f"/projects/{PROJECT_ID}/deployments/{DEPLOYMENT_ID}/runs")
        result = rv.json()
        self.assertIsInstance(result["runs"], list)
        self.assertIsInstance(result["total"], int)
        self.assertEqual(rv.status_code, 200)

    def test_create_run(self):
        rv = TEST_CLIENT.post(f"/projects/foo/deployments/{DEPLOYMENT_ID}/runs", json={})
        result = rv.json()
        expected = {'message': 'The specified project does not exist'}
        self.assertIsInstance(result, dict)
        self.assertEqual(rv.status_code, 404)

        rv = TEST_CLIENT.post(f"/projects/{PROJECT_ID}/deployments/foo/runs", json={})
        result = rv.json()
        expected = {'message': 'The specified deployment does not exist'}
        self.assertIsInstance(result, dict)
        self.assertEqual(rv.status_code, 404)

        rv = TEST_CLIENT.post(f"/projects/{PROJECT_ID}/deployments/{DEPLOYMENT_ID_2}/runs", json={})
        result = rv.json()
        expected = {'message': 'Necessary at least one operator.'}
        self.assertIsInstance(result, dict)
        self.assertEqual(rv.status_code, 400)

        rv = TEST_CLIENT.post(f"/projects/{PROJECT_ID}/deployments/{DEPLOYMENT_ID}/runs")
        result = rv.json()
        self.assertIsInstance(result, dict)
        self.assertIn("uuid", result)
        self.assertIn("operators", result)
        self.assertEqual(DEPLOYMENT_ID, result["deploymentId"])
        self.assertEqual(rv.status_code, 200)

    def test_get_deployment_log(self):
        rv = TEST_CLIENT.get(f"/projects/{PROJECT_ID}/deployments/foo/runs/latest/logs")
        result = rv.json()
        expected = {"message": "The specified deployment does not exist"}
        self.assertDictEqual(expected, result)
        self.assertEqual(rv.status_code, 404)

        # rv = TEST_CLIENT.get(f"/projects/{PROJECT_ID}/deployments/{DEPLOYMENT_ID}/runs/latest/logs")
        # result = rv.json()
        # self.assertIsInstance(result, list)
        # self.assertEqual(rv.status_code, 200)

    def test_get_run(self):
        rv = TEST_CLIENT.get(f"/projects/{PROJECT_ID}/deployments/{DEPLOYMENT_ID}/runs/latest")
        result = rv.json()
        self.assertIsInstance(result, dict)
        self.assertEqual(rv.status_code, 200)

    def test_delete_run(self):
        rv = TEST_CLIENT.delete(f"/projects/{PROJECT_ID}/deployments/{DEPLOYMENT_ID}/runs/latest")
        result = rv.json()
        expected = {"message": "Deployment deleted."}
        self.assertDictEqual(expected, result)
        self.assertEqual(rv.status_code, 200)
