# -*- coding: utf-8 -*-
import unittest

from fastapi.testclient import TestClient

from projects.api.main import app
from projects.database import session_scope

import tests.util as util

app.dependency_overrides[session_scope] = util.override_session_scope
TEST_CLIENT = TestClient(app)


class TestParameters(unittest.TestCase):
    maxDiff = None

    def setUp(self):
        """
        Sets up the test before running it.
        """
        util.create_mocks()

    def tearDown(self):
        """
        Deconstructs the test after running it.
        """
        util.delete_mocks()

    def test_list_parameters_task_not_found(self):
        """
        Should return an http status 404 and an error message.
        """
        task_id = "unk"

        rv = TEST_CLIENT.get(f"/tasks/{task_id}/parameters")
        result = rv.json()
        expected = {
            "message": "The specified task does not exist",
            "code": "TaskNotFound",
        }
        self.assertDictEqual(expected, result)
        self.assertEqual(rv.status_code, 404)

    def test_list_parameters_success(self):
        """
        Should return an empty list.
        """
        task_id = util.MOCK_UUID_1

        rv = TEST_CLIENT.get(f"/tasks/{task_id}/parameters")
        result = rv.json()
        expected = util.MOCK_PARAMETERS_TASK_1
        self.assertListEqual(expected, result)
        self.assertEqual(rv.status_code, 200)
