# -*- coding: utf-8 -*-
from json import dumps
from unittest import TestCase

from fastapi.testclient import TestClient

from projects.api.main import app
from projects.controllers.utils import uuid_alpha
from projects.database import engine

TEST_CLIENT = TestClient(app)

OPERATOR_ID = str(uuid_alpha())
OPERATOR_ID_2 = str(uuid_alpha())
OPERATOR_ID_3 = str(uuid_alpha())
NAME = "foo"
NAME_2 = "bar"
NAME_3 = "bar"
NAME_4 = "bar"
COPY_NAME = "foobar"
DEPLOYMENT_MOCK_NAME = "Foo Deployment"
DESCRIPTION = "long foo"
PROJECT_ID = str(uuid_alpha())
EXPERIMENT_ID = str(uuid_alpha())
EXPERIMENT_ID_2 = str(uuid_alpha())
EXPERIMENT_ID_3 = str(uuid_alpha())
EXPERIMENT_ID_4 = str(uuid_alpha())
DEPLOYMENT_ID = str(uuid_alpha())
DEPLOYMENT_ID_2 = str(uuid_alpha())
TEMPLATE_ID = str(uuid_alpha())
TEMPLATE_ID_2 = str(uuid_alpha())
TASK_ID = str(uuid_alpha())
TASK_ID_2 = str(uuid_alpha())
TASK_DATASET_ID = str(uuid_alpha())
TASK_DATASET_TAGS = ["DATASETS"]
TASK_DATASET_TAGS_JSON = dumps(TASK_DATASET_TAGS)
RUN_ID = str(uuid_alpha())
PARAMETERS = {"coef": 0.1, "dataset": "dataset_name.csv"}
POSITION = 0
POSITION_2 = 1
POSITION_3 = 2
POSITION_X = 0.3
POSITION_Y = 0.5
STATUS = "Pending"
URL = None
IMAGE = "platiagro/platiagro-experiment-image:0.3.0"
COMMANDS = ["CMD"]
COMMANDS_JSON = dumps(COMMANDS)
ARGUMENTS = ["ARG"]
ARGUMENTS_JSON = dumps(ARGUMENTS)
TAGS = ["PREDICTOR"]
CATEGORY = "DEFAULT"
CATEGORY_DATASET = "DATASETS"
DATA_IN = ""
DATA_OUT = ""
DOCS = ""
TAGS_JSON = dumps(TAGS)
TASKS_JSON = dumps(
    [
        {
            "uuid": OPERATOR_ID,
            "position_x": 0.0,
            "position_y": 0.0,
            "task_id": TASK_ID,
            "dependencies": [],
        },
    ]
)

TASKS_JSON_2 = dumps(
    [
        {
            "uuid": OPERATOR_ID,
            "position_x": 0.0,
            "position_y": 0.0,
            "task_id": TASK_DATASET_ID,
            "dependencies": [],
        },
        {
            "uuid": OPERATOR_ID_2,
            "position_x": 0.0,
            "position_y": 0.0,
            "task_id": TASK_ID_2,
            "dependencies": [OPERATOR_ID],
        },
    ]
)

PARAMETERS_JSON = dumps(PARAMETERS)
EXPERIMENT_NOTEBOOK_PATH = "Experiment.ipynb"
DEPLOYMENT_NOTEBOOK_PATH = "Deployment.ipynb"
CREATED_AT = "2000-01-01 00:00:00"
CREATED_AT_ISO = "2000-01-01T00:00:00"
UPDATED_AT = "2000-01-01 00:00:00"
UPDATED_AT_ISO = "2000-01-01T00:00:00"

DEPENDENCIES_EMPTY = []
DEPENDENCIES_EMPTY_JSON = dumps(DEPENDENCIES_EMPTY)
DEPENDENCIES_OP_ID = [OPERATOR_ID]
DEPENDENCIES_OP_ID_JSON = dumps(DEPENDENCIES_OP_ID)
TENANT = "anonymous"


