# -*- coding: utf-8 -*-
from io import BytesIO
from json import dumps
from re import S
from tests.test_datasets import TASK_ID
from unittest import TestCase

from fastapi.testclient import TestClient
from minio.error import BucketAlreadyOwnedByYou

from projects.api.main import app
from projects.controllers.utils import uuid_alpha
from projects.database import engine
from projects.kfp import kfp_client
from projects.object_storage import BUCKET_NAME, MINIO_CLIENT

TEST_CLIENT = TestClient(app)

PROJECT_ID = str(uuid_alpha())
EXPERIMENT_ID = str(uuid_alpha())
EXPERIMENT_ID_2 = str(uuid_alpha())
OPERATOR_ID = str(uuid_alpha())
OPERATOR_ID_2 = str(uuid_alpha())
LATEST_RUN = "latest"
TASK_ID = str(uuid_alpha())
NAME = "foo"
IMAGE = "platiagro/platiagro-experiment-image-test:0.2.0"
CATEGORY = "DEFAULT"
CREATED_AT = "2000-01-01 00:00:00"
UPDATED_AT = "2000-01-01 00:00:00"

CONTENT_DISPOSITION = "attachment; filename=results.zip"
CONTENT_TYPE = "application/x-zip-compressed"

MOCK_EXPERIMENT_PATH = "tests/resources/mocked_experiment.yaml"
MOCK_DESTINATION_PATH = "tests/resources/mocked.yaml"
TENANT = "anonymous"


