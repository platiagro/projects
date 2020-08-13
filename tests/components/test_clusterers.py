from os import environ, path, remove
from requests import get

from pytest import fixture
from papermill import execute_notebook

from .utils import creates_iris_metadata, creates_titanic_metadata, \
    creates_mock_dataset, delete_mock_dataset
from projects.controllers.utils import uuid_alpha

import os

EXPERIMENT_ID = str(uuid_alpha())
OPERATOR_ID = str(uuid_alpha())
RUN_ID = str(uuid_alpha())

IRIS_DATASET = "iris.csv"
TITANIC_DATASET = "titanic.csv"


@fixture(scope="module", autouse=True)
def setup(request):
    # Set environment variables needed to run notebooks
    environ["EXPERIMENT_ID"] = EXPERIMENT_ID
    environ["OPERATOR_ID"] = OPERATOR_ID
    environ["RUN_ID"] = RUN_ID

    iris_content = \
        get('https://raw.githubusercontent.com/platiagro/datasets/master/samples/iris.csv').content

    titanic_content = \
        get('https://raw.githubusercontent.com/platiagro/datasets/master/samples/titanic.csv').content

    os.makedirs('/tmp/data', exist_ok=True)

    # IRIS_DATASET = 'iris.csv'
    with open('/tmp/data/iris.csv', 'wb') as f:
        f.write(iris_content)

    # Creates iris dataset
    creates_mock_dataset(IRIS_DATASET, iris_content)
    creates_iris_metadata(IRIS_DATASET)

    # TITANIC_DATASET = 'titanic.csv'
    with open('/tmp/data/titanic.csv', 'wb') as f:
        f.write(titanic_content)

    # Creates titanic dataset
    creates_mock_dataset(TITANIC_DATASET, titanic_content)
    creates_titanic_metadata(TITANIC_DATASET)

    def delete_datasets():
        files_after_executed = ["Model.py", "contract.json"]

        for generated_file in files_after_executed:
            if path.exists(generated_file):
                remove(generated_file)

        # delete datasets
        delete_mock_dataset(IRIS_DATASET)
        delete_mock_dataset(TITANIC_DATASET)

    request.addfinalizer(delete_datasets)

# Teste OK
def test_kmeans(setup):
    experiment_path = "samples/kmeans-clustering/Experiment.ipynb"
    deployment_path = "samples/kmeans-clustering/Deployment.ipynb"

    # Run test with iris and titanic datasets
    execute_notebook(experiment_path, "/dev/null", parameters=dict(dataset=IRIS_DATASET))
    execute_notebook(experiment_path, "/dev/null", parameters=dict(dataset=TITANIC_DATASET))

    # Deploy component
    execute_notebook(deployment_path, "/dev/null")

# Teste OK
def test_isolation_foresting(setup):
    experiment_path = "samples/isolation-forest-clustering/Experiment.ipynb"
    deployment_path = "samples/isolation-forest-clustering/Deployment.ipynb"
 
    # Run test with iris and titanic datasets
    execute_notebook(experiment_path, "/dev/null", parameters=dict(dataset=IRIS_DATASET))
    execute_notebook(experiment_path, "/dev/null", parameters=dict(dataset=TITANIC_DATASET))

    # Deploy component
    execute_notebook(deployment_path, "/dev/null")
