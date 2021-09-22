# -*- coding: utf-8 -*-
import unittest
import unittest.mock as mock

from projects.agent import main

import tests.util as util

main.session_scope = util.override_session_scope


class TestWatchers(unittest.TestCase):
    maxDiff = None

    # def setUp(self):
    #     self.maxDiff = None

    # def tearDown(self):
    #     pass

    # def test_workflow_watcher_update(self):

    #     manifest_file_ref = open('tests/resources/mock_manifest.json')
    #     manifest_as_dict = load(manifest_file_ref)

    #     # testing if it's working
    #     try:
    #         update_status(manifest_as_dict, session)
    #     except Exception as e:
    #         self.fail(f'Errors found while running test: {e}')

    #     # checking error raising if wrong json
    #     manifest_as_dict = {"foo": "bar"}
    #     with self.assertRaises(KeyError):
    #         update_status(manifest_as_dict, session)

    # def test_deployment_watcher_update(self):

    #     manifest_file_ref = open('tests/resources/deployment_mock_manifest.json')
    #     manifest_as_dict = load(manifest_file_ref)

    #     # testing if it's working
    #     try:
    #         update_seldon_deployment(manifest_as_dict, session)
    #     except Exception as e:
    #         self.fail(f'Errors found while running test: {e}')

    #     # checking error raising if wrong json
    #     manifest_as_dict = {"foo": "bar"}
    #     with self.assertRaises(KeyError):
    #         update_status(manifest_as_dict, session)
