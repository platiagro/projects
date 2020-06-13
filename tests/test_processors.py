from os import environ, path, remove
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
IRIS_TARGET = "Species"
TITANIC_DATASET = "titanic_mock"
TITANIC_TARGET = "Survived"


class TestProcessors(TestCase):
    def setUp(self):
        # Set environment variables needed to run notebooks
        environ["EXPERIMENT_ID"] = EXPERIMENT_ID
        environ["KERNEL_ID"] = KERNEL_ID
        environ["OPERATOR_ID"] = OPERATOR_ID

        iris_content = \
            get('https://raw.githubusercontent.com/platiagro/datasets/master/samples/iris.csv').content

        titanic_content = \
            get('https://raw.githubusercontent.com/platiagro/datasets/master/samples/titanic.csv').content

        # Creates mock iris dataset
        creates_mock_dataset(IRIS_DATASET, iris_content)
        creates_iris_metadata(IRIS_DATASET)

        # Creates mock titanic dataset
        creates_mock_dataset(TITANIC_DATASET, titanic_content)
        creates_titanic_metadata(TITANIC_DATASET)

    def tearDown(self):
        if path.exists("CustomTransfomer.py"):
            remove("CustomTransfomer.py")

    def test_filter_selection(self):
        input_path = "samples/filter-selection/Experiment.ipynb"

        # Run test with iris dataset
        execute_notebook(input_path, "-", parameters=dict(dataset=IRIS_DATASET, targe=IRIS_TARGET))

        # Run test with iris dataset
        execute_notebook(input_path, "-", parameters=dict(dataset=TITANIC_DATASET, targe=TITANIC_TARGET))

        # Delete modified dataset
        delete_mock_dataset(IRIS_DATASET)
        delete_mock_dataset(TITANIC_DATASET)

    def test_imputer(self):
        input_path = "samples/imputer/Experiment.ipynb"

        # Run test with iris dataset
        execute_notebook(input_path, "-", parameters=dict(dataset=IRIS_DATASET, targe=IRIS_TARGET))

        # Run test with iris dataset
        execute_notebook(input_path, "-", parameters=dict(dataset=TITANIC_DATASET, targe=TITANIC_TARGET))

    def test_normalizer(self):
        input_path = "samples/normalizer/Experiment.ipynb"

        # Run test with iris dataset
        execute_notebook(input_path, "-", parameters=dict(dataset=IRIS_DATASET, targe=IRIS_TARGET))

        # Run test with iris dataset
        execute_notebook(input_path, "-", parameters=dict(dataset=TITANIC_DATASET, targe=TITANIC_TARGET))

    def test_pre_selection(self):
        input_path = "samples/pre-selection/Experiment.ipynb"

        # Run test with iris dataset
        execute_notebook(input_path, "-", parameters=dict(dataset=IRIS_DATASET, targe=IRIS_TARGET))

        # Run test with iris dataset
        execute_notebook(input_path, "-", parameters=dict(dataset=TITANIC_DATASET, targe=TITANIC_TARGET))
        # Delete modified dataset
        delete_mock_dataset(IRIS_DATASET)
        delete_mock_dataset(TITANIC_DATASET)

    def test_robust_scaler(self):
        input_path = "samples/normalizer/Experiment.ipynb"

        # Run test with iris dataset
        execute_notebook(input_path, "-", parameters=dict(dataset=IRIS_DATASET, targe=IRIS_TARGET))

        # Run test with iris dataset
        execute_notebook(input_path, "-", parameters=dict(dataset=TITANIC_DATASET, targe=TITANIC_TARGET))

    def test_variance_threshold(self):
        input_path = "samples/normalizer/Experiment.ipynb"

        # Run test with iris dataset
        execute_notebook(input_path, "-", parameters=dict(dataset=IRIS_DATASET, targe=IRIS_TARGET))

        # Run test with iris dataset
        execute_notebook(input_path, "-", parameters=dict(dataset=TITANIC_DATASET, targe=TITANIC_TARGET))

        # Delete modified dataset
        delete_mock_dataset(IRIS_DATASET)
        delete_mock_dataset(TITANIC_DATASET)
