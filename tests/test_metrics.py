# -*- coding: utf-8 -*-
from io import BytesIO
from json import dumps
from unittest import TestCase

from minio.error import BucketAlreadyOwnedByYou

from projects.api.main import app
from projects.controllers.utils import uuid_alpha
from projects.object_storage import BUCKET_NAME, MINIO_CLIENT

PROJECT_ID = str(uuid_alpha())
EXPERIMENT_ID = str(uuid_alpha())
OPERATOR_ID = str(uuid_alpha())
METRICS_NAME = f"experiments/{EXPERIMENT_ID}/operators/{OPERATOR_ID}/metrics.json"
METRICS = [{"r2_score": 1.0}, {"accuracy": 1.0, "scores": [1.0, 0.5, 0.1]}]

class TestMetrics(TestCase):
    def setUp(self):
        self.maxDiff = None
        try:
            MINIO_CLIENT.make_bucket(BUCKET_NAME)
        except BucketAlreadyOwnedByYou:
            pass

        buffer = BytesIO(dumps(METRICS).encode())
        MINIO_CLIENT.put_object(
            bucket_name=BUCKET_NAME,
            object_name=METRICS_NAME,
            data=buffer,
            length=buffer.getbuffer().nbytes,
        )

    def tearDown(self):
        prefix = f"experiments/{EXPERIMENT_ID}"
        for obj in MINIO_CLIENT.list_objects(BUCKET_NAME, prefix=prefix, recursive=True):
            MINIO_CLIENT.remove_object(BUCKET_NAME, obj.object_name)

    def test_list_metrics(self):
        with app.test_client() as c:
            rv = c.get(f"/projects/{PROJECT_ID}/experiments/{EXPERIMENT_ID}/operators/{OPERATOR_ID}/metrics")
            result = rv.get_json()
            self.assertIsInstance(result, list)
