# -*-  coding: utf-8 -*-
from io import BytesIO
from json import dumps
from unittest import TestCase
from unittest.mock import patch

from fastapi.testclient import TestClient
from minio.error import BucketAlreadyOwnedByYou
from platiagro import CATEGORICAL, DATETIME, NUMERICAL
from requests import Response

from projects.api.main import app
from projects.controllers.utils import uuid_alpha
from projects.database import engine
from projects.object_storage import BUCKET_NAME, MINIO_CLIENT

TEST_CLIENT = TestClient(app)

DEPLOYMENT_ID = str(uuid_alpha())
NAME = "foo-bar"
PROJECT_ID = str(uuid_alpha())
CREATED_AT = "2000-01-01 00:00:00"
UPDATED_AT = "2000-01-01 00:00:00"
EXPERIMENT_ID = str(uuid_alpha())
POSITION = 0
STATUS = "Pending"
URL = None
DATASET = "mock.csv"

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
            f"VALUES (%s, %s, %s, %s)"
        )
        conn.execute(text, (PROJECT_ID, NAME, CREATED_AT, UPDATED_AT,))

        text = (
            f"INSERT INTO experiments (uuid, name, project_id, position, is_active, created_at, updated_at) "
            f"VALUES (%s, %s, %s, %s, %s, %s, %s)"
        )
        conn.execute(text, (EXPERIMENT_ID, NAME, PROJECT_ID, POSITION, 1, CREATED_AT, UPDATED_AT,))

        text = (
            f"INSERT INTO deployments (uuid, name, project_id, experiment_id, position, is_active, status, url, created_at, updated_at) "
            f"VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
        )
        conn.execute(text, (DEPLOYMENT_ID, NAME, PROJECT_ID, EXPERIMENT_ID, POSITION, 1, STATUS, URL, CREATED_AT, UPDATED_AT,))

        conn.close()

        # uploads mock dataset
        try:
            MINIO_CLIENT.make_bucket(BUCKET_NAME)
        except BucketAlreadyOwnedByYou:
            pass

        file = BytesIO((
            b'col0,col1,col2,col3,col4,col5\n'
            b'01/01/2000,5.1,3.5,1.4,0.2,Iris-setosa\n'
            b'01/01/2000,5.1,3.5,1.4,0.2,Iris-setosa\n'
            b'01/01/2000,5.1,3.5,1.4,0.2,Iris-setosa\n'
        ))
        MINIO_CLIENT.put_object(
            bucket_name=BUCKET_NAME,
            object_name=f"datasets/{DATASET}/{DATASET}",
            data=file,
            length=file.getbuffer().nbytes,
        )
        metadata = {
            "columns": ["col0", "col1", "col2", "col3", "col4", "col5"],
            "featuretypes": [DATETIME, NUMERICAL, NUMERICAL, NUMERICAL, NUMERICAL, CATEGORICAL],
            "filename": DATASET,
        }
        buffer = BytesIO(dumps(metadata).encode())
        MINIO_CLIENT.put_object(
            bucket_name=BUCKET_NAME,
            object_name=f"datasets/{DATASET}/{DATASET}.metadata",
            data=buffer,
            length=buffer.getbuffer().nbytes,
        )

    @classmethod
    def tearDownClass(cls):
        MINIO_CLIENT.remove_object(
            bucket_name=BUCKET_NAME,
            object_name=f"datasets/{DATASET}/{DATASET}.metadata",
        )
        MINIO_CLIENT.remove_object(
            bucket_name=BUCKET_NAME,
            object_name=f"datasets/{DATASET}/{DATASET}",
        )

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
        rv = TEST_CLIENT.post(f"/projects/foo/deployments/{DEPLOYMENT_ID}/predictions")
        result = rv.json()
        expected = {"message": "The specified project does not exist"}
        self.assertEqual(result, expected)
        self.assertEqual(rv.status_code, 404)

        rv = TEST_CLIENT.post(f"/projects/{PROJECT_ID}/deployments/foo/predictions")
        result = rv.json()
        expected = {"message": "The specified deployment does not exist"}
        self.assertEqual(result, expected)
        self.assertEqual(rv.status_code, 404)

        rv = TEST_CLIENT.post(f"/projects/{PROJECT_ID}/deployments/{DEPLOYMENT_ID}/predictions")
        result = rv.json()
        expected = {"message": "either form-data or json is required"}
        self.assertEqual(result, expected)
        self.assertEqual(rv.status_code, 400)

        rv = TEST_CLIENT.post(f"/projects/{PROJECT_ID}/deployments/{DEPLOYMENT_ID}/predictions", json={})
        result = rv.json()
        expected = {"message": "either dataset name or file is required"}
        self.assertEqual(result, expected)
        self.assertEqual(rv.status_code, 400)

        rv = TEST_CLIENT.post(f"/projects/{PROJECT_ID}/deployments/{DEPLOYMENT_ID}/predictions", json={"dataset": "unk"})
        result = rv.json()
        expected = {"message": "a valid dataset is required"}
        self.assertEqual(result, expected)
        self.assertEqual(rv.status_code, 400)

        # successful load dataset request
        # building a functional response for mocked post
        mocked_response = Response()
        mocked_response.status_code = 200
        mocked_response._content = b'{ "foo": "bar" }'
        mock_requests.post.return_value = mocked_response

        rv = TEST_CLIENT.post(
            f"/projects/{PROJECT_ID}/deployments/{DEPLOYMENT_ID}/predictions", 
            json={"dataset": DATASET}
        )
        result = rv.json()
        result = rv.json()
        self.assertIsInstance(result, dict)
        self.assertEqual(rv.status_code, 200)

        # successful csv request
        # building a functional response for mocked post
        mocked_response = Response()
        mocked_response.status_code = 200
        mocked_response._content = b'{ "foo": "bar" }'
        mock_requests.post.return_value = mocked_response

        # reading file for request
        mocked_dataset = open(MOCKED_DATASET_PATH, "rb")
        files = {"file": (
                    "dataset.csv",
                    mocked_dataset,
                    "multipart/form-data"
                    )}

        rv = TEST_CLIENT.post(
            f"/projects/{PROJECT_ID}/deployments/{DEPLOYMENT_ID}/predictions",
            files=files
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
        files = {"file": (
                    "dataset.csv",
                    mocked_dataset,
                    "multipart/form-data"
                    )}

        rv = TEST_CLIENT.post(
            f"/projects/{PROJECT_ID}/deployments/{DEPLOYMENT_ID}/predictions",
            files=files
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
        files = {"file": (
                    "dataset.csv",
                    mocked_dataset,
                    "multipart/form-data"
                    )}

        rv = TEST_CLIENT.post(
            f"/projects/{PROJECT_ID}/deployments/{DEPLOYMENT_ID}/predictions",
            files=files
        )
        result = rv.json()
        self.assertIsInstance(result, dict)
        self.assertEqual(rv.status_code, 200)
