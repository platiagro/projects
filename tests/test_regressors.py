from io import BytesIO
from json import dumps
from os import stat
from requests import get
from unittest import TestCase

from papermill import execute_notebook
from minio.error import BucketAlreadyOwnedByYou

from projects.controllers.utils import uuid_alpha
from projects.object_storage import BUCKET_NAME, MINIO_CLIENT

EXPERIMENT_ID = str(uuid_alpha())
KERNEL_ID = str(uuid_alpha())
OPERATOR_ID = str(uuid_alpha())

BOSTON_CONTENT = get('https://raw.githubusercontent.com/platiagro/datasets/master/samples/boston.csv')
BOSTON_DATASET = "boston_mock.csv"
BOSTON_TARGET = "medv"

IRIS_CONTENT = get('https://raw.githubusercontent.com/platiagro/datasets/master/samples/iris.csv')
IRIS_DATASET = "iris_mock.csv"
IRIS_TARGET = "PetalWidthCm"

class TestRegressors(TestCase):
    def setUp(self):
        try:
            MINIO_CLIENT.make_bucket(BUCKET_NAME)
        except BucketAlreadyOwnedByYou:
            pass

        file = BytesIO(BOSTON_CONTENT.content)
        MINIO_CLIENT.put_object(
            bucket_name=BUCKET_NAME,
            object_name=f"datasets/{BOSTON_DATASET}/{BOSTON_DATASET}",
            data=file,
            length=file.getbuffer().nbytes,
        )
        
        metadata_stat = stat(f"tests/{BOSTON_DATASET}.metadata")
        with open(f"tests/{BOSTON_DATASET}.metadata", "rb") as data:
            MINIO_CLIENT.put_object(
                bucket_name=BUCKET_NAME,
                object_name=f"datasets/{BOSTON_DATASET}/{BOSTON_DATASET}.metadata",
                data=data,
                length=metadata_stat.st_size,
            )

        file = BytesIO(IRIS_CONTENT.content)
        MINIO_CLIENT.put_object(
            bucket_name=BUCKET_NAME,
            object_name=f"datasets/{IRIS_DATASET}/{IRIS_DATASET}",
            data=file,
            length=file.getbuffer().nbytes,
        )

        metadata_stat = stat(f"tests/{IRIS_DATASET}.metadata")
        with open(f"tests/{IRIS_DATASET}.metadata", "rb") as data:
            MINIO_CLIENT.put_object(
                bucket_name=BUCKET_NAME,
                object_name=f"datasets/{IRIS_DATASET}/{IRIS_DATASET}.metadata",
                data=data,
                length=metadata_stat.st_size,
            )

    def tearDown(self):
        for obj in MINIO_CLIENT.list_objects(BUCKET_NAME, prefix=f"datasets/{BOSTON_DATASET}", recursive=True):
            MINIO_CLIENT.remove_object(BUCKET_NAME, obj.object_name)

        for obj in MINIO_CLIENT.list_objects(BUCKET_NAME, prefix=f"datasets/{IRIS_DATASET}", recursive=True):
            MINIO_CLIENT.remove_object(BUCKET_NAME, obj.object_name)

    # def test_automl_regressor(self):
    #     input_path = "samples/automl-regressor/Experiment.ipynb"

    #     # Run test with boston dataset
    #     execute_notebook(input_path, "-", parameters=dict(dataset=BOSTON_DATASET, target=BOSTON_TARGET))

    #     # Run test with titanic dataset
    #     execute_notebook(input_path, "-", parameters=dict(dataset=TITANIC_DATASET, target=TITANIC_TARGET))

    def test_linear_regression(self):
        input_path = "samples/linear-regression/Experiment.ipynb"

        # Run test with boston dataset
        execute_notebook(input_path, "-", parameters=dict(dataset=BOSTON_DATASET, target=BOSTON_TARGET))

        # Run test with titanic dataset
        execute_notebook(input_path, "-", parameters=dict(dataset=IRIS_DATASET, target=IRIS_TARGET))

    # def test_mlp_regressor(self):
    #     input_path = "samples/mlp-regressor/Experiment.ipynb"

    #     # Run test with boston dataset
    #     execute_notebook(input_path, "-", parameters=dict(dataset=BOSTON_DATASET, target=BOSTON_TARGET))

    #     # Run test with titanic dataset
    #     execute_notebook(input_path, "-", parameters=dict(dataset=TITANIC_DATASET, target=TITANIC_TARGET))

    # def test_random_forest_regressor(self):
    #     input_path = "samples/random-forest-regressor/Experiment.ipynb"

    #     # Run test with boston dataset
    #     execute_notebook(input_path, "-", parameters=dict(dataset=BOSTON_DATASET, target=BOSTON_TARGET))

    #     # Run test with titanic dataset
    #     execute_notebook(input_path, "-", parameters=dict(dataset=TITANIC_DATASET, target=TITANIC_TARGET))

    # def test_svr(self):
    #     input_path = "samples/svr/Experiment.ipynb"

    #     # Run test with boston dataset
    #     execute_notebook(input_path, "-", parameters=dict(dataset=BOSTON_DATASET, target=BOSTON_TARGET))

    #     # Run test with titanic dataset
    #     execute_notebook(input_path, "-", parameters=dict(dataset=TITANIC_DATASET, target=TITANIC_TARGET))
