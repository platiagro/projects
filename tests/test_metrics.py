# -*- coding: utf-8 -*-
from json import dumps
from unittest import TestCase

import platiagro

from projects.api.main import app
from projects.controllers.utils import uuid_alpha
from projects.database import engine
from projects.object_storage import BUCKET_NAME, MINIO_CLIENT

PROJECT_ID = str(uuid_alpha())
EXPERIMENT_ID = str(uuid_alpha())
TASK_ID = str(uuid_alpha())
OPERATOR_ID = str(uuid_alpha())
RUN_ID = str(uuid_alpha())
NAME = "foo"
DESCRIPTION = "long foo"
TARGET = "col4"
POSITION = 0
PARAMETERS = {}
COMMANDS = ["CMD"]
COMMANDS_JSON = dumps(COMMANDS)
ARGUMENTS = ["ARG"]
ARGUMENTS_JSON = dumps(ARGUMENTS)
IMAGE = "platiagro/platiagro-experiment-image:0.2.0"
TAGS = ["PREDICTOR"]
TAGS_JSON = dumps(TAGS)
PARAMETERS_JSON = dumps(PARAMETERS)
EXPERIMENT_NOTEBOOK_PATH = f"minio://{BUCKET_NAME}/tasks/{TASK_ID}/Experiment.ipynb"
DEPLOYMENT_NOTEBOOK_PATH = f"minio://{BUCKET_NAME}/tasks/{TASK_ID}/Deployment.ipynb"
CREATED_AT = "2000-01-01 00:00:00"
UPDATED_AT = "2000-01-01 00:00:00"

EXPERIMENT_ID = str(uuid_alpha())
OPERATOR_ID = str(uuid_alpha())
RUN_ID = str(uuid_alpha())


class TestMetrics(TestCase):
    def setUp(self):
        self.maxDiff = None
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
            f"INSERT INTO operators (uuid, experiment_id, task_id, parameters, created_at, updated_at) "
            f"VALUES ('{OPERATOR_ID}', '{EXPERIMENT_ID}', '{TASK_ID}', '{PARAMETERS_JSON}', '{CREATED_AT}', '{UPDATED_AT}')"
        )
        conn.execute(text)
        conn.close()

        platiagro.save_metrics(experiment_id=EXPERIMENT_ID,
                               operator_id=OPERATOR_ID,
                               run_id=RUN_ID,
                               accuracy=1.0)

    def tearDown(self):
        prefix = f"experiments/{EXPERIMENT_ID}"
        for obj in MINIO_CLIENT.list_objects(BUCKET_NAME, prefix=prefix, recursive=True):
            MINIO_CLIENT.remove_object(BUCKET_NAME, obj.object_name)

        conn = engine.connect()
        text = f"DELETE FROM operators WHERE experiment_id = '{EXPERIMENT_ID}'"
        conn.execute(text)

        text = f"DELETE FROM tasks WHERE uuid = '{TASK_ID}'"
        conn.execute(text)

        text = f"DELETE FROM experiments WHERE project_id = '{PROJECT_ID}'"
        conn.execute(text)

        text = f"DELETE FROM projects WHERE uuid = '{PROJECT_ID}'"
        conn.execute(text)
        conn.close()

    def test_list_metrics(self):
        with app.test_client() as c:
            rv = c.get(f"/projects/1/experiments/unk/runs/unk/operators/{OPERATOR_ID}/metrics")
            result = rv.get_json()
            expected = {"message": "The specified project does not exist"}
            self.assertDictEqual(expected, result)
            self.assertEqual(rv.status_code, 404)

            rv = c.get(f"/projects/{PROJECT_ID}/experiments/unk/runs/unk/operators/{OPERATOR_ID}/metrics")
            result = rv.get_json()
            expected = {"message": "The specified experiment does not exist"}
            self.assertDictEqual(expected, result)
            self.assertEqual(rv.status_code, 404)

            rv = c.get(f"/projects/{PROJECT_ID}/experiments/{EXPERIMENT_ID}/runs/{RUN_ID}/operators/{OPERATOR_ID}/metrics")
            result = rv.get_json()
            self.assertIsInstance(result, list)
            self.assertEqual(result, [{"accuracy": 1.0}])
