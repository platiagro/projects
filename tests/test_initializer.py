# -*- coding: utf-8 -*-
from os import remove
from unittest import TestCase

from projects.initializer import init_artifacts, init_tasks

EXPERIMENT_NOTEBOOK_PATH = "Experiment.ipynb"
EXPERIMENT_NOTEBOOK = '{"cells":[{"cell_type":"code","execution_count":null,"metadata":{},"outputs":[],"source":[]}],"metadata":{"kernelspec":{"display_name":"Python 3","language":"python","name":"python3"},"language_info":{"codemirror_mode":{"name":"ipython","version":3},"file_extension":".py","mimetype":"text/x-python","name":"python","nbconvert_exporter":"python","pygments_lexer":"ipython3","version":"3.6.9"}},"nbformat":4,"nbformat_minor":4}'
DEPLOYMENT_NOTEBOOK_PATH = "Deployment.ipynb"
DEPLOYMENT_NOTEBOOK = '{"cells":[{"cell_type":"code","execution_count":null,"metadata":{},"outputs":[],"source":[]}],"metadata":{"kernelspec":{"display_name":"Python 3","language":"python","name":"python3"},"language_info":{"codemirror_mode":{"name":"ipython","version":3},"file_extension":".py","mimetype":"text/x-python","name":"python","nbconvert_exporter":"python","pygments_lexer":"ipython3","version":"3.6.9"}},"nbformat":4,"nbformat_minor":4}'
ARTIFACTS_CONFIG_PATH = "tst_artifacts_config.json"
TASKS_CONFIG_PATH = "tst_tasks_config.json"
TASKS_CONFIG = f'[{{"name":"foo","description":"foo bar","tags":["DEFAULT"],"image":"image","commands":["CMD"],"arguments":["ARG"],"experimentNotebook":"{EXPERIMENT_NOTEBOOK_PATH}","deploymentNotebook":"{DEPLOYMENT_NOTEBOOK_PATH}"}},{{"name":"bar","description":"bar foo","tags":["DEFAULT"],"image":"image","commands":["CMD"],"arguments":["ARG"],"experimentNotebook":"{EXPERIMENT_NOTEBOOK_PATH}"}},{{"name":"foo","description":"foo bar","tags":["DEFAULT"],"image":"image","commands":["CMD"],"arguments":["ARG"],"deploymentNotebook":"{DEPLOYMENT_NOTEBOOK_PATH}"}}]'
ARTIFACTS_CONFIG = f'[{{"file_path":"{DEPLOYMENT_NOTEBOOK_PATH}","object_name":"artifacts/{DEPLOYMENT_NOTEBOOK_PATH}"}}]'

class TestInitializer(TestCase):

    def setUp(self):
        with open(EXPERIMENT_NOTEBOOK_PATH, "w+") as f:
            f.write(EXPERIMENT_NOTEBOOK)

        with open(DEPLOYMENT_NOTEBOOK_PATH, "w+") as f:
            f.write(DEPLOYMENT_NOTEBOOK)

        with open(ARTIFACTS_CONFIG_PATH, "w+") as f:
            f.write(ARTIFACTS_CONFIG)

        with open(TASKS_CONFIG_PATH, "w+") as f:
            f.write(TASKS_CONFIG)

    def tearDown(self):
        remove(DEPLOYMENT_NOTEBOOK_PATH)
        remove(EXPERIMENT_NOTEBOOK_PATH)
        remove(TASKS_CONFIG_PATH)
        remove(ARTIFACTS_CONFIG_PATH)

    def test_init_artifacts(self):
        init_artifacts(ARTIFACTS_CONFIG_PATH)

    def test_init_tasks(self):
        init_tasks(TASKS_CONFIG_PATH)

