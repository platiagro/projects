# -*- coding: utf-8 -*-
from os import remove
from unittest import TestCase

from projects.samples import init_components

EXPERIMENT_NOTEBOOK_PATH = "Experiment.ipynb"
EXPERIMENT_NOTEBOOK = '{"cells":[{"cell_type":"code","execution_count":null,"metadata":{},"outputs":[],"source":[]}],"metadata":{"kernelspec":{"display_name":"Python 3","language":"python","name":"python3"},"language_info":{"codemirror_mode":{"name":"ipython","version":3},"file_extension":".py","mimetype":"text/x-python","name":"python","nbconvert_exporter":"python","pygments_lexer":"ipython3","version":"3.6.9"}},"nbformat":4,"nbformat_minor":4}'
DEPLOYMENT_NOTEBOOK_PATH = "Deployment.ipynb"
DEPLOYMENT_NOTEBOOK = '{"cells":[{"cell_type":"code","execution_count":null,"metadata":{},"outputs":[],"source":[]}],"metadata":{"kernelspec":{"display_name":"Python 3","language":"python","name":"python3"},"language_info":{"codemirror_mode":{"name":"ipython","version":3},"file_extension":".py","mimetype":"text/x-python","name":"python","nbconvert_exporter":"python","pygments_lexer":"ipython3","version":"3.6.9"}},"nbformat":4,"nbformat_minor":4}'
CONFIG_PATH = "config.json"
CONFIG = f'[{{"name":"foo","description":"foo bar","tags":["DEFAULT"],"experimentNotebook":"{EXPERIMENT_NOTEBOOK_PATH}","deploymentNotebook":"{DEPLOYMENT_NOTEBOOK_PATH}"}}]'


class TestApi(TestCase):

    def setUp(self):
        with open(EXPERIMENT_NOTEBOOK_PATH, "w+") as f:
            f.write(EXPERIMENT_NOTEBOOK)

        with open(DEPLOYMENT_NOTEBOOK_PATH, "w+") as f:
            f.write(DEPLOYMENT_NOTEBOOK)

        with open(CONFIG_PATH, "w+") as f:
            f.write(CONFIG)

    def tearDown(self):
        remove(DEPLOYMENT_NOTEBOOK_PATH)
        remove(EXPERIMENT_NOTEBOOK_PATH)
        remove(CONFIG_PATH)

    def test_init_components(self):
        init_components(CONFIG_PATH)
