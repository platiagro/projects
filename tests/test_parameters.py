# -*- coding: utf-8 -*-
import unittest
import unittest.mock as mock

from fastapi.testclient import TestClient

from projects.api.main import app
from projects.database import session_scope

import tests.util as util

app.dependency_overrides[session_scope] = util.override_session_scope
TEST_CLIENT = TestClient(app)


class TestParameters(unittest.TestCase):
    maxDiff = None

    # def setUp(self):
    #     self.maxDiff = None
    #     conn = engine.connect()
    #     text = (
    #         f"INSERT INTO tasks (uuid, name, description, image, commands, arguments, category, tags, data_in, data_out, docs, parameters, "
    #         f"experiment_notebook_path, deployment_notebook_path, cpu_limit, cpu_request, memory_limit, memory_request, "
    #         f"readiness_probe_initial_delay_seconds, is_default, created_at, updated_at) "
    #         f"VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
    #     )
    #     conn.execute(text, (TASK_ID, NAME, DESCRIPTION, IMAGE, COMMANDS_JSON, ARGUMENTS_JSON, CATEGORY, TAGS_JSON, DATA_IN, DATA_OUT, DOCS, dumps([]),
    #                         EXPERIMENT_NOTEBOOK_PATH, DEPLOYMENT_NOTEBOOK_PATH, "100m", "100m", "1Gi", "1Gi", 300, 0, CREATED_AT, UPDATED_AT,))
    #     conn.close()

    # def tearDown(self):
    #     conn = engine.connect()
    #     text = f"DELETE FROM tasks WHERE uuid = '{TASK_ID}'"
    #     conn.execute(text)
    #     conn.close()

    # def test_list_parameters(self):
    #     rv = TEST_CLIENT.get("/tasks/unk/parameters")
    #     result = rv.json()
    #     expected = {"message": "The specified task does not exist"}
    #     self.assertDictEqual(expected, result)
    #     self.assertEqual(rv.status_code, 404)

    #     rv = TEST_CLIENT.get(f"/tasks/{TASK_ID}/parameters")
    #     result = rv.json()
    #     self.assertIsInstance(result, list)
