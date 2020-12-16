# -*- coding: utf-8 -*-
from json import dumps
from unittest import TestCase

from projects.api.main import app
from projects.controllers.utils import uuid_alpha
from projects.database import engine


EXPERIMENT_ID = str(uuid_alpha())
OPERATOR_ID = str(uuid_alpha())
OPERATOR_ID_2 = str(uuid_alpha())
PROJECT_ID = str(uuid_alpha())
TASK_ID = str(uuid_alpha())
TEMPLATE_ID = str(uuid_alpha())
NAME = "foo"
PARAMETERS = {"coef": 0.1}
PARAMETERS_JSON = dumps(PARAMETERS)
POSITION_X = 0.3
POSITION_Y = 0.5
TASK = {
    'dependencies': [],
    'position_x': None,
    'position_y': None,
    'task_id': TASK_ID,
    'uuid': OPERATOR_ID
}
TASKS_JSON = dumps([TASK])
CREATED_AT = "2000-01-01 00:00:00"
CREATED_AT_ISO = "2000-01-01T00:00:00"
UPDATED_AT = "2000-01-01 00:00:00"
UPDATED_AT_ISO = "2000-01-01T00:00:00"

DEPENDENCIES_EMPTY = []
DEPENDENCIES_EMPTY_JSON = dumps(DEPENDENCIES_EMPTY)
DEPENDENCIES_OP_ID = [OPERATOR_ID]
DEPENDENCIES_OP_ID_JSON = dumps(DEPENDENCIES_OP_ID)


