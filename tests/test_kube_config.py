import unittest
import unittest.mock as mock
import pytest

from projects.kubernetes.kube_config import load_kube_config
from projects.exceptions import InternalServerError

class TestLoadKubeConfig(unittest.TestCase):
    @mock.patch("kubernetes.config.load_kube_config")
    def test_load_kube_config_success(self, mock_load_kube_config):
        self.assertIsNone(load_kube_config())

    @mock.patch("kubernetes.config.load_kube_config", side_effect=Exception)
    @mock.patch("kubernetes.config.load_incluster_config")
    def test_load_incluster_config(self, mock_load_kube_config, mock_load_incluster_config):
        self.assertIsNone(load_kube_config())

    @mock.patch("kubernetes.config.load_kube_config", side_effect=Exception)
    @mock.patch("kubernetes.config.load_incluster_config", side_effect=Exception)
    def test_load_kube_config_fail(self, mock_load_kube_config, mock_load_incluster_config):
        with pytest.raises(InternalServerError):
            load_kube_config()
