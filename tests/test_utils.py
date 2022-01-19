import unittest

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

    def test_check_valid_email(self):
        email = "teste@teste.com"
        self.assertTrue(utils.check_email(email))

    def test_check_invalid_email(self):
        email = "testeteste.com"
        self.assertFalse(utils.check_email(email))
