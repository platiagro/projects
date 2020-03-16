# -*- coding: utf-8 -*-
import unittest

from projects.api.main import app

PROJECT_ID = "51c487dd-f9f5-4e91-9477-406c72392f47"
EXPERIMENT_ID = "a9127077-44cf-44b4-adbe-5a168ca7d51a"
OPERATOR_ID = "2b457c55-2e2c-485a-a1c3-db4492dace33"


class TestFigures(unittest.TestCase):

    def test_list_figures(self):
        with app.test_client() as c:
            rv = c.get("/projects/{}/experiments/{}/operators/{}/figures".format(PROJECT_ID, EXPERIMENT_ID, OPERATOR_ID))
            result = rv.get_json()
            self.assertIsInstance(result, list)
