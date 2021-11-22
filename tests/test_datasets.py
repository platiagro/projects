# -*- coding: utf-8 -*-
import unittest
import unittest.mock as mock

from fastapi.testclient import TestClient

from projects.api.main import app
from projects.database import session_scope

import tests.util as util

app.dependency_overrides[session_scope] = util.override_session_scope
TEST_CLIENT = TestClient(app)


class TestDatasets(unittest.TestCase):
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

    def test_list_datasets_project_not_found(self):
        """
        Should return an http status 404 and a message 'specified project does not exist'.
        """
        project_id = "unk"
        experiment_id = util.MOCK_UUID_1
        run_id = "latest"
        operator_id = util.MOCK_UUID_1

        rv = TEST_CLIENT.get(
            f"/projects/{project_id}/experiments/{experiment_id}/runs/{run_id}/operators/{operator_id}/datasets"
        )
        result = rv.json()

        expected = {
            "message": "The specified project does not exist",
            "code": "ProjectNotFound",
        }
        self.assertDictEqual(expected, result)
        self.assertEqual(rv.status_code, 404)

    def test_list_datasets_experiment_not_found(self):
        """
        Should return an http status 404 and a message 'specified experiment does not exist'.
        """
        project_id = util.MOCK_UUID_1
        experiment_id = "unk"
        run_id = "latest"
        operator_id = util.MOCK_UUID_1

        rv = TEST_CLIENT.get(
            f"/projects/{project_id}/experiments/{experiment_id}/runs/{run_id}/operators/{operator_id}/datasets"
        )
        result = rv.json()

        expected = {
            "message": "The specified experiment does not exist",
            "code": "ExperimentNotFound",
        }
        self.assertDictEqual(expected, result)
        self.assertEqual(rv.status_code, 404)

    def test_list_datasets_operator_not_found(self):
        """
        Should return an http status 404 and a message 'specified operator does not exist'.
        """
        project_id = util.MOCK_UUID_1
        experiment_id = util.MOCK_UUID_1
        run_id = "latest"
        operator_id = "unk"

        rv = TEST_CLIENT.get(
            f"/projects/{project_id}/experiments/{experiment_id}/runs/{run_id}/operators/{operator_id}/datasets"
        )
        result = rv.json()

        expected = {
            "message": "The specified operator does not exist",
            "code": "OperatorNotFound",
        }
        self.assertDictEqual(expected, result)
        self.assertEqual(rv.status_code, 404)

    @mock.patch(
        "kfp.Client",
        return_value=util.MOCK_KFP_CLIENT,
    )
    @mock.patch(
        "projects.controllers.experiments.runs.datasets.stat_dataset",
        side_effect=util.FILE_NOT_FOUND_ERROR,
    )
    def test_list_datasets_dataset_not_found(self, mock_stat_dataset, mock_kfp_client):
        """
        Should return an http status 404 and a message 'specified run does not contain dataset'.
        """
        project_id = util.MOCK_UUID_1
        experiment_id = util.MOCK_UUID_1
        run_id = "unk"
        operator_id = util.MOCK_UUID_1
        name = util.IRIS_DATASET_NAME

        rv = TEST_CLIENT.get(
            f"/projects/{project_id}/experiments/{experiment_id}/runs/{run_id}/operators/{operator_id}/datasets"
        )
        result = rv.json()

        expected = {
            "message": "The specified run does not contain dataset",
            "code": "DatasetNotFound",
        }
        self.assertDictEqual(expected, result)
        self.assertEqual(rv.status_code, 404)

        mock_kfp_client.assert_any_call(host="http://ml-pipeline.kubeflow:8888")
        mock_stat_dataset.assert_any_call(
            name=name, operator_id=operator_id, run_id=run_id
        )

    @mock.patch(
        "kfp.Client",
        return_value=util.MOCK_KFP_CLIENT,
    )
    @mock.patch(
        "projects.controllers.experiments.runs.datasets.stat_dataset",
        return_value={
            "columns": util.IRIS_COLUMNS,
            "featuretypes": util.IRIS_FEATURETYPES,
            "original-filename": util.IRIS_DATASET_NAME,
            "total": len(util.IRIS_DATA_ARRAY),
        },
    )
    @mock.patch(
        "projects.controllers.experiments.runs.datasets.load_dataset",
        return_value=util.IRIS_DATAFRAME,
    )
    def test_list_datasets_success(
        self, mock_load_dataset, mock_stat_dataset, mock_kfp_client
    ):
        """
        Should return a experiment successfully.
        """
        name = util.IRIS_DATASET_NAME
        project_id = util.MOCK_UUID_1
        experiment_id = util.MOCK_UUID_1
        run_id = "latest"
        operator_id = util.MOCK_UUID_2

        rv = TEST_CLIENT.get(
            f"/projects/{project_id}/experiments/{experiment_id}/runs/{run_id}/operators/{operator_id}/datasets"
        )
        result = rv.json()

        expected = {
            "columns": [
                "SepalLengthCm",
                "SepalWidthCm",
                "PetalLengthCm",
                "PetalWidthCm",
                "Species",
            ],
            "data": [
                [5.1, 3.5, 1.4, 0.2, "Iris-setosa"],
                [4.9, 3.0, 1.4, 0.2, "Iris-setosa"],
                [4.7, 3.2, 1.3, 0.2, "Iris-setosa"],
                [4.6, 3.1, 1.5, 0.2, "Iris-setosa"],
            ],
            "total": 4,
        }

        self.assertDictEqual(expected, result)
        self.assertEqual(rv.status_code, 200)

        mock_kfp_client.assert_any_call(host="http://ml-pipeline.kubeflow:8888")
        mock_stat_dataset.assert_any_call(
            name=name, operator_id=operator_id, run_id="4546465"
        )
        mock_load_dataset.assert_any_call(
            name=name, run_id="4546465", operator_id=operator_id, page=1, page_size=10
        )

    @mock.patch(
        "kfp.Client",
        return_value=util.MOCK_KFP_CLIENT,
    )
    @mock.patch(
        "projects.controllers.experiments.runs.datasets.stat_dataset",
        side_effect=util.FILE_NOT_FOUND_ERROR,
    )
    def test_list_datasets_no_dataset_assigned_to_run(
        self, mock_stat_dataset, mock_kfp_client
    ):
        """
        Should return an http status 404 and a message 'No dataset assigned to the run'.
        """
        project_id = util.MOCK_UUID_1
        experiment_id = util.MOCK_UUID_1
        run_id = "latest"
        operator_id = util.MOCK_UUID_1
        name = util.IRIS_DATASET_NAME

        rv = TEST_CLIENT.get(
            f"/projects/{project_id}/experiments/{experiment_id}/runs/{run_id}/operators/{operator_id}/datasets"
        )
        result = rv.json()
        expected = {
            "message": "The specified run does not contain dataset",
            "code": "DatasetNotFound",
        }
        self.assertDictEqual(expected, result)
        self.assertEqual(rv.status_code, 404)

        mock_kfp_client.assert_any_call(host="http://ml-pipeline.kubeflow:8888")
        mock_stat_dataset.assert_any_call(
            name=name, operator_id=operator_id, run_id="4546465"
        )

    @mock.patch(
        "kfp.Client",
        return_value=util.MOCK_KFP_CLIENT,
    )
    @mock.patch(
        "projects.controllers.experiments.runs.datasets.stat_dataset",
        return_value={
            "columns": util.IRIS_HEADERLESS_COLUMNS,
            "featuretypes": util.IRIS_FEATURETYPES,
            "original-filename": util.IRIS_DATASET_NAME,
            "total": len(util.IRIS_DATA_ARRAY),
        },
    )
    @mock.patch(
        "projects.controllers.experiments.runs.datasets.load_dataset",
        side_effect=util.mock_load_dataset,
    )
    def test_list_datasets_page_size_1(
        self, mock_load_dataset, mock_stat_dataset, mock_kfp_client
    ):
        """
        Should return a list of data and columns with one element.
        """
        project_id = util.MOCK_UUID_1
        experiment_id = util.MOCK_UUID_1
        run_id = "latest"
        operator_id = util.MOCK_UUID_2
        name = util.IRIS_DATASET_NAME

        rv = TEST_CLIENT.get(
            f"/projects/{project_id}/experiments/{experiment_id}/runs/{run_id}/operators/{operator_id}/datasets?page=1&page_size=1"
        )
        result = rv.json()

        expected = {
            "columns": [
                "col0",
                "col1",
                "col2",
                "col3",
                "col4",
            ],
            "data": [
                [5.1, 3.5, 1.4, 0.2, "Iris-setosa"],
            ],
            "total": 4,
        }
        self.assertDictEqual(expected, result)

        mock_kfp_client.assert_any_call(host="http://ml-pipeline.kubeflow:8888")
        mock_stat_dataset.assert_any_call(
            name=name, operator_id=operator_id, run_id="4546465"
        )
        mock_load_dataset.assert_any_call(
            name=name, run_id="4546465", operator_id=operator_id, page=1, page_size=1
        )

    @mock.patch(
        "kfp.Client",
        return_value=util.MOCK_KFP_CLIENT,
    )
    @mock.patch(
        "projects.controllers.experiments.runs.datasets.stat_dataset",
        return_value={
            "columns": util.IRIS_HEADERLESS_COLUMNS,
            "featuretypes": util.IRIS_FEATURETYPES,
            "original-filename": util.IRIS_DATASET_NAME,
        },
    )
    @mock.patch(
        "projects.controllers.experiments.runs.datasets.load_dataset",
        side_effect=util.mock_load_dataset,
    )
    def test_list_datasets_page_size_minus_1(
        self, mock_load_dataset, mock_stat_dataset, mock_kfp_client
    ):
        """
        Should return the dataset formatted as a .CSV file with one less page.
        """
        project_id = util.MOCK_UUID_1
        experiment_id = util.MOCK_UUID_1
        run_id = "latest"
        operator_id = util.MOCK_UUID_2
        name = util.IRIS_DATASET_NAME

        rv = TEST_CLIENT.get(
            f"/projects/{project_id}/experiments/{experiment_id}/runs/{run_id}/operators/{operator_id}/datasets?page=1&page_size=-1"
        )
        result = rv.json()
        expected = {
            "columns": ["col0", "col1", "col2", "col3", "col4"],
            "data": [
                [5.1, 3.5, 1.4, 0.2, "Iris-setosa"],
                [4.9, 3.0, 1.4, 0.2, "Iris-setosa"],
                [4.7, 3.2, 1.3, 0.2, "Iris-setosa"],
            ],
            "total": 3,
        }
        self.assertDictEqual(expected, result)
        self.assertEqual(rv.status_code, 200)

        mock_kfp_client.assert_any_call(host="http://ml-pipeline.kubeflow:8888")
        mock_stat_dataset.assert_any_call(
            name=name, operator_id=operator_id, run_id="4546465"
        )
        mock_load_dataset.assert_any_call(
            name=name, run_id="4546465", operator_id=operator_id, page=1, page_size=-1
        )

    @mock.patch(
        "kfp.Client",
        return_value=util.MOCK_KFP_CLIENT,
    )
    @mock.patch(
        "projects.controllers.experiments.runs.datasets.stat_dataset",
        return_value={
            "columns": util.IRIS_HEADERLESS_COLUMNS,
            "featuretypes": util.IRIS_FEATURETYPES,
            "original-filename": util.IRIS_DATASET_NAME,
        },
    )
    @mock.patch(
        "projects.controllers.experiments.runs.datasets.load_dataset",
        side_effect=util.mock_load_dataset,
    )
    def test_list_datasets_page_not_exist(
        self, mock_load_dataset, mock_stat_dataset, mock_kfp_client
    ):
        """
        Should return the dataset formatted as a .CSV file with three pages.
        """
        project_id = util.MOCK_UUID_1
        experiment_id = util.MOCK_UUID_1
        run_id = "latest"
        operator_id = util.MOCK_UUID_1
        name = util.IRIS_DATASET_NAME

        rv = TEST_CLIENT.get(
            f"/projects/{project_id}/experiments/{experiment_id}/runs/{run_id}/operators/{operator_id}/datasets?page=2&page_size=3"
        )
        result = rv.json()
        expected = {
            "columns": ["col0", "col1", "col2", "col3", "col4"],
            "data": [
                [5.1, 3.5, 1.4, 0.2, "Iris-setosa"],
                [4.9, 3.0, 1.4, 0.2, "Iris-setosa"],
                [4.7, 3.2, 1.3, 0.2, "Iris-setosa"],
            ],
            "total": 3,
        }
        self.assertDictEqual(expected, result)
        self.assertEqual(rv.status_code, 200)

        mock_kfp_client.assert_any_call(host="http://ml-pipeline.kubeflow:8888")
        mock_stat_dataset.assert_any_call(
            name=name, operator_id=operator_id, run_id="4546465"
        )
        mock_load_dataset.assert_any_call(
            name=name, run_id="4546465", operator_id=operator_id, page=2, page_size=3
        )
