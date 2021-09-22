# -*- coding: utf-8 -*-
import unittest
import unittest.mock as mock

from fastapi.testclient import TestClient

from projects.api.main import app
from projects.database import session_scope

import tests.util as util

app.dependency_overrides[session_scope] = util.override_session_scope
TEST_CLIENT = TestClient(app)


class TestExperimentData(unittest.TestCase):
    maxDiff = None

    # def setUp(self):
    #     conn = engine.connect()
    #     text = (
    #         f"INSERT INTO projects (uuid, name, created_at, updated_at, tenant) "
    #         f"VALUES (%s, %s, %s, %s, %s)"
    #     )
    #     conn.execute(text, (PROJECT_ID, NAME, CREATED_AT, UPDATED_AT, TENANT,))

    #     text = (
    #         f"INSERT INTO experiments (uuid, name, project_id, position, is_active, created_at, updated_at) "
    #         f"VALUES (%s, %s, %s, %s, %s, %s, %s)"
    #     )
    #     conn.execute(text, (EXPERIMENT_ID, NAME, PROJECT_ID, 1, 1, CREATED_AT, UPDATED_AT))
    #     conn.close()

    # def tearDown(self):
    #     conn = engine.connect()
    #     text = f"DELETE FROM experiments WHERE project_id = '{PROJECT_ID}'"
    #     conn.execute(text)

    #     text = f"DELETE FROM projects WHERE uuid = '{PROJECT_ID}'"
    #     conn.execute(text)
    #     conn.close()

    # @patch("kubernetes.client.CoreV1Api")
    # @patch("kubernetes.stream.stream")
    # def test_get_data(self, mock_k8s_stream, mock_client):
    #     rv = TEST_CLIENT.get(f"/projects/unk/experiments/{EXPERIMENT_ID}/data")
    #     result = rv.json()
    #     expected = {"message": "The specified project does not exist"}
    #     self.assertDictEqual(expected, result)
    #     self.assertEqual(rv.status_code, 404)

    #     rv = TEST_CLIENT.get(f"/projects/{PROJECT_ID}/experiments/unk/data")
    #     result = rv.json()
    #     expected = {"message": "The specified experiment does not exist"}
    #     self.assertDictEqual(expected, result)
    #     self.assertEqual(rv.status_code, 404)

    #     # mock the kubernetes client methods
    #     mock_api_instance = mock_client.return_value
    #     mock_api_instance.read_namespaced_pod.return_value.status.phase = "Running"

    #     # mock kubernetes stream methods
    #     mock_container_stream = mock_k8s_stream.return_value
    #     # this is needed to break the while loop
    #     mock_container_stream.is_open.side_effect = [True, False]
    #     mock_container_stream.read_stdout.return_value = "Z2l0aHViLmNvbS9wbGF0aWFncm8vcHJvamVjdHM="

    #     rv = TEST_CLIENT.get(f"/projects/{PROJECT_ID}/experiments/{EXPERIMENT_ID}/data")
    #     mock_api_instance.create_namespaced_pod.assert_called()
    #     mock_api_instance.delete_namespaced_pod.assert_called()
    #     self.assertEqual(rv.status_code, 200)
    #     self.assertEqual(
    #         rv.headers.get("Content-Disposition"),
    #         CONTENT_DISPOSITION
    #     )
    #     self.assertEqual(
    #         rv.headers.get("Content-Type"),
    #         CONTENT_TYPE
    #     )
