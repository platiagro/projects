# -*- coding: utf-8 -*-
from io import BytesIO
from unittest import TestCase
from uuid import uuid4

from minio.error import BucketAlreadyOwnedByYou

from projects.api.main import app
from projects.database import engine
from projects.object_storage import BUCKET_NAME, MINIO_CLIENT

COMPONENT_ID = str(uuid4())
NAME = "foo"
DESCRIPTION = "long foo"
TRAINING_NOTEBOOK_PATH = "minio://{}/components/{}/Training.ipynb".format(BUCKET_NAME, COMPONENT_ID)
INFERENCE_NOTEBOOK_PATH = "minio://{}/components/{}/Inference.ipynb".format(BUCKET_NAME, COMPONENT_ID)
CREATED_AT = "2000-01-01 00:00:00"
UPDATED_AT = "2000-01-01 00:00:00"


class TestParameters(TestCase):

    def setUp(self):
        conn = engine.connect()
        text = "INSERT INTO components (uuid, name, description, training_notebook_path, inference_notebook_path, is_default, created_at, updated_at) VALUES ('{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}')".format(COMPONENT_ID, NAME, DESCRIPTION, TRAINING_NOTEBOOK_PATH, INFERENCE_NOTEBOOK_PATH, 0, CREATED_AT, UPDATED_AT)
        conn.execute(text)
        conn.close()

        try:
            MINIO_CLIENT.make_bucket(BUCKET_NAME)
        except BucketAlreadyOwnedByYou:
            pass

        file = BytesIO(b'{"cells":[{"cell_type":"code","execution_count":null,"metadata":{},"outputs":[],"source":[]}],"metadata":{"kernelspec":{"display_name":"Python 3","language":"python","name":"python3"},"language_info":{"codemirror_mode":{"name":"ipython","version":3},"file_extension":".py","mimetype":"text/x-python","name":"python","nbconvert_exporter":"python","pygments_lexer":"ipython3","version":"3.6.9"}},"nbformat":4,"nbformat_minor":4}')
        MINIO_CLIENT.put_object(
            bucket_name=BUCKET_NAME,
            object_name=TRAINING_NOTEBOOK_PATH[len("minio://{}/".format(BUCKET_NAME)):],
            data=file,
            length=file.getbuffer().nbytes,
        )

    def tearDown(self):
        conn = engine.connect()
        text = "DELETE FROM components WHERE uuid = '{}'".format(COMPONENT_ID)
        conn.execute(text)
        conn.close()

        prefix = "components/{}".format(COMPONENT_ID)
        for obj in MINIO_CLIENT.list_objects(BUCKET_NAME, prefix=prefix, recursive=True):
            MINIO_CLIENT.remove_object(BUCKET_NAME, obj.object_name)

    def test_list_parameters(self):
        with app.test_client() as c:
            rv = c.get("/components/{}/parameters".format(COMPONENT_ID))
            result = rv.get_json()
            self.assertIsInstance(result, list)
