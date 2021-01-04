# -*- coding: utf-8 -*-
from json import dumps
from unittest import TestCase

from projects.api.main import app
from projects.controllers.utils import uuid_alpha
from projects.database import engine
from projects.kfp import KFP_CLIENT
from projects.object_storage import BUCKET_NAME

OPERATOR_ID = str(uuid_alpha())
OPERATOR_ID_2 = str(uuid_alpha())
NAME = "foo"
NAME_2 = "bar"
DEPLOYMENT_MOCK_NAME = "Foo Deployment"
DESCRIPTION = "long foo"
PROJECT_ID = str(uuid_alpha())
EXPERIMENT_ID = str(uuid_alpha())
EXPERIMENT_ID_2 = str(uuid_alpha())
DEPLOYMENT_ID = str(uuid_alpha())
DEPLOYMENT_ID_2 = str(uuid_alpha())
TASK_ID = str(uuid_alpha())
RUN_ID = str(uuid_alpha())
PARAMETERS = {"coef": 0.1, "dataset": "dataset_name.csv"}
POSITION = 0
POSITION_2 = 1
POSITION_X = 0.3
POSITION_Y = 0.5
IMAGE = "platiagro/platiagro-experiment-image:0.2.0"
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


class TestDeployments(TestCase):
    def setUp(self):
        self.maxDiff = None

        with open("tests/resources/mocked_deployment.yaml", "r") as file:
            content = file.read()

        content = content.replace("$deploymentId", DEPLOYMENT_ID)
        with open("tests/resources/mocked.yaml", "w") as file:
            file.write(content)

        # Run a default pipeline for tests
        kfp_experiment = KFP_CLIENT.create_experiment(name=DEPLOYMENT_ID)
        KFP_CLIENT.run_pipeline(
            experiment_id=kfp_experiment.id,
            job_name=DEPLOYMENT_ID,
            pipeline_package_path="tests/resources/mocked.yaml",
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
            f"INSERT INTO experiments (uuid, name, project_id, position, is_active, created_at, updated_at) "
            f"VALUES ('{EXPERIMENT_ID_2}', '{NAME_2}', '{PROJECT_ID}', '{POSITION_2}', 1, '{CREATED_AT}', '{UPDATED_AT}')"
        )
        conn.execute(text)

        text = (
            f"INSERT INTO deployments (uuid, name, project_id, experiment_id, position, is_active, created_at, updated_at) "
            f"VALUES ('{DEPLOYMENT_ID}', '{NAME}', '{PROJECT_ID}', '{EXPERIMENT_ID}', '{POSITION}', 1, '{CREATED_AT}', '{UPDATED_AT}')"
        )
        conn.execute(text)

        text = (
            f"INSERT INTO deployments (uuid, name, project_id, experiment_id, position, is_active, created_at, updated_at) "
            f"VALUES ('{DEPLOYMENT_ID_2}', '{NAME_2}', '{PROJECT_ID}', '{EXPERIMENT_ID}', '{POSITION}', 1, '{CREATED_AT}', '{UPDATED_AT}')"
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
            f"INSERT INTO operators (uuid, deployment_id, task_id, parameters, position_x, position_y, created_at, updated_at, dependencies) "
            f"VALUES ('{OPERATOR_ID}', '{DEPLOYMENT_ID}', '{TASK_ID}', '{PARAMETERS_JSON}', '{POSITION_X}', "
            f"'{POSITION_Y}', '{CREATED_AT}', '{UPDATED_AT}', '{DEPENDENCIES_EMPTY_JSON}')"
        )
        conn.execute(text)

        text = (
            f"INSERT INTO operators (uuid, experiment_id, task_id, parameters, position_x, position_y, created_at, updated_at, dependencies) "
            f"VALUES ('{OPERATOR_ID_2}', '{EXPERIMENT_ID_2}', '{TASK_ID}', '{PARAMETERS_JSON}', '{POSITION_X}', "
            f"'{POSITION_Y}', '{CREATED_AT}', '{UPDATED_AT}', '{DEPENDENCIES_EMPTY_JSON}')"
        )
        conn.execute(text)
        conn.close()

    def tearDown(self):
        conn = engine.connect()

        text = f"DELETE FROM operators WHERE experiment_id in" \
               f"(SELECT uuid FROM experiments where project_id = '{PROJECT_ID}')"
        conn.execute(text)

        text = f"DELETE FROM operators WHERE deployment_id in" \
               f"(SELECT uuid FROM deployments where project_id = '{PROJECT_ID}')"
        conn.execute(text)

        text = f"DELETE FROM tasks WHERE uuid IN ('{TASK_ID}', '{TASK_DATASET_ID}')"
        conn.execute(text)

        text = f"DELETE FROM deployments WHERE project_id = '{PROJECT_ID}'"
        conn.execute(text)

        text = f"DELETE FROM deployments WHERE name = '{DEPLOYMENT_MOCK_NAME}'"
        conn.execute(text)

        text = f"DELETE FROM experiments WHERE project_id = '{PROJECT_ID}'"
        conn.execute(text)

        text = f"DELETE FROM projects WHERE uuid = '{PROJECT_ID}'"
        conn.execute(text)
        conn.close()

    def test_list_deployments(self):
        with app.test_client() as c:
            rv = c.get(f"/projects/foo/deployments")
            result = rv.get_json()
            expected = {"message": "The specified project does not exist"}
            self.assertEqual(rv.status_code, 404)

            rv = c.get(f"/projects/{PROJECT_ID}/deployments")
            result = rv.get_json()
            self.assertIsInstance(result, list)
            self.assertEqual(rv.status_code, 200)

    def test_create_deployment(self):
        with app.test_client() as c:
            rv = c.post(f"/projects/foo/deployments")
            result = rv.get_json()
            expected = {"message": "The specified project does not exist"}
            self.assertEqual(rv.status_code, 400)

            rv = c.post(f"/projects/{PROJECT_ID}/deployments", json={
                "templateId": "mock",
            })
            result = rv.get_json()
            expected = {"message": "templateId is not implemented yet"}
            self.assertIsInstance(result, dict)
            self.assertEqual(rv.status_code, 400)

            rv = c.post(f"/projects/{PROJECT_ID}/deployments", json={
                "experiments": [],
            })
            result = rv.get_json()
            expected = {"message": "experiments were not specified"}
            self.assertIsInstance(result, dict)
            self.assertEqual(rv.status_code, 400)

            rv = c.post(f"/projects/{PROJECT_ID}/deployments", json={
                "experiments": ["unk"],
            })
            result = rv.get_json()
            expected = {"message": "some experiments do not exist"}
            self.assertIsInstance(result, dict)
            self.assertEqual(rv.status_code, 400)

            rv = c.post(f"/projects/{PROJECT_ID}/deployments", json={
                "experiments": [EXPERIMENT_ID_2],
            })
            result = rv.get_json()
            self.assertIsInstance(result, list)
            self.assertIn("operators", result[0])
            operator = result[0]["operators"][0]
            self.assertEqual(TASK_ID, operator["taskId"])

    def test_get_deployment(self):
        with app.test_client() as c:
            rv = c.get(f"/projects/foo/deployments/{DEPLOYMENT_ID}")
            result = rv.get_json()
            expected = {"message": "The specified project does not exist"}
            self.assertEqual(rv.status_code, 404)

            rv = c.get(f"/projects/foo/deployments/foo-bar")
            result = rv.get_json()
            expected = {"message": "The specified deployment does not exist"}
            self.assertEqual(rv.status_code, 404)

            rv = c.get(f"/projects/{PROJECT_ID}/deployments/{DEPLOYMENT_ID}")
            result = rv.get_json()
            self.assertIsInstance(result, dict)
            self.assertEqual(rv.status_code, 200)

    def test_delete_deployment(self):
        with app.test_client() as c:
            rv = c.get(f"/projects/foo/deployments/{DEPLOYMENT_ID}")
            result = rv.get_json()
            expected = {"message": "The specified project does not exist"}
            self.assertEqual(rv.status_code, 404)

            rv = c.delete(f"/projects/{PROJECT_ID}/deployments/buz-qux")
            result = rv.get_json()
            expected = {"message": "The specified deployment does not exist"}
            self.assertDictEqual(expected, result)
            self.assertEqual(rv.status_code, 404)

            rv = c.delete(f"/projects/{PROJECT_ID}/deployments/{DEPLOYMENT_ID}")
            result = rv.get_json()
            expected = {"message": "Deployment deleted"}
            self.assertDictEqual(expected, result)
            self.assertEqual(rv.status_code, 200)

    def test_update_deployment(self):
        with app.test_client() as c:
            rv = c.patch(f"/projects/foo/deployments/{DEPLOYMENT_ID}", json={})
            result = rv.get_json()
            expected = {"message": "The specified project does not exist"}
            self.assertEqual(rv.status_code, 404)

            rv = c.patch(f"/projects/{PROJECT_ID}/deployments/buz-qux", json={})
            result = rv.get_json()
            expected = {"message": "The specified deployment does not exist"}
            self.assertDictEqual(expected, result)
            self.assertEqual(rv.status_code, 404)

            rv = c.patch(f"/projects/{PROJECT_ID}/deployments/{DEPLOYMENT_ID_2}", json={"name": NAME})
            result = rv.get_json()
            expected = {"message": "a deployment with that name already exists"}
            self.assertDictEqual(expected, result)
            self.assertEqual(rv.status_code, 400)

            rv = c.patch(f"/projects/{PROJECT_ID}/deployments/{DEPLOYMENT_ID}", json={"name": "Foo Bar"})
            result = rv.get_json()
            self.assertIsInstance(result, dict)
            self.assertEqual(rv.status_code, 200)
