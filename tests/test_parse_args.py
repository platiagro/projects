# -*- coding: utf-8 -*-
import unittest

from projects.api.main import parse_args


class TestParseArgs(unittest.TestCase):
    def test_parse_args_empty(self):
        """
        Should parse empty args and return default host and port.
        """
        parser = parse_args([])
        self.assertEqual(parser.host, "127.0.0.1")
        self.assertEqual(parser.port, 8080)

    def test_parse_args_host(self):
        """
        Should parse a valid host string and return host value.
        """
        parser = parse_args(["--host", "0.0.0.0"])
        self.assertEqual(parser.host, "0.0.0.0")
        self.assertEqual(parser.port, 8080)

    def test_parse_args_port(self):
        """
        Should parse a valid port string and return host value.
        """
        parser = parse_args(["--port", "3000"])
        self.assertEqual(parser.host, "127.0.0.1")
        self.assertEqual(parser.port, 3000)
