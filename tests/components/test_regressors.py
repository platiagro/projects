from os import environ, path, remove
from requests import get

from pytest import fixture
from papermill import execute_notebook

from .utils import creates_boston_metadata, creates_titanic_metadata, \
    creates_mock_dataset, delete_mock_dataset
from projects.controllers.utils import uuid_alpha

import os

EXPERIMENT_ID = str(uuid_alpha())
OPERATOR_ID = str(uuid_alpha())
RUN_ID = str(uuid_alpha())

BOSTON_DATASET = "boston.csv"
BOSTON_TARGET = "medv"

TITANIC_DATASET = "titanic.csv"
TITANIC_TARGET = "Fare"


@fixture(scope="module", autouse=True)
def setup(request):
    # Set environment variables needed to run notebooks
    environ["EXPERIMENT_ID"] = EXPERIMENT_ID
    environ["OPERATOR_ID"] = OPERATOR_ID
    environ["RUN_ID"] = RUN_ID

    boston_content = \
        get('https://raw.githubusercontent.com/platiagro/datasets/master/samples/boston.csv').content

    titanic_content = \
        get('https://raw.githubusercontent.com/platiagro/datasets/master/samples/titanic.csv').content

    # Creates mock boston dataset
    creates_mock_dataset(BOSTON_DATASET, boston_content)
    creates_boston_metadata(BOSTON_DATASET)

    os.makedirs('/tmp/data', exist_ok=True)

    # BOSTON_DATASET = 'boston.csv'
    with open('/tmp/data/boston.csv', 'wb') as f:
        f.write(boston_content)

    # Creates mock titanic dataset
    creates_mock_dataset(TITANIC_DATASET, titanic_content)
    creates_titanic_metadata(TITANIC_DATASET)

    # TITANIC_DATASET = 'titanic.csv'
    with open('/tmp/data/titanic.csv', 'wb') as f:
        f.write(titanic_content)

    def delete_datasets():
        files_after_executed = ["Model.py", "contract.json"]

        for generated_file in files_after_executed:
            if path.exists(generated_file):
                remove(generated_file)

        # Delete datasets
        delete_mock_dataset(BOSTON_DATASET)
        delete_mock_dataset(TITANIC_DATASET)

    request.addfinalizer(delete_datasets)

# Teste OK
def test_automl_regressor(setup):
    experiment_path = "samples/automl-regressor/Experiment.ipynb"
    deployment_path = "samples/automl-regressor/Deployment.ipynb"

    # Run test with boston and titanic datasets
    execute_notebook(experiment_path, "/dev/null", parameters=dict(dataset=BOSTON_DATASET, target=BOSTON_TARGET))
    execute_notebook(experiment_path, "/dev/null", parameters=dict(dataset=TITANIC_DATASET, target=TITANIC_TARGET))

    # Deploy component
    execute_notebook(deployment_path, "/dev/null")

# Problema no Notebook
def test_linear_regression(setup):
    experiment_path = "samples/linear-regression/Experiment.ipynb"
    deployment_path = "samples/linear-regression/Deployment.ipynb"

    # Run test with boston and titanic datasets
    execute_notebook(experiment_path, "/dev/null", parameters=dict(dataset=BOSTON_DATASET, target=BOSTON_TARGET))
    execute_notebook(experiment_path, "/dev/null", parameters=dict(dataset=BOSTON_DATASET, target=BOSTON_TARGET))

    # Deploy component
    execute_notebook(deployment_path, "/dev/null")

# Teste OK
def test_mlp_regressor(setup):
    experiment_path = "samples/mlp-regressor/Experiment.ipynb"
    deployment_path = "samples/mlp-regressor/Deployment.ipynb"

    # Run test with boston and titanic datasets
    execute_notebook(experiment_path, "/dev/null", parameters=dict(dataset=BOSTON_DATASET, target=BOSTON_TARGET))
    execute_notebook(experiment_path, "/dev/null", parameters=dict(dataset=TITANIC_DATASET, target=TITANIC_TARGET))

    # Deploy component
    execute_notebook(deployment_path, "/dev/null")

# Teste OK
def test_random_forest_regressor(setup):
    experiment_path = "samples/random-forest-regressor/Experiment.ipynb"
    deployment_path = "samples/random-forest-regressor/Deployment.ipynb"

    # Run test with boston and titanic datasets
    execute_notebook(experiment_path, "/dev/null", parameters=dict(dataset=BOSTON_DATASET, target=BOSTON_TARGET))
    execute_notebook(experiment_path, "/dev/null", parameters=dict(dataset=TITANIC_DATASET, target=TITANIC_TARGET))

    # Deploy component
    execute_notebook(deployment_path, "/dev/null")

# Teste OK
def test_svr(setup):
    experiment_path = "samples/svr/Experiment.ipynb"
    deployment_path = "samples/svr/Deployment.ipynb"

    # Run test with boston and titanic datasets
    execute_notebook(experiment_path, "/dev/null", parameters=dict(dataset=BOSTON_DATASET, target=BOSTON_TARGET))
    execute_notebook(experiment_path, "/dev/null", parameters=dict(dataset=TITANIC_DATASET, target=TITANIC_TARGET))

    # Deploy component
    execute_notebook(deployment_path, "/dev/null")
