from os import environ
from requests import get
from unittest import TestCase

from papermill import execute_notebook

from .utils import creates_iris_metadata, creates_titanic_metadata, \
    creates_mock_dataset, delete_mock_dataset
from projects.controllers.utils import uuid_alpha

EXPERIMENT_ID = str(uuid_alpha())
KERNEL_ID = str(uuid_alpha())
OPERATOR_ID = str(uuid_alpha())

IRIS_DATASET = "iris_mock"
TITANIC_DATASET = "titanic_mock"


class TestClusteres(TestCase):
    def setUp(self):
        # Set environment variables needed to run notebooks
        environ["EXPERIMENT_ID"] = EXPERIMENT_ID
        environ["KERNEL_ID"] = KERNEL_ID
        environ["OPERATOR_ID"] = OPERATOR_ID

        iris_content = \
            get('https://raw.githubusercontent.com/platiagro/datasets/master/samples/iris.csv').content

        titanic_content = \
            get('https://raw.githubusercontent.com/platiagro/datasets/master/samples/titanic.csv').content

        # Creates iris dataset
        creates_mock_dataset(IRIS_DATASET, iris_content)
        creates_iris_metadata(IRIS_DATASET)

        # Creates titanic dataset
        creates_mock_dataset(TITANIC_DATASET, titanic_content)
        creates_titanic_metadata(TITANIC_DATASET)

    def tearDown(self):
        # Delete mock datasets
        delete_mock_dataset(IRIS_DATASET)
        # delete_mock_dataset(TITANIC_DATASET)

    def test_kmeans(self):
        input_path = "samples/kmeans-clustering/Experiment.ipynb"

        # Run test with iris dataset
        execute_notebook(input_path, "-", parameters=dict(dataset=IRIS_DATASET))

        # Run with titanic dataset
        execute_notebook(input_path, "-", parameters=dict(dataset=TITANIC_DATASET))

    def test_isolation_foresting(self):
        input_path = "samples/isolation-forest-clustering/Experiment.ipynb"

        # Run test with iris dataset
        execute_notebook(input_path, "-", parameters=dict(dataset=IRIS_DATASET))

        # Run with titanic dataset
        execute_notebook(input_path, "-", parameters=dict(dataset=TITANIC_DATASET))
