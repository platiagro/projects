# -*- coding: utf-8 -*-
import unittest
import unittest.mock as mock

from fastapi.testclient import TestClient

from projects.api.main import app
from projects.database import session_scope

import tests.util as util

app.dependency_overrides[session_scope] = util.override_session_scope
TEST_CLIENT = TestClient(app)


class TestPredictions(unittest.TestCase):
    maxDiff = None

    def test_create_prediction(self, mock_requests):
        """
        Should return an http status 404 and an error message.
        """
        project_id = "unk"
        deployment_id = "unk"

        rv = TEST_CLIENT.post(
            f"/projects/{project_id}/deployments/{deployment_id}/predictions"
        )
        result = rv.json()

        expected = {"message": "The specified deployment does not exist"}
        self.assertEqual(result, expected)
        self.assertEqual(rv.status_code, 404)

    # @patch("projects.controllers.predictions.requests")
    def test_create_prediction(self, mock_requests):
        rv = TEST_CLIENT.post(f"/projects/foo/deployments/{DEPLOYMENT_ID}/predictions")
        result = rv.json()
        expected = {"message": "The specified project does not exist"}
        self.assertEqual(result, expected)
        self.assertEqual(rv.status_code, 404)

    #     rv = TEST_CLIENT.post(f"/projects/{PROJECT_ID}/deployments/{DEPLOYMENT_ID}/predictions")
    #     result = rv.json()
    #     expected = {"message": "either form-data or json is required"}
    #     self.assertEqual(result, expected)
    #     self.assertEqual(rv.status_code, 400)

    #     rv = TEST_CLIENT.post(f"/projects/{PROJECT_ID}/deployments/{DEPLOYMENT_ID}/predictions", json={})
    #     result = rv.json()
    #     expected = {"message": "either dataset name or file is required"}
    #     self.assertEqual(result, expected)
    #     self.assertEqual(rv.status_code, 400)

    #     rv = TEST_CLIENT.post(f"/projects/{PROJECT_ID}/deployments/{DEPLOYMENT_ID}/predictions", json={"dataset": "unk"})
    #     result = rv.json()
    #     expected = {"message": "a valid dataset is required"}
    #     self.assertEqual(result, expected)
    #     self.assertEqual(rv.status_code, 400)

    #     # building a functional response for mocked post
    #     mocked_response = Response()
    #     mocked_response.status_code = 200
    #     mocked_response._content = b'{ "foo": "bar" }'
    #     mock_requests.post.return_value = mocked_response

    #     # successful load dataset request
    #     rv = TEST_CLIENT.post(
    #         f"/projects/{PROJECT_ID}/deployments/{DEPLOYMENT_ID}/predictions",
    #         json={"dataset": DATASET}
    #     )
    #     result = rv.json()
    #     self.assertIsInstance(result, dict)
    #     self.assertEqual(rv.status_code, 200)

    #     rv = TEST_CLIENT.post(
    #        f"/projects/{PROJECT_ID}/deployments/{DEPLOYMENT_ID}/predictions",
    #        json={"dataset": IMAGE_DATASET}
    #     )
    #     result = rv.json()
    #     self.assertIsInstance(result, dict)
    #     self.assertEqual(rv.status_code, 200)

    #     # successful csv request
    #     # reading file for request
    #     mocked_dataset = open(MOCKED_DATASET_PATH, "rb")
    #     files = {"file": (
    #                 "dataset.csv",
    #                 mocked_dataset,
    #                 "multipart/form-data"
    #                 )}

    #     rv = TEST_CLIENT.post(
    #         f"/projects/{PROJECT_ID}/deployments/{DEPLOYMENT_ID}/predictions",
    #         files=files
    #     )
    #     result = rv.json()
    #     self.assertIsInstance(result, dict)
    #     self.assertEqual(rv.status_code, 200)

    #     # successful base64 request
    #     # reading file for request
    #     mocked_dataset = open(MOCKED_DATASET_BASE64_PATH, "rb")
    #     files = {"file": (
    #                 "dataset.csv",
    #                 mocked_dataset,
    #                 "multipart/form-data"
    #                 )}

    #     rv = TEST_CLIENT.post(
    #         f"/projects/{PROJECT_ID}/deployments/{DEPLOYMENT_ID}/predictions",
    #         files=files
    #     )
    #     result = rv.json()
    #     self.assertIsInstance(result, dict)
    #     self.assertEqual(rv.status_code, 200)

    #     # successful strData request
    #     # reading file for request
    #     mocked_dataset = open(MOCKED_DATASET_STRDATA_PATH, "rb")
    #     files = {"file": (
    #                 "dataset.csv",
    #                 mocked_dataset,
    #                 "multipart/form-data"
    #                 )}

    #     rv = TEST_CLIENT.post(
    #         f"/projects/{PROJECT_ID}/deployments/{DEPLOYMENT_ID}/predictions",
    #         files=files
    #     )
    #     result = rv.json()
    #     self.assertIsInstance(result, dict)
    #     self.assertEqual(rv.status_code, 200)
