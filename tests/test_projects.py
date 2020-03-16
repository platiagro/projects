# -*- coding: utf-8 -*-
from unittest import TestCase

from projects.api.main import app
from projects.database import engine

UUID = "6814cdae-d88d-4c4d-bfb6-9ea6d6086dc4"
NAME = "foo"
CREATED_AT = "2000-01-01 00:00:00"
CREATED_AT_ISO = "2000-01-01T00:00:00"
UPDATED_AT = "2000-01-01 00:00:00"
UPDATED_AT_ISO = "2000-01-01T00:00:00"


class TestProjects(TestCase):
    def setUp(self):
        conn = engine.connect()
        text = "INSERT INTO projects (uuid, name, created_at, updated_at) VALUES ('{}', '{}', '{}', '{}')".format(UUID, NAME, CREATED_AT, UPDATED_AT)
        conn.execute(text)
        conn.close()

    def tearDown(self):
        conn = engine.connect()
        text = "DELETE FROM projects WHERE uuid = '{}'".format(UUID)
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
                "name": "foo",
            })
            result = rv.get_json()
            expected = {
                "name": "foo",
                "experiments": [],
            }
            # uuid, created_at, updated_at are machine-generated
            # we assert they exist, but we don't assert their values
            machine_generated = ["uuid", "createdAt", "updatedAt"]
            for attr in machine_generated:
                self.assertIn(attr, result)
                del result[attr]
            self.assertDictEqual(expected, result)

    def test_get_project(self):
        with app.test_client() as c:
            rv = c.get("/projects/foo")
            result = rv.get_json()
            expected = {"message": "The specified project does not exist"}
            self.assertDictEqual(expected, result)
            self.assertEqual(rv.status_code, 404)

            rv = c.get("/projects/{}".format(UUID))
            result = rv.get_json()
            expected = {
                "uuid": UUID,
                "name": NAME,
                "experiments": [],
                "createdAt": CREATED_AT_ISO,
                "updatedAt": UPDATED_AT_ISO,
            }
            self.assertDictEqual(expected, result)

    def test_update_project(self):
        with app.test_client() as c:
            rv = c.patch("/projects/foo", json={})
            result = rv.get_json()
            expected = {"message": "The specified project does not exist"}
            self.assertDictEqual(expected, result)
            self.assertEqual(rv.status_code, 404)

            rv = c.patch("/projects/{}".format(UUID), json={
                "unk": "bar",
            })
            result = rv.get_json()
            self.assertEqual(rv.status_code, 400)

            rv = c.patch("/projects/{}".format(UUID), json={
                "name": "bar",
            })
            result = rv.get_json()
            expected = {
                "uuid": UUID,
                "name": "bar",
                "experiments": [],
                "createdAt": CREATED_AT_ISO,
            }
            machine_generated = ["updatedAt"]
            for attr in machine_generated:
                self.assertIn(attr, result)
                del result[attr]
            self.assertDictEqual(expected, result)
