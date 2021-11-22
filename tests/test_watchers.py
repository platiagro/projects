# -*- coding: utf-8 -*-
import json
import unittest

from projects.agent.watchers.workflow import update_status, update_seldon_deployment

import tests.util as util


class TestWatchers(unittest.TestCase):
    maxDiff = None

    def setUp(self):
        """
        Sets up the test before running it.
        """
        util.create_mocks()

    def tearDown(self):
        """
        Deconstructs the test after running it.
        """
        util.delete_mocks()

    def test_update_status_key_error(self):
        """
        Should raise a KeyError when workflow_manifest is invalid.
        """
        workflow_manifest = {"foo": "bar"}
        session = next(util.override_session_scope())
        with self.assertRaises(KeyError):
            update_status(workflow_manifest, session)

    def test_update_status_success(self):
        """
        Should update status of an operator successfully.
        """
        with open("tests/resources/mock_manifest.json") as manifest_file_ref:
            manifest_as_dict = json.load(manifest_file_ref)
        session = next(util.override_session_scope())

        update_status(manifest_as_dict, session)

    def test_update_seldon_deployment_success(self):
        """
        Should update status of a deployment successfully.
        """
        deployment_id = util.MOCK_UUID_1
        status = "Succeeded"
        created_at_str = "2021-06-24T14:42:09Z"
        session = next(util.override_session_scope())
        update_seldon_deployment(deployment_id, status, created_at_str, session)
