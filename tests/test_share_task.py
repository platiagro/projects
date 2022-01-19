import unittest
import unittest.mock as mock
from datetime import datetime
import pytest
import pkgutil

from projects import models
from projects.share_task.main import parse_args, make_email_message, run
from projects.kfp.emails import send_email
from projects.schemas.mailing import EmailSchema
from projects.kfp import KF_PIPELINES_NAMESPACE
import tests.util as util


class TestShareTask(unittest.TestCase):

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
    @mock.patch("smtplib.SMTP_SSL", return_value = util.MOCK_SEND_EMAIL)
    def test_send_email(self, mock_ssl_context, mock_server):
        path = "./tests/resources/folder_send_email"
        run(path, "dviana@cpqd.com.br", "teste", str(datetime.now()))
