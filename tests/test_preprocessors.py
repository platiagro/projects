from os import environ, path, remove
from requests import get
from unittest import TestCase

from papermill import execute_notebook

from .utils import creates_iris_metadata, creates_titanic_metadata, \
    creates_mock_dataset, creates_eucalyptus_metadata, delete_mock_dataset
from projects.controllers.utils import uuid_alpha

EXPERIMENT_ID = str(uuid_alpha())
OPERATOR_ID = str(uuid_alpha())
RUN_ID = str(uuid_alpha())

IRIS_DATASET = "iris_mock"
IRIS_TARGET = "Species"

TITANIC_DATASET = "titanic_mock"
TITANIC_TARGET = "Survived"

EUCALYPTUS_DATASET = "eucalyptus_mock"
EUCALYPTUS_TARGET = "Utility"


class TestProcessors(TestCase):
    def setUp(self):
        # Set environment variables needed to run notebooks
        environ["EXPERIMENT_ID"] = EXPERIMENT_ID
        environ["OPERATOR_ID"] = OPERATOR_ID
        environ["RUN_ID"] = RUN_ID

        iris_content = \
            get('https://raw.githubusercontent.com/platiagro/datasets/master/samples/iris.csv').content

        titanic_content = \
            get('https://raw.githubusercontent.com/platiagro/datasets/master/samples/titanic.csv').content

        eucalyptus_content = \
            get("https://raw.githubusercontent.com/platiagro/datasets/master/samples/eucalyptus.csv").content

        # Creates mock iris dataset
        creates_mock_dataset(IRIS_DATASET, iris_content)
        creates_iris_metadata(IRIS_DATASET)

        # Creates mock titanic dataset
        creates_mock_dataset(TITANIC_DATASET, titanic_content)
        creates_titanic_metadata(TITANIC_DATASET)

        # Creates mock eucalyptus dataset
        creates_mock_dataset(EUCALYPTUS_DATASET, eucalyptus_content)
        creates_eucalyptus_metadata(EUCALYPTUS_DATASET)

    def tearDown(self):
        files_after_executed = ["CustomTransformer.py", "simulated.py", "tgraph.py"]

        for generated_file in files_after_executed:
            if path.exists(generated_file):
                remove(generated_file)

        # Delete dataset if any remain in Minio
        delete_mock_dataset(IRIS_DATASET)
        delete_mock_dataset(TITANIC_DATASET)
        delete_mock_dataset(EUCALYPTUS_DATASET)

    def test_filter_selection(self):
        input_path = "samples/filter-selection/Experiment.ipynb"

        # Run test with iris dataset
        execute_notebook(input_path, "-", parameters=dict(dataset=IRIS_DATASET, target=IRIS_TARGET))

        # Run test with iris dataset
        execute_notebook(input_path, "tests/output.ipynb", parameters=dict(dataset=TITANIC_DATASET,
                                                                           target=TITANIC_TARGET,
                                                                           features_to_filter=["PassengerId"]))

        # Delete modified dataset
        delete_mock_dataset(IRIS_DATASET)
        delete_mock_dataset(TITANIC_DATASET)

    def test_imputer(self):
        input_path = "samples/imputer/Experiment.ipynb"

        # Run test with iris dataset
        execute_notebook(input_path, "-", parameters=dict(dataset=IRIS_DATASET, target=IRIS_TARGET))

        # Run test with iris dataset
        execute_notebook(input_path, "-", parameters=dict(dataset=TITANIC_DATASET, target=TITANIC_TARGET))

    def test_normalizer(self):
        input_path = "samples/normalizer/Experiment.ipynb"

        # Run test with iris dataset
        execute_notebook(input_path, "-", parameters=dict(dataset=IRIS_DATASET, target=IRIS_TARGET))

        # Run test with iris dataset
        execute_notebook(input_path, "-", parameters=dict(dataset=TITANIC_DATASET, target=TITANIC_TARGET))

    def test_pre_selection(self):
        input_path = "samples/pre-selection/Experiment.ipynb"

        # Run test with iris dataset
        execute_notebook(input_path, "-", parameters=dict(dataset=IRIS_DATASET, target=IRIS_TARGET))

        # Run test with iris dataset
        execute_notebook(input_path, "-", parameters=dict(dataset=TITANIC_DATASET, target=TITANIC_TARGET))
        # Delete modified dataset
        delete_mock_dataset(IRIS_DATASET)
        delete_mock_dataset(TITANIC_DATASET)

    def test_robust_scaler(self):
        input_path = "samples/normalizer/Experiment.ipynb"

        # Run test with iris dataset
        execute_notebook(input_path, "-", parameters=dict(dataset=IRIS_DATASET, target=IRIS_TARGET))

        # Run test with iris dataset
        execute_notebook(input_path, "-", parameters=dict(dataset=TITANIC_DATASET, target=TITANIC_TARGET))

    def test_variance_threshold(self):
        input_path = "samples/normalizer/Experiment.ipynb"

        # Run test with iris dataset
        execute_notebook(input_path, "-", parameters=dict(dataset=IRIS_DATASET, target=IRIS_TARGET))

        # Run test with iris dataset
        execute_notebook(input_path, "-", parameters=dict(dataset=TITANIC_DATASET, target=TITANIC_TARGET))

        # Delete modified dataset
        delete_mock_dataset(IRIS_DATASET)
        delete_mock_dataset(TITANIC_DATASET)

    # def test_rfe_selector(self):
    #     input_path = "samples/rfe-selector/Experiment.ipynb"

    #     # Run test with eucalyptus dataset
    #     execute_notebook(input_path, "tests/output.ipynb", parameters=dict(dataset=EUCALYPTUS_DATASET, target=EUCALYPTUS_TARGET))

    # def test_simulated_annealing(self):
    #     input_path = "samples/simulated-annealing/Experiment.ipynb"

    #     # Run test with eucalyptus dataset
    #     execute_notebook(input_path, "tests/output.ipynb", parameters=dict(dataset=EUCALYPTUS_DATASET, target=EUCALYPTUS_TARGET))

    #     # Delete modified dataset
    #     delete_mock_dataset(EUCALYPTUS_DATASET)

    # def test_transformation_graph(self):
    #     input_path = "samples/transformation-graph/Experiment.ipynb"

    #     # Run test with eucalyptus dataset
    #     execute_notebook(input_path, "-", parameters=dict(dataset=EUCALYPTUS_DATASET, target=EUCALYPTUS_TARGET))

    #     # Delete modified dataset
    #     delete_mock_dataset(EUCALYPTUS_DATASET)
