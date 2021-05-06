# -*- coding: utf-8 -*-
import time
from json import dumps
from unittest import TestCase

from fastapi.testclient import TestClient

from projects.api.main import app
from projects.controllers.utils import uuid_alpha
from projects.database import engine
from projects.kfp import kfp_client

TEST_CLIENT = TestClient(app)

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
IMAGE = "busybox"
COMMANDS = None
ARGUMENTS = ["echo", "-e", "hello\nhello"]
TAGS = ["PREDICTOR"]
TAGS_JSON = dumps(TAGS)
PARAMETERS_JSON = dumps(PARAMETERS)
EXPERIMENT_NOTEBOOK_PATH = "Experiment.ipynb"
DEPLOYMENT_NOTEBOOK_PATH = "Deployment.ipynb"
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
        self.maxDiff = None

        conn = engine.connect()
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
            f"INSERT INTO tasks (uuid, name, description, image, commands, arguments, tags, parameters, "
            f"experiment_notebook_path, deployment_notebook_path, cpu_limit, cpu_request, memory_limit, memory_request, "
            f"readiness_probe_initial_delay_seconds, is_default, created_at, updated_at) "
            f"VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
        )
        conn.execute(text, (TASK_ID, NAME, DESCRIPTION, IMAGE, COMMANDS, ARGUMENTS, TAGS_JSON, dumps([]),
                            EXPERIMENT_NOTEBOOK_PATH, DEPLOYMENT_NOTEBOOK_PATH, "100m", "100m", "1Gi", "1Gi", 300, 0, CREATED_AT, UPDATED_AT,))

        text = (
            f"INSERT INTO tasks (uuid, name, description, image, commands, arguments, tags, parameters, "
            f"experiment_notebook_path, deployment_notebook_path, cpu_limit, cpu_request, memory_limit, memory_request, "
            f"readiness_probe_initial_delay_seconds, is_default, created_at, updated_at) "
            f"VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
        )
        conn.execute(text, (TASK_DATASET_ID, NAME, DESCRIPTION, IMAGE, COMMANDS, ARGUMENTS, TASK_DATASET_TAGS_JSON, dumps([]),
                            EXPERIMENT_NOTEBOOK_PATH, DEPLOYMENT_NOTEBOOK_PATH, "100m", "100m", "1Gi", "1Gi", 300, 0, CREATED_AT, UPDATED_AT,))

        text = (
            f"INSERT INTO operators (uuid, name, status, status_message, experiment_id, task_id, parameters, position_x, position_y, dependencies, created_at, updated_at) "
            f"VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
        )
        conn.execute(text, (OPERATOR_ID, None, "Unset", None, EXPERIMENT_ID, TASK_ID, PARAMETERS_JSON, POSITION_X,
                            POSITION_Y, DEPENDENCIES_EMPTY_JSON, CREATED_AT, UPDATED_AT,))
        conn.close()

        # Creates pipelines for log generation
        with open("tests/resources/mocked_experiment.yaml", "r") as file:
            content = file.read()
        content = content.replace("$experimentId", EXPERIMENT_ID)
        content = content.replace("$taskName", NAME)
        content = content.replace("$operatorId", OPERATOR_ID)
        with open("tests/resources/mocked.yaml", "w") as file:
            file.write(content)
        kfp_experiment = kfp_client().create_experiment(name=EXPERIMENT_ID)
        kfp_client().run_pipeline(
            experiment_id=kfp_experiment.id,
            job_name=f"experiment-{EXPERIMENT_ID}",
            pipeline_package_path="tests/resources/mocked.yaml",
        )

        # Awaits 30 seconds (for the pipeline to run and complete)
        # It's a bad solution since the pod may not have completed yet
        # subprocess.run(['kubectl', 'wait', ...]) would be a better solution,
        # but its not compatible with the version of argo workflows we're using
        time.sleep(30)

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
        rv = TEST_CLIENT.get(f"/projects/{PROJECT_ID}/experiments/{EXPERIMENT_ID}/runs")
        result = rv.json()
        self.assertIsInstance(result["runs"], list)
        self.assertIsInstance(result["total"], int)
        self.assertEqual(rv.status_code, 200)

    def test_create_run(self):
        rv = TEST_CLIENT.post(f"/projects/{PROJECT_ID}/experiments/{EXPERIMENT_ID}/runs", json={})
        result = rv.json()
        self.assertIsInstance(result, dict)
        self.assertIn("operators", result)
        self.assertIn("uuid", result)
        self.assertEqual(rv.status_code, 200)

        rv = TEST_CLIENT.get(f"/projects/{PROJECT_ID}/experiments/{EXPERIMENT_ID}")
        result = rv.json()
        operator = result["operators"][0]
        self.assertEqual("Pending", operator["status"])

    def test_get_run(self):
        rv = TEST_CLIENT.get(f"/projects/{PROJECT_ID}/experiments/{EXPERIMENT_ID}/runs/notRealRun")
        result = rv.json()
        expected = {"message": "The specified run does not exist"}
        self.assertDictEqual(expected, result)
        self.assertEqual(rv.status_code, 404)

        rv = TEST_CLIENT.get(f"/projects/{PROJECT_ID}/experiments/{EXPERIMENT_ID}/runs/latest")
        result = rv.json()
        self.assertIsInstance(result, dict)
        self.assertIn("operators", result)
        self.assertIn("uuid", result)
        self.assertEqual(rv.status_code, 200)

    def test_terminate_run(self):
        rv = TEST_CLIENT.delete(f"/projects/{PROJECT_ID}/experiments/{EXPERIMENT_ID}/runs/notRealRun")
        result = rv.json()
        expected = {"message": "The specified run does not exist"}
        self.assertDictEqual(expected, result)
        self.assertEqual(rv.status_code, 404)

        rv = TEST_CLIENT.delete(f"/projects/{PROJECT_ID}/experiments/{EXPERIMENT_ID}/runs/latest")
        result = rv.json()
        expected = {"message": "Run terminated."}
        self.assertDictEqual(expected, result)
        self.assertEqual(rv.status_code, 200)

    # def test_retry_run(self):
    #         TEST_CLIENT.delete(f"/projects/{PROJECT_ID}/experiments/{EXPERIMENT_ID}/runs/latest")

    #         rv = TEST_CLIENT.post(f"/projects/{PROJECT_ID}/experiments/{EXPERIMENT_ID}/runs/latest/retry")
    #         result = rv.json()
    #         expected = {"message": "Run re-initiated successfully"}
    #         self.assertDictEqual(expected, result)
    #         self.assertEqual(rv.status_code, 200)
