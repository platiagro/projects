# -*- coding: utf-8 -*-
import unittest
import unittest.mock as mock
import requests
import json
from io import BytesIO

from fastapi.testclient import TestClient

from projects.api.main import app
from projects.database import session_scope

import tests.util as util

app.dependency_overrides[session_scope] = util.override_session_scope
TEST_CLIENT = TestClient(app)


class TestPredictions(unittest.TestCase):
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

    def test_create_prediction_deployments_does_not_exist(self):
        """
        Should return an http status 404 and an error message "The specified deployment does not exist".
        """
        project_id = util.MOCK_UUID_1
        deployment_id = "unk"

        rv = TEST_CLIENT.post(
            f"/projects/{project_id}/deployments/{deployment_id}/predictions"
        )
        result = rv.json()

        expected = {"message": "The specified deployment does not exist"}
        self.assertEqual(result, expected)
        self.assertEqual(rv.status_code, 404)

    def test_create_prediction_projects_does_not_exist(self):
        """
        Should return an http status 404 and an error message "The specified projects does not exist".
        """
        project_id = "unk"
        deployment_id = util.MOCK_UUID_1

        rv = TEST_CLIENT.post(
            f"/projects/{project_id}/deployments/{deployment_id}/predictions"
        )
        result = rv.json()
        expected = {"message": "The specified project does not exist"}
        self.assertEqual(result, expected)
        self.assertEqual(rv.status_code, 404)

    def test_create_prediction_form_required(self):
        """
        Should return an http status 400 and a message 'either form-data or json is required'.
        """
        project_id = util.MOCK_UUID_1
        deployment_id = util.MOCK_UUID_1

        rv = TEST_CLIENT.post(
            f"/projects/{project_id}/deployments/{deployment_id}/predictions"
        )
        result = rv.json()
        expected = {"message": "either form-data or json is required"}
        self.assertEqual(result, expected)
        self.assertEqual(rv.status_code, 400)

    def test_create_prediction_dataset_name_required(self):
        """
        Should return an http status 400 and a message 'either dataset name or file is required'.
        """
        project_id = util.MOCK_UUID_1
        deployment_id = util.MOCK_UUID_1

        rv = TEST_CLIENT.post(
            f"/projects/{project_id}/deployments/{deployment_id}/predictions", json={}
        )
        result = rv.json()
        expected = {"message": "either dataset name or file is required"}
        self.assertEqual(result, expected)
        self.assertEqual(rv.status_code, 400)

    @mock.patch(
        "projects.controllers.predictions.load_dataset",
        side_effect=util.FILE_NOT_FOUND_ERROR,
    )
    def test_create_prediction_dataset_required(self, mock_load_dataset):
        """
        Should return an http status 400 and a message 'a valid dataset is required'.
        """
        project_id = util.MOCK_UUID_1
        deployment_id = util.MOCK_UUID_1
        name_dataset = "unk"

        rv = TEST_CLIENT.post(
            f"/projects/{project_id}/deployments/{deployment_id}/predictions",
            json={"dataset": name_dataset},
        )
        result = rv.json()
        expected = {"message": "a valid dataset is required"}
        self.assertEqual(result, expected)
        self.assertEqual(rv.status_code, 400)

        mock_load_dataset.assert_any_call(name_dataset)

    @mock.patch(
        "projects.controllers.predictions.load_dataset",
        return_value=util.IRIS_DATAFRAME,
    )
    @mock.patch(
        "requests.post",
        return_value=util.MOCK_POST_PREDICTION,
    )
    def test_create_prediction_dataset(
        self,
        mock_requests_post,
        mock_load_dataset,
    ):
        """
        Should load dataset request successfully.
        """
        project_id = util.MOCK_UUID_1
        deployment_id = util.MOCK_UUID_1
        name = util.IRIS_DATASET_NAME
        url = "http://uuid-1-model.anonymous:8000/api/v1.0/predictions"

        rv = TEST_CLIENT.post(
            f"/projects/{project_id}/deployments/{deployment_id}/predictions",
            json={"dataset": name},
        )
        result = rv.json()
        self.assertIsInstance(result, dict)
        self.assertEqual(rv.status_code, 200)

        mock_load_dataset.assert_any_call(name)
        mock_requests_post.assert_any_call(
            url=url,
            json={
                "data": {
                    "names": [
                        "SepalLengthCm",
                        "SepalWidthCm",
                        "PetalLengthCm",
                        "PetalWidthCm",
                        "Species",
                    ],
                    "ndarray": [
                        [5.1, 3.5, 1.4, 0.2, "Iris-setosa"],
                        [4.9, 3.0, 1.4, 0.2, "Iris-setosa"],
                        [4.7, 3.2, 1.3, 0.2, "Iris-setosa"],
                        [4.6, 3.1, 1.5, 0.2, "Iris-setosa"],
                    ],
                }
            },
        )

    @mock.patch(
        "projects.controllers.predictions.load_dataset",
        return_value=util.IRIS_DATAFRAME,
    )
    @mock.patch(
        "requests.post",
        return_value=util.MOCK_POST_PREDICTION,
    )
    def test_create_prediction_dataset_image(
        self,
        mock_requests_post,
        mock_load_dataset,
    ):
        """
        Should load the dataset request with an image successfully.
        """
        project_id = util.MOCK_UUID_1
        deployment_id = util.MOCK_UUID_1
        dataset_name = "mock.jpg"

        url = "http://uuid-1-model.anonymous:8000/api/v1.0/predictions"
        rv = TEST_CLIENT.post(
            f"/projects/{project_id}/deployments/{deployment_id}/predictions",
            json={"dataset": dataset_name},
        )
        result = rv.json()
        self.assertIsInstance(result, dict)
        self.assertEqual(rv.status_code, 200)

        mock_load_dataset.assert_any_call(dataset_name)
        mock_requests_post.assert_any_call(
            url=url,
            json={
                "data": {
                    "names": [
                        "SepalLengthCm",
                        "SepalWidthCm",
                        "PetalLengthCm",
                        "PetalWidthCm",
                        "Species",
                    ],
                    "ndarray": [
                        [5.1, 3.5, 1.4, 0.2, "Iris-setosa"],
                        [4.9, 3.0, 1.4, 0.2, "Iris-setosa"],
                        [4.7, 3.2, 1.3, 0.2, "Iris-setosa"],
                        [4.6, 3.1, 1.5, 0.2, "Iris-setosa"],
                    ],
                }
            },
        )
