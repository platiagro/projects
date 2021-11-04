# -*- coding: utf-8 -*-
import unittest
import unittest.mock as mock

from fastapi.testclient import TestClient

from projects.api.main import app
from projects.database import session_scope

import tests.util as util

app.dependency_overrides[session_scope] = util.override_session_scope
TEST_CLIENT = TestClient(app)


class TestResponses(unittest.TestCase):
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

    def test_create_response_deployment_not_found(self):
        """
        Should return a http status 404 and an error message.
        """
        project_id = util.MOCK_UUID_1
        deployment_id = "unk"

        rv = TEST_CLIENT.post(
            f"/projects/{project_id}/deployments/{deployment_id}/responses",
            json={},
        )
        result = rv.json()

        expected = {"message": "The specified deployment does not exist"}
        self.assertDictEqual(expected, result)
        self.assertEqual(rv.status_code, 404)

    @mock.patch(
        "requests.post",
        return_value=util.MOCK_POST_PREDICTION,
    )
    def test_create_response_success_1(
        self,
        mock_requests_post,
    ):
        """
        Should create and return a response successfully.
        """
        project_id = util.MOCK_UUID_1
        deployment_id = util.MOCK_UUID_1
        data = {"data": {"ndarray": [[1, 2, "a"]]}}

        rv = TEST_CLIENT.post(
            f"/projects/{project_id}/deployments/{deployment_id}/responses",
            json=data,
        )
        result = rv.json()
        expected = {"message": "OK"}
        self.assertEqual(result, expected)
        self.assertEqual(rv.status_code, 200)

        mock_requests_post.assert_any_call(
            "http://broker-ingress.knative-eventing.svc.cluster.local/anonymous/default",
            json={
                "data": {
                    "ndarray": [[1, 2, "a"]],
                    "names": ["0", "1", "2"],
                },
            },
            headers={
                "Ce-Id": mock.ANY,
                "Ce-Specversion": "1.0",
                "Ce-Type": f"deployment.{deployment_id}",
                "Ce-Source": "logger.anonymous",
            },
        )

    @mock.patch(
        "requests.post",
        return_value=util.MOCK_POST_PREDICTION,
    )
    def test_create_response_success_2(
        self,
        mock_requests_post,
    ):
        """
        Should create and return a response successfully.
        """
        project_id = util.MOCK_UUID_1
        deployment_id = util.MOCK_UUID_1
        data = {"strData": "texto"}

        rv = TEST_CLIENT.post(
            f"/projects/{project_id}/deployments/{deployment_id}/responses",
            json=data,
        )
        result = rv.json()
        expected = {"message": "OK"}
        self.assertEqual(result, expected)
        self.assertEqual(rv.status_code, 200)

        mock_requests_post.assert_any_call(
            "http://broker-ingress.knative-eventing.svc.cluster.local/anonymous/default",
            json={
                "data": {
                    "ndarray": [["texto"]],
                    "names": ["strData"],
                },
            },
            headers={
                "Ce-Id": mock.ANY,
                "Ce-Specversion": "1.0",
                "Ce-Type": f"deployment.{deployment_id}",
                "Ce-Source": "logger.anonymous",
            },
        )

    @mock.patch(
        "requests.post",
        return_value=util.MOCK_POST_PREDICTION,
    )
    def test_create_response_success_3(
        self,
        mock_requests_post,
    ):
        """
        Should create and return a response successfully.
        """
        project_id = util.MOCK_UUID_1
        deployment_id = util.MOCK_UUID_1
        data = {"binData": "Cg=="}

        rv = TEST_CLIENT.post(
            f"/projects/{project_id}/deployments/{deployment_id}/responses",
            json=data,
        )
        result = rv.json()
        expected = {"message": "OK"}
        self.assertEqual(result, expected)
        self.assertEqual(rv.status_code, 200)

        mock_requests_post.assert_any_call(
            "http://broker-ingress.knative-eventing.svc.cluster.local/anonymous/default",
            json={
                "data": {
                    "ndarray": [["Cg=="]],
                    "names": ["binData"],
                },
            },
            headers={
                "Ce-Id": mock.ANY,
                "Ce-Specversion": "1.0",
                "Ce-Type": f"deployment.{deployment_id}",
                "Ce-Source": "logger.anonymous",
            },
        )
