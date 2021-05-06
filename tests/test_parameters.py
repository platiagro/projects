# -*- coding: utf-8 -*-
from io import BytesIO
from json import dumps
from unittest import TestCase

from fastapi.testclient import TestClient

from projects.api.main import app
from projects.controllers.utils import uuid_alpha
from projects.database import engine

TEST_CLIENT = TestClient(app)

TASK_ID = str(uuid_alpha())
NAME = "foo"
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
CREATED_AT = "2000-01-01 00:00:00"
UPDATED_AT = "2000-01-01 00:00:00"


class TestParameters(TestCase):

    def setUp(self):
        self.maxDiff = None
        conn = engine.connect()
        text = (
            f"INSERT INTO tasks (uuid, name, description, image, commands, arguments, tags, parameters, "
            f"experiment_notebook_path, deployment_notebook_path, cpu_limit, cpu_request, memory_limit, memory_request, "
            f"readiness_probe_initial_delay_seconds, is_default, created_at, updated_at) "
            f"VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
        )
        conn.execute(text, (TASK_ID, NAME, DESCRIPTION, IMAGE, COMMANDS_JSON, ARGUMENTS_JSON, TAGS_JSON, dumps([]),
                            EXPERIMENT_NOTEBOOK_PATH, DEPLOYMENT_NOTEBOOK_PATH, "100m", "100m", "1Gi", "1Gi", 300, 0, CREATED_AT, UPDATED_AT,))
        conn.close()

    def tearDown(self):
        conn = engine.connect()
        text = f"DELETE FROM tasks WHERE uuid = '{TASK_ID}'"
        conn.execute(text)
        conn.close()

    def test_list_parameters(self):
        rv = TEST_CLIENT.get("/tasks/unk/parameters")
        result = rv.json()
        expected = {"message": "The specified task does not exist"}
        self.assertDictEqual(expected, result)
        self.assertEqual(rv.status_code, 404)

        rv = TEST_CLIENT.get(f"/tasks/{TASK_ID}/parameters")
        result = rv.json()
        self.assertIsInstance(result, list)
