from os import environ
from requests import get
from unittest import TestCase

from papermill import execute_notebook

from .utils import creates_boston_metadata, creates_titanic_metadata, \
    creates_mock_dataset, delete_mock_dataset
from projects.controllers.utils import uuid_alpha

EXPERIMENT_ID = str(uuid_alpha())
OPERATOR_ID = str(uuid_alpha())
RUN_ID = str(uuid_alpha())

BOSTON_DATASET = "boston_mock"
BOSTON_TARGET = "medv"
TITANIC_DATASET = "titanic_mock"
TITANIC_TARGET = "Fare"


class TestRegressors(TestCase):
    def setUp(self):
        # Set environment variables needed to run notebooks
        environ["EXPERIMENT_ID"] = EXPERIMENT_ID
        environ["OPERATOR_ID"] = OPERATOR_ID
        environ["RUN_ID"] = RUN_ID

        boston_content = \
            get('https://raw.githubusercontent.com/platiagro/datasets/master/samples/boston.csv').content

        titanic_content = \
            get('https://raw.githubusercontent.com/platiagro/datasets/master/samples/titanic.csv').content

        # Creates mock iris dataset
        creates_mock_dataset(BOSTON_DATASET, boston_content)
        creates_boston_metadata(BOSTON_DATASET)

        # Creates mock titanic dataset
        creates_mock_dataset(TITANIC_DATASET, titanic_content)
        creates_titanic_metadata(TITANIC_DATASET)

    def tearDown(self):
        # Delete datasets
        delete_mock_dataset(BOSTON_DATASET)
        delete_mock_dataset(TITANIC_DATASET)

    def test_automl_regressor(self):
        input_path = "samples/automl-regressor/Experiment.ipynb"

        # Run test with boston dataset
        execute_notebook(input_path, "-", parameters=dict(dataset=BOSTON_DATASET, target=BOSTON_TARGET))

        # Run test with titanic dataset
        execute_notebook(input_path, "-", parameters=dict(dataset=TITANIC_DATASET, target=TITANIC_TARGET))

    def test_linear_regression(self):
        input_path = "samples/linear-regression/Experiment.ipynb"

        # Run test with boston dataset
        execute_notebook(input_path, "-", parameters=dict(dataset=BOSTON_DATASET, target=BOSTON_TARGET))

        # Run test with titanic dataset
        execute_notebook(input_path, "-", parameters=dict(dataset=BOSTON_DATASET, target=BOSTON_TARGET))

    def test_mlp_regressor(self):
        input_path = "samples/mlp-regressor/Experiment.ipynb"

        # Run test with boston dataset
        execute_notebook(input_path, "-", parameters=dict(dataset=BOSTON_DATASET, target=BOSTON_TARGET))

        # Run test with titanic dataset
        execute_notebook(input_path, "-", parameters=dict(dataset=TITANIC_DATASET, target=TITANIC_TARGET))

    def test_random_forest_regressor(self):
        input_path = "samples/random-forest-regressor/Experiment.ipynb"

        # Run test with boston dataset
        execute_notebook(input_path, "-", parameters=dict(dataset=BOSTON_DATASET, target=BOSTON_TARGET))

        # Run test with titanic dataset
        execute_notebook(input_path, "-", parameters=dict(dataset=TITANIC_DATASET, target=TITANIC_TARGET))

    def test_svr(self):
        input_path = "samples/svr/Experiment.ipynb"

        # Run test with boston dataset
        execute_notebook(input_path, "-", parameters=dict(dataset=BOSTON_DATASET, target=BOSTON_TARGET))

        # Run test with titanic dataset
        execute_notebook(input_path, "-", parameters=dict(dataset=TITANIC_DATASET, target=TITANIC_TARGET))
