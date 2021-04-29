# -*- coding: utf-8 -*-
import multiprocessing
import os
from unittest import TestCase

import uvicorn
from fastapi import FastAPI
from fastapi.testclient import TestClient

from projects.api.main import app, parse_args
from projects.controllers.utils import uuid_alpha
from projects.database import engine

TEST_CLIENT = TestClient(app)

PROJECT_ID = str(uuid_alpha())
DEPLOYMENT_ID = str(uuid_alpha())
EXPERIMENT_ID = None
NAME = "foo"
CREATED_AT = "2000-01-01 00:00:00"
UPDATED_AT = "2000-01-01 00:00:00"
DESCRIPTION = "Description"
POSITION = 0
STATUS = "Pending"
URL = None


class TestResponses(TestCase):

    def setUp(self):
        os.environ["BROKER_URL"] = "http://localhost:8000"
        app = FastAPI()

        @app.post("/")
        async def root():
            return {}

        self.proc = multiprocessing.Process(target=uvicorn.run, args=(app,))
        self.proc.start()

        conn = engine.connect()
        text = (
            f"INSERT INTO projects (uuid, name, description, created_at, updated_at) "
            f"VALUES (%s, %s, %s, %s, %s)"
        )
        conn.execute(text, (PROJECT_ID, NAME, DESCRIPTION, CREATED_AT, UPDATED_AT,))

        text = (
            f"INSERT INTO deployments (uuid, name, project_id, experiment_id, position, is_active, status, url, created_at, updated_at) "
            f"VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
        )
        conn.execute(text, (DEPLOYMENT_ID, NAME, PROJECT_ID, EXPERIMENT_ID, POSITION, 1, STATUS, URL, CREATED_AT, UPDATED_AT,))

        conn.close()

    def tearDown(self):
        self.proc.terminate()

        conn = engine.connect()

        text = f"DELETE FROM deployments WHERE project_id = '{PROJECT_ID}'"
        conn.execute(text)

        text = f"DELETE FROM projects WHERE uuid = '{PROJECT_ID}'"
        conn.execute(text)

        conn.close()

    def test_parse_args(self):
        parser = parse_args([])
        self.assertEqual(parser.port, 8080)
        self.assertFalse(parser.enable_cors)

    def test_post(self):
        rv = TEST_CLIENT.post(f"/projects/{PROJECT_ID}/deployments/{DEPLOYMENT_ID}/responses", json={
            "data": {
                "ndarray": [
                    [1, 2, "a"]
                ]
            }
        })
        result = rv.text
        expected = "{\"message\":\"OK\"}"
        self.assertEqual(result, expected)
        self.assertEqual(rv.status_code, 200)

        rv = TEST_CLIENT.post(f"/projects/{PROJECT_ID}/deployments/{DEPLOYMENT_ID}/responses", json={
            "strData": "texto"
        })
        result = rv.text
        expected = "{\"message\":\"OK\"}"
        self.assertEqual(result, expected)
        self.assertEqual(rv.status_code, 200)

        rv = TEST_CLIENT.post(f"/projects/{PROJECT_ID}/deployments/{DEPLOYMENT_ID}/responses", json={
            "binData": "Cg=="
        })
        result = rv.text
        expected = "{\"message\":\"OK\"}"
        self.assertEqual(result, expected)
        self.assertEqual(rv.status_code, 200)
