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
OUTPUT_PATH = "tests/output.ipynb"

IRIS_DATASET = "iris_mock.csv"
IRIS_TARGET = "medv"
TITANIC_DATASET = "titanic_mock.csv"
TITANIC_TARGET = "Survived"


class TestProcessors(TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_filter_selection(self):
        pass

    def test_imputer(self):
        pass

    def test_normalizer(self):
        pass

    def test_pre_selection(self):
        pass

    def test_robust_scaler(self):
        pass

    def test_variance_threshold(self):
        pass
