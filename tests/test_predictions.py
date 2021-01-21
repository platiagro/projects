# -*-  coding: utf-8 -*-
from unittest import TestCase
from unittest.mock import patch

from fastapi.testclient import TestClient
from requests import Response

from projects.api.main import app
from projects.controllers.utils import uuid_alpha
from projects.database import engine

TEST_CLIENT = TestClient(app)

DEPLOYMENT_ID = str(uuid_alpha())
NAME = "foo-bar"
PROJECT_ID = str(uuid_alpha())
CREATED_AT = "2000-01-01 00:00:00"
UPDATED_AT = "2000-01-01 00:00:00"
EXPERIMENT_ID = str(uuid_alpha())
POSITION = 0

MOCKED_DATASET_PATH = "tests/resources/mocked_dataset.csv"
MOCKED_DATASET_NO_HEADER_PATH = "tests/resources/mocked_dataset_no_header.csv"
MOCKED_DATASET_BASE64_PATH = "tests/resources/mocked_dataset_base64.jpeg"
MOCKED_DATASET_STRDATA_PATH = "tests/resources/mocked_dataset_strdata.txt"


class TestPredictions(TestCase):

    @classmethod
    def setUpClass(cls):
        cls.maxDiff = None

        conn = engine.connect()
        text = (
            f"INSERT INTO projects (uuid, name, created_at, updated_at) "
            f"VALUES (uuid, name, created_at, updated_at)"
        )
        conn.execute(text, (PROJECT_ID, NAME, CREATED_AT, UPDATED_AT,))

        text = (
            f"INSERT INTO experiments (uuid, name, project_id, position, is_active, created_at, updated_at) "
            f"VALUES (uuid, name, project_id, position, is_active, created_at, updated_at)"
        )
        conn.execute(text, (EXPERIMENT_ID, NAME, PROJECT_ID, POSITION, 1, CREATED_AT, UPDATED_AT,))

        text = (
            f"INSERT INTO deployments (uuid, name, project_id, experiment_id, position, is_active, created_at, updated_at) "
            f"VALUES (uuid, name, project_id, experiment_id, position, is_active, created_at, updated_at)"
        )
        conn.execute(text, (DEPLOYMENT_ID, NAME, PROJECT_ID, EXPERIMENT_ID, POSITION, 1, CREATED_AT, UPDATED_AT,))

        conn.close()

    @classmethod
    def tearDownClass(cls):
        conn = engine.connect()

        text = f"DELETE FROM deployments WHERE project_id = '{PROJECT_ID}'"
        conn.execute(text)

        text = f"DELETE FROM experiments WHERE project_id = '{PROJECT_ID}'"
        conn.execute(text)

        text = f"DELETE FROM projects WHERE uuid = '{PROJECT_ID}'"
        conn.execute(text)

        conn.close()

    @patch("projects.controllers.predictions.requests")
    def test_create_prediction(self, mock_requests):
        rv = TEST_CLIENT.post(f"/projects/foo/deployments/{DEPLOYMENT_ID}/predictions", content_type="multipart/formdata")
        result = rv.json()
        expected = {"message": "The specified project does not exist"}
        self.assertIsInstance(result, dict)
        self.assertEqual(result, expected)
        self.assertEqual(rv.status_code, 404)

        rv = TEST_CLIENT.post(f"/projects/{PROJECT_ID}/deployments/foo/predictions", content_type="multipart/formdata")
        result = rv.json()
        expected = {"message": "The specified deployment does not exist"}
        self.assertIsInstance(result, dict)
        self.assertEqual(result, expected)
        self.assertEqual(rv.status_code, 404)

        rv = TEST_CLIENT.post(f"/projects/{PROJECT_ID}/deployments/{DEPLOYMENT_ID}/predictions", content_type='multipart/form-data')
        result = rv.json()
        expected = {"message": "file is required."}
        self.assertIsInstance(result, dict)
        self.assertEqual(result, expected)
        self.assertEqual(rv.status_code, 400)

        # reading file for request
        mocked_dataset = open(MOCKED_DATASET_NO_HEADER_PATH, "rb")
        data = dict(
            miles="1",
            file=mocked_dataset,
        )

        rv = TEST_CLIENT.post(
            f"/projects/{PROJECT_ID}/deployments/{DEPLOYMENT_ID}/predictions",
            content_type='multipart/form-data',
            data=data
        )
        result = rv.json()
        expected = {"message": "file needs a header."}
        self.assertIsInstance(result, dict)
        self.assertEqual(result, expected)
        self.assertEqual(rv.status_code, 400)

        # successful csv request
        # building a functional response for mocked post
        mocked_response = Response()
        mocked_response.status_code = 200
        mocked_response._content = b'{ "foo": "bar" }'
        mock_requests.post.return_value = mocked_response

        # reading file for request
        mocked_dataset = open(MOCKED_DATASET_PATH, "rb")
        data = dict(
            miles="1",
            file=mocked_dataset,
        )

        rv = TEST_CLIENT.post(
            f"/projects/{PROJECT_ID}/deployments/{DEPLOYMENT_ID}/predictions",
            content_type='multipart/form-data',
            data=data
        )
        result = rv.json()
        self.assertIsInstance(result, dict)
        self.assertEqual(rv.status_code, 200)

        # successful base64 request
        # building a functional response for mocked post
        mocked_response = Response()
        mocked_response.status_code = 200
        mocked_response._content = b'{ "foo": "bar" }'
        mock_requests.post.return_value = mocked_response

        # reading file for request
        mocked_dataset = open(MOCKED_DATASET_BASE64_PATH, "rb")
        data = dict(
            miles="1",
            file=mocked_dataset,
        )

        rv = TEST_CLIENT.post(
            f"/projects/{PROJECT_ID}/deployments/{DEPLOYMENT_ID}/predictions",
            content_type='multipart/form-data',
            data=data
        )
        result = rv.json()
        self.assertIsInstance(result, dict)
        self.assertEqual(rv.status_code, 200)

        # successful strData request
        # building a functional response for mocked post
        mocked_response = Response()
        mocked_response.status_code = 200
        mocked_response._content = b'{ "foo": "bar" }'
        mock_requests.post.return_value = mocked_response

        # reading file for request
        mocked_dataset = open(MOCKED_DATASET_STRDATA_PATH, "rb")
        data = dict(
            miles="1",
            file=mocked_dataset,
        )

        rv = TEST_CLIENT.post(
            f"/projects/{PROJECT_ID}/deployments/{DEPLOYMENT_ID}/predictions",
            content_type='multipart/form-data',
            data=data
        )
        result = rv.json()
        self.assertIsInstance(result, dict)
        self.assertEqual(rv.status_code, 200)
