# -*- coding: utf-8 -*-
from io import BytesIO
from json import dumps
from unittest import TestCase

from minio.error import BucketAlreadyOwnedByYou
from platiagro import CATEGORICAL, DATETIME, NUMERICAL

from projects.api.main import app
from projects.controllers.utils import uuid_alpha
from projects.database import engine
from projects.object_storage import BUCKET_NAME, MINIO_CLIENT

PROJECT_ID = str(uuid_alpha())
EXPERIMENT_ID = str(uuid_alpha())
TASK_ID = str(uuid_alpha())
NAME = "foo"
DESCRIPTION = "long foo"
DATASET = "mock.csv"
TARGET = "col4"
POSITION = 0
PARAMETERS = {"dataset": DATASET}
COMMANDS = ["CMD"]
COMMANDS_JSON = dumps(COMMANDS)
ARGUMENTS = ["ARG"]
ARGUMENTS_JSON = dumps(ARGUMENTS)
IMAGE = "platiagro/platiagro-notebook-image-test:0.1.0"
TAGS = ["PREDICTOR"]
TAGS_JSON = dumps(TAGS)
PARAMETERS_JSON = dumps(PARAMETERS)
EXPERIMENT_NOTEBOOK_PATH = f"minio://{BUCKET_NAME}/tasks/{TASK_ID}/Experiment.ipynb"
DEPLOYMENT_NOTEBOOK_PATH = f"minio://{BUCKET_NAME}/tasks/{TASK_ID}/Deployment.ipynb"
RUN_ID = str(uuid_alpha())
OPERATOR_ID = str(uuid_alpha())
OPERATOR_ID2 = str(uuid_alpha())
CREATED_AT = "2000-01-01 00:00:00"
UPDATED_AT = "2000-01-01 00:00:00"


