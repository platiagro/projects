import unittest
import pytest


from projects import utils


class TestUtils(unittest.TestCase):

    def test_to_camel_case(self):
        snake = "test_to_camel_case"
        camel = "testToCamelCase"
        self.assertEqual(utils.to_camel_case(snake), camel)

    def test_to_snake_case(self):
        snake = "test_to_camel_case"
        camel = "testToCamelCase"
        self.assertEqual(utils.to_snake_case(camel), snake)
