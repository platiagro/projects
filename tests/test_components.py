# -*- coding: utf-8 -*-
from io import BytesIO
from json import dumps, loads
from unittest import TestCase

import requests
from minio.error import BucketAlreadyOwnedByYou

from projects.api.main import app
from projects.controllers.utils import uuid_alpha
from projects.database import engine
from projects.jupyter import JUPYTER_ENDPOINT, COOKIES, HEADERS
from projects.object_storage import BUCKET_NAME, MINIO_CLIENT

COMPONENT_ID = str(uuid_alpha())
NAME = "foo"
DESCRIPTION = "long foo"
TAGS = ["PREDICTOR"]
TAGS_JSON = dumps(TAGS)
TRAINING_NOTEBOOK_PATH = f"minio://{BUCKET_NAME}/components/{COMPONENT_ID}/Experiment.ipynb"
INFERENCE_NOTEBOOK_PATH = f"minio://{BUCKET_NAME}/components/{COMPONENT_ID}/Deployment.ipynb"
IS_DEFAULT = False
PARAMETERS = [{"default": True, "name": "shuffle", "type": "boolean"}]
CREATED_AT = "2000-01-01 00:00:00"
CREATED_AT_ISO = "2000-01-01T00:00:00"
UPDATED_AT = "2000-01-01 00:00:00"
UPDATED_AT_ISO = "2000-01-01T00:00:00"
SAMPLE_NOTEBOOK = '{"cells":[{"cell_type":"code","execution_count":null,"metadata":{"tags":["parameters"]},"outputs":[],"source":["shuffle = True #@param {type: \\"boolean\\"}"]}],"metadata":{"kernelspec":{"display_name":"Python 3","language":"python","name":"python3"},"language_info":{"codemirror_mode":{"name":"ipython","version":3},"file_extension":".py","mimetype":"text/x-python","name":"python","nbconvert_exporter":"python","pygments_lexer":"ipython3","version":"3.6.9"}},"nbformat":4,"nbformat_minor":4}'


