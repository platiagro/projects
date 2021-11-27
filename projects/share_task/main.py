# -*- coding: utf-8 -*-
"""
Task sharing Job (by email).
"""
import argparse
import logging
import os
import pkgutil
import shutil
import sys
from typing import List
import asyncio

from jinja2 import Template
from fastapi_mail import ConnectionConfig, FastMail, MessageSchema


def run(source: str, emails: str, task_name: str, requested_at):
    """
    A job that sends an email with the contents of a task attached.

    Parameters
    ----------
    source : str
    emails : str
    """
    emails = emails.split(" ")
    logging.info("Sharing Task.")
    logging.info(f"source = {source}")
    logging.info(f"emails = {emails}")
    logging.info(f"requested_at = {requested_at}")
    logging.info(f"task_name = {task_name}")

    filename = "task"  # get source folder name (which should be the task name)
    # build the zipfile
    shutil.make_archive(filename, "zip", source)

    email_message_template = pkgutil.get_data("projects", "config/email-template.html")

    mail_username = os.getenv("MAIL_USERNAME", "")
    mail_password = os.getenv("MAIL_PASSWORD", "")
    mail_sender_address = os.getenv("MAIL_SENDER_ADDRESS", "")
    mail_server = os.getenv("MAIL_SERVER", "")
    mail_port = int(os.getenv("MAIL_PORT", 587))
    mail_tls = bool(os.getenv("MAIL_TLS", True))
    mail_ssl = bool(os.getenv("MAIL_SSL", False))
    CONNECTION_CONFIG = ConnectionConfig(
        MAIL_USERNAME=mail_username,
        MAIL_PASSWORD=mail_password,
        MAIL_FROM=mail_sender_address,
        MAIL_PORT=mail_port,
        MAIL_SERVER=mail_server,
        MAIL_TLS=mail_tls,
        MAIL_SSL=mail_ssl,
        USE_CREDENTIALS=True,
    )

    body = make_email_message(email_message_template, task_name)
    message = MessageSchema(
        subject="Arquivos da tarefa",
        recipients=emails,  # List of recipients, as many as you can pass
        body=body,
        attachments=[f"{filename}.zip"],
        subtype="html",
    )
    fm = FastMail(CONNECTION_CONFIG)
    loop = asyncio.get_event_loop()
    loop.create_task(fm.send_message(message))

    logging.info("Done!")


def make_email_message(html_file_content, task_name):
    """
    Build an email body message for a specific task.

    Parameters
    ----------
    html_file_content: bytes
    task_name : str

    Returns
    -------
    template: str
    """
    # byte to string
    html_string = str(html_file_content, "utf-8")

    # body message html string to Jinja2 template
    jinja2_like_template = Template(html_string)

    template = jinja2_like_template.render(task_name=task_name)
    return template


def parse_args(args):
    """Takes argv and parses API options."""
    parser = argparse.ArgumentParser(
        description="Share Task Job"
    )
    parser.add_argument(
        "--source", type=str, help="Source directory",
    )
    parser.add_argument(
        "--emails", type=str, help="List of emails",
    )
    parser.add_argument(
        "--task-name", type=str, help="Task's name",
    )
    parser.add_argument(
        "--requested-at", type=str, help="Request time",
    )
    parser.add_argument(
        "--log-level",
        nargs="?",
        choices=["NOTSET", "DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
        default="INFO",
        const="INFO",
        help="Log level",
    )

    return parser.parse_args(args)


if __name__ == "__main__":
    args = parse_args(sys.argv[1:])

    logging.basicConfig(level=args.log_level)

    run(source=args.source, emails=args.emails, task_name=args.task_name, requested_at=args.requested_at)
