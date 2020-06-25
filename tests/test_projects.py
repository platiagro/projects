# -*- coding: utf-8 -*-
from unittest import TestCase

from projects.api.main import app
from projects.controllers.utils import uuid_alpha
from projects.database import engine

PROJECT_ID = str(uuid_alpha())
NAME = "foo"
CREATED_AT = "2000-01-01 00:00:00"
CREATED_AT_ISO = "2000-01-01T00:00:00"
UPDATED_AT = "2000-01-01 00:00:00"
UPDATED_AT_ISO = "2000-01-01T00:00:00"
EXPERIMENT_ID = str(uuid_alpha())
EXPERIMENT_NAME = "Novo experimento"
DESCRIPTION= "Description"

PROJECT_ID_2 = str(uuid_alpha())
NAME_2 = "foo 2"


class TestProjects(TestCase):
    def setUp(self):
        self.maxDiff = None
        conn = engine.connect()
        text = (
            f"INSERT INTO projects (uuid, name, created_at, updated_at, description) "
            f"VALUES ('{PROJECT_ID}', '{NAME}', '{CREATED_AT}', '{UPDATED_AT}', '{DESCRIPTION}')"
        )
        conn.execute(text)

        text = (
            f"INSERT INTO projects (uuid, name, created_at, updated_at, description) "
            f"VALUES ('{PROJECT_ID_2}', '{NAME_2}', '{CREATED_AT}', '{UPDATED_AT}', '{DESCRIPTION}')"
        )
        conn.execute(text)

        text = (
            f"INSERT INTO experiments (uuid, name, project_id, dataset, target, position, is_active, created_at, updated_at) "
            f"VALUES ('{EXPERIMENT_ID}', '{EXPERIMENT_NAME}', '{PROJECT_ID}', null, null, 0, 1, '{CREATED_AT}', '{UPDATED_AT}')"
        )

        conn.execute(text)
        conn.close()

    def tearDown(self):
        conn = engine.connect()
        text = f"DELETE FROM experiments WHERE uuid = '{EXPERIMENT_ID}'"
        conn.execute(text)

        text = f"DELETE FROM projects WHERE uuid = '{PROJECT_ID}'"
        conn.execute(text)

        text = f"DELETE FROM projects WHERE uuid = '{PROJECT_ID_2}'"
        conn.execute(text)
        conn.close()

    def test_list_projects(self):
        with app.test_client() as c:
            rv = c.get("/projects")
            result = rv.get_json()
            self.assertIsInstance(result, list)

    def test_create_project(self):
        with app.test_client() as c:
            rv = c.post("/projects", json={})
            result = rv.get_json()
            expected = {"message": "name is required"}
            self.assertDictEqual(expected, result)
            self.assertEqual(rv.status_code, 400)

            rv = c.post("/projects", json={
                "name": NAME
            })
            result = rv.get_json()
            expected = {"message": "a project with that name already exists"}
            self.assertDictEqual(expected, result)
            self.assertEqual(rv.status_code, 400)

            project_name = str(uuid_alpha())

            rv = c.post("/projects", json={
                "name": project_name,
                "description": "description"
            })
            result = rv.get_json()
            result_experiments = result.pop("experiments")
            expected = {
                "name": project_name,
                "description": "description",
            }
            # uuid, created_at, updated_at are machine-generated
            # we assert they exist, but we don't assert their values
            machine_generated = ["uuid", "createdAt", "updatedAt"]
            for attr in machine_generated:
                self.assertIn(attr, result)
                del result[attr]
            self.assertDictEqual(expected, result)

            expected = {
                "name": EXPERIMENT_NAME,
                "dataset": None,
                "target": None,
                "position": 0,
                "isActive": True,
                "operators": [],
            }
            self.assertEqual(len(result_experiments), 1)
            machine_generated = ["uuid", "projectId", "createdAt", "updatedAt"]
            for attr in machine_generated:
                self.assertIn(attr, result_experiments[0])
                del result_experiments[0][attr]
            self.assertDictEqual(expected, result_experiments[0])

    def test_get_project(self):
        with app.test_client() as c:
            rv = c.get("/projects/foo")
            result = rv.get_json()
            expected = {"message": "The specified project does not exist"}
            self.assertDictEqual(expected, result)
            self.assertEqual(rv.status_code, 404)

            rv = c.get(f"/projects/{PROJECT_ID}")
            result = rv.get_json()
            result_experiments = result.pop("experiments")
            expected = {
                "uuid": PROJECT_ID,
                "name": NAME,
                "createdAt": CREATED_AT_ISO,
                "updatedAt": UPDATED_AT_ISO,
                "description": DESCRIPTION,
            }
            self.assertDictEqual(expected, result)

            expected = {
                "uuid": EXPERIMENT_ID,
                "name": EXPERIMENT_NAME,
                "projectId": PROJECT_ID,
                "dataset": None,
                "target": None,
                "position": 0,
                "isActive": True,
                "operators": [],
            }
            self.assertEqual(len(result_experiments), 1)
            machine_generated = ["createdAt", "updatedAt"]
            for attr in machine_generated:
                self.assertIn(attr, result_experiments[0])
                del result_experiments[0][attr]
            self.assertDictEqual(expected, result_experiments[0])

    def test_update_project(self):
        with app.test_client() as c:
            rv = c.patch("/projects/foo", json={})
            result = rv.get_json()
            expected = {"message": "The specified project does not exist"}
            self.assertDictEqual(expected, result)
            self.assertEqual(rv.status_code, 404)

            rv = c.patch(f"/projects/{PROJECT_ID}", json={
                "name": NAME_2,
            })
            result = rv.get_json()
            expected = {"message": "a project with that name already exists"}
            self.assertDictEqual(expected, result)
            self.assertEqual(rv.status_code, 400)

            rv = c.patch(f"/projects/{PROJECT_ID}", json={
                "unk": "bar",
            })
            self.assertEqual(rv.status_code, 400)

            # update project using the same name
            rv = c.patch(f"/projects/{PROJECT_ID}", json={
                "name": NAME,
            })
            self.assertEqual(rv.status_code, 200)

            rv = c.patch(f"/projects/{PROJECT_ID}", json={
                "name": "bar",
            })
            result = rv.get_json()
            result_experiments = result.pop("experiments")
            expected = {
                "uuid": PROJECT_ID,
                "name": "bar",
                "createdAt": CREATED_AT_ISO,
                "description": DESCRIPTION,
            }
            machine_generated = ["updatedAt"]
            for attr in machine_generated:
                self.assertIn(attr, result)
                del result[attr]
            self.assertDictEqual(expected, result)

            expected = {
                "uuid": EXPERIMENT_ID,
                "name": EXPERIMENT_NAME,
                "projectId": PROJECT_ID,
                "dataset": None,
                "target": None,
                "position": 0,
                "isActive": True,
                "operators": [],
            }
            self.assertEqual(len(result_experiments), 1)
            machine_generated = ["createdAt", "updatedAt"]
            for attr in machine_generated:
                self.assertIn(attr, result_experiments[0])
                del result_experiments[0][attr]
            self.assertDictEqual(expected, result_experiments[0])

    def test_delete_project(self):
        with app.test_client() as c:
            rv = c.delete("/projects/unk")
            result = rv.get_json()
            expected = {"message": "The specified project does not exist"}
            self.assertDictEqual(expected, result)
            self.assertEqual(rv.status_code, 404)

            rv = c.delete(f"/projects/{PROJECT_ID}")
            result = rv.get_json()
            expected = {"message": "Project deleted"}
            self.assertDictEqual(expected, result)

    def test_pagination_project(self):
        with app.test_client() as p:
            rv = p.get("/projects/?page=1&page_size=1")
            result = rv.get_json()
            self.assertIsInstance(result, list)



