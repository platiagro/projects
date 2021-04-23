# -*- coding: utf-8 -*-
# import subprocess
import time
from json import dumps
from unittest import TestCase

from fastapi.testclient import TestClient

from projects.api.main import app
from projects.controllers.utils import uuid_alpha
from projects.database import engine
from projects.kfp import kfp_client


TEST_CLIENT = TestClient(app)

PROJECT_ID = str(uuid_alpha())
NAME = "foo"
CREATED_AT = "2000-01-01 00:00:00"
UPDATED_AT = "2000-01-01 00:00:00"
DESCRIPTION = "Description"
OPERATOR_ID = str(uuid_alpha())
POSITION_X = 0.3
POSITION_Y = 0.5
PARAMETERS = {"coef": 0.1}
PARAMETERS_JSON = dumps(PARAMETERS)
TASK_ID = str(uuid_alpha())
EXPERIMENT_ID = str(uuid_alpha())
DEPLOYMENT_ID = str(uuid_alpha())
DEPENDENCIES_OP_ID = []
DEPENDENCIES_OP_ID_JSON = dumps(DEPENDENCIES_OP_ID)
IMAGE = "platiagro/platiagro-experiment-image:0.2.0"
TAGS = ["PREDICTOR"]
TAGS_JSON = dumps(TAGS)
EXPERIMENT_NOTEBOOK_PATH = ""
DEPLOYMENT_NOTEBOOK_PATH = ""
EXPERIMENT_NAME = "Experimento 1"


class TestLogs(TestCase):

    def setUp(self):
        self.maxDiff = None

        conn = engine.connect()
        text = (
            f"INSERT INTO projects (uuid, name, description, created_at, updated_at) "
            f"VALUES (%s, %s, %s, %s, %s)"
        )
        conn.execute(text, (PROJECT_ID, NAME, DESCRIPTION, CREATED_AT, UPDATED_AT,))

        text = (
            f"INSERT INTO experiments (uuid, name, project_id, position, is_active, created_at, updated_at) "
            f"VALUES (%s, %s, %s, %s, %s, %s, %s)"
        )
        conn.execute(text, (EXPERIMENT_ID, EXPERIMENT_NAME, PROJECT_ID, 0, 1, CREATED_AT, UPDATED_AT,))

        text = (
            f"INSERT INTO deployments (uuid, name, project_id, experiment_id, position, is_active, created_at, updated_at) "
            f"VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"
        )
        conn.execute(text, (DEPLOYMENT_ID, NAME, PROJECT_ID, EXPERIMENT_ID, 0, 1, CREATED_AT, UPDATED_AT,))

        text = (
            f"INSERT INTO tasks (uuid, name, description, image, commands, arguments, tags, parameters, experiment_notebook_path, deployment_notebook_path, is_default, created_at, updated_at) "
            f"VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
        )
        conn.execute(text, (TASK_ID, NAME, DESCRIPTION, IMAGE, None, None, TAGS_JSON,
                            dumps([]), EXPERIMENT_NOTEBOOK_PATH, EXPERIMENT_NOTEBOOK_PATH, 0, CREATED_AT, UPDATED_AT,))

        text = (
            f"INSERT INTO operators (uuid, name, status, status_message, experiment_id, task_id, parameters, position_x, position_y, dependencies, created_at, updated_at) "
            f"VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
        )
        conn.execute(text, (OPERATOR_ID, None, "Unset", None, EXPERIMENT_ID, TASK_ID, PARAMETERS_JSON, POSITION_X,
                            POSITION_Y, DEPENDENCIES_OP_ID_JSON, CREATED_AT, UPDATED_AT,))

        text = (
            f"INSERT INTO operators (uuid, name, status, status_message, deployment_id, task_id, parameters, position_x, position_y, dependencies, created_at, updated_at) "
            f"VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
        )
        conn.execute(text, (OPERATOR_ID_2, None, "Unset", None, DEPLOYMENT_ID, TASK_ID, PARAMETERS_JSON,
                            POSITION_X, POSITION_Y, DEPENDENCIES_OP_ID_JSON, CREATED_AT, UPDATED_AT,))
        conn.close()

        with open("tests/resources/mocked_experiment.yaml", "r") as file:
            content = file.read()

        content = content.replace("$experimentId", EXPERIMENT_ID)
        with open("tests/resources/mocked.yaml", "w") as file:
            file.write(content)

        # Run a default pipeline for log generation
        kfp_experiment = kfp_client().create_experiment(name=EXPERIMENT_ID)
        kfp_client().run_pipeline(
            experiment_id=kfp_experiment.id,
            job_name=EXPERIMENT_ID,
            pipeline_package_path="tests/resources/mocked.yaml",
        )

        # Awaits the pod to run and complete
        time.sleep(30)
        # subprocess.check_output(
        #     ["kubectl", "-n", KF_PIPELINES_NAMESPACE, "wait", "--for=condition=complete", "pod", "-l", "pipelines.kubeflow.org/cache_enabled=true"],
        #     timeout=30,
        # )

    def tearDown(self):
        conn = engine.connect()
        text = f"DELETE FROM operators WHERE uuid = '{OPERATOR_ID}'"
        conn.execute(text)

        text = f"DELETE FROM deployments WHERE uuid = '{DEPLOYMENT_ID}'"
        conn.execute(text)

        text = f"DELETE FROM experiments WHERE uuid = '{EXPERIMENT_ID}'"
        conn.execute(text)

        text = f"DELETE FROM tasks WHERE uuid = '{TASK_ID}'"
        conn.execute(text)

        text = f"DELETE FROM projects WHERE uuid = '{PROJECT_ID}'"
        conn.execute(text)
        conn.close()

    def test_list_logs(self):
        rv = TEST_CLIENT.get(f"/projects/{PROJECT_ID}/experiments/{EXPERIMENT_ID}/runs/latest/logs")
        result = rv.json()
        expected = {
            "total": 0,
            "logs": []
        }
        self.assertEqual(rv.status_code, 200)
        self.assertDictEqual(result, expected)

        rv = TEST_CLIENT.get(f"/projects/{PROJECT_ID}/deployments/{DEPLOYMENT_ID}/runs/latest/logs")
        result = rv.json()
        expected = {
            "total": 0,
            "logs": []
        }
        self.assertEqual(rv.status_code, 200)
        self.assertDictEqual(result, expected)