class TestComponents(TestCase):
    def setUp(self):
        self.maxDiff = None
        conn = engine.connect()
        text = (
            f"INSERT INTO components (uuid, name, description, tags, training_notebook_path, inference_notebook_path, is_default, created_at, updated_at) "
            f"VALUES ('{COMPONENT_ID}', '{NAME}', '{DESCRIPTION}', '{TAGS_JSON}', '{TRAINING_NOTEBOOK_PATH}', '{INFERENCE_NOTEBOOK_PATH}', 0, '{CREATED_AT}', '{UPDATED_AT}')"
        )
        conn.execute(text)
        conn.close()

        try:
            MINIO_CLIENT.make_bucket(BUCKET_NAME)
        except BucketAlreadyOwnedByYou:
            pass

        file = BytesIO(SAMPLE_NOTEBOOK.encode("utf-8"))
        MINIO_CLIENT.put_object(
            bucket_name=BUCKET_NAME,
            object_name=TRAINING_NOTEBOOK_PATH[len(f"minio://{BUCKET_NAME}/"):],
            data=file,
            length=file.getbuffer().nbytes,
        )

        file = BytesIO(b'{"cells":[{"cell_type":"code","execution_count":null,"metadata":{},"outputs":[],"source":[]}],"metadata":{"kernelspec":{"display_name":"Python 3","language":"python","name":"python3"},"language_info":{"codemirror_mode":{"name":"ipython","version":3},"file_extension":".py","mimetype":"text/x-python","name":"python","nbconvert_exporter":"python","pygments_lexer":"ipython3","version":"3.6.9"}},"nbformat":4,"nbformat_minor":4}')
        MINIO_CLIENT.put_object(
            bucket_name=BUCKET_NAME,
            object_name=INFERENCE_NOTEBOOK_PATH[len(f"minio://{BUCKET_NAME}/"):],
            data=file,
            length=file.getbuffer().nbytes,
        )

        session = requests.Session()
        session.cookies.update(COOKIES)
        session.headers.update(HEADERS)
        session.hooks = {
            "response": lambda r, *args, **kwargs: r.raise_for_status(),
        }

        session.put(
            url=f"{JUPYTER_ENDPOINT}/api/contents/components",
            data=dumps({"type": "directory", "content": None}),
        )

        session.put(
            url=f"{JUPYTER_ENDPOINT}/api/contents/components/{COMPONENT_ID}",
            data=dumps({"type": "directory", "content": None}),
        )

        session.put(
            url=f"{JUPYTER_ENDPOINT}/api/contents/components/{COMPONENT_ID}/Deployment.ipynb",
            data=dumps({"type": "notebook", "content": loads(SAMPLE_NOTEBOOK)}),
        )

        session.put(
            url=f"{JUPYTER_ENDPOINT}/api/contents/components/{COMPONENT_ID}/Experiment.ipynb",
            data=dumps({"type": "notebook", "content": loads(SAMPLE_NOTEBOOK)}),
        )

    def tearDown(self):
        prefix = f"components/{COMPONENT_ID}"
        for obj in MINIO_CLIENT.list_objects(BUCKET_NAME, prefix=prefix, recursive=True):
            MINIO_CLIENT.remove_object(BUCKET_NAME, obj.object_name)

        conn = engine.connect()
        text = f"DELETE FROM components WHERE uuid = '{COMPONENT_ID}'"
        conn.execute(text)
        conn.close()

    def test_list_components(self):
        with app.test_client() as c:
            rv = c.get("/components")
            result = rv.get_json()
            self.assertIsInstance(result, list)

    def test_create_component(self):
        with app.test_client() as c:
            # when name is missing
            # should raise bad request
            rv = c.post("/components", json={})
            result = rv.get_json()
            expected = {"message": "name is required"}
            self.assertDictEqual(expected, result)
            self.assertEqual(rv.status_code, 400)

            # when invalid tag is sent
            # should raise bad request
            rv = c.post("/components", json={
                "name": "test",
                "description": "long test",
                "tags": ["UNK"],
                "copyFrom": COMPONENT_ID,
            })
            result = rv.get_json()
            self.assertEqual(rv.status_code, 400)

            # when copyFrom and trainingNotebook/inferenceNotebook are sent
            # should raise bad request
            rv = c.post("/components", json={
                "name": "test",
                "description": "long test",
                "tags": TAGS,
                "copyFrom": COMPONENT_ID,
                "trainingNotebook": loads(SAMPLE_NOTEBOOK),
                "inferenceNotebook": loads(SAMPLE_NOTEBOOK),
            })
            result = rv.get_json()
            expected = {"message": "Either provide notebooks or a component to copy from"}
            self.assertDictEqual(expected, result)
            self.assertEqual(rv.status_code, 400)

            # when copyFrom uuid does note exist
            # should raise bad request
            rv = c.post("/components", json={
                "name": "test",
                "description": "long test",
                "tags": TAGS,
                "copyFrom": "unk",
            })
            result = rv.get_json()
            expected = {"message": "Source component does not exist"}
            self.assertDictEqual(expected, result)
            self.assertEqual(rv.status_code, 400)

            # when neither copyFrom nor trainingNotebook/inferenceNotebook are sent
            # should create a component using an empty template notebook
            rv = c.post("/components", json={
                "name": "test",
                "description": "long test",
            })
            result = rv.get_json()
            expected = {
                "name": "test",
                "description": "long test",
                "tags": ["DEFAULT"],
                "isDefault": IS_DEFAULT,
                "parameters": [
                    {"default": "iris", "name": "dataset", "type": "string"},
                    {"default": "Species", "name": "target", "type": "string"},
                ],
            }
            # uuid, training_notebook_path, inference_notebook_path, created_at, updated_at
            # are machine-generated we assert they exist, but we don't assert their values
            machine_generated = [
                "uuid",
                "trainingNotebookPath",
                "inferenceNotebookPath",
                "createdAt",
                "updatedAt",
            ]
            for attr in machine_generated:
                self.assertIn(attr, result)
                del result[attr]
            self.assertDictEqual(expected, result)

            # when copyFrom is sent
            # should create a component copying notebooks from copyFrom
            rv = c.post("/components", json={
                "name": "test",
                "description": "long test",
                "tags": TAGS,
                "copyFrom": COMPONENT_ID,
            })
            result = rv.get_json()
            expected = {
                "name": "test",
                "description": "long test",
                "tags": TAGS,
                "isDefault": IS_DEFAULT,
                "parameters": PARAMETERS,
            }
            machine_generated = [
                "uuid",
                "trainingNotebookPath",
                "inferenceNotebookPath",
                "createdAt",
                "updatedAt",
            ]
            for attr in machine_generated:
                self.assertIn(attr, result)
                del result[attr]
            self.assertDictEqual(expected, result)

            # when trainingNotebook and inferenceNotebook are sent
            # should create a component using their values as source
            rv = c.post("/components", json={
                "name": "test",
                "description": "long test",
                "tags": TAGS,
                "trainingNotebook": loads(SAMPLE_NOTEBOOK),
                "inferenceNotebook": loads(SAMPLE_NOTEBOOK),
            })
            result = rv.get_json()
            expected = {
                "name": "test",
                "description": "long test",
                "tags": TAGS,
                "isDefault": IS_DEFAULT,
                "parameters": PARAMETERS,
            }
            machine_generated = [
                "uuid",
                "trainingNotebookPath",
                "inferenceNotebookPath",
                "createdAt",
                "updatedAt",
            ]
            for attr in machine_generated:
                self.assertIn(attr, result)
                del result[attr]
            self.assertDictEqual(expected, result)

    def test_get_component(self):
        with app.test_client() as c:
            rv = c.get("/components/foo")
            result = rv.get_json()
            expected = {"message": "The specified component does not exist"}
            self.assertDictEqual(expected, result)
            self.assertEqual(rv.status_code, 404)

            rv = c.get(f"/components/{COMPONENT_ID}")
            result = rv.get_json()
            expected = {
                "uuid": COMPONENT_ID,
                "name": "foo",
                "description": DESCRIPTION,
                "tags": TAGS,
                "trainingNotebookPath": TRAINING_NOTEBOOK_PATH,
                "inferenceNotebookPath": INFERENCE_NOTEBOOK_PATH,
                "isDefault": IS_DEFAULT,
                "parameters": PARAMETERS,
                "createdAt": CREATED_AT_ISO,
                "updatedAt": UPDATED_AT_ISO,
            }
            self.assertDictEqual(expected, result)

    def test_update_component(self):
        with app.test_client() as c:
            rv = c.patch("/components/foo", json={})
            result = rv.get_json()
            expected = {"message": "The specified component does not exist"}
            self.assertDictEqual(expected, result)
            self.assertEqual(rv.status_code, 404)

            rv = c.patch(f"/components/{COMPONENT_ID}", json={
                "unk": "bar",
            })
            result = rv.get_json()
            self.assertEqual(rv.status_code, 400)

            rv = c.patch(f"/components/{COMPONENT_ID}", json={
                "name": "bar",
            })
            result = rv.get_json()
            expected = {
                "uuid": COMPONENT_ID,
                "name": "bar",
                "description": DESCRIPTION,
                "tags": TAGS,
                "trainingNotebookPath": TRAINING_NOTEBOOK_PATH,
                "inferenceNotebookPath": INFERENCE_NOTEBOOK_PATH,
                "isDefault": IS_DEFAULT,
                "parameters": PARAMETERS,
                "createdAt": CREATED_AT_ISO,
            }
            machine_generated = ["updatedAt"]
            for attr in machine_generated:
                self.assertIn(attr, result)
                del result[attr]
            self.assertDictEqual(expected, result)

            rv = c.patch(f"/components/{COMPONENT_ID}", json={
                "tags": ["UNK"],
            })
            result = rv.get_json()
            self.assertEqual(rv.status_code, 400)

            rv = c.patch(f"/components/{COMPONENT_ID}", json={
                "tags": ["FEATURE_ENGINEERING"],
            })
            result = rv.get_json()
            expected = {
                "uuid": COMPONENT_ID,
                "name": "bar",
                "description": DESCRIPTION,
                "tags": ["FEATURE_ENGINEERING"],
                "trainingNotebookPath": TRAINING_NOTEBOOK_PATH,
                "inferenceNotebookPath": INFERENCE_NOTEBOOK_PATH,
                "isDefault": IS_DEFAULT,
                "parameters": PARAMETERS,
                "createdAt": CREATED_AT_ISO,
            }
            machine_generated = ["updatedAt"]
            for attr in machine_generated:
                self.assertIn(attr, result)
                del result[attr]
            self.assertDictEqual(expected, result)

            rv = c.patch(f"/components/{COMPONENT_ID}", json={
                "trainingNotebook": loads(SAMPLE_NOTEBOOK),
            })
            result = rv.get_json()
            expected = {
                "uuid": COMPONENT_ID,
                "name": "bar",
                "description": DESCRIPTION,
                "tags": ["FEATURE_ENGINEERING"],
                "trainingNotebookPath": TRAINING_NOTEBOOK_PATH,
                "inferenceNotebookPath": INFERENCE_NOTEBOOK_PATH,
                "isDefault": IS_DEFAULT,
                "parameters": PARAMETERS,
                "createdAt": CREATED_AT_ISO,
            }
            machine_generated = ["updatedAt"]
            for attr in machine_generated:
                self.assertIn(attr, result)
                del result[attr]
            self.assertDictEqual(expected, result)

            rv = c.patch(f"/components/{COMPONENT_ID}", json={
                "inferenceNotebook": loads(SAMPLE_NOTEBOOK),
            })
            result = rv.get_json()
            expected = {
                "uuid": COMPONENT_ID,
                "name": "bar",
                "description": DESCRIPTION,
                "tags": ["FEATURE_ENGINEERING"],
                "trainingNotebookPath": TRAINING_NOTEBOOK_PATH,
                "inferenceNotebookPath": INFERENCE_NOTEBOOK_PATH,
                "isDefault": IS_DEFAULT,
                "parameters": PARAMETERS,
                "createdAt": CREATED_AT_ISO,
            }
            machine_generated = ["updatedAt"]
            for attr in machine_generated:
                self.assertIn(attr, result)
                del result[attr]
            self.assertDictEqual(expected, result)

    def test_delete_component(self):
        with app.test_client() as c:
            rv = c.delete("/components/unk")
            result = rv.get_json()
            expected = {"message": "The specified component does not exist"}
            self.assertDictEqual(expected, result)
            self.assertEqual(rv.status_code, 404)

            rv = c.delete(f"/components/{COMPONENT_ID}")
            result = rv.get_json()
            expected = {"message": "Component deleted"}
            self.assertDictEqual(expected, result)
