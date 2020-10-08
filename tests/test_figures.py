# -*- coding: utf-8 -*-
from unittest import TestCase

import matplotlib.pyplot as plt
import numpy as np

import platiagro
from projects.api.main import app
from projects.controllers.utils import uuid_alpha
from projects.object_storage import BUCKET_NAME, MINIO_CLIENT

PROJECT_ID = str(uuid_alpha())
EXPERIMENT_ID = str(uuid_alpha())
OPERATOR_ID = str(uuid_alpha())
RUN_ID = str(uuid_alpha())


class TestFigures(TestCase):
    def setUp(self):
        self.maxDiff = None

        t = np.arange(0.0, 2.0, 0.01)
        s = 1 + np.sin(2 * np.pi * t)
        fig, ax = plt.subplots()
        ax.plot(t, s)

        platiagro.save_figure(experiment_id=EXPERIMENT_ID,
                              operator_id=OPERATOR_ID,
                              run_id=RUN_ID,
                              figure=fig)

    def tearDown(self):
        prefix = f"experiments/{EXPERIMENT_ID}"
        for obj in MINIO_CLIENT.list_objects(BUCKET_NAME, prefix=prefix, recursive=True):
            MINIO_CLIENT.remove_object(BUCKET_NAME, obj.object_name)

    def test_list_figures(self):
        with app.test_client() as c:
            rv = c.get(f"/projects/{PROJECT_ID}/experiments/{EXPERIMENT_ID}/operators/{OPERATOR_ID}/figures")
            result = rv.get_json()
            self.assertIsInstance(result, list)

    def test_list_figures_by_run_id(self):
        with app.test_client() as c:
            rv = c.get(f"/projects/{PROJECT_ID}/experiments/{EXPERIMENT_ID}/operators/{OPERATOR_ID}/figures/{RUN_ID}")
            result = rv.get_json()
            self.assertIsInstance(result, list)
