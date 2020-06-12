from os import stat
from io import BytesIO
from json import dumps
from unittest import TestCase

import papermill as pm

from minio.error import BucketAlreadyOwnedByYou
from platiagro import CATEGORICAL, DATETIME, NUMERICAL

from projects.controllers.utils import uuid_alpha
from projects.object_storage import BUCKET_NAME, MINIO_CLIENT

EXPERIMENT_ID = str(uuid_alpha())
KERNEL_ID = str(uuid_alpha())
OPERATOR_ID = str(uuid_alpha())
RUN_ID = str(uuid_alpha())

IRIS_DATASET = "iris_mock.csv"
IRIS_TARGET = "species"
TITANIC_DATASET = "titanic_mock.csv"
TITANIC_TARGET = "Survived"


class TestClassifiers(TestCase):
    def setUp(self):
        try:
            MINIO_CLIENT.make_bucket(BUCKET_NAME)
        except BucketAlreadyOwnedByYou:
            pass

        file_stat = stat(f"tests/{IRIS_DATASET}")
        with open(f"tests/{IRIS_DATASET}", 'rb') as data:
            MINIO_CLIENT.put_object(
                bucket_name=BUCKET_NAME,
                object_name=f"datasets/{IRIS_DATASET}/{IRIS_DATASET}",
                data=data,
                length=file_stat.st_size,
            )

        metadata_stat = stat(f"tests/{IRIS_DATASET}.metadata")
        with open(f"tests/{IRIS_DATASET}.metadata", 'rb') as data:
            MINIO_CLIENT.put_object(
                bucket_name=BUCKET_NAME,
                object_name=f"datasets/{IRIS_DATASET}/{IRIS_DATASET}.metadata",
                data=data,
                length=metadata_stat.st_size,
            )

        file_stat = stat(f"tests/{TITANIC_DATASET}")
        with open(f"tests/{TITANIC_DATASET}", 'rb') as data:
            MINIO_CLIENT.put_object(
                bucket_name=BUCKET_NAME,
                object_name=f"datasets/{TITANIC_DATASET}/{TITANIC_DATASET}",
                data=data,
                length=file_stat.st_size,
            )

        metadata_stat = stat(f"tests/{TITANIC_DATASET}.metadata")
        with open(f"tests/{TITANIC_DATASET}.metadata", 'rb') as data:
            MINIO_CLIENT.put_object(
                bucket_name=BUCKET_NAME,
                object_name=f"datasets/{TITANIC_DATASET}/{TITANIC_DATASET}.metadata",
                data=data,
                length=metadata_stat.st_size,
            )

    def tearDown(self):
        for obj in MINIO_CLIENT.list_objects(BUCKET_NAME, prefix=f"datasets/{IRIS_DATASET}", recursive=True):
            MINIO_CLIENT.remove_object(BUCKET_NAME, obj.object_name)

        for obj in MINIO_CLIENT.list_objects(BUCKET_NAME, prefix=f"datasets/{TITANIC_DATASET}", recursive=True):
            MINIO_CLIENT.remove_object(BUCKET_NAME, obj.object_name)

    def test_run_automl_classifier(self):
        input_path = "samples/automl-classifier/Experiment.ipynb"

        # Run with iris dataset
        pm.execute_notebook(input_path, OUTPUT_PATH, parameters=dict(dataset=IRIS_DATASET,target=IRIS_TARGET))

        # Run with titanic dataset
        pm.execute_notebook(input_path, OUTPUT_PATH, parameters=dict(dataset=TITANIC_DATASET,target=TITANIC_TARGET))

    def test_run_logistic_regression(self):
        input_path = "samples/logistic-regression/Experiment.ipynb"

        # Run test with iris dataset
        pm.execute_notebook(input_path, "-", parameters=dict(dataset=IRIS_DATASET, target=IRIS_TARGET))

        # Run test with titanic dataset
        pm.execute_notebook(input_path, "-", parameters=dict(dataset=TITANIC_DATASET,target=TITANIC_TARGET))

    def test_run_mlp_classifier(self):
        input_path = "samples/mlp-classifier/Experiment.ipynb"

        # Run test with iris dataset
        pm.execute_notebook(input_path, "-", parameters=dict(dataset=IRIS_DATASET, target=IRIS_TARGET))

        # Run test with titanic dataset
        pm.execute_notebook(input_path, "-", parameters=dict(dataset=TITANIC_DATASET,target=TITANIC_TARGET))

    def test_run_random_forest_classifier(self):
        input_path = "samples/random-forest-classifier/Experiment.ipynb"

        # Run test with iris dataset
        pm.execute_notebook(input_path, "-", parameters=dict(dataset=IRIS_DATASET, target=IRIS_TARGET))

        # Run test with titanic dataset
        pm.execute_notebook(input_path, "-", parameters=dict(dataset=TITANIC_DATASET,target=TITANIC_TARGET))

    def test_run_svc(self):
        input_path = "samples/svc/Experiment.ipynb"

        # Run test with iris dataset
        pm.execute_notebook(input_path, "-", parameters=dict(dataset=IRIS_DATASET, target=IRIS_TARGET))

        # Run test with titanic dataset
        pm.execute_notebook(input_path, "-", parameters=dict(dataset=TITANIC_DATASET, target=TITANIC_TARGET))