class TestDatasets(TestCase):
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

        text = (
            f"INSERT INTO operators (uuid, experiment_id, task_id, parameters, created_at, updated_at) "
            f"VALUES ('{OPERATOR_ID2}', '{EXPERIMENT_ID}', '{TASK_ID}', '{PARAMETERS_JSON}', '{CREATED_AT}', '{UPDATED_AT}')"
        )
        conn.execute(text)
        conn.close()

        # uploads mock dataset
        try:
            MINIO_CLIENT.make_bucket(BUCKET_NAME)
        except BucketAlreadyOwnedByYou:
            pass

        file = BytesIO((
            b'col0,col1,col2,col3,col4,col5\n'
            b'01/01/2000,5.1,3.5,1.4,0.2,Iris-setosa\n'
            b'01/01/2000,5.1,3.5,1.4,0.2,Iris-setosa\n'
            b'01/01/2000,5.1,3.5,1.4,0.2,Iris-setosa\n'
        ))
        MINIO_CLIENT.put_object(
            bucket_name=BUCKET_NAME,
            object_name=f"datasets/{DATASET}/{DATASET}",
            data=file,
            length=file.getbuffer().nbytes,
        )
        metadata = {
            "columns": ["col0", "col1", "col2", "col3", "col4", "col5"],
            "featuretypes": [DATETIME, NUMERICAL, NUMERICAL, NUMERICAL, NUMERICAL, CATEGORICAL],
            "filename": DATASET,
            "run_id": RUN_ID,
        }
        buffer = BytesIO(dumps(metadata).encode())
        MINIO_CLIENT.put_object(
            bucket_name=BUCKET_NAME,
            object_name=f"datasets/{DATASET}/{DATASET}.metadata",
            data=buffer,
            length=buffer.getbuffer().nbytes,
        )
        MINIO_CLIENT.copy_object(
            bucket_name=BUCKET_NAME,
            object_name=f"datasets/{DATASET}/runs/{RUN_ID}/operators/{OPERATOR_ID}/{DATASET}/{DATASET}",
            object_source=f"/{BUCKET_NAME}/datasets/{DATASET}/{DATASET}",
        )
        MINIO_CLIENT.copy_object(
            bucket_name=BUCKET_NAME,
            object_name=f"datasets/{DATASET}/runs/{RUN_ID}/operators/{OPERATOR_ID}/{DATASET}/{DATASET}.metadata",
            object_source=f"/{BUCKET_NAME}/datasets/{DATASET}/{DATASET}.metadata",
        )

    def tearDown(self):
        MINIO_CLIENT.remove_object(
            bucket_name=BUCKET_NAME,
            object_name=f"datasets/{DATASET}/runs/{RUN_ID}/operators/{OPERATOR_ID}/{DATASET}/{DATASET}.metadata",
        )
        MINIO_CLIENT.remove_object(
            bucket_name=BUCKET_NAME,
            object_name=f"datasets/{DATASET}/runs/{RUN_ID}/operators/{OPERATOR_ID}/{DATASET}/{DATASET}",
        )
        MINIO_CLIENT.remove_object(
            bucket_name=BUCKET_NAME,
            object_name=f"datasets/{DATASET}/{DATASET}.metadata",
        )
        MINIO_CLIENT.remove_object(
            bucket_name=BUCKET_NAME,
            object_name=f"datasets/{DATASET}/{DATASET}",
        )

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

    def test_get_dataset(self):
        with app.test_client() as c:
            rv = c.get(f"/projects/unk/experiments/{EXPERIMENT_ID}/operators/{OPERATOR_ID}/datasets")
            result = rv.get_json()
            expected = {"message": "The specified project does not exist"}
            self.assertDictEqual(expected, result)
            self.assertEqual(rv.status_code, 404)

            rv = c.get(f"/projects/{PROJECT_ID}/experiments/unk/operators/{OPERATOR_ID}/datasets")
            result = rv.get_json()
            expected = {"message": "The specified experiment does not exist"}
            self.assertDictEqual(expected, result)
            self.assertEqual(rv.status_code, 404)

            rv = c.get(f"/projects/{PROJECT_ID}/experiments/{EXPERIMENT_ID}/operators/unk/datasets")
            result = rv.get_json()
            expected = {"message": "The specified operator does not exist"}
            self.assertDictEqual(expected, result)
            self.assertEqual(rv.status_code, 404)

            rv = c.get(f"/projects/{PROJECT_ID}/experiments/{EXPERIMENT_ID}/operators/{OPERATOR_ID2}/datasets")
            result = rv.get_json()
            expected = {
                "columns": ["col0", "col1", "col2", "col3", "col4", "col5"],
                "data": [
                    ["01/01/2000", 5.1, 3.5, 1.4, 0.2, "Iris-setosa"],
                    ["01/01/2000", 5.1, 3.5, 1.4, 0.2, "Iris-setosa"],
                    ["01/01/2000", 5.1, 3.5, 1.4, 0.2, "Iris-setosa"]
                ],
                "total": 3
            }
            self.assertDictEqual(expected, result)

            rv = c.get(f"/projects/{PROJECT_ID}/experiments/{EXPERIMENT_ID}/operators/{OPERATOR_ID}/datasets")
            result = rv.get_json()
            expected = {
                "columns": ["col0", "col1", "col2", "col3", "col4", "col5"],
                "data": [
                    ["01/01/2000", 5.1, 3.5, 1.4, 0.2, "Iris-setosa"],
                    ["01/01/2000", 5.1, 3.5, 1.4, 0.2, "Iris-setosa"],
                    ["01/01/2000", 5.1, 3.5, 1.4, 0.2, "Iris-setosa"]
                ],
                "total": 3
            }
            self.assertDictEqual(result, expected)

            rv = c.get(f"/projects/{PROJECT_ID}/experiments/{EXPERIMENT_ID}/operators/{OPERATOR_ID}/datasets/{RUN_ID}")
            result = rv.get_json()
            expected = {
                "columns": ["col0", "col1", "col2", "col3", "col4", "col5"],
                "data": [
                    ["01/01/2000", 5.1, 3.5, 1.4, 0.2, "Iris-setosa"],
                    ["01/01/2000", 5.1, 3.5, 1.4, 0.2, "Iris-setosa"],
                    ["01/01/2000", 5.1, 3.5, 1.4, 0.2, "Iris-setosa"]
                ],
                "total": 3
            }
            self.assertDictEqual(result, expected)