class TestResults(TestCase):
    def setUp(self):
        conn = engine.connect()
        text = (
            f"INSERT INTO projects (uuid, name, created_at, updated_at, tenant) "
            f"VALUES (%s, %s, %s, %s, %s)"
        )
        conn.execute(text, (PROJECT_ID, NAME, CREATED_AT, UPDATED_AT, TENANT,))

        text = (
            f"INSERT INTO experiments (uuid, name, project_id, position, is_active, created_at, updated_at) "
            f"VALUES (%s, %s, %s, %s, %s, %s, %s)"
        )
        conn.execute(text, (EXPERIMENT_ID, NAME, PROJECT_ID, 1, 1, CREATED_AT, UPDATED_AT))

        text = (
            f"INSERT INTO experiments (uuid, name, project_id, position, is_active, created_at, updated_at) "
            f"VALUES (%s, %s, %s, %s, %s, %s, %s)"
        )
        conn.execute(text, (EXPERIMENT_ID_2, NAME, PROJECT_ID, 1, 1, CREATED_AT, UPDATED_AT))

        text = (
            f"INSERT INTO tasks (uuid, name, image, category, parameters, "
            f"experiment_notebook_path, cpu_limit, cpu_request, memory_limit, memory_request, "
            f"readiness_probe_initial_delay_seconds, is_default, created_at, updated_at) "
            f"VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
        )
        conn.execute(text, (TASK_ID, NAME, IMAGE, CATEGORY, dumps([]),
                            "Experiment.ipynb", "100m", "100m", "1Gi", "1Gi", 300, 0, CREATED_AT, UPDATED_AT,))

        text = (
            f"INSERT INTO operators (uuid, status, experiment_id, task_id, parameters, created_at, updated_at) "
            f"VALUES (%s, %s, %s, %s, %s, %s, %s)"
        )
        conn.execute(text, (OPERATOR_ID, "Unset", EXPERIMENT_ID, TASK_ID, dumps([]), CREATED_AT, UPDATED_AT,))

        text = (
            f"INSERT INTO operators (uuid, status, experiment_id, task_id, parameters, created_at, updated_at) "
            f"VALUES (%s, %s, %s, %s, %s, %s, %s)"
        )
        conn.execute(text, (OPERATOR_ID_2, "Unset", EXPERIMENT_ID, TASK_ID, dumps([]), CREATED_AT, UPDATED_AT,))

        with open(MOCK_EXPERIMENT_PATH, "r") as file:
            content = file.read()
        content = content.replace("$experimentId", EXPERIMENT_ID)
        content = content.replace("$taskName", NAME)
        content = content.replace("$operatorId", OPERATOR_ID)
        content = content.replace("$image", IMAGE)
        with open(MOCK_DESTINATION_PATH, "w") as file:
            file.write(content)
        kfp_experiment = kfp_client().create_experiment(name=EXPERIMENT_ID)
        run = kfp_client().run_pipeline(
            experiment_id=kfp_experiment.id,
            job_name=f"experiment-{EXPERIMENT_ID}",
            pipeline_package_path=MOCK_DESTINATION_PATH,
        )
        self.run_id = run.id

        with open(MOCK_EXPERIMENT_PATH, "r") as file:
            content = file.read()
        content = content.replace("$experimentId", EXPERIMENT_ID_2)
        content = content.replace("$taskName", NAME)
        content = content.replace("$operatorId", OPERATOR_ID)
        content = content.replace("$image", IMAGE)
        with open(MOCK_DESTINATION_PATH, "w") as file:
            file.write(content)
        kfp_experiment = kfp_client().create_experiment(name=EXPERIMENT_ID_2)
        run = kfp_client().run_pipeline(
            experiment_id=kfp_experiment.id,
            job_name=f"experiment-{EXPERIMENT_ID_2}",
            pipeline_package_path=MOCK_DESTINATION_PATH,
        )
        self.run_id_empty = run.id

        try:
            MINIO_CLIENT.make_bucket(BUCKET_NAME)
        except BucketAlreadyOwnedByYou:
            pass

        buffer = BytesIO()

        MINIO_CLIENT.put_object(
            bucket_name=BUCKET_NAME,
            object_name=f"experiments/{EXPERIMENT_ID}/operators/{OPERATOR_ID}/{self.run_id}/figure-000101000000000000.png",
            data=buffer,
            length=buffer.getbuffer().nbytes,
        )

        MINIO_CLIENT.put_object(
            bucket_name=BUCKET_NAME,
            object_name=f"experiments/{EXPERIMENT_ID}/operators/{OPERATOR_ID}/{self.run_id}/.metadata",
            data=buffer,
            length=buffer.getbuffer().nbytes,
        )

        MINIO_CLIENT.put_object(
            bucket_name=BUCKET_NAME,
            object_name=f"experiments/{EXPERIMENT_ID}/operators/{OPERATOR_ID}/foo/.metadata",
            data=buffer,
            length=buffer.getbuffer().nbytes,
        )

    def tearDown(self):
        kfp_experiment = kfp_client().get_experiment(experiment_name=EXPERIMENT_ID)
        kfp_client().experiments.delete_experiment(id=kfp_experiment.id)

        kfp_experiment = kfp_client().get_experiment(experiment_name=EXPERIMENT_ID_2)
        kfp_client().experiments.delete_experiment(id=kfp_experiment.id)

        MINIO_CLIENT.remove_object(
            bucket_name=BUCKET_NAME,
            object_name=f"experiments/{EXPERIMENT_ID}/operators/{OPERATOR_ID}/{self.run_id}/figure-000101000000000000.png",
        )

        MINIO_CLIENT.remove_object(
            bucket_name=BUCKET_NAME,
            object_name=f"experiments/{EXPERIMENT_ID}/operators/{OPERATOR_ID}/foo/.metadata",
        )

        MINIO_CLIENT.remove_object(
            bucket_name=BUCKET_NAME,
            object_name=f"experiments/{EXPERIMENT_ID}/operators/{OPERATOR_ID}/{self.run_id}/.metadata",
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

    def test_get_results(self):
        rv = TEST_CLIENT.get(f"/projects/unk/experiments/{EXPERIMENT_ID}/runs/{LATEST_RUN}/results")
        result = rv.json()
        expected = {"message": "The specified project does not exist"}
        self.assertDictEqual(expected, result)
        self.assertEqual(rv.status_code, 404)

        rv = TEST_CLIENT.get(f"/projects/{PROJECT_ID}/experiments/unk/runs/{LATEST_RUN}/results")
        result = rv.json()
        expected = {"message": "The specified experiment does not exist"}
        self.assertDictEqual(expected, result)
        self.assertEqual(rv.status_code, 404)

        rv = TEST_CLIENT.get(f"/projects/{PROJECT_ID}/experiments/{EXPERIMENT_ID}/runs/unk/results")
        result = rv.json()
        expected = {"message": "The specified run does not exist"}
        self.assertDictEqual(expected, result)
        self.assertEqual(rv.status_code, 404)

        rv = TEST_CLIENT.get(f"/projects/{PROJECT_ID}/experiments/{EXPERIMENT_ID_2}/runs/{self.run_id_empty}/results")
        result = rv.json()
        expected = {"message": "The specified run has no results"}
        self.assertDictEqual(expected, result)
        self.assertEqual(rv.status_code, 404)

        rv = TEST_CLIENT.get(f"/projects/{PROJECT_ID}/experiments/{EXPERIMENT_ID}/runs/{self.run_id}/results")
        self.assertEqual(rv.status_code, 200)
        self.assertEqual(
            rv.headers.get("Content-Disposition"),
            CONTENT_DISPOSITION
        )
        self.assertEqual(
            rv.headers.get("Content-Type"),
            CONTENT_TYPE
        )

        # test `run_id=latest`
        rv = TEST_CLIENT.get(f"/projects/{PROJECT_ID}/experiments/{EXPERIMENT_ID}/runs/{LATEST_RUN}/results")
        self.assertEqual(rv.status_code, 200)
        self.assertEqual(
            rv.headers.get("Content-Disposition"),
            CONTENT_DISPOSITION
        )
        self.assertEqual(
            rv.headers.get("Content-Type"),
            CONTENT_TYPE
        )

    def test_get_operators_results(self):
        rv = TEST_CLIENT.get(f"/projects/unk/experiments/{EXPERIMENT_ID}/runs/{LATEST_RUN}/operators/{OPERATOR_ID}/results")
        result = rv.json()
        expected = {"message": "The specified project does not exist"}
        self.assertDictEqual(expected, result)
        self.assertEqual(rv.status_code, 404)

        rv = TEST_CLIENT.get(f"/projects/{PROJECT_ID}/experiments/unk/runs/{LATEST_RUN}/operators/{OPERATOR_ID}/results")
        result = rv.json()
        expected = {"message": "The specified experiment does not exist"}
        self.assertDictEqual(expected, result)
        self.assertEqual(rv.status_code, 404)

        rv = TEST_CLIENT.get(f"/projects/{PROJECT_ID}/experiments/{EXPERIMENT_ID}/runs/unk/operators/{OPERATOR_ID}/results")
        result = rv.json()
        expected = {"message": "The specified run does not exist"}
        self.assertDictEqual(expected, result)
        self.assertEqual(rv.status_code, 404)

        rv = TEST_CLIENT.get(f"/projects/{PROJECT_ID}/experiments/{EXPERIMENT_ID}/runs/{LATEST_RUN}/operators/unk/results")
        result = rv.json()
        expected = {"message": "The specified operator does not exist"}
        self.assertDictEqual(expected, result)
        self.assertEqual(rv.status_code, 404)

        rv = TEST_CLIENT.get(f"/projects/{PROJECT_ID}/experiments/{EXPERIMENT_ID}/runs/{LATEST_RUN}/operators/{OPERATOR_ID_2}/results")
        result = rv.json()
        expected = {"message": "The specified operator has no results"}
        self.assertDictEqual(expected, result)
        self.assertEqual(rv.status_code, 404)

        rv = TEST_CLIENT.get(f"/projects/{PROJECT_ID}/experiments/{EXPERIMENT_ID}/runs/{self.run_id}/operators/{OPERATOR_ID}/results")
        self.assertEqual(rv.status_code, 200)
        self.assertEqual(
            rv.headers.get("Content-Disposition"),
            CONTENT_DISPOSITION
        )
        self.assertEqual(
            rv.headers.get("Content-Type"),
            CONTENT_TYPE
        )

        # test `run_id=latest`
        rv = TEST_CLIENT.get(f"/projects/{PROJECT_ID}/experiments/{EXPERIMENT_ID}/runs/{LATEST_RUN}/operators/{OPERATOR_ID}/results")
        self.assertEqual(rv.status_code, 200)
        self.assertEqual(
            rv.headers.get("Content-Disposition"),
            CONTENT_DISPOSITION
        )
        self.assertEqual(
            rv.headers.get("Content-Type"),
            CONTENT_TYPE
        )