class TestDeployments(TestCase):
    def setUp(self):
        self.maxDiff = None

        conn = engine.connect()
        text = (
            f"INSERT INTO projects (uuid, name, created_at, updated_at, tenant) "
            f"VALUES (%s, %s, %s, %s, %s)"
        )
        conn.execute(
            text,
            (
                PROJECT_ID,
                NAME,
                CREATED_AT,
                UPDATED_AT,
                TENANT,
            ),
        )

        text = (
            f"INSERT INTO experiments (uuid, name, project_id, position, is_active, created_at, updated_at) "
            f"VALUES (%s, %s, %s, %s, %s, %s, %s)"
        )
        conn.execute(
            text,
            (
                EXPERIMENT_ID,
                NAME,
                PROJECT_ID,
                POSITION,
                1,
                CREATED_AT,
                UPDATED_AT,
            ),
        )

        text = (
            f"INSERT INTO experiments (uuid, name, project_id, position, is_active, created_at, updated_at) "
            f"VALUES (%s, %s, %s, %s, %s, %s, %s)"
        )
        conn.execute(
            text,
            (
                EXPERIMENT_ID_2,
                NAME_2,
                PROJECT_ID,
                POSITION_2,
                1,
                CREATED_AT,
                UPDATED_AT,
            ),
        )

        text = (
            f"INSERT INTO experiments (uuid, name, project_id, position, is_active, created_at, updated_at) "
            f"VALUES (%s, %s, %s, %s, %s, %s, %s)"
        )
        conn.execute(
            text,
            (
                EXPERIMENT_ID_3,
                NAME_3,
                PROJECT_ID,
                POSITION_3,
                1,
                CREATED_AT,
                UPDATED_AT,
            ),
        )
        text = (
            f"INSERT INTO experiments (uuid, name, project_id, position, is_active, created_at, updated_at) "
            f"VALUES (%s, %s, %s, %s, %s, %s, %s)"
        )
        conn.execute(
            text,
            (
                EXPERIMENT_ID_4,
                NAME_3,
                PROJECT_ID,
                POSITION_3,
                1,
                CREATED_AT,
                UPDATED_AT,
            ),
        )

        text = (
            f"INSERT INTO deployments (uuid, name, project_id, experiment_id, position, is_active, status, url, created_at, updated_at) "
            f"VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
        )
        conn.execute(
            text,
            (
                DEPLOYMENT_ID,
                NAME,
                PROJECT_ID,
                EXPERIMENT_ID,
                POSITION,
                1,
                STATUS,
                URL,
                CREATED_AT,
                UPDATED_AT,
            ),
        )

        text = (
            f"INSERT INTO deployments (uuid, name, project_id, experiment_id, position, is_active, status, url, created_at, updated_at) "
            f"VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
        )
        conn.execute(
            text,
            (
                DEPLOYMENT_ID_2,
                NAME_2,
                PROJECT_ID,
                EXPERIMENT_ID,
                POSITION,
                1,
                STATUS,
                URL,
                CREATED_AT,
                UPDATED_AT,
            ),
        )

        text = (
            f"INSERT INTO tasks (uuid, name, description, image, commands, arguments, category, "
            f"tags, data_in, data_out, docs, parameters, experiment_notebook_path, "
            f"deployment_notebook_path, cpu_limit, cpu_request, memory_limit, memory_request, "
            f"readiness_probe_initial_delay_seconds, is_default, created_at, updated_at) "
            f"VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
        )
        conn.execute(
            text,
            (
                TASK_ID,
                NAME,
                DESCRIPTION,
                IMAGE,
                COMMANDS_JSON,
                ARGUMENTS_JSON,
                CATEGORY,
                TAGS_JSON,
                DATA_IN,
                DATA_OUT,
                DOCS,
                dumps([]),
                EXPERIMENT_NOTEBOOK_PATH,
                DEPLOYMENT_NOTEBOOK_PATH,
                "100m",
                "100m",
                "1Gi",
                "1Gi",
                300,
                0,
                CREATED_AT,
                UPDATED_AT,
            ),
        )

        text = (
            f"INSERT INTO tasks (uuid, name, description, image, commands, arguments, category, "
            f"tags, data_in, data_out, docs, parameters, experiment_notebook_path, "
            f"deployment_notebook_path, cpu_limit, cpu_request, memory_limit, memory_request, "
            f"readiness_probe_initial_delay_seconds, is_default, created_at, updated_at) "
            f"VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
        )
        conn.execute(
            text,
            (
                TASK_ID_2,
                NAME,
                DESCRIPTION,
                IMAGE,
                COMMANDS_JSON,
                ARGUMENTS_JSON,
                CATEGORY,
                TAGS_JSON,
                DATA_IN,
                DATA_OUT,
                DOCS,
                dumps([]),
                EXPERIMENT_NOTEBOOK_PATH,
                DEPLOYMENT_NOTEBOOK_PATH,
                "100m",
                "100m",
                "1Gi",
                "1Gi",
                300,
                0,
                CREATED_AT,
                UPDATED_AT,
            ),
        )

        text = (
            f"INSERT INTO tasks (uuid, name, description, image, commands, arguments, category, "
            f"tags, data_in, data_out, docs, parameters, experiment_notebook_path, "
            f"deployment_notebook_path, cpu_limit, cpu_request, memory_limit, memory_request, "
            f"readiness_probe_initial_delay_seconds, is_default, created_at, updated_at) "
            f"VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
        )

        conn.execute(
            text,
            (
                TASK_DATASET_ID,
                NAME,
                DESCRIPTION,
                IMAGE,
                COMMANDS_JSON,
                ARGUMENTS_JSON,
                CATEGORY_DATASET,
                TASK_DATASET_TAGS_JSON,
                DATA_IN,
                DATA_OUT,
                DOCS,
                dumps([]),
                EXPERIMENT_NOTEBOOK_PATH,
                DEPLOYMENT_NOTEBOOK_PATH,
                "100m",
                "100m",
                "1Gi",
                "1Gi",
                300,
                0,
                CREATED_AT,
                UPDATED_AT,
            ),
        )

        text = (
            f"INSERT INTO operators (uuid, name, status, status_message, deployment_id, task_id, parameters, position_x, position_y, dependencies, created_at, updated_at) "
            f"VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
        )
        conn.execute(
            text,
            (
                OPERATOR_ID,
                None,
                "Unset",
                None,
                DEPLOYMENT_ID,
                TASK_ID,
                PARAMETERS_JSON,
                POSITION_X,
                POSITION_Y,
                DEPENDENCIES_EMPTY_JSON,
                CREATED_AT,
                UPDATED_AT,
            ),
        )

        text = (
            f"INSERT INTO operators (uuid, name, status, status_message, experiment_id, task_id, parameters, position_x, position_y, dependencies, created_at, updated_at) "
            f"VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
        )
        conn.execute(
            text,
            (
                OPERATOR_ID_2,
                None,
                "Unset",
                None,
                EXPERIMENT_ID_2,
                TASK_ID,
                PARAMETERS_JSON,
                POSITION_X,
                POSITION_Y,
                DEPENDENCIES_EMPTY_JSON,
                CREATED_AT,
                UPDATED_AT,
            ),
        )

        text = (
            f"INSERT INTO operators (uuid, name, status, status_message, experiment_id, task_id, parameters, position_x, position_y, dependencies, created_at, updated_at) "
            f"VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
        )
        conn.execute(
            text,
            (
                OPERATOR_ID_3,
                None,
                "Unset",
                None,
                EXPERIMENT_ID_4,
                TASK_DATASET_ID,
                PARAMETERS_JSON,
                POSITION_X,
                POSITION_Y,
                DEPENDENCIES_EMPTY_JSON,
                CREATED_AT,
                UPDATED_AT,
            ),
        )

        text = (
            f"INSERT INTO templates (uuid, name, tasks, deployment_id, created_at, updated_at, tenant) "
            f"VALUES (%s, %s, %s, %s, %s, %s, %s)"
        )
        conn.execute(
            text,
            (
                TEMPLATE_ID,
                NAME,
                TASKS_JSON,
                DEPLOYMENT_ID,
                CREATED_AT,
                UPDATED_AT,
                TENANT,
            ),
        )

        text = (
            f"INSERT INTO templates (uuid, name, tasks, deployment_id, created_at, updated_at, tenant) "
            f"VALUES (%s, %s, %s, %s, %s, %s, %s)"
        )
        conn.execute(
            text,
            (
                TEMPLATE_ID_2,
                NAME,
                TASKS_JSON_2,
                DEPLOYMENT_ID,
                CREATED_AT,
                UPDATED_AT,
                TENANT,
            ),
        )

        conn.close()

    def tearDown(self):
        conn = engine.connect()

        text = f"DELETE FROM templates WHERE uuid = '{TEMPLATE_ID}'"
        conn.execute(text)

        text = f"DELETE FROM templates WHERE uuid = '{TEMPLATE_ID_2}'"
        conn.execute(text)

        text = (
            f"DELETE FROM operators WHERE experiment_id in"
            f"(SELECT uuid FROM experiments where project_id = '{PROJECT_ID}')"
        )
        conn.execute(text)

        text = (
            f"DELETE FROM operators WHERE deployment_id in"
            f"(SELECT uuid FROM deployments where project_id = '{PROJECT_ID}')"
        )
        conn.execute(text)

        text = f"DELETE FROM tasks WHERE uuid IN ('{TASK_ID}', '{TASK_DATASET_ID}', '{TASK_ID_2}')"
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
        rv = TEST_CLIENT.get(f"/projects/foo/deployments")
        result = rv.json()
        self.assertEqual(rv.status_code, 404)

        rv = TEST_CLIENT.get(f"/projects/{PROJECT_ID}/deployments")
        result = rv.json()
        self.assertIsInstance(result["deployments"], list)
        self.assertIsInstance(result["total"], int)
        self.assertEqual(rv.status_code, 200)

    def test_create_deployment(self):
        rv = TEST_CLIENT.post(f"/projects/foo/deployments", json={})
        result = rv.json()
        self.assertEqual(rv.status_code, 404)

        rv = TEST_CLIENT.post(
            f"/projects/{PROJECT_ID}/deployments",
            json={
                "templateId": "mock",
            },
        )
        result = rv.json()
        self.assertIsInstance(result, dict)
        self.assertEqual(rv.status_code, 404)

        rv = TEST_CLIENT.post(
            f"/projects/{PROJECT_ID}/deployments",
            json={
                "copyFrom": "unk",
            },
        )
        result = rv.json()
        self.assertEqual(rv.status_code, 400)

        rv = TEST_CLIENT.post(
            f"/projects/{PROJECT_ID}/deployments",
            json={
                "experiments": [],
            },
        )
        result = rv.json()
        self.assertIsInstance(result, dict)
        self.assertEqual(rv.status_code, 400)

        rv = TEST_CLIENT.post(
            f"/projects/{PROJECT_ID}/deployments",
            json={
                "experiments": ["unk"],
            },
        )
        result = rv.json()
        self.assertIsInstance(result, dict)
        self.assertEqual(rv.status_code, 400)

        # experiment with no operator at all!
        rv = TEST_CLIENT.post(
            f"/projects/{PROJECT_ID}/deployments",
            json={
                "experiments": [EXPERIMENT_ID_3],
            },
        )
        result = rv.json()
        expected = {"message": "Necessary at least one operator."}
        self.assertDictEqual(expected, result)
        self.assertEqual(rv.status_code, 400)

        # experiment with only datasource operator
        rv = TEST_CLIENT.post(
            f"/projects/{PROJECT_ID}/deployments",
            json={
                "experiments": [EXPERIMENT_ID_4],
            },
        )
        result = rv.json()
        expected = {"message": "Necessary at least one operator that is not a data source."}
        self.assertDictEqual(expected, result)
        self.assertEqual(rv.status_code, 400)

        rv = TEST_CLIENT.post(
            f"/projects/{PROJECT_ID}/deployments",
            json={
                "experiments": [EXPERIMENT_ID_2],
            },
        )
        result = rv.json()["deployments"]
        self.assertIsInstance(result, list)
        self.assertIn("operators", result[0])
        operators_list = result[0]["operators"]

        # setting default values to boolean variables
        created_operator_contains_dataset_task = False
        some_operator_depends_on_the_dataset = False

        dependencies_map = {}
        deployment_tasks = []
        source_tasks = [TASK_ID, ]

        for operator in operators_list:

            operator_name = operator.get("name")
            operator_dependencies = operator.get('dependencies')
            operator_task_id = operator.get("taskId")

            if operator_name == "Fonte de dados":
                created_operator_contains_dataset_task = True
                dataset_operator_uuid = operator.get("uuid")
            elif operator_task_id in source_tasks:
                dependencies_map.update({
                    operator.get('uuid'): operator_dependencies,
                    })
                deployment_tasks.append(operator_task_id)
            else:
                raise Exception("Non-datasource task in the deployment that is not contained in the experiment")

        for dependencies_list in dependencies_map.values():
            non_dataset_operators_have_dependencies = True if dependencies_list else False
            if dataset_operator_uuid in dependencies_list:
                some_operator_depends_on_the_dataset = True

        # ensuring that all operators except dataset has dependency
        self.assertTrue(non_dataset_operators_have_dependencies)

        # ensuring at least one operator depends on the dataset
        self.assertTrue(some_operator_depends_on_the_dataset)

        # ensuring that deployment has a dataset operator
        self.assertTrue(created_operator_contains_dataset_task)

        # ensuring that deployment and experiment has the same non-datasource tasks
        self.assertListEqual(source_tasks, deployment_tasks)

        # deployments from template
        rv = TEST_CLIENT.post(
            f"/projects/{PROJECT_ID}/deployments", json={"templateId": TEMPLATE_ID}
        )
        result = rv.json()["deployments"]
        self.assertIsInstance(result, list)
        self.assertEqual(rv.status_code, 200)

        # With templates that have operators with dependencies
        rv = TEST_CLIENT.post(
            f"/projects/{PROJECT_ID}/deployments", json={"templateId": TEMPLATE_ID_2}
        )
        result = rv.json()["deployments"]
        self.assertIsInstance(result, list)
        self.assertIn("operators", result[0])

        rv = TEST_CLIENT.post(
            f"/projects/{PROJECT_ID}/deployments",
            json={
                "copyFrom": DEPLOYMENT_ID,
            },
        )
        result = rv.json()
        self.assertEqual(rv.status_code, 400)

        rv = TEST_CLIENT.post(
            f"/projects/{PROJECT_ID}/deployments",
            json={
                "copyFrom": DEPLOYMENT_ID,
                "name": NAME,
            },
        )
        result = rv.json()
        self.assertEqual(rv.status_code, 400)

        rv = TEST_CLIENT.post(
            f"/projects/{PROJECT_ID}/deployments",
            json={
                "copyFrom": DEPLOYMENT_ID,
                "name": COPY_NAME,
            },
        )

        result = rv.json()["deployments"]

        self.assertIsInstance(result, list)
        self.assertEqual(COPY_NAME, result[0]["name"])
        self.assertIn("operators", result[0])
        self.assertEqual(rv.status_code, 200)

        operators_list = result[0]["operators"]

        # setting default values to boolean variables
        created_operator_contains_dataset_task = False
        some_operator_depends_on_the_dataset = False

        dependencies_map = {}
        deployment_tasks = []
        source_tasks = [TASK_ID, ]

        for operator in operators_list:

            operator_name = operator.get("name")
            operator_dependencies = operator.get('dependencies')
            operator_task_id = operator.get("taskId")

            if operator_name == "Fonte de dados":
                created_operator_contains_dataset_task = True
                dataset_operator_uuid = operator.get("uuid")
            elif operator_task_id in source_tasks:
                dependencies_map.update({
                    operator.get('uuid'): operator_dependencies,
                    })
                deployment_tasks.append(operator_task_id)
            else:
                raise Exception("Non-datasource task in the deployment that is not contained in the experiment")

        for dependencies_list in dependencies_map.values():
            non_dataset_operators_have_dependencies = True if dependencies_list else False
            if dataset_operator_uuid in dependencies_list:
                some_operator_depends_on_the_dataset = True

        # ensuring that all operators except dataset has dependency
        self.assertTrue(non_dataset_operators_have_dependencies)

        # ensuring at least one operator depends on the dataset
        self.assertTrue(some_operator_depends_on_the_dataset)

        # ensuring that deployment has a dataset operator
        self.assertTrue(created_operator_contains_dataset_task)

        # ensuring that deployment and experiment has the same non-datasource tasks
        self.assertListEqual(source_tasks, deployment_tasks)

    def test_get_deployment(self):
        rv = TEST_CLIENT.get(f"/projects/foo/deployments/{DEPLOYMENT_ID}")
        result = rv.json()
        self.assertEqual(rv.status_code, 404)

        rv = TEST_CLIENT.get(f"/projects/foo/deployments/foo-bar")
        result = rv.json()
        expected = {"message": "The specified project does not exist"}
        self.assertDictEqual(expected, result)
        self.assertEqual(rv.status_code, 404)

        rv = TEST_CLIENT.get(f"/projects/{PROJECT_ID}/deployments/foo")
        result = rv.json()
        expected = {"message": "The specified deployment does not exist"}
        self.assertIsInstance(result, dict)
        self.assertDictEqual(expected, result)
        self.assertEqual(rv.status_code, 404)

        rv = TEST_CLIENT.get(f"/projects/{PROJECT_ID}/deployments/{DEPLOYMENT_ID}")
        result = rv.json()
        self.assertIsInstance(result, dict)
        self.assertEqual(rv.status_code, 200)

    def test_delete_deployment(self):
        rv = TEST_CLIENT.get(f"/projects/foo/deployments/{DEPLOYMENT_ID}")
        result = rv.json()
        expected = {"message": "The specified project does not exist"}
        self.assertEqual(rv.status_code, 404)

        rv = TEST_CLIENT.delete(f"/projects/{PROJECT_ID}/deployments/buz-qux")
        result = rv.json()
        expected = {"message": "The specified deployment does not exist"}
        self.assertDictEqual(expected, result)
        self.assertEqual(rv.status_code, 404)

        rv = TEST_CLIENT.delete(f"/projects/{PROJECT_ID}/deployments/{DEPLOYMENT_ID}")
        result = rv.json()
        expected = {"message": "Deployment deleted"}
        self.assertDictEqual(expected, result)
        self.assertEqual(rv.status_code, 200)

    def test_update_deployment(self):
        rv = TEST_CLIENT.patch(f"/projects/foo/deployments/{DEPLOYMENT_ID}", json={})
        result = rv.json()
        expected = {"message": "The specified project does not exist"}
        self.assertEqual(rv.status_code, 404)

        rv = TEST_CLIENT.patch(f"/projects/{PROJECT_ID}/deployments/buz-qux", json={})
        result = rv.json()
        expected = {"message": "The specified deployment does not exist"}
        self.assertDictEqual(expected, result)
        self.assertEqual(rv.status_code, 404)

        rv = TEST_CLIENT.patch(
            f"/projects/{PROJECT_ID}/deployments/{DEPLOYMENT_ID_2}", json={"name": NAME}
        )
        result = rv.json()
        expected = {"message": "a deployment with that name already exists"}
        self.assertDictEqual(expected, result)
        self.assertEqual(rv.status_code, 400)

        rv = TEST_CLIENT.patch(
            f"/projects/{PROJECT_ID}/deployments/{DEPLOYMENT_ID}",
            json={"name": "Foo Bar"},
        )
        result = rv.json()
        self.assertIsInstance(result, dict)
        self.assertEqual(rv.status_code, 200)
