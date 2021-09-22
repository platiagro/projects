# -*- coding: utf-8 -*-
import unittest
import unittest.mock as mock

from fastapi.testclient import TestClient

from projects.api.main import app
from projects.database import session_scope

import tests.util as util

app.dependency_overrides[session_scope] = util.override_session_scope
TEST_CLIENT = TestClient(app)


class TestFigures(unittest.TestCase):
    maxDiff = None

    # def setUp(self):
    #     self.maxDiff = None
    #     conn = engine.connect()
    #     text = (
    #         f"INSERT INTO projects (uuid, name, created_at, updated_at, tenant) "
    #         f"VALUES (%s, %s, %s, %s, %s)"
    #     )
    #     conn.execute(
    #         text,
    #         (
    #             PROJECT_ID,
    #             NAME,
    #             CREATED_AT,
    #             UPDATED_AT,
    #             TENANT,
    #         ),
    #     )

    #     text = (
    #         f"INSERT INTO experiments (uuid, name, project_id, position, is_active, created_at, updated_at) "
    #         f"VALUES (%s, %s, %s, %s, %s, %s, %s)"
    #     )
    #     conn.execute(
    #         text,
    #         (
    #             EXPERIMENT_ID,
    #             NAME,
    #             PROJECT_ID,
    #             POSITION,
    #             1,
    #             CREATED_AT,
    #             UPDATED_AT,
    #         ),
    #     )

    #     text = (
    #         f"INSERT INTO tasks (uuid, name, description, image, commands, arguments, tags, parameters, "
    #         f"experiment_notebook_path, deployment_notebook_path, cpu_limit, cpu_request, memory_limit, memory_request, "
    #         f"readiness_probe_initial_delay_seconds, is_default, created_at, updated_at) "
    #         f"VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
    #     )
    #     conn.execute(
    #         text,
    #         (
    #             TASK_ID,
    #             NAME,
    #             DESCRIPTION,
    #             IMAGE,
    #             COMMANDS_JSON,
    #             ARGUMENTS_JSON,
    #             TAGS_JSON,
    #             dumps([]),
    #             EXPERIMENT_NOTEBOOK_PATH,
    #             DEPLOYMENT_NOTEBOOK_PATH,
    #             "100m",
    #             "100m",
    #             "1Gi",
    #             "1Gi",
    #             300,
    #             0,
    #             CREATED_AT,
    #             UPDATED_AT,
    #         ),
    #     )

    #     text = (
    #         f"INSERT INTO operators (uuid, name, status, status_message, experiment_id, task_id, parameters, created_at, updated_at) "
    #         f"VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)"
    #     )
    #     conn.execute(
    #         text,
    #         (
    #             OPERATOR_ID,
    #             None,
    #             "Unset",
    #             None,
    #             EXPERIMENT_ID,
    #             TASK_ID,
    #             PARAMETERS_JSON,
    #             CREATED_AT,
    #             UPDATED_AT,
    #         ),
    #     )
    #     conn.close()

    #     t = np.arange(0.0, 2.0, 0.01)
    #     s = 1 + np.sin(2 * np.pi * t)
    #     fig, ax = plt.subplots()
    #     ax.plot(t, s)

    #     platiagro.save_figure(
    #         experiment_id=EXPERIMENT_ID,
    #         operator_id=OPERATOR_ID,
    #         run_id=RUN_ID,
    #         figure=fig,
    #     )

    # def tearDown(self):
    #     prefix = "Experiments/{EXPERIMENT_ID}"
    #     for obj in MINIO_CLIENT.list_objects(
    #         BUCKET_NAME, prefix=prefix, recursive=True
    #     ):
    #         MINIO_CLIENT.remove_object(BUCKET_NAME, obj.object_name)

    #     conn = engine.connect()
    #     text = f"DELETE FROM operators WHERE experiment_id = '{EXPERIMENT_ID}'"
    #     conn.execute(text)

    #     text = f"DELETE FROM tasks WHERE uuid = '{TASK_ID}'"
    #     conn.execute(text)

    #     text = f"DELETE FROM experiments WHERE project_id = '{PROJECT_ID}'"
    #     conn.execute(text)

    #     text = f"DELETE FROM projects WHERE uuid = '{PROJECT_ID}'"
    #     conn.execute(text)
    #     conn.close()

    # def test_list_figures(self):
    #     rv = TEST_CLIENT.get(
    #         f"/projects/1/experiments/unk/runs/unk/operators/{OPERATOR_ID}/figures"
    #     )
    #     result = rv.json()
    #     expected = {"message": "The specified project does not exist"}
    #     self.assertDictEqual(expected, result)
    #     self.assertEqual(rv.status_code, 404)

    #     rv = TEST_CLIENT.get(
    #         f"/projects/{PROJECT_ID}/experiments/unk/runs/unk/operators/{OPERATOR_ID}/figures"
    #     )
    #     result = rv.json()
    #     expected = {"message": "The specified experiment does not exist"}
    #     self.assertDictEqual(expected, result)
    #     self.assertEqual(rv.status_code, 404)

    #     rv = TEST_CLIENT.get(
    #         f"/projects/{PROJECT_ID}/experiments/{EXPERIMENT_ID}/runs/{RUN_ID}/operators/{OPERATOR_ID}/figures"
    #     )
    #     result = rv.json()
    #     self.assertIsInstance(result, list)
