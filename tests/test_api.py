# -*- coding: utf-8 -*-
from unittest import TestCase

from fastapi.testclient import TestClient

from projects.api.main import app, parse_args

TEST_CLIENT = TestClient(app)


class TestApi(TestCase):

    def test_parse_args(self):
        parser = parse_args([])
        self.assertEqual(parser.port, 8080)
        self.assertFalse(parser.enable_cors)

        parser = parse_args(["--enable-cors", "--port", "3000"])
        self.assertEqual(parser.port, 3000)
        self.assertTrue(parser.enable_cors)

    def test_ping(self):
        rv = TEST_CLIENT.get("/")
        result = rv.text
        expected = "pong"
        self.assertEqual(result, expected)
        self.assertEqual(rv.status_code, 200)
