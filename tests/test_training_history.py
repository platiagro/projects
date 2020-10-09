# -*- coding: utf-8 -*-
from unittest import TestCase

from projects.api.main import app
from projects.controllers.utils import uuid_alpha
from projects.database import engine

EXPERIMENT_ID = str(uuid_alpha())
PROJECT_ID = str(uuid_alpha())
TRAINING_HISTORY_ID = str(uuid_alpha())
NAME = "foo"
POSITION = 0
CREATED_AT = "2000-01-01 00:00:00"
CREATED_AT_ISO = "2000-01-01T00:00:00"
UPDATED_AT = "2000-01-01 00:00:00"
UPDATED_AT_ISO = "2000-01-01T00:00:00"


class TestTrainingHistory(TestCase):
    def setUp(self):
        self.maxDiff = None
        conn = engine.connect()
        text = (
            f"INSERT INTO projects (uuid, name, created_at, updated_at) "
            f"VALUES ('{PROJECT_ID}', '{NAME}', '{CREATED_AT}', '{UPDATED_AT}')"
        )
        conn.execute(text)

        text = (
            f"INSERT INTO experiments (uuid, name, project_id, position, is_active, created_at, updated_at) "
            f"VALUES ('{EXPERIMENT_ID}', '{NAME}', '{PROJECT_ID}', '{POSITION}', 1, '{CREATED_AT}', '{UPDATED_AT}')"
        )
        conn.execute(text)

        text = (
            f"INSERT INTO training_history (uuid, project_id, experiment_id, run_id, details, created_at) "
            f"VALUES ('{TRAINING_HISTORY_ID}', '{PROJECT_ID}', '{EXPERIMENT_ID}', '123', '[]', '{CREATED_AT}')"
        )
        conn.execute(text)

        conn.close()

    def tearDown(self):
        conn = engine.connect()

        text = f"DELETE FROM training_history WHERE project_id in ('{PROJECT_ID}')"
        conn.execute(text)

        text = f"DELETE FROM experiments WHERE project_id in ('{PROJECT_ID}')"
        conn.execute(text)

        text = f"DELETE FROM projects WHERE uuid = '{PROJECT_ID}'"
        conn.execute(text)

        conn.close()

    def test_list_training_history(self):
        with app.test_client() as c:
            rv = c.get(f"/projects/unk/experiments/{EXPERIMENT_ID}/trainingHistory")
            result = rv.get_json()
            expected = {"message": "The specified project does not exist"}
            self.assertDictEqual(expected, result)
            self.assertEqual(rv.status_code, 404)

            rv = c.get(f"/projects/{PROJECT_ID}/experiments/unk/trainingHistory")
            result = rv.get_json()
            expected = {"message": "The specified experiment does not exist"}
            self.assertDictEqual(expected, result)
            self.assertEqual(rv.status_code, 404)

            rv = c.get(f"/projects/{PROJECT_ID}/experiments/{EXPERIMENT_ID}/trainingHistory")
            result = rv.get_json()
            self.assertIsInstance(result, list)

    def test_create_training_history(self):
        with app.test_client() as c:
            rv = c.post(f"/projects/unk/experiments/{EXPERIMENT_ID}/trainingHistory", json={})
            result = rv.get_json()
            expected = {"message": "The specified project does not exist"}
            self.assertDictEqual(expected, result)
            self.assertEqual(rv.status_code, 404)

            rv = c.post(f"/projects/{PROJECT_ID}/experiments/unk/trainingHistory", json={})
            result = rv.get_json()
            expected = {"message": "The specified experiment does not exist"}
            self.assertDictEqual(expected, result)
            self.assertEqual(rv.status_code, 404)

            rv = c.post(f"/projects/{PROJECT_ID}/experiments/{EXPERIMENT_ID}/trainingHistory", json={})
            result = rv.get_json()
            expected = {'message': 'Run id can not be null.'}
            self.assertDictEqual(expected, result)
            self.assertEqual(rv.status_code, 400)

            rv = c.post(f"/projects/{PROJECT_ID}/experiments/{EXPERIMENT_ID}/trainingHistory", json={
                "runId": "runId",
                "operators": [
                    {
                        "unk": "unk"
                    }
                ]
            })
            result = rv.get_json()
            expected = {'message': 'Invalid operator in request.'}
            self.assertDictEqual(expected, result)
            self.assertEqual(rv.status_code, 400)

            rv = c.post(f"/projects/{PROJECT_ID}/experiments/{EXPERIMENT_ID}/trainingHistory", json={
                "runId": "runId",
                "operators": [
                    {
                        "operatorId": "operatorId",
                        "taskId": "taskId",
                        "parameters": []
                    }
                ]
            })
            result = rv.get_json()
            expected = {
                "projectId": PROJECT_ID,
                "experimentId": EXPERIMENT_ID,
                "runId": "runId",
                "details": [
                    {
                        "operatorId": "operatorId",
                        "taskId": "taskId",
                        "parameters": []
                    }
                ]
            }
            # uuid, created_at are machine-generated
            # we assert they exist, but we don't assert their values
            machine_generated = ["uuid", "createdAt"]
            for attr in machine_generated:
                self.assertIn(attr, result)
                del result[attr]
            self.assertDictEqual(expected, result)

    def test_delete_training_history(self):
        with app.test_client() as c:
            rv = c.delete(f"/projects/unk/experiments/{EXPERIMENT_ID}/trainingHistory/{TRAINING_HISTORY_ID}")
            result = rv.get_json()
            expected = {"message": "The specified project does not exist"}
            self.assertDictEqual(expected, result)
            self.assertEqual(rv.status_code, 404)

            rv = c.delete(f"/projects/{PROJECT_ID}/experiments/unk/trainingHistory/{TRAINING_HISTORY_ID}")
            result = rv.get_json()
            expected = {"message": "The specified experiment does not exist"}
            self.assertDictEqual(expected, result)
            self.assertEqual(rv.status_code, 404)

            rv = c.delete(f"/projects/{PROJECT_ID}/experiments/{EXPERIMENT_ID}/trainingHistory/unk")
            result = rv.get_json()
            expected = {"message": "The specified training history does not exist"}
            self.assertDictEqual(expected, result)
            self.assertEqual(rv.status_code, 404)

            rv = c.delete(f"/projects/{PROJECT_ID}/experiments/{EXPERIMENT_ID}/trainingHistory/{TRAINING_HISTORY_ID}")
            result = rv.get_json()
            expected = {"message": "Training history deleted"}
            self.assertDictEqual(expected, result)
