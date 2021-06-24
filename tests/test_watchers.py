# -*- coding: utf-8 -*-
from json import dumps, load

from projects.agent.watchers.workflow import update_status, watch_workflows
from unittest import TestCase

from fastapi.testclient import TestClient
from projects.kubernetes.kube_config import load_kube_config
from kubernetes import client



from projects.api.main import app
from projects.database import engine, Session

class TestWatchers(TestCase):
    def setUp(self):
        self.maxDiff = None

        
    def tearDown(self):
        pass

    def test_workflow_watcher_update(self):
        session = Session()
        
        manifest_file_ref = open('mock_manifest.json')
        manifest_as_dict = load(manifest_file_ref)
        
        try:
            update_status(manifest_as_dict, session)
        except Exception as e:
            self.fail(f'Errors found while running test: {e}')    