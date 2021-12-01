import unittest
from datetime import datetime
import pytest
import pkgutil

from projects.share_task.main import parse_args, make_email_message


class TestShareTask(unittest.TestCase):

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