from os import environ, makedirs, path, remove
from requests import get
from unittest import TestCase

from pytest import fixture
from papermill import execute_notebook

from .utils import creates_iris_metadata, creates_titanic_metadata, \
    creates_mock_dataset, delete_mock_dataset
from projects.controllers.utils import uuid_alpha
from projects.database import init_db

EXPERIMENT_ID = str(uuid_alpha())
OPERATOR_ID = str(uuid_alpha())
RUN_ID = str(uuid_alpha())

IRIS_DATASET = "iris.csv"
IRIS_DATASET_FULL_PATH = f"/tmp/data/{IRIS_DATASET}"
IRIS_TARGET = "Species"

TITANIC_DATASET = "titanic.csv"
TITANIC_DATASET_FULL_PATH = f"/tmp/data/{TITANIC_DATASET}"
TITANIC_TARGET = "Survived"


class TestClassifiers(TestCase):

    def setUp(self):
        # Set environment variables needed to run notebooks
        environ["EXPERIMENT_ID"] = EXPERIMENT_ID
        environ["OPERATOR_ID"] = OPERATOR_ID
        environ["RUN_ID"] = RUN_ID

        iris_content = \
            get("https://raw.githubusercontent.com/platiagro/datasets/master/samples/iris.csv").content

        titanic_content = \
            get("https://raw.githubusercontent.com/platiagro/datasets/master/samples/titanic.csv").content

        # Creates mock iris dataset
        creates_mock_dataset(IRIS_DATASET, iris_content)
        creates_iris_metadata(IRIS_DATASET)

        makedirs("/tmp/data", exist_ok=True)

        with open(IRIS_DATASET_FULL_PATH, "wb") as f:
            f.write(iris_content)

        # Creates mock titanic dataset
        creates_mock_dataset(TITANIC_DATASET, titanic_content)
        creates_titanic_metadata(TITANIC_DATASET)

        with open(TITANIC_DATASET_FULL_PATH, "wb") as f:
            f.write(titanic_content)

    def tearDown(self):
        files_after_executed = ["Model.py", "contract.json"]

        for generated_file in files_after_executed:
            if path.exists(generated_file):
                remove(generated_file)

        # delete datasets
        delete_mock_dataset(IRIS_DATASET)
        delete_mock_dataset(TITANIC_DATASET)

    def test_run_automl_classifier(self):
        experiment_path = "samples/automl-classifier/Experiment.ipynb"
        deployment_path = "samples/automl-classifier/Deployment.ipynb"

        # Run with iris and titanic datasets
        execute_notebook(experiment_path, "/dev/null", parameters=dict(dataset=IRIS_DATASET_FULL_PATH,
                                                                       target=IRIS_TARGET))
        execute_notebook(experiment_path, "/dev/null", parameters=dict(dataset=TITANIC_DATASET_FULL_PATH,
                                                                       target=TITANIC_TARGET))

        # Deploy component
        execute_notebook(deployment_path, "/dev/null")

    def test_run_logistic_regression(self):
        experiment_path = "samples/logistic-regression/Experiment.ipynb"
        deployment_path = "samples/logistic-regression/Deployment.ipynb"

        # Run test with iris and titanic datasets
        execute_notebook(experiment_path, "/dev/null", parameters=dict(dataset=IRIS_DATASET_FULL_PATH,
                                                                       target=IRIS_TARGET))
        execute_notebook(experiment_path, "/dev/null", parameters=dict(dataset=TITANIC_DATASET_FULL_PATH,
                                                                       target=TITANIC_TARGET))

        # Deploy component
        execute_notebook(deployment_path, "/dev/null")

    def test_run_mlp_classifier(self):
        experiment_path = "samples/mlp-classifier/Experiment.ipynb"
        deployment_path = "samples/mlp-classifier/Deployment.ipynb"

        # Run test with iris and titanic datasets
        execute_notebook(experiment_path, "/dev/null", parameters=dict(dataset=IRIS_DATASET_FULL_PATH,
                                                                       target=IRIS_TARGET))
        execute_notebook(experiment_path, "/dev/null", parameters=dict(dataset=TITANIC_DATASET_FULL_PATH,
                                                                       target=TITANIC_TARGET))

        # Deploy component
        execute_notebook(deployment_path, "/dev/null")

    def test_run_random_forest_classifier(self):
        experiment_path = "samples/random-forest-classifier/Experiment.ipynb"
        deployment_path = "samples/random-forest-classifier/Deployment.ipynb"

        # Run test with iris and titanic datasets
        execute_notebook(experiment_path, "/dev/null", parameters=dict(dataset=IRIS_DATASET_FULL_PATH,
                                                                       target=IRIS_TARGET))
        execute_notebook(experiment_path, "/dev/null", parameters=dict(dataset=TITANIC_DATASET_FULL_PATH,
                                                                       target=TITANIC_TARGET))

        # Deploy component
        execute_notebook(deployment_path, "/dev/null")

    def test_run_svc(self):
        experiment_path = "samples/svc/Experiment.ipynb"
        deployment_path = "samples/svc/Deployment.ipynb"

        # Run test with iris and titanic datasets
        execute_notebook(experiment_path, "/dev/null", parameters=dict(dataset=IRIS_DATASET_FULL_PATH,
                                                                       target=IRIS_TARGET))
        execute_notebook(experiment_path, "/dev/null", parameters=dict(dataset=TITANIC_DATASET_FULL_PATH,
                                                                       target=TITANIC_TARGET))

        # Deploy component
        execute_notebook(deployment_path, "/dev/null")
