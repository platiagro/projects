# -*- coding: utf-8 -*-
import unittest
import unittest.mock as mock

from fastapi.testclient import TestClient

from projects.api.main import app
from projects.database import session_scope

import tests.util as util

app.dependency_overrides[session_scope] = util.override_session_scope
TEST_CLIENT = TestClient(app)


class TestMonitorings(unittest.TestCase):
    maxDiff = None

    # def setUp(self):
    #     self.maxDiff = None
    #     conn = engine.connect()
    #     text = (
    #         f"INSERT INTO tasks (uuid, name, description, image, commands, arguments, category, tags, data_in, data_out, docs, parameters, "
    #         f"experiment_notebook_path, deployment_notebook_path, cpu_limit, cpu_request, memory_limit, memory_request, "
    #         f"readiness_probe_initial_delay_seconds, is_default, created_at, updated_at) "
    #         f"VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
    #     )
    #     conn.execute(text, (TASK_ID, NAME, DESCRIPTION, IMAGE, None, None, CATEGORY, TAGS_JSON, DATA_IN, DATA_OUT, DOCS, PARAMETERS_JSON,
    #                         EXPERIMENT_NOTEBOOK_PATH, DEPLOYMENT_NOTEBOOK_PATH, "100m", "100m", "1Gi", "1Gi", 300, 0, CREATED_AT, UPDATED_AT,))

    #     text = (
    #         f"INSERT INTO tasks (uuid, name, description, image, commands, arguments, category, tags, data_in, data_out, docs, parameters, "
    #         f"experiment_notebook_path, deployment_notebook_path, cpu_limit, cpu_request, memory_limit, memory_request, "
    #         f"readiness_probe_initial_delay_seconds, is_default, created_at, updated_at) "
    #         f"VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
    #     )
    #     conn.execute(text, (TASK_ID_2, NAME, DESCRIPTION, IMAGE, None, None, CATEGORY, TAGS_JSON, DATA_IN, DATA_OUT, DOCS, PARAMETERS_JSON,
    #                         EXPERIMENT_NOTEBOOK_PATH, DEPLOYMENT_NOTEBOOK_PATH, "100m", "100m", "1Gi", "1Gi", 300, 0, CREATED_AT, UPDATED_AT,))

    #     text = (
    #         f"INSERT INTO projects (uuid, name, created_at, updated_at, tenant) "
    #         f"VALUES (%s, %s, %s, %s, %s)"
    #     )
    #     conn.execute(text, (PROJECT_ID, NAME, CREATED_AT, UPDATED_AT, TENANT,))

    #     text = (
    #         f"INSERT INTO experiments (uuid, name, project_id, position, is_active, created_at, updated_at) "
    #         f"VALUES (%s, %s, %s, %s, %s, %s, %s)"
    #     )
    #     conn.execute(text, (EXPERIMENT_ID, NAME, PROJECT_ID, POSITION, 1, CREATED_AT, UPDATED_AT,))

    #     text = (
    #         f"INSERT INTO deployments (uuid, name, project_id, experiment_id, position, is_active, status, url, created_at, updated_at) "
    #         f"VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
    #     )
    #     conn.execute(text, (DEPLOYMENT_ID, NAME, PROJECT_ID, EXPERIMENT_ID, POSITION, 1, STATUS, URL, CREATED_AT, UPDATED_AT,))

    #     text = (
    #         f"INSERT INTO monitorings (uuid, deployment_id, task_id, created_at) "
    #         f"VALUES (%s, %s, %s, %s)"
    #     )
    #     conn.execute(text, (MONITORING_ID, DEPLOYMENT_ID, TASK_ID, CREATED_AT))

    #     conn.close()

    # def tearDown(self):
    #     conn = engine.connect()

    #     text = f"DELETE FROM monitorings WHERE deployment_id = '{DEPLOYMENT_ID}'"
    #     conn.execute(text)

    #     text = f"DELETE FROM deployments WHERE project_id = '{PROJECT_ID}'"
    #     conn.execute(text)

    #     text = f"DELETE FROM experiments WHERE project_id in ('{PROJECT_ID}')"
    #     conn.execute(text)

    #     text = f"DELETE FROM projects WHERE uuid = '{PROJECT_ID}'"
    #     conn.execute(text)

    #     text = f"DELETE FROM tasks WHERE uuid = '{TASK_ID}'"
    #     conn.execute(text)

    #     text = f"DELETE FROM tasks WHERE uuid = '{TASK_ID_2}'"
    #     conn.execute(text)
    #     conn.close()

    # def test_list_monitorings(self):
    #     rv = TEST_CLIENT.get("/projects/unk/deployments/unk/monitorings")
    #     result = rv.json()
    #     expected = {"message": "The specified project does not exist"}
    #     self.assertDictEqual(expected, result)
    #     self.assertEqual(rv.status_code, 404)

    #     rv = TEST_CLIENT.get(f"/projects/{PROJECT_ID}/deployments/unk/monitorings")
    #     result = rv.json()
    #     expected = {"message": "The specified deployment does not exist"}
    #     self.assertDictEqual(expected, result)
    #     self.assertEqual(rv.status_code, 404)

    #     rv = TEST_CLIENT.get(f"/projects/{PROJECT_ID}/deployments/{DEPLOYMENT_ID}/monitorings")
    #     result = rv.json()
    #     self.assertIsInstance(result["monitorings"], list)
    #     self.assertIsInstance(result["total"], int)
    #     self.assertEqual(rv.status_code, 200)

    # def test_create_monitoring(self):
    #     rv = TEST_CLIENT.post("/projects/unk/deployments/unk/monitorings", json={
    #         "taskId": TASK_ID_2,
    #     })
    #     result = rv.json()
    #     expected = {"message": "The specified project does not exist"}
    #     self.assertDictEqual(expected, result)
    #     self.assertEqual(rv.status_code, 404)

    #     rv = TEST_CLIENT.post(f"/projects/{PROJECT_ID}/deployments/unk/monitorings", json={
    #         "taskId": TASK_ID_2,
    #     })
    #     result = rv.json()
    #     expected = {"message": "The specified deployment does not exist"}
    #     self.assertDictEqual(expected, result)
    #     self.assertEqual(rv.status_code, 404)

    #     rv = TEST_CLIENT.post(
    #         f"/projects/{PROJECT_ID}/deployments/{DEPLOYMENT_ID}/monitorings",
    #         json={
    #             "taskId": "unk",
    #         }
    #     )
    #     result = rv.json()
    #     expected = {"message": "The specified task does not exist"}
    #     self.assertDictEqual(expected, result)
    #     self.assertEqual(rv.status_code, 404)

    #     rv = TEST_CLIENT.post(
    #         f"/projects/{PROJECT_ID}/deployments/{DEPLOYMENT_ID}/monitorings",
    #         json={
    #             "taskId": TASK_ID_2,
    #         }
    #     )
    #     result = rv.json()
    #     expected = {
    #         "deploymentId": DEPLOYMENT_ID,
    #         "taskId": TASK_ID_2,
    #     }
    #     machine_generated = ["uuid", "createdAt", "task"]
    #     for attr in machine_generated:
    #         self.assertIn(attr, result)
    #         del result[attr]
    #     self.assertDictEqual(expected, result)

    # def test_delete_monitoring(self):
    #     rv = TEST_CLIENT.delete(f"/projects/unk/deployments/unk/monitorings/unk")
    #     result = rv.json()
    #     expected = {"message": "The specified project does not exist"}
    #     self.assertDictEqual(expected, result)
    #     self.assertEqual(rv.status_code, 404)

    #     rv = TEST_CLIENT.delete(f"/projects/{PROJECT_ID}/deployments/unk/monitorings/unk")
    #     result = rv.json()
    #     expected = {"message": "The specified deployment does not exist"}
    #     self.assertDictEqual(expected, result)
    #     self.assertEqual(rv.status_code, 404)

    #     rv = TEST_CLIENT.delete(f"/projects/{PROJECT_ID}/deployments/{DEPLOYMENT_ID}/monitorings/unk")
    #     result = rv.json()
    #     expected = {"message": "The specified monitoring does not exist"}
    #     self.assertDictEqual(expected, result)
    #     self.assertEqual(rv.status_code, 404)

    #     rv = TEST_CLIENT.delete(f"/projects/{PROJECT_ID}/deployments/{DEPLOYMENT_ID}/monitorings/{MONITORING_ID}")
    #     result = rv.json()
    #     expected = {"message": "Monitoring deleted"}
    #     self.assertDictEqual(expected, result)

    # def test_list_figures_monitoring(self):
    #     rv = TEST_CLIENT.get(f"/projects/1/deployments/unk/monitorings/unk/figures")
    #     result = rv.json()
    #     expected = {"message": "The specified project does not exist"}
    #     self.assertDictEqual(expected, result)
    #     self.assertEqual(rv.status_code, 404)

    #     rv = TEST_CLIENT.get(f"/projects/{PROJECT_ID}/deployments/unk/monitorings/unk/figures")
    #     result = rv.json()
    #     expected = {"message": "The specified deployment does not exist"}
    #     self.assertDictEqual(expected, result)
    #     self.assertEqual(rv.status_code, 404)

    #     rv = TEST_CLIENT.get(f"/projects/{PROJECT_ID}/deployments/{DEPLOYMENT_ID}/monitorings/{MONITORING_ID}/figures")
    #     result = rv.json()
    #     self.assertIsInstance(result, list)
    #     self.assertEqual(rv.status_code, 200)
