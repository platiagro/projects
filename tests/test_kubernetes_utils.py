# -*- coding: utf-8 -*-
import unittest
import unittest.mock as mock
import pytest

from fastapi.testclient import TestClient
from kubernetes.client.rest import ApiException

from projects.api.main import app
from projects.database import session_scope
from projects.kubernetes import utils
from projects.exceptions import InternalServerError

import tests.util as util

app.dependency_overrides[session_scope] = util.override_session_scope
TEST_CLIENT = TestClient(app)


class TestDeployments(unittest.TestCase):
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

    @mock.patch(
        "kubernetes.client.CoreV1Api",
        return_value=util.MOCK_CORE_V1_API_NOT_BOUND,
    )
    @mock.patch(
        "kubernetes.config.load_kube_config",
    )
    def test_volume_exists_false(self, mock_api, mock_kube_config):
        self.assertFalse(utils.volume_exists("name", "namespace"))

    @mock.patch(
        "kubernetes.client.CoreV1Api",
        return_value=util.MOCK_CORE_V1_API_EXCEPT,
    )
    @mock.patch(
        "kubernetes.config.load_kube_config",
    )
    def test_volume_exists_except(self, mock_api, mock_kube_config):
        self.assertFalse(utils.volume_exists("name", "namespace"))

    @mock.patch(
        "kubernetes.client.CoreV1Api",
        return_value=util.MOCK_CORE_V1_API_EXCEPT,
    )
    @mock.patch(
        "kubernetes.config.load_kube_config",
    )
    def test_get_volume_from_pod_except(self, mock_api, mock_kube_config):
        with pytest.raises(InternalServerError):
            self.assertFalse(utils.get_volume_from_pod("volume_name", "namespace", "experiment_id"))
