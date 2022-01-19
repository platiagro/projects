import unittest
import unittest.mock as mock
from datetime import datetime
import pytest
import os
import pkgutil

from fastapi.testclient import TestClient

from projects import models
from projects.api.main import app
from projects.database import session_scope
from projects.share_task.main import parse_args, make_email_message, run
from projects.kfp.emails import send_email
from projects.schemas.mailing import EmailSchema
from projects.kfp import KF_PIPELINES_NAMESPACE
import tests.util as util


app.dependency_overrides[session_scope] = util.override_session_scope
TEST_CLIENT = TestClient(app)

HOST_URL = "http://ml-pipeline.kubeflow:8888"


class TestShareTask(unittest.TestCase):

    def setUp(self):
        """
        Sets up the test before running it.
        """
        test_file = open("task.zip", "w+")
        test_file.close()
        util.create_mocks()

    def tearDown(self):
        """
        Deconstructs the test after running it.
        """
        os.remove("task.zip")
        util.delete_mocks()

    def test_parse_args_success(self):
        args = list()
        args.append("--source")
        args.append("source")
        args.append("--emails")
        args.append("email1 email2 email3")
        args.append("--task-name")
        args.append("task name")
        args.append("--requested-at")
        now = str(datetime.utcnow())
        args.append(now)
        args.append("--log-level")
        args.append("INFO")
        args = parse_args(args)
        self.assertEqual(args.source, "source")
        self.assertEqual(args.emails, "email1 email2 email3")
        self.assertEqual(args.task_name, "task name")
        self.assertEqual(args.requested_at, now)
        self.assertEqual(args.log_level, "INFO")

    def test_parse_args_fail(self):
        with pytest.raises(SystemExit):
            args = list()
            args.append(str(datetime.utcnow()))
            args.append("--log-level")
            args.append("info")
            parse_args(args)

    def test_make_email_message_success(self):
        email_message_template = pkgutil.get_data("projects", "config/email-template.html")
        html_string = make_email_message(email_message_template, "task_name")
        self.assertIsInstance(html_string, str)

    def test_make_email_message_fail(self):
        with pytest.raises(TypeError):
            email_message_template = "test"
            html_string = make_email_message(email_message_template, "task_name")
            self.assertIsInstance(html_string, str)

    @mock.patch(
        "kfp.Client",
        return_value=util.MOCK_KFP_CLIENT,
    )
    def test_task_creation_component_functions(
        self, mock_kfp_client
    ):
        task = util.TestingSessionLocal().query(models.Task).get(util.MOCK_UUID_6)
        send_email(task, email_schema=EmailSchema, namespace=KF_PIPELINES_NAMESPACE)

    @mock.patch("ssl.create_default_context")
    @mock.patch("shutil.make_archive")
    @mock.patch("smtplib.SMTP_SSL", return_value=util.MOCK_SEND_EMAIL)
    def test_send_email(self, mock_ssl_context, mock_zip, mock_server):
        path = "/path/to/file"
        self.assertTrue(run(path, "teste@teste.com.br", "teste", str(datetime.now())))

    @mock.patch(
        "kfp.Client",
        return_value=util.MOCK_KFP_CLIENT,
    )
    def test_send_email_api(self, mock_kfp_client):
        task_id = util.MOCK_UUID_4

        rv = TEST_CLIENT.post(
            f"/tasks/{task_id}/emails",
            json={"emails": ["test@test.com.br"]}
        )
        result = rv.json()
        expected = {"message": "email has been sent"}
        self.assertDictEqual(expected, result)

    @mock.patch(
        "kfp.Client",
        return_value=util.MOCK_KFP_CLIENT,
    )
    def test_send_email_api_not_found(self, mock_kfp_client):
        task_id = "invalid"

        rv = TEST_CLIENT.post(
            f"/tasks/{task_id}/emails",
            json={"emails": ["test@test.com.br"]}
        )
        result = rv.json()
        expected = {
            "message": "The specified task does not exist",
            "code": "TaskNotFound",
        }
        self.assertDictEqual(expected, result)
        self.assertEqual(rv.status_code, 404)

    @mock.patch(
        "kfp.Client",
        return_value=util.MOCK_KFP_CLIENT,
    )
    def test_send_email_api_invalid_email(self, mock_kfp_client):
        task_id = util.MOCK_UUID_4

        rv = TEST_CLIENT.post(
            f"/tasks/{task_id}/emails",
            json={"emails": ["testtest.com.br"]}
        )
        result = rv.json()

        self.assertEqual(rv.status_code, 422)

    @mock.patch(
        "kfp.Client",
        return_value=util.MOCK_KFP_CLIENT_EXCEPT_404,
    )
    def test_kfp_client_not_found(self, mock_kfp_client):
        task_id = util.MOCK_UUID_4

        rv = TEST_CLIENT.post(
            f"/tasks/{task_id}/emails",
            json={"emails": ["test@test.com.br"]}
        )
        result = rv.json()

        self.assertEqual(rv.status_code, 404)
    
    @mock.patch(
        "kfp.Client",
        return_value=util.MOCK_KFP_CLIENT_EXCEPT_403,
    )
    def test_kfp_client_forbidden(self, mock_kfp_client):
        task_id = util.MOCK_UUID_4

        rv = TEST_CLIENT.post(
            f"/tasks/{task_id}/emails",
            json={"emails": ["test@test.com.br"]}
        )
        result = rv.json()

        self.assertEqual(rv.status_code, 403)

    @mock.patch(
        "kfp.Client",
        return_value=util.MOCK_KFP_CLIENT_EXCEPT_SERVICE_UNAVAILABLE,
    )
    def test_kfp_client_service_unavailable_bad_upstream(self, mock_kfp_client):
        task_id = util.MOCK_UUID_4

        rv = TEST_CLIENT.post(
            f"/tasks/{task_id}/emails",
            json={"emails": ["test@test.com.br"]}
        )
        result = rv.json()

        self.assertEqual(rv.status_code, 503)
        self.assertEqual(rv.reason, "Service Unavailable")
    
    @mock.patch(
        "kfp.Client",
        return_value=util.MOCK_KFP_CLIENT_EXCEPT_MAX_RETRY,
    )
    def test_kfp_client_service_unavailable_max_retry(self, mock_kfp_client):
        task_id = util.MOCK_UUID_4

        rv = TEST_CLIENT.post(
            f"/tasks/{task_id}/emails",
            json={"emails": ["test@test.com.br"]}
        )
        result = rv.json()

        self.assertEqual(rv.status_code, 503)