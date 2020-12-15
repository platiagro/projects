# -*- coding: utf-8 -*-
from json import dumps
from unittest import TestCase

from projects.api.main import app
from projects.controllers.utils import uuid_alpha
from projects.database import engine
from projects.kfp import KFP_CLIENT
from projects.object_storage import BUCKET_NAME

DEPLOYMENT_ID = str(uuid_alpha())
NAME = "foo-bar"
PROJECT_ID = str(uuid_alpha())
CREATED_AT = "2000-01-01 00:00:00"
UPDATED_AT = "2000-01-01 00:00:00"
EXPERIMENT_ID = str(uuid_alpha())
POSITION = 0
OPERATOR_ID = str(uuid_alpha())
TASK_ID = str(uuid_alpha())
PARAMETERS_JSON = dumps({"coef": 0.1})
DEP_EMPTY_JSON = dumps([])
IMAGE = "platiagro/platiagro-notebook-image:0.2.0"
ARGUMENTS_JSON = dumps(["ARG"])
COMMANDS_JSON = dumps(["CMD"])
TAGS_JSON = dumps(["PREDICTOR"])
DEPLOY_NOTEBOOK_PATH = f"minio://{BUCKET_NAME}/tasks/{TASK_ID}/Deployment.ipynb"
EX_NOTEBOOK_PATH = f"minio://{BUCKET_NAME}/tasks/{TASK_ID}/Experiment.ipynb"


class TestDeploymentsRuns(TestCase):

    @classmethod
    def setUpClass(cls):
        cls.maxDiff = None

        kfp_experiment = KFP_CLIENT.create_experiment(name=DEPLOYMENT_ID)
        KFP_CLIENT.run_pipeline(
            experiment_id=kfp_experiment.id,
            job_name=DEPLOYMENT_ID,
            pipeline_package_path="tests/resources/mocked_deployment.yaml",
        )

        conn = engine.connect()
        text = (
            f"INSERT INTO tasks (uuid, name, description, image, commands, arguments, tags, experiment_notebook_path, deployment_notebook_path, is_default, created_at, updated_at) "
            f"VALUES ('{TASK_ID}', 'name', 'desc', '{IMAGE}', '{COMMANDS_JSON}', '{ARGUMENTS_JSON}', '{TAGS_JSON}', '{EX_NOTEBOOK_PATH}', '{DEPLOY_NOTEBOOK_PATH}', 0, '{CREATED_AT}', '{UPDATED_AT}')"
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
            f"INSERT INTO operators (uuid, experiment_id, deployment_id, task_id, parameters, created_at, updated_at, dependencies) "
            f"VALUES ('{OPERATOR_ID}', '{EXPERIMENT_ID}', '{DEPLOYMENT_ID}', '{TASK_ID}', '{PARAMETERS_JSON}', '{CREATED_AT}', '{UPDATED_AT}', '{DEP_EMPTY_JSON}')"
        )
        conn.execute(text)
        conn.close()

    @classmethod
    def tearDownClass(cls):
        conn = engine.connect()

        text = f"DELETE FROM operators WHERE 1 = 1"
        conn.execute(text)

        text = f"DELETE FROM deployments WHERE project_id = '{PROJECT_ID}'"
        conn.execute(text)

        text = f"DELETE FROM experiments WHERE project_id = '{PROJECT_ID}'"
        conn.execute(text)

        text = f"DELETE FROM projects WHERE uuid = '{PROJECT_ID}'"
        conn.execute(text)

        conn.close()

    def test_list_runs(self):
        with app.test_client() as c:
            rv = c.get(f"/projects/{PROJECT_ID}/deployments/{DEPLOYMENT_ID}/runs")
            result = rv.get_json()
            self.assertIsInstance(result, list)
            self.assertEqual(rv.status_code, 200)

    def test_create_run(self):
        with app.test_client() as c:
            rv = c.post(f"/projects/{PROJECT_ID}/deployments/{DEPLOYMENT_ID}/runs", json={})
            result = rv.get_json()
            expected = {'message': 'Necessary at least one operator.'}
            self.assertIsInstance(result, dict)

            rv = c.post(f"/projects/{PROJECT_ID}/deployments/{DEPLOYMENT_ID}/runs")
            result = rv.get_json()
            self.assertIsInstance(result, dict)
            self.assertIn("runId", result)
            self.assertIn("message", result)
            self.assertEqual(rv.status_code, 200)

    def test_get_deployment_log(self):
        with app.test_client() as c:
            rv = c.get(f"/projects/{PROJECT_ID}/deployments/foo/runs/latest/logs")
            result = rv.get_json()
            expected = {"message": "The specified deployment does not exist"}
            self.assertDictEqual(expected, result)
            self.assertEqual(rv.status_code, 404)

            # rv = c.get(f"/projects/{PROJECT_ID}/deployments/{DEPLOYMENT_ID}/runs/latest/logs")
            # result = rv.get_json()
            # self.assertIsInstance(result, list)
            # self.assertEqual(rv.status_code, 200)

    # def test_get_run(self):
    #     with app.test_client() as c:
    #         rv = c.get(f"/projects/{PROJECT_ID}/deployments/{DEPLOYMENT_ID}/runs/latest")
    #         result = rv.get_json()
    #         self.assertIsInstance(result, dict)
    #         self.assertIn("url", result)
    #         self.assertIn("experimentId", result)
    #         self.assertIn("createdAt", result)
    #         self.assertEqual(rv.status_code, 200)

    # def test_delete_run(self):
    #     with app.test_client() as c:
    #         rv = c.delete(f"/projects/{PROJECT_ID}/deployments/{DEPLOYMENT_ID}/runs/latest")
    #         result = rv.get_json()
    #         expected = {"message": "Deployment deleted."}
    #         self.assertDictEqual(expected, result)
    #         self.assertEqual(rv.status_code, 200)