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

    def setUp(self):
        """
        Sets up the test before running it.
        """
        util.create_mocks()

    def tearDown(self):
        """
        Deconstructs the test after running it.
        """
        util.delete_mocks()

    def test_get_data_does_project_exist(self):
        """
        Should return an http status 404 and a message "The specified project does not exist".
        """
        experiment_id = util.MOCK_UUID_1

        rv = TEST_CLIENT.get(f"/projects/unk/experiments/{experiment_id}/data")
        result = rv.json()
        expected = {
            "message": "The specified project does not exist",
            "code": "ProjectNotFound",
            "status_code": 404,
        }
        self.assertDictEqual(expected, result)
        self.assertEqual(rv.status_code, 404)

    def test_get_data_does_experiment_exist(self):
        """
        Should return an http status 404 and a message "The specified experiment does not exist".
        """
        project_id = util.MOCK_UUID_1

        rv = TEST_CLIENT.get(f"/projects/{project_id}/experiments/unk/data")
        result = rv.json()
        expected = {
            "message": "The specified experiment does not exist",
            "code": "ExperimentNotFound",
            "status_code": 404,
        }
        self.assertDictEqual(expected, result)
        self.assertEqual(rv.status_code, 404)

    @mock.patch(
        "kubernetes.client.CoreV1Api",
        return_value=util.MOCK_CORE_V1_API,
    )
    @mock.patch(
        "kubernetes.stream.stream",
        return_value=util.MOCK_STREAM,
    )
    @mock.patch(
        "kubernetes.config.load_kube_config",
    )
    def teste_get_data(self, mock_load_config, mock_k8s_stream, mock_core_v1_api):
        """
        Should load data request successfully.
        """
        project_id = util.MOCK_UUID_1
        experiment_id = util.MOCK_UUID_1
        content_disposition = util.CONTENT_DISPOSITION
        content_type = util.CONTENT_TYPE

        rv = TEST_CLIENT.get(f"/projects/{project_id}/experiments/{experiment_id}/data")
        self.assertEqual(rv.status_code, 200)
        self.assertEqual(rv.headers.get("Content-Disposition"), content_disposition)
        self.assertEqual(rv.headers.get("Content-Type"), content_type)
        mock_core_v1_api.assert_any_call()
        mock_k8s_stream.assert_any_call(
            util.MOCK_CORE_V1_API.connect_get_namespaced_pod_exec,
            name="download-uuid-1",
            namespace="anonymous",
            command=[
                "/bin/sh",
                "-c",
                "apk add zip -q && zip -q -r - /tmp/data | base64",
            ],
            container="main",
            stderr=True,
            stdin=False,
            stdout=True,
            tty=False,
            _preload_content=False,
        )
        mock_load_config.assert_any_call()
