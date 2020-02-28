# -*- coding: utf-8 -*-
import unittest

from projects.database import init_db


class TestDatabase(unittest.TestCase):

    def test_init_db(self):
        init_db()
