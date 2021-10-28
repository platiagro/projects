# -*- coding: utf-8 -*-
import io
import unittest
import unittest.mock as mock

from fastapi.testclient import TestClient
from minio.datatypes import Object
from urllib3.response import HTTPResponse

from projects.api.main import app
from projects.database import session_scope
from projects.object_storage import BUCKET_NAME, MINIO_CLIENT

import tests.util as util

app.dependency_overrides[session_scope] = util.override_session_scope
TEST_CLIENT = TestClient(app)


class TestResults(unittest.TestCase):
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

    def test_get_results_project_not_found(self):
        """
        Should return an http status 404 and an error message.
        """
        project_id = "unk"
        experiment_id = "unk"
        run_id = "unk"

        rv = TEST_CLIENT.get(
            f"/projects/{project_id}/experiments/{experiment_id}/runs/{run_id}/results"
        )
        result = rv.json()
        expected = {"message": "The specified project does not exist"}
        self.assertDictEqual(expected, result)
        self.assertEqual(rv.status_code, 404)

    def test_get_results_experiment_not_found(self):
        """
        Should return an http status 404 and an error message.
        """
        project_id = util.MOCK_UUID_1
        experiment_id = "unk"
        run_id = "unk"

        rv = TEST_CLIENT.get(
            f"/projects/{project_id}/experiments/{experiment_id}/runs/{run_id}/results"
        )
        result = rv.json()
        expected = {"message": "The specified experiment does not exist"}
        self.assertDictEqual(expected, result)
        self.assertEqual(rv.status_code, 404)

    @mock.patch(
        "kfp.Client",
        return_value=util.MOCK_KFP_CLIENT,
    )
    @mock.patch.object(MINIO_CLIENT, "make_bucket")
    @mock.patch.object(
        MINIO_CLIENT,
        "list_objects",
        return_value=[],
    )
    def test_get_results_no_results(
        self, mock_list_objects, mock_make_bucket, mock_kfp_client
    ):
        """
        Should return an http status 404 and an error message.
        """
        project_id = util.MOCK_UUID_1
        experiment_id = util.MOCK_UUID_1
        run_id = "latest"

        rv = TEST_CLIENT.get(
            f"/projects/{project_id}/experiments/{experiment_id}/runs/{run_id}/results"
        )
        result = rv.json()
        expected = {"message": "The specified run has no results"}
        self.assertDictEqual(expected, result)
        self.assertEqual(rv.status_code, 404)

        mock_kfp_client.assert_any_call(host="http://ml-pipeline.kubeflow:8888")
        mock_make_bucket.assert_any_call(BUCKET_NAME)
        mock_list_objects.assert_any_call(
            bucket_name=BUCKET_NAME,
            prefix=f"experiments/{experiment_id}/operators/",
            recursive=True,
        )

    @mock.patch(
        "kfp.Client",
        return_value=util.MOCK_KFP_CLIENT,
    )
    @mock.patch.object(MINIO_CLIENT, "make_bucket")
    @mock.patch.object(
        MINIO_CLIENT,
        "list_objects",
        return_value=[
            Object(
                BUCKET_NAME,
                f"experiments/{util.MOCK_UUID_1}/operators/{util.MOCK_UUID_1}/{util.MOCK_RUN_ID}/figure-202110281200000000.png",
            )
        ],
    )
    @mock.patch.object(
        MINIO_CLIENT,
        "get_object",
        return_value=HTTPResponse(body=io.BytesIO(b""), preload_content=False),
    )
    def test_get_results_success(
        self, mock_get_object, mock_list_objects, mock_make_bucket, mock_kfp_client
    ):
        """
        Should return results successfully.
        """
        project_id = util.MOCK_UUID_1
        experiment_id = util.MOCK_UUID_1
        run_id = "latest"

        rv = TEST_CLIENT.get(
            f"/projects/{project_id}/experiments/{experiment_id}/runs/{run_id}/results"
        )
        self.assertEqual(rv.status_code, 200)
        self.assertEqual(
            rv.headers.get("Content-Disposition"), "attachment; filename=results.zip"
        )
        self.assertEqual(rv.headers.get("Content-Type"), "application/x-zip-compressed")

        mock_kfp_client.assert_any_call(host="http://ml-pipeline.kubeflow:8888")
        mock_make_bucket.assert_any_call(BUCKET_NAME)
        mock_list_objects.assert_any_call(
            bucket_name=BUCKET_NAME,
            prefix=f"experiments/{experiment_id}/operators/",
            recursive=True,
        )
        mock_get_object.assert_any_call(
            bucket_name=BUCKET_NAME,
            object_name=f"experiments/{experiment_id}/operators/{util.MOCK_UUID_1}/{util.MOCK_RUN_ID}/figure-202110281200000000.png",
        )

    def test_get_operators_results_project_not_found(self):
        """
        Should return an http status 404 and an error message.
        """
        project_id = "unk"
        experiment_id = "unk"
        run_id = "unk"
        operator_id = "unk"

        rv = TEST_CLIENT.get(
            f"/projects/{project_id}/experiments/{experiment_id}/runs/{run_id}/operators/{operator_id}/results"
        )
        result = rv.json()
        expected = {"message": "The specified project does not exist"}
        self.assertDictEqual(expected, result)
        self.assertEqual(rv.status_code, 404)

    def test_get_operators_results_experiment_not_found(self):
        """
        Should return an http status 404 and an error message.
        """
        project_id = util.MOCK_UUID_1
        experiment_id = "unk"
        run_id = "unk"
        operator_id = "unk"

        rv = TEST_CLIENT.get(
            f"/projects/{project_id}/experiments/{experiment_id}/runs/{run_id}/operators/{operator_id}/results"
        )
        result = rv.json()
        expected = {"message": "The specified experiment does not exist"}
        self.assertDictEqual(expected, result)
        self.assertEqual(rv.status_code, 404)

    def test_get_operators_results_operator_not_found(self):
        """
        Should return an http status 404 and an error message.
        """
        project_id = util.MOCK_UUID_1
        experiment_id = util.MOCK_UUID_1
        run_id = "latest"
        operator_id = "unk"

        rv = TEST_CLIENT.get(
            f"/projects/{project_id}/experiments/{experiment_id}/runs/{run_id}/operators/{operator_id}/results"
        )
        result = rv.json()
        expected = {"message": "The specified operator does not exist"}
        self.assertDictEqual(expected, result)
        self.assertEqual(rv.status_code, 404)

    @mock.patch(
        "kfp.Client",
        return_value=util.MOCK_KFP_CLIENT,
    )
    @mock.patch.object(MINIO_CLIENT, "make_bucket")
    @mock.patch.object(
        MINIO_CLIENT,
        "list_objects",
        return_value=[],
    )
    def test_get_operators_results_operator_no_results(
        self, mock_list_objects, mock_make_bucket, mock_kfp_client
    ):
        """
        Should return an http status 404 and an error message.
        """
        project_id = util.MOCK_UUID_1
        experiment_id = util.MOCK_UUID_1
        run_id = "latest"
        operator_id = util.MOCK_UUID_1

        rv = TEST_CLIENT.get(
            f"/projects/{project_id}/experiments/{experiment_id}/runs/{run_id}/operators/{operator_id}/results"
        )
        result = rv.json()
        expected = {"message": "The specified operator has no results"}
        self.assertDictEqual(expected, result)
        self.assertEqual(rv.status_code, 404)

        mock_kfp_client.assert_any_call(host="http://ml-pipeline.kubeflow:8888")
        mock_make_bucket.assert_any_call(BUCKET_NAME)
        mock_list_objects.assert_any_call(
            bucket_name=BUCKET_NAME,
            prefix=f"experiments/{experiment_id}/operators/{operator_id}",
            recursive=True,
        )

    @mock.patch(
        "kfp.Client",
        return_value=util.MOCK_KFP_CLIENT,
    )
    @mock.patch.object(MINIO_CLIENT, "make_bucket")
    @mock.patch.object(
        MINIO_CLIENT,
        "list_objects",
        return_value=[
            Object(
                BUCKET_NAME,
                f"experiments/{util.MOCK_UUID_1}/operators/{util.MOCK_UUID_1}/{util.MOCK_RUN_ID}/figure-202110281200000000.png",
            )
        ],
    )
    @mock.patch.object(
        MINIO_CLIENT,
        "get_object",
        return_value=HTTPResponse(body=io.BytesIO(b""), preload_content=False),
    )
    def test_get_operators_results_operator_success(
        self, mock_get_object, mock_list_objects, mock_make_bucket, mock_kfp_client
    ):
        """
        Should return results successfully.
        """
        project_id = util.MOCK_UUID_1
        experiment_id = util.MOCK_UUID_1
        run_id = "latest"
        operator_id = util.MOCK_UUID_1

        rv = TEST_CLIENT.get(
            f"/projects/{project_id}/experiments/{experiment_id}/runs/{run_id}/operators/{operator_id}/results"
        )
        self.assertEqual(rv.status_code, 200)
        self.assertEqual(
            rv.headers.get("Content-Disposition"), "attachment; filename=results.zip"
        )
        self.assertEqual(rv.headers.get("Content-Type"), "application/x-zip-compressed")

        mock_kfp_client.assert_any_call(host="http://ml-pipeline.kubeflow:8888")
        mock_make_bucket.assert_any_call(BUCKET_NAME)
        mock_list_objects.assert_any_call(
            bucket_name=BUCKET_NAME,
            prefix=f"experiments/{experiment_id}/operators/{operator_id}",
            recursive=True,
        )
        mock_get_object.assert_any_call(
            bucket_name=BUCKET_NAME,
            object_name=f"experiments/{experiment_id}/operators/{operator_id}/{util.MOCK_RUN_ID}/figure-202110281200000000.png",
        )
