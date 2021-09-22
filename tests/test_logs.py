# -*- coding: utf-8 -*-
import unittest
import unittest.mock as mock

from fastapi.testclient import TestClient

from projects.api.main import app
from projects.database import session_scope

import tests.util as util

app.dependency_overrides[session_scope] = util.override_session_scope
TEST_CLIENT = TestClient(app)


class TestLogs(unittest.TestCase):
    maxDiff = None

    # def setUp(self):
    #     self.maxDiff = None

    #     conn = engine.connect()
    #     text = (
    #         f"INSERT INTO projects (uuid, name, description, created_at, updated_at, tenant) "
    #         f"VALUES (%s, %s, %s, %s, %s, %s)"
    #     )
    #     conn.execute(text, (PROJECT_ID, NAME, DESCRIPTION, CREATED_AT, UPDATED_AT, TENANT,))

    #     text = (
    #         f"INSERT INTO experiments (uuid, name, project_id, position, is_active, created_at, updated_at) "
    #         f"VALUES (%s, %s, %s, %s, %s, %s, %s)"
    #     )
    #     conn.execute(text, (EXPERIMENT_ID, EXPERIMENT_NAME, PROJECT_ID, 0, 1, CREATED_AT, UPDATED_AT,))

    #     text = (
    #         f"INSERT INTO deployments (uuid, name, project_id, experiment_id, position, is_active, status, url, created_at, updated_at) "
    #         f"VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
    #     )
    #     conn.execute(text, (DEPLOYMENT_ID, NAME, PROJECT_ID, EXPERIMENT_ID, 0, 1, STATUS, URL, CREATED_AT, UPDATED_AT,))

    #     text = (
    #         f"INSERT INTO tasks (uuid, name, description, image, commands, arguments, category, tags, data_in, data_out, docs, parameters, "
    #         f"experiment_notebook_path, deployment_notebook_path, cpu_limit, cpu_request, memory_limit, memory_request, "
    #         f"readiness_probe_initial_delay_seconds, is_default, created_at, updated_at) "
    #         f"VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
    #     )
    #     conn.execute(text, (TASK_ID, NAME, DESCRIPTION, IMAGE, None, None, CATEGORY, TAGS_JSON, DATA_IN, DATA_OUT, DOCS, dumps([]),
    #                         EXPERIMENT_NOTEBOOK_PATH, EXPERIMENT_NOTEBOOK_PATH, "100m", "100m", "1Gi", "1Gi", 300, 0, CREATED_AT, UPDATED_AT,))

    #     text = (
    #         f"INSERT INTO operators (uuid, name, status, status_message, experiment_id, task_id, parameters, position_x, position_y, dependencies, created_at, updated_at) "
    #         f"VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
    #     )
    #     conn.execute(text, (OPERATOR_ID, None, "Unset", None, EXPERIMENT_ID, TASK_ID, PARAMETERS_JSON, POSITION_X,
    #                         POSITION_Y, DEPENDENCIES_OP_ID_JSON, CREATED_AT, UPDATED_AT,))

    #     text = (
    #         f"INSERT INTO operators (uuid, name, status, status_message, deployment_id, task_id, parameters, position_x, position_y, dependencies, created_at, updated_at) "
    #         f"VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
    #     )
    #     conn.execute(text, (OPERATOR_ID_2, None, "Unset", None, DEPLOYMENT_ID, TASK_ID, PARAMETERS_JSON,
    #                         POSITION_X, POSITION_Y, DEPENDENCIES_OP_ID_JSON, CREATED_AT, UPDATED_AT,))
    #     conn.close()

    #     # Creates pipelines for log generation
    #     with open("tests/resources/mocked_experiment.yaml", "r") as file:
    #         content = file.read()
    #     content = content.replace("$experimentId", EXPERIMENT_ID)
    #     content = content.replace("$taskName", NAME)
    #     content = content.replace("$operatorId", OPERATOR_ID)
    #     content = content.replace("$image", IMAGE)
    #     with open("tests/resources/mocked.yaml", "w") as file:
    #         file.write(content)
    #     kfp_experiment = kfp_client().create_experiment(name=EXPERIMENT_ID)
    #     kfp_client().run_pipeline(
    #         experiment_id=kfp_experiment.id,
    #         job_name=f"experiment-{EXPERIMENT_ID}",
    #         pipeline_package_path="tests/resources/mocked.yaml",
    #     )

    #     with open("tests/resources/mocked_deployment.yaml", "r") as file:
    #         content = file.read()
    #     content = content.replace("$deploymentId", DEPLOYMENT_ID)
    #     content = content.replace("$taskName", NAME)
    #     content = content.replace("$operatorId", OPERATOR_ID_2)
    #     with open("tests/resources/mocked.yaml", "w") as file:
    #         file.write(content)
    #     kfp_experiment = kfp_client().create_experiment(name=DEPLOYMENT_ID)
    #     kfp_client().run_pipeline(
    #         experiment_id=kfp_experiment.id,
    #         job_name=f"deployment-{DEPLOYMENT_ID}",
    #         pipeline_package_path="tests/resources/mocked.yaml",
    #     )

    # def tearDown(self):
    #     kfp_experiment = kfp_client().get_experiment(experiment_name=EXPERIMENT_ID)
    #     kfp_client().experiments.delete_experiment(id=kfp_experiment.id)

    #     kfp_experiment = kfp_client().get_experiment(experiment_name=DEPLOYMENT_ID)
    #     kfp_client().experiments.delete_experiment(id=kfp_experiment.id)

    #     conn = engine.connect()
    #     text = f"DELETE FROM operators WHERE uuid IN ('{OPERATOR_ID}', '{OPERATOR_ID_2}')"
    #     conn.execute(text)

    #     text = f"DELETE FROM deployments WHERE uuid = '{DEPLOYMENT_ID}'"
    #     conn.execute(text)

    #     text = f"DELETE FROM experiments WHERE uuid = '{EXPERIMENT_ID}'"
    #     conn.execute(text)

    #     text = f"DELETE FROM tasks WHERE uuid = '{TASK_ID}'"
    #     conn.execute(text)

    #     text = f"DELETE FROM projects WHERE uuid = '{PROJECT_ID}'"
    #     conn.execute(text)
    #     conn.close()

    # def test_list_logs(self):

    #     was_expected_log_found = False
    #     for _ in range(TIMEOUT):
    #         rv = TEST_CLIENT.get(f"/projects/{PROJECT_ID}/experiments/{EXPERIMENT_ID}/runs/latest/logs")

    #         #  If not 200, let's make sure it's because the pipeline hasn't even started
    #         if rv.status_code != 200:
    #             self.assertEqual(rv.status_code, 500)
    #             self.assertRaises(TypeError)

    #             tolerable_error_keytext = "the server could not find the requested resource"
    #             result = rv.json().get('message')
    #             self.assertIn(tolerable_error_keytext, result)
    #             continue

    #         result = rv.json()
    #         result_logs = result.get("logs")
    #         expected = {
    #             "level": "INFO",
    #             "title": NAME,
    #             "message": "hello\nhello",
    #         }
    #         log = result_logs[0]

    #         # the keys 'title' and 'created_at' from json are machine-generated
    #         # we assert they exist, but we don't assert their values
    #         # to compare the log with result we have to eliminate this key
    #         machine_generated = ["createdAt"]
    #         for attr in machine_generated:
    #             self.assertIn(attr, log)
    #             del log[attr]

    #         self.assertIn(log.get('level').lower(), LOG_LEVELS.keys())
    #         if log == expected:
    #             was_expected_log_found = True
    #             break

    #         # code logic must handle exception regarding container creation, returning 200
    #         rv = TEST_CLIENT.get(f"/projects/{PROJECT_ID}/deployments/{DEPLOYMENT_ID}/runs/latest/logs")
    #         self.assertEqual(rv.status_code, 200)

    #         time.sleep(1)

    #     # making sure we found expected log before timeout
    #     self.assertTrue(was_expected_log_found)
