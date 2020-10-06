from os import environ, makedirs, path, remove
from requests import get
from unittest import TestCase

from pytest import fixture
from papermill import execute_notebook

from .utils import creates_mock_dataset, creates_coco_metadata, delete_mock_dataset
from projects.controllers.utils import uuid_alpha

EXPERIMENT_ID = str(uuid_alpha())
OPERATOR_ID = str(uuid_alpha())
RUN_ID = str(uuid_alpha())

COCO_DATASET = "COCO.zip"
COCO_DATASET_FULL_PATH = f"/tmp/data/{COCO_DATASET}"


class TestYolo(TestCase):

    def setUp(self):
        # Set environment variables needed to run notebooks
        environ["EXPERIMENT_ID"] = EXPERIMENT_ID
        environ["OPERATOR_ID"] = OPERATOR_ID
        environ["RUN_ID"] = RUN_ID

        coco_content = \
            get("https://raw.githubusercontent.com/platiagro/datasets/master/samples/coco.zip").content

        # Creates mock coco dataset
        creates_mock_dataset(COCO_DATASET, coco_content)
        creates_coco_metadata(COCO_DATASET)

        with open(COCO_DATASET_FULL_PATH, "wb") as f:
            f.write(coco_content)

    def tearDown(self):
        files_after_executed = ["Model.py", "contract.json"]

        for generated_file in files_after_executed:
            if path.exists(generated_file):
                remove(generated_file)

        # Delete dataset
        delete_mock_dataset(COCO_DATASET)

    def test_yolo(self):
        experiment_path = "samples/default-yolo/Experiment.ipynb"
        deployment_path = "samples/default-yolo/Deployment.ipynb"

        # Run test with COCO dataset
        execute_notebook(experiment_path, "/dev/null", parameters=dict(dataset=COCO_DATASET_FULL_PATH))
