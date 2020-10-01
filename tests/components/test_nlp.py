from os import environ, makedirs, path, remove
from requests import get
from unittest import TestCase

from pytest import fixture
from papermill import execute_notebook

from .utils import creates_mock_dataset, creates_imdb_metadata, delete_mock_dataset
from projects.controllers.utils import uuid_alpha

EXPERIMENT_ID = str(uuid_alpha())
OPERATOR_ID = str(uuid_alpha())
RUN_ID = str(uuid_alpha())

IMDB_DATASET = "IMDB.csv"
IMDB_DATASET_FULL_PATH = f"/tmp/data/{IMDB_DATASET}"
IMDB_TARGET = "label"


class TestNLP(TestCase):

    def setUp(self):
        # Set environment variables needed to run notebooks
        environ["EXPERIMENT_ID"] = EXPERIMENT_ID
        environ["OPERATOR_ID"] = OPERATOR_ID
        environ["RUN_ID"] = RUN_ID

        imdb_content = \
            get("https://raw.githubusercontent.com/platiagro/datasets/master/samples/imdb.csv").content

        # Creates mock imdb dataset
        creates_mock_dataset(IMDB_DATASET, imdb_content)
        creates_imdb_metadata(IMDB_DATASET)

        with open(IMDB_DATASET_FULL_PATH, "wb") as f:
            f.write(imdb_content)

    def tearDown(self):
        files_after_executed = ["Model.py", "contract.json"]

        for generated_file in files_after_executed:
            if path.exists(generated_file):
                remove(generated_file)

        # Delete dataset
        delete_mock_dataset(IMDB_DATASET)

    def test_nlp_text_pre_processor(self):
        experiment_path = "samples/nlp-text-pre-processor/Experiment.ipynb"

        # Run test with IMDB dataset
        execute_notebook(experiment_path, "/dev/null", parameters=dict(dataset=IMDB_DATASET_FULL_PATH,
                                                                       target=IMDB_TARGET,
                                                                       model_features="text"))
