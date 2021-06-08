# -*- coding: utf-8 -*-
from unittest import TestCase

from fastapi.testclient import TestClient

from projects.api.main import app
from projects.controllers.utils import uuid_alpha
from projects.database import engine

TEST_CLIENT = TestClient(app)

PROJECT_ID = str(uuid_alpha())
NAME = "foo"
NAME_2 = "foo 2"
NAME_3 = "foo 3"
CREATED_AT = "2000-01-01 00:00:00"
CREATED_AT_ISO = "2000-01-01T00:00:00"
UPDATED_AT = "2000-01-01 00:00:00"
UPDATED_AT_ISO = "2000-01-01T00:00:00"
EXPERIMENT_ID = str(uuid_alpha())
EXPERIMENT_NAME = "Experimento 1"
EXPERIMENT_ID_2 = str(uuid_alpha())
DEPLOYMENT_ID = str(uuid_alpha())
DESCRIPTION = "Description"
STATUS = "Pending"
URL = None

PROJECT_ID_2 = str(uuid_alpha())
PROJECT_ID_3 = str(uuid_alpha())
NAME_2 = "foo 2"


class TestProjects(TestCase):
    def setUp(self):
        self.maxDiff = None
        conn = engine.connect()
        text = (
            f"INSERT INTO projects (uuid, name, description, created_at, updated_at) "
            f"VALUES (%s, %s, %s, %s, %s)"
        )
        conn.execute(text, (PROJECT_ID, NAME, DESCRIPTION, CREATED_AT, UPDATED_AT,))

        text = (
            f"INSERT INTO projects (uuid, name, description, created_at, updated_at) "
            f"VALUES (%s, %s, %s, %s, %s)"
        )
        conn.execute(text, (PROJECT_ID_2, NAME_2, DESCRIPTION, CREATED_AT, UPDATED_AT,))

        text = (
            f"INSERT INTO projects (uuid, name, description, created_at, updated_at) "
            f"VALUES (%s, %s, %s, %s, %s)"
        )
        conn.execute(text, (PROJECT_ID_3, NAME_3, DESCRIPTION, CREATED_AT, UPDATED_AT,))

        text = (
            f"INSERT INTO experiments (uuid, name, project_id, position, is_active, created_at, updated_at) "
            f"VALUES (%s, %s, %s, %s, %s, %s, %s)"
        )
        conn.execute(text, (EXPERIMENT_ID, EXPERIMENT_NAME, PROJECT_ID, 0, 1, CREATED_AT, UPDATED_AT,))

        text = (
            f"INSERT INTO experiments (uuid, name, project_id, position, is_active, created_at, updated_at) "
            f"VALUES (%s, %s, %s, %s, %s, %s, %s)"
        )
        conn.execute(text, (EXPERIMENT_ID_2, EXPERIMENT_NAME, PROJECT_ID_3, 0, 1, CREATED_AT, UPDATED_AT,))

        text = (
            f"INSERT INTO deployments (uuid, name, project_id, experiment_id, position, is_active, status, url, created_at, updated_at) "
            f"VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
        )
        conn.execute(text, (DEPLOYMENT_ID, NAME, PROJECT_ID_3, EXPERIMENT_ID_2, '0', 1, STATUS, URL, CREATED_AT, UPDATED_AT,))
        conn.close()

    def tearDown(self):
        conn = engine.connect()
        text = f"DELETE FROM deployments WHERE uuid = '{DEPLOYMENT_ID}'"
        conn.execute(text)

        text = f"DELETE FROM experiments WHERE uuid = '{EXPERIMENT_ID}'"
        conn.execute(text)

        text = f"DELETE FROM experiments WHERE uuid = '{EXPERIMENT_ID_2}'"
        conn.execute(text)

        text = f"DELETE FROM projects WHERE uuid = '{PROJECT_ID}'"
        conn.execute(text)

        text = f"DELETE FROM projects WHERE uuid = '{PROJECT_ID_2}'"
        conn.execute(text)

        text = f"DELETE FROM projects WHERE uuid = '{PROJECT_ID_3}'"
        conn.execute(text)
        conn.close()

    def test_list_projects(self):
        rv = TEST_CLIENT.get("/projects")
        result = rv.json()
        self.assertIsInstance(result['projects'], list)
        self.assertEqual(rv.status_code, 200)

        rv = TEST_CLIENT.get("/projects?order=uuid asc")
        result = rv.json()
        self.assertIsInstance(result["projects"], list)
        self.assertIsInstance(result["total"], int)
        self.assertEqual(rv.status_code, 200)

        rv = TEST_CLIENT.get("/projects?page=1")
        result = rv.json()
        self.assertIsInstance(result["projects"], list)
        self.assertIsInstance(result["total"], int)
        self.assertEqual(rv.status_code, 200)

        rv = TEST_CLIENT.get(f"/projects?name={NAME}&page=1&order=uuid asc")
        result = rv.json()
        self.assertIsInstance(result["projects"], list)
        self.assertIsInstance(result["total"], int)
        self.assertEqual(rv.status_code, 200)

        rv = TEST_CLIENT.get(f"/projects?name={NAME}&page=1&page_size=10&order=name desc")
        result = rv.json()
        self.assertIsInstance(result["projects"], list)
        self.assertIsInstance(result["total"], int)
        self.assertEqual(rv.status_code, 200)

        rv = TEST_CLIENT.get("/projects?order=name desc")
        result = rv.json()
        self.assertIsInstance(result["projects"], list)
        self.assertIsInstance(result["total"], int)
        self.assertEqual(rv.status_code, 200)

        rv = TEST_CLIENT.get("/projects?order=name unk")
        result = rv.json()
        expected = {"message": "Invalid order argument"}
        self.assertDictEqual(expected, result)
        self.assertEqual(rv.status_code, 400)

        rv = TEST_CLIENT.get("/projects?order=name")
        result = rv.json()
        expected = {"message": "Invalid order argument"}
        self.assertDictEqual(expected, result)
        self.assertEqual(rv.status_code, 400)

    def test_create_project(self):
        rv = TEST_CLIENT.post("/projects", json={})
        result = rv.json()
        expected = {"message": "name is required"}
        self.assertDictEqual(expected, result)
        self.assertEqual(rv.status_code, 400)

        rv = TEST_CLIENT.post("/projects", json={
            "name": NAME
        })
        result = rv.json()
        expected = {"message": "a project with that name already exists"}
        self.assertDictEqual(expected, result)
        self.assertEqual(rv.status_code, 400)

        project_name = str(uuid_alpha())

        rv = TEST_CLIENT.post("/projects", json={
            "name": project_name,
            "description": "description"
        })
        result = rv.json()
        result_experiments = result.pop("experiments")
        expected = {
            "name": project_name,
            "description": "description",
            "hasDeployment": False,
            "hasExperiment": True,
            "hasPreDeployment": False,
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
            "position": 0,
            "isActive": True,
            "operators": [],
        }
        self.assertEqual(len(result_experiments), 1)
        machine_generated = ["uuid", "projectId", "createdAt", "updatedAt", "deployments"]
        for attr in machine_generated:
            self.assertIn(attr, result_experiments[0])
            del result_experiments[0][attr]
        self.assertDictEqual(expected, result_experiments[0])

    def test_get_project(self):
        rv = TEST_CLIENT.get("/projects/foo")
        result = rv.json()
        expected = {"message": "The specified project does not exist"}
        self.assertDictEqual(expected, result)
        self.assertEqual(rv.status_code, 404)

        rv = TEST_CLIENT.get(f"/projects/{PROJECT_ID}")
        result = rv.json()
        result_experiments = result.pop("experiments")
        expected = {
            "uuid": PROJECT_ID,
            "name": NAME,
            "createdAt": CREATED_AT_ISO,
            "updatedAt": UPDATED_AT_ISO,
            "description": DESCRIPTION,
            "hasDeployment": False,
            "hasExperiment": True,
            "hasPreDeployment": False,
        }
        self.assertDictEqual(expected, result)

        expected = {
            "uuid": EXPERIMENT_ID,
            "name": EXPERIMENT_NAME,
            "projectId": PROJECT_ID,
            "position": 0,
            "isActive": True,
            "operators": [],
            "deployments": [],
        }
        self.assertEqual(len(result_experiments), 1)
        machine_generated = ["createdAt", "updatedAt"]
        for attr in machine_generated:
            self.assertIn(attr, result_experiments[0])
            del result_experiments[0][attr]
        self.assertDictEqual(expected, result_experiments[0])

        rv = TEST_CLIENT.get(f"/projects/{PROJECT_ID_3}")
        result = rv.json()
        result_experiments = result.pop("experiments")
        expected = {
            "uuid": PROJECT_ID_3,
            "name": NAME_3,
            "createdAt": CREATED_AT_ISO,
            "updatedAt": UPDATED_AT_ISO,
            "description": DESCRIPTION,
            "hasDeployment": False,
            "hasExperiment": True,
            "hasPreDeployment": True,
        }
        self.assertDictEqual(expected, result)

    def test_update_project(self):
        rv = TEST_CLIENT.patch("/projects/foo", json={})
        result = rv.json()
        expected = {"message": "The specified project does not exist"}
        self.assertDictEqual(expected, result)
        self.assertEqual(rv.status_code, 404)

        rv = TEST_CLIENT.patch(f"/projects/{PROJECT_ID}", json={
            "name": NAME_2,
        })
        result = rv.json()
        expected = {"message": "a project with that name already exists"}
        self.assertDictEqual(expected, result)
        self.assertEqual(rv.status_code, 400)

        rv = TEST_CLIENT.patch(f"/projects/{PROJECT_ID}", json={
            "unk": "bar",
        })
        self.assertEqual(rv.status_code, 400)

        # update project using the same name
        rv = TEST_CLIENT.patch(f"/projects/{PROJECT_ID}", json={
            "name": NAME,
        })
        self.assertEqual(rv.status_code, 200)

        rv = TEST_CLIENT.patch(f"/projects/{PROJECT_ID}", json={
            "name": "bar",
        })
        result = rv.json()
        result_experiments = result.pop("experiments")
        expected = {
            "uuid": PROJECT_ID,
            "name": "bar",
            "createdAt": CREATED_AT_ISO,
            "description": DESCRIPTION,
            "hasPreDeployment": False,
            "hasDeployment": False,
            "hasExperiment": True,
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
            "position": 0,
            "isActive": True,
            "operators": [],
            "deployments": [],
        }
        self.assertEqual(len(result_experiments), 1)
        machine_generated = ["createdAt", "updatedAt"]
        for attr in machine_generated:
            self.assertIn(attr, result_experiments[0])
            del result_experiments[0][attr]
        self.assertDictEqual(expected, result_experiments[0])

    def test_delete_project(self):
        rv = TEST_CLIENT.delete("/projects/unk")
        result = rv.json()
        expected = {"message": "The specified project does not exist"}
        self.assertDictEqual(expected, result)
        self.assertEqual(rv.status_code, 404)

        rv = TEST_CLIENT.delete(f"/projects/{PROJECT_ID}")
        result = rv.json()
        expected = {"message": "Project deleted"}
        self.assertDictEqual(expected, result)

    def test_delete_projects(self):
        rv = TEST_CLIENT.post("/projects/deleteprojects", json=[])
        result = rv.json()
        expected = {"message": "inform at least one project"}
        self.assertDictEqual(expected, result)
        self.assertEqual(rv.status_code, 400)

        rv = TEST_CLIENT.post("/projects/deleteprojects", json=[PROJECT_ID_2])
        result = rv.json()
        expected = {"message": "Successfully removed projects"}
        self.assertDictEqual(expected, result)
        self.assertEqual(rv.status_code, 200)
