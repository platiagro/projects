# -*-  coding: utf-8 -*-
from requests import Response
from unittest import TestCase
from unittest.mock import Mock, patch

from projects.api.main import app
from projects.controllers.utils import uuid_alpha
from projects.database import engine
from projects.kfp import KFP_CLIENT
from projects.object_storage import BUCKET_NAME, MINIO_CLIENT

DEPLOYMENT_ID = str(uuid_alpha())
NAME = "foo-bar"
PROJECT_ID = str(uuid_alpha())
CREATED_AT = "2000-01-01 00:00:00"
UPDATED_AT = "2000-01-01 00:00:00"
EXPERIMENT_ID = str(uuid_alpha())
POSITION = 0

MOCKED_DATASET_PATH = "tests/resources/mocked_dataset.csv"
MOCKED_DATASET_NO_HEADER_PATH = "tests/resources/mocked_dataset_no_header.csv"

class TestPredictions(TestCase):

    @classmethod
    def setUpClass(cls):
        cls.maxDiff = None

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
            f"INSERT INTO deployments (uuid, name, project_id, experiment_id, position, is_active, created_at, updated_at) "
            f"VALUES ('{DEPLOYMENT_ID}', '{NAME}', '{PROJECT_ID}', '{EXPERIMENT_ID}', '{POSITION}', 1, '{CREATED_AT}', '{UPDATED_AT}')"
        )
        conn.execute(text)

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
        with app.test_client() as c:
            rv = c.post(f"/projects/foo/deployments/{DEPLOYMENT_ID}/predictions", content_type="multipart/formdata")
            result = rv.get_json()
            expected = {"message": "The specified project does not exist"}
            self.assertIsInstance(result, dict)
            self.assertEqual(result, expected)
            self.assertEqual(rv.status_code, 404)

            rv = c.post(f"/projects/{PROJECT_ID}/deployments/foo/predictions", content_type="multipart/formdata")
            result = rv.get_json()
            expected = {"message": "The specified deployment does not exist"}
            self.assertIsInstance(result, dict)
            self.assertEqual(result, expected)
            self.assertEqual(rv.status_code, 404)            

            rv = c.post(f"/projects/{PROJECT_ID}/deployments/{DEPLOYMENT_ID}/predictions", content_type='multipart/form-data')
            result = rv.get_json()
            expected = {"message": "`file` is required."}
            self.assertIsInstance(result, dict)
            self.assertEqual(result, expected)
            self.assertEqual(rv.status_code, 400)

            # reading file for request
            mocked_dataset = open(MOCKED_DATASET_NO_HEADER_PATH, "rb")
            data = dict(miles="1",
                file=mocked_dataset,
            )

            rv = c.post(f"/projects/{PROJECT_ID}/deployments/{DEPLOYMENT_ID}/predictions", 
                content_type='multipart/form-data',
                data=data
            )
            result = rv.get_json()
            expected = {"message": "`file` needs a header."}
            self.assertIsInstance(result, dict)
            self.assertEqual(result, expected)
            self.assertEqual(rv.status_code, 400)

            # succesfull request
            # building a functional response for mocked post
            mocked_response = Response()
            mocked_response.status_code = 200
            mocked_response._content = b'{ "foo": "bar" }'
            mock_requests.post.return_value = mocked_response

            # reading file for request
            mocked_dataset = open(MOCKED_DATASET_PATH, "rb")
            data = dict(miles="1",
                file=mocked_dataset,
            )

            rv = c.post(f"/projects/{PROJECT_ID}/deployments/{DEPLOYMENT_ID}/predictions", 
                content_type='multipart/form-data',
                data=data
            )
            result = rv.get_json()
            self.assertIsInstance(result, dict)
            self.assertEqual(rv.status_code, 200)

