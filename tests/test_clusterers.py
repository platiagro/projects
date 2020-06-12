from io import BytesIO
from json import dumps
from os import stat, environ
from requests import get, post
from unittest import TestCase

from papermill import execute_notebook

from minio.error import BucketAlreadyOwnedByYou

from projects.controllers.utils import uuid_alpha
from projects.object_storage import BUCKET_NAME, MINIO_CLIENT

EXPERIMENT_ID = str(uuid_alpha())
KERNEL_ID = str(uuid_alpha())
OPERATOR_ID = str(uuid_alpha())

IRIS_CONTENT = get('https://raw.githubusercontent.com/platiagro/datasets/master/samples/iris.csv')
IRIS_DATASET = "iris_mock.csv"

TITANIC_CONTENT = get('https://raw.githubusercontent.com/platiagro/datasets/master/samples/titanic.csv')
TITANIC_DATASET = "titanic_mock.csv"

class TestClusteres(TestCase):
    def setUp(self):
        # Set environment variables needed to run notebooks
        environ["EXPERIMENT_ID"] = EXPERIMENT_ID
        environ["KERNEL_ID"] = KERNEL_ID
        environ["OPERATOR_ID"] = OPERATOR_ID

        try:
            MINIO_CLIENT.make_bucket(BUCKET_NAME)
        except BucketAlreadyOwnedByYou:
            pass

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

        file = BytesIO(TITANIC_CONTENT.content)
        MINIO_CLIENT.put_object(
            bucket_name=BUCKET_NAME,
            object_name=f"datasets/{TITANIC_DATASET}/{TITANIC_DATASET}",
            data=file,
            length=file.getbuffer().nbytes,
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

    def test_kmeans(self):
        input_path = "samples/kmeans-clustering/Experiment.ipynb"

        # Run test with boston dataset
        execute_notebook(input_path, "-", parameters=dict(dataset=IRIS_DATASET))

        # Run with titanic dataset
        execute_notebook(input_path, "-", parameters=dict(dataset=TITANIC_DATASET))

    def test_isolation_foresting(self):
        input_path = "samples/isolation-forest-clustering/Experiment.ipynb"

        # Run test with boston dataset
        execute_notebook(input_path, "-", parameters=dict(dataset=IRIS_DATASET))

        # Run with titanic dataset
        execute_notebook(input_path, "-", parameters=dict(dataset=TITANIC_DATASET))
