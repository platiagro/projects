# -*- coding: utf-8 -*-
import os
os.environ["ENABLE_CORS"] = "1"
from unittest import TestCase

from fastapi.testclient import TestClient

from projects.api.main import app, parse_args

TEST_CLIENT = TestClient(app)


class TestApi(TestCase):

    def test_parse_args(self):
        parser = parse_args([])
        self.assertEqual(parser.host, "127.0.0.1")
        self.assertEqual(parser.port, 8080)

        parser = parse_args(["--host", "0.0.0.0"])
        self.assertEqual(parser.host, "0.0.0.0")

        parser = parse_args(["--port", "3000"])
        self.assertEqual(parser.port, 3000)

    def test_ping(self):
        rv = TEST_CLIENT.get("/")
        result = rv.text
        expected = "pong"
        self.assertEqual(result, expected)
        self.assertEqual(rv.status_code, 200)
        self.assertTrue("Access-Control-Allow-Origin" in rv.headers)
        self.assertTrue("Access-Control-Allow-Methods" in rv.headers)
        self.assertTrue("Access-Control-Allow-Headers" in rv.headers)

    def test_options_preflight(self):
        rv = TEST_CLIENT.options("/")
        self.assertEqual(rv.status_code, 200)
        self.assertTrue("Access-Control-Allow-Origin" in rv.headers)
        self.assertTrue("Access-Control-Allow-Methods" in rv.headers)
        self.assertTrue("Access-Control-Allow-Headers" in rv.headers)