class TestTemplates(TestCase):
    def setUp(self):
        self.maxDiff = None
        conn = engine.connect()
        text = (
            f"INSERT INTO tasks (uuid, name, description, image, commands, arguments, tags, experiment_notebook_path, deployment_notebook_path, is_default, created_at, updated_at) "
            f"VALUES ('{TASK_ID}', 'name', 'desc', 'image', '{dumps(['CMD'])}', '{dumps(['ARG'])}', '{dumps(['TAGS'])}', 'experiment_path', 'deploy_path', 0, '{CREATED_AT}', '{UPDATED_AT}')"
        )
        conn.execute(text)

        text = (
            f"INSERT INTO projects (uuid, name, created_at, updated_at) "
            f"VALUES ('{PROJECT_ID}', '{NAME}', '{CREATED_AT}', '{UPDATED_AT}')"
        )
        conn.execute(text)

        text = (
            f"INSERT INTO experiments (uuid, name, project_id, position, is_active, created_at, updated_at) VALUES "
            f"('{EXPERIMENT_ID}', '{NAME}', '{PROJECT_ID}', 0, 1, '{CREATED_AT}', '{UPDATED_AT}')"
        )
        conn.execute(text)

        text = (
            f"INSERT INTO operators (uuid, experiment_id, task_id, parameters, position_x, position_y, created_at, updated_at, dependencies) "
            f"VALUES ('{OPERATOR_ID}', '{EXPERIMENT_ID}', '{TASK_ID}', '{PARAMETERS_JSON}', '{POSITION_X}', "
            f"'{POSITION_Y}', '2000-01-02 00:00:00', '{UPDATED_AT}', '{DEPENDENCIES_EMPTY_JSON}')"
        )
        conn.execute(text)

        text = (
            f"INSERT INTO operators (uuid, experiment_id, task_id, parameters, position_x, position_y, created_at, updated_at, dependencies) "
            f"VALUES ('{OPERATOR_ID_2}', '{EXPERIMENT_ID}', '{TASK_ID}', '{PARAMETERS_JSON}', '{POSITION_X}',"
            f" '{POSITION_Y}', '{CREATED_AT}', '{UPDATED_AT}', '{DEPENDENCIES_OP_ID_JSON}')"
        )
        conn.execute(text)

        text = (
            f"INSERT INTO templates (uuid, name, tasks, created_at, updated_at) "
            f"VALUES ('{TEMPLATE_ID}', '{NAME}', '{TASKS_JSON}', '{CREATED_AT}', '{UPDATED_AT}')"
        )
        conn.execute(text)
        conn.close()

    def tearDown(self):
        conn = engine.connect()
        text = f"DELETE FROM templates WHERE uuid = '{TEMPLATE_ID}'"
        conn.execute(text)

        text = f"DELETE FROM operators WHERE experiment_id = '{EXPERIMENT_ID}'"
        conn.execute(text)

        text = f"DELETE FROM experiments WHERE project_id = '{PROJECT_ID}'"
        conn.execute(text)

        text = f"DELETE FROM projects WHERE uuid = '{PROJECT_ID}'"
        conn.execute(text)

        text = f"DELETE FROM tasks WHERE uuid = '{TASK_ID}'"
        conn.execute(text)
        conn.close()

    def test_list_templates(self):
        with app.test_client() as c:
            rv = c.get("/templates")
            result = rv.get_json()
            self.assertIsInstance(result, list)

    def test_create_template(self):
        with app.test_client() as c:
            rv = c.post("/templates", json={})
            result = rv.get_json()
            expected = {"message": "name is required"}
            self.assertDictEqual(expected, result)
            self.assertEqual(rv.status_code, 400)

            rv = c.post("/templates", json={
                "name": "foo",
            })
            result = rv.get_json()
            expected = {"message": "experimentId is required"}
            self.assertDictEqual(expected, result)
            self.assertEqual(rv.status_code, 400)

            rv = c.post("/templates", json={
                "name": "foo",
                "experimentId": "UNK",
            })
            result = rv.get_json()
            expected = {"message": "The specified experiment does not exist"}
            self.assertDictEqual(expected, result)
            self.assertEqual(rv.status_code, 400)

            rv = c.post("/templates", json={
                "name": "foo",
                "experimentId": EXPERIMENT_ID,
            })
            result = rv.get_json()
            expected = {
                "name": "foo",
                "tasks": [
                    {
                        'dependencies': [],
                        'position_x': POSITION_X,
                        'position_y': POSITION_Y,
                        'task_id': TASK_ID,
                        'uuid': OPERATOR_ID
                    },
                    {
                        'dependencies': [OPERATOR_ID],
                        'position_x': POSITION_X,
                        'position_y': POSITION_Y,
                        'task_id': TASK_ID,
                        'uuid': OPERATOR_ID_2
                    }
                ],
            }
            # uuid, created_at, updated_at are machine-generated
            # we assert they exist, but we don't assert their values
            machine_generated = ["uuid", "createdAt", "updatedAt"]
            for attr in machine_generated:
                self.assertIn(attr, result)
                del result[attr]
            self.assertDictEqual(expected, result)

    def test_get_template(self):
        with app.test_client() as c:
            rv = c.get("/templates/foo")
            result = rv.get_json()
            expected = {"message": "The specified template does not exist"}
            self.assertDictEqual(expected, result)
            self.assertEqual(rv.status_code, 404)

            rv = c.get(f"/templates/{TEMPLATE_ID}")
            result = rv.get_json()
            expected = {
                "uuid": TEMPLATE_ID,
                "name": NAME,
                "tasks": [TASK],
                "createdAt": CREATED_AT_ISO,
                "updatedAt": UPDATED_AT_ISO,
            }
            self.assertDictEqual(expected, result)

    def test_update_template(self):
        with app.test_client() as c:
            rv = c.patch("/templates/foo", json={})
            result = rv.get_json()
            expected = {"message": "The specified template does not exist"}
            self.assertDictEqual(expected, result)
            self.assertEqual(rv.status_code, 404)

            rv = c.patch(f"/templates/{TEMPLATE_ID}", json={
                "unk": "bar",
            })
            result = rv.get_json()
            self.assertEqual(rv.status_code, 400)

            rv = c.patch(f"/templates/{TEMPLATE_ID}", json={
                "name": "bar",
            })
            result = rv.get_json()
            expected = {
                "uuid": TEMPLATE_ID,
                "name": "bar",
                "tasks": [TASK],
                "createdAt": CREATED_AT_ISO,
            }
            machine_generated = ["updatedAt"]
            for attr in machine_generated:
                self.assertIn(attr, result)
                del result[attr]
            self.assertDictEqual(expected, result)

    def test_delete_template(self):
        with app.test_client() as c:
            rv = c.delete("/templates/unk")
            result = rv.get_json()
            expected = {"message": "The specified template does not exist"}
            self.assertDictEqual(expected, result)
            self.assertEqual(rv.status_code, 404)

            rv = c.delete(f"/templates/{TEMPLATE_ID}")
            result = rv.get_json()
            expected = {"message": "Template deleted"}
            self.assertDictEqual(expected, result)
