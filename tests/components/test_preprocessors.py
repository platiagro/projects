from os import environ, makedirs, path, remove
from requests import get
from unittest import TestCase

from pytest import fixture
from papermill import execute_notebook

from .utils import creates_boston_metadata, creates_iris_metadata, creates_titanic_metadata, \
    creates_mock_dataset, creates_eucalyptus_metadata, delete_mock_dataset
from projects.controllers.utils import uuid_alpha

EXPERIMENT_ID = str(uuid_alpha())
OPERATOR_ID = str(uuid_alpha())
RUN_ID = str(uuid_alpha())

IRIS_DATASET = "iris.csv"
IRIS_TARGET = "Species"

TITANIC_DATASET = "titanic.csv"
TITANIC_TARGET = "Survived"

EUCALYPTUS_DATASET = "eucalyptus.csv"
EUCALYPTUS_TARGET = "Utility"

BOSTON_DATASET = "boston.csv"
BOSTON_TARGET = "medv"


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

        eucalyptus_content = \
            get("https://raw.githubusercontent.com/platiagro/datasets/master/samples/eucalyptus.csv").content

        boston_content = \
            get("https://raw.githubusercontent.com/platiagro/datasets/master/samples/boston.csv").content

        # Creates mock iris dataset
        creates_mock_dataset(IRIS_DATASET, iris_content)
        creates_iris_metadata(IRIS_DATASET)

        makedirs("/tmp/data", exist_ok=True)

        with open(f"/tmp/data/{IRIS_DATASET}", "wb") as f:
            f.write(iris_content)

        # Creates mock titanic dataset
        creates_mock_dataset(TITANIC_DATASET, titanic_content)
        creates_titanic_metadata(TITANIC_DATASET)

        with open(f"/tmp/data/{TITANIC_DATASET}", "wb") as f:
            f.write(titanic_content)

        # Creates mock eucalyptus dataset
        creates_mock_dataset(EUCALYPTUS_DATASET, eucalyptus_content)
        creates_eucalyptus_metadata(EUCALYPTUS_DATASET)

        with open(f"/tmp/data/{EUCALYPTUS_DATASET}", "wb") as f:
            f.write(eucalyptus_content)

        # Creates mock boston dataset
        creates_mock_dataset(BOSTON_DATASET, boston_content)
        creates_boston_metadata(BOSTON_DATASET)

        with open(f"/tmp/data/{BOSTON_DATASET}", "wb") as f:
            f.write(boston_content)

    def tearDown(self):
        files_after_executed = ["CustomTransformer.py", "simulated.py", "tgraph.py",
                                "Model.py", "contract.json"]

        for generated_file in files_after_executed:
            if path.exists(generated_file):
                remove(generated_file)

        # Delete dataset
        delete_mock_dataset(IRIS_DATASET)
        delete_mock_dataset(TITANIC_DATASET)
        delete_mock_dataset(EUCALYPTUS_DATASET)
        delete_mock_dataset(BOSTON_DATASET)

    def test_filter_selection(self):
        experiment_path = "samples/filter-selection/Experiment.ipynb"
        deployment_path = "samples/filter-selection/Deployment.ipynb"

        # Run test with iris and titanic datasets
        execute_notebook(experiment_path, "/dev/null", parameters=dict(dataset=IRIS_DATASET,
                                                                       target=IRIS_TARGET))
        execute_notebook(experiment_path, "/dev/null", parameters=dict(dataset=TITANIC_DATASET,
                                                                       target=TITANIC_TARGET,
                                                                       features_to_filter=["PassengerId"]))

        # Deploy component
        execute_notebook(deployment_path, "/dev/null")

    def test_imputer(self):
        experiment_path = "samples/imputer/Experiment.ipynb"
        deployment_path = "samples/imputer/Deployment.ipynb"

        # Run test with iris and titanic datasets
        execute_notebook(experiment_path, "/dev/null", parameters=dict(dataset=IRIS_DATASET,
                                                                       target=IRIS_TARGET))
        execute_notebook(experiment_path, "/dev/null", parameters=dict(dataset=TITANIC_DATASET,
                                                                       target=TITANIC_TARGET))

        # Deploy component
        execute_notebook(deployment_path, "/dev/null")

    def test_normalizer(self):
        experiment_path = "samples/normalizer/Experiment.ipynb"
        deployment_path = "samples/normalizer/Deployment.ipynb"

        # Run test with iris and titanic datasets
        execute_notebook(experiment_path, "/dev/null", parameters=dict(dataset=IRIS_DATASET,
                                                                       target=IRIS_TARGET))
        execute_notebook(experiment_path, "/dev/null", parameters=dict(dataset=TITANIC_DATASET,
                                                                       target=TITANIC_TARGET))

        # Deploy component
        execute_notebook(deployment_path, "/dev/null")

    def test_pre_selection(self):
        experiment_path = "samples/pre-selection/Experiment.ipynb"
        deployment_path = "samples/pre-selection/Deployment.ipynb"

        # Run test with iris and titanic datasets
        execute_notebook(experiment_path, "/dev/null", parameters=dict(dataset=IRIS_DATASET,
                                                                       target=IRIS_TARGET))
        execute_notebook(experiment_path, "/dev/null", parameters=dict(dataset=TITANIC_DATASET,
                                                                       target=TITANIC_TARGET))

        # Deploy component
        execute_notebook(deployment_path, "/dev/null")

    def test_robust_scaler(self):
        experiment_path = "samples/robust-scaler/Experiment.ipynb"
        deployment_path = "samples/robust-scaler/Deployment.ipynb"

        # Run test with iris and titanic datasets
        execute_notebook(experiment_path, "/dev/null", parameters=dict(dataset=IRIS_DATASET,
                                                                       target=IRIS_TARGET))
        execute_notebook(experiment_path, "/dev/null", parameters=dict(dataset=TITANIC_DATASET,
                                                                       target=TITANIC_TARGET))

        # Deploy component
        execute_notebook(deployment_path, "/dev/null")

    def test_variance_threshold(self):
        experiment_path = "samples/variance-threshold/Experiment.ipynb"
        deployment_path = "samples/variance-threshold/Deployment.ipynb"

        # Run test with iris and titanic datasets
        execute_notebook(experiment_path, "/dev/null", parameters=dict(dataset=IRIS_DATASET,
                                                                       target=IRIS_TARGET))
        execute_notebook(experiment_path, "/dev/null", parameters=dict(dataset=TITANIC_DATASET,
                                                                       target=TITANIC_TARGET))

        # Deploy component
        execute_notebook(deployment_path, "/dev/null")

    def test_rfe_selector(self):
        experiment_path = "samples/rfe-selector/Experiment.ipynb"
        deployment_path = "samples/rfe-selector/Deployment.ipynb"

        # Run test with boston dataset
        execute_notebook(experiment_path, "/dev/null", parameters=dict(dataset=BOSTON_DATASET,
                                                                       target=BOSTON_TARGET))

        # Deploy component
        execute_notebook(deployment_path, "/dev/null")

    def test_simulated_annealing(self):
        experiment_path = "samples/simulated-annealing/Experiment.ipynb"
        deployment_path = "samples/simulated-annealing/Deployment.ipynb"

        # Run test with eucalyptus dataset
        execute_notebook(experiment_path, "/dev/null", parameters=dict(dataset=EUCALYPTUS_DATASET,
                                                                       target=EUCALYPTUS_TARGET))

        # Deploy component
        execute_notebook(deployment_path, "/dev/null")

    def test_transformation_graph(self):
        experiment_path = "samples/transformation-graph/Experiment.ipynb"
        deployment_path = "samples/transformation-graph/Deployment.ipynb"

        # Run test with eucalyptus dataset
        execute_notebook(experiment_path, "/dev/null",
                         parameters=dict(dataset=EUCALYPTUS_DATASET, target=EUCALYPTUS_TARGET))

        # Deploy component
        execute_notebook(deployment_path, "/dev/null")
