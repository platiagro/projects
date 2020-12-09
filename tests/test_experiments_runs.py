# -*- coding: utf-8 -*-
from json import dumps
from unittest import TestCase

from projects.api.main import app
from projects.controllers.utils import uuid_alpha
from projects.database import engine
from projects.kfp import KFP_CLIENT
from projects.object_storage import BUCKET_NAME

OPERATOR_ID = str(uuid_alpha())
NAME = "foo"
DESCRIPTION = "long foo"
PROJECT_ID = str(uuid_alpha())
EXPERIMENT_ID = str(uuid_alpha())
TASK_ID = str(uuid_alpha())
RUN_ID = str(uuid_alpha())
PARAMETERS = {"coef": 0.1}
POSITION = 0
POSITION_X = 0.3
POSITION_Y = 0.5
IMAGE = "platiagro/platiagro-notebook-image-test:0.2.0"
COMMANDS = ["CMD"]
COMMANDS_JSON = dumps(COMMANDS)
ARGUMENTS = ["ARG"]
ARGUMENTS_JSON = dumps(ARGUMENTS)
TAGS = ["PREDICTOR"]
TAGS_JSON = dumps(TAGS)
PARAMETERS_JSON = dumps(PARAMETERS)
EXPERIMENT_NOTEBOOK_PATH = f"minio://{BUCKET_NAME}/tasks/{TASK_ID}/Experiment.ipynb"
DEPLOYMENT_NOTEBOOK_PATH = f"minio://{BUCKET_NAME}/tasks/{TASK_ID}/Deployment.ipynb"
CREATED_AT = "2000-01-01 00:00:00"
CREATED_AT_ISO = "2000-01-01T00:00:00"
UPDATED_AT = "2000-01-01 00:00:00"
UPDATED_AT_ISO = "2000-01-01T00:00:00"

DEPENDENCIES_EMPTY = []
DEPENDENCIES_EMPTY_JSON = dumps(DEPENDENCIES_EMPTY)

TASK_DATASET_ID = str(uuid_alpha())
TASK_DATASET_TAGS = ["DATASETS"]
TASK_DATASET_TAGS_JSON = dumps(TASK_DATASET_TAGS)


class TestExperimentsRuns(TestCase):
    def setUp(self):
        # Run a default pipeline for tests
        kfp_experiment = KFP_CLIENT.create_experiment(name=EXPERIMENT_ID)
        a = KFP_CLIENT.run_pipeline(
            experiment_id=kfp_experiment.id,
            job_name=EXPERIMENT_ID,
            pipeline_package_path="tests/resources/mocked_experiment.yaml",
        )

        conn = engine.connect()
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
            f"INSERT INTO tasks (uuid, name, description, image, commands, arguments, tags, experiment_notebook_path, deployment_notebook_path, is_default, created_at, updated_at) "
            f"VALUES ('{TASK_ID}', '{NAME}', '{DESCRIPTION}', '{IMAGE}', '{COMMANDS_JSON}', '{ARGUMENTS_JSON}', '{TAGS_JSON}', '{EXPERIMENT_NOTEBOOK_PATH}', '{DEPLOYMENT_NOTEBOOK_PATH}', 0, '{CREATED_AT}', '{UPDATED_AT}')"
        )
        conn.execute(text)

        text = (
            f"INSERT INTO tasks (uuid, name, description, image, commands, arguments, tags, experiment_notebook_path, deployment_notebook_path, is_default, created_at, updated_at) "
            f"VALUES ('{TASK_DATASET_ID}', '{NAME}', '{DESCRIPTION}', '{IMAGE}', '{COMMANDS_JSON}', '{ARGUMENTS_JSON}', '{TASK_DATASET_TAGS_JSON}', '{EXPERIMENT_NOTEBOOK_PATH}', '{DEPLOYMENT_NOTEBOOK_PATH}', 0, '{CREATED_AT}', '{UPDATED_AT}')"
        )
        conn.execute(text)

        text = (
            f"INSERT INTO operators (uuid, experiment_id, task_id, parameters, position_x, position_y, created_at, updated_at, dependencies) "
            f"VALUES ('{OPERATOR_ID}', '{EXPERIMENT_ID}', '{TASK_ID}', '{PARAMETERS_JSON}', '{POSITION_X}', "
            f"'{POSITION_Y}', '{CREATED_AT}', '{UPDATED_AT}', '{DEPENDENCIES_EMPTY_JSON}')"
        )
        conn.execute(text)
        conn.close()

    def tearDown(self):
        conn = engine.connect()

        text = f"DELETE FROM operators WHERE experiment_id in" \
               f"(SELECT uuid  FROM experiments where project_id = '{PROJECT_ID}')"
        conn.execute(text)

        text = f"DELETE FROM tasks WHERE uuid IN ('{TASK_ID}', '{TASK_DATASET_ID}')"
        conn.execute(text)

        text = f"DELETE FROM experiments WHERE project_id = '{PROJECT_ID}'"
        conn.execute(text)

        text = f"DELETE FROM projects WHERE uuid = '{PROJECT_ID}'"
        conn.execute(text)
        conn.close()

    def test_list_runs(self):
        with app.test_client() as c:
            rv = c.get(f"/projects/{PROJECT_ID}/experiments/{EXPERIMENT_ID}/runs")
            result = rv.get_json()
            self.assertIsInstance(result, list)
            self.assertEqual(rv.status_code, 200)

    def test_create_run(self):
        with app.test_client() as c:
            rv = c.post(f"/projects/{PROJECT_ID}/experiments/{EXPERIMENT_ID}/runs", json={})
            result = rv.get_json()
            self.assertIsInstance(result, dict)
            self.assertIn("operators", result)
            self.assertIn("runId", result)
            self.assertEqual(rv.status_code, 200)

    def test_get_run(self):
        with app.test_client() as c:
            rv = c.get(f"/projects/{PROJECT_ID}/experiments/{EXPERIMENT_ID}/runs/notRealRun")
            result = rv.get_json()
            expected = {"message": "The specified run does not exist"}
            self.assertDictEqual(expected, result)
            self.assertEqual(rv.status_code, 404)

            rv = c.get(f"/projects/{PROJECT_ID}/experiments/{EXPERIMENT_ID}/runs/latest")
            result = rv.get_json()
            self.assertIsInstance(result, dict)
            self.assertEqual(rv.status_code, 200)

    def test_terminate_run(self):
        with app.test_client() as c:
            rv = c.delete(f"/projects/{PROJECT_ID}/experiments/{EXPERIMENT_ID}/runs/latest")
            result = rv.get_json()
            expected = {"message": "Run terminated."}
            self.assertDictEqual(expected, result)
            self.assertEqual(rv.status_code, 200)

    # def test_retry_run(self):
    #     with app.test_client() as c:
    #         c.delete(f"/projects/{PROJECT_ID}/experiments/{EXPERIMENT_ID}/runs/latest")

    #         rv = c.post(f"/projects/{PROJECT_ID}/experiments/{EXPERIMENT_ID}/runs/latest/retry")
    #         result = rv.get_json()
    #         expected = {"message": "Run re-initiated successfully"}
    #         self.assertDictEqual(expected, result)  
    #         self.assertEqual(rv.status_code, 200)
