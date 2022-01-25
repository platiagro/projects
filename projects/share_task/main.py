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
import smtplib
import ssl

from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email import encoders

from jinja2 import Template


def run(source: str, emails: str, task_name: str, requested_at):
    """
    A job that sends an email with the contents of a task attached.

    Parameters
    ----------
    source : str
    emails : str
    """
    emails = emails.split(" ")
    logging.info(f"Sharing Task {task_name}.")
    logging.info(f"source = {source}")
    logging.info(f"emails = {emails}")
    logging.info(f"requested_at = {requested_at}")
    logging.info(f"task_name = {task_name}")
    filename = "task"

    # build the zipfile
    shutil.make_archive(filename, "zip", source)

    mail_sender_address = os.getenv("MAIL_SENDER_ADDRESS", "")
    mail_password = os.getenv("MAIL_PASSWORD", "")
    mail_server = os.getenv("MAIL_SERVER", "")
    mail_port = int(os.getenv("MAIL_PORT", 465))
    email_message_template = pkgutil.get_data("projects", "config/email-template.html")
    html_string = make_email_message(email_message_template, task_name)
    text = MIMEText(html_string, "html")

    message = MIMEMultipart()

    with open(f"{filename}.zip", "rb") as attachment:
        # Add file as application/octet-stream
        # Email client can usually download this automatically as attachment
        part = MIMEBase("application", "octet-stream")
        part.set_payload(attachment.read())

    # Encode file in ASCII characters to send by email
    encoders.encode_base64(part)

    # Add header as key/value pair to attachment part
    part.add_header(
        "Content-Disposition",
        f"attachment; filename= {filename}.zip",
    )
    message.attach(part)
    message.attach(text)
    message["Subject"] = f"Conteúdo da task {task_name}"
    try:
        context = ssl.create_default_context()
        with smtplib.SMTP_SSL(mail_server, mail_port, context=context) as server:
            server.login(mail_sender_address, mail_password)
            for email in emails:
                server.sendmail(
                    mail_sender_address, email, message.as_string()
                )
    except smtplib.SMTPAuthenticationError:
        logging.error("Error authenticating email.")
        return False
    logging.info("Done!")
    return True

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
        "--task-name", type=str, default="task", help="Task's name",
    )
    parser.add_argument(
        "--requested-at", type=str, default="", help="Request time",
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


    run(source=args.source, emails=args.emails, task_name=args.task_name, requested_at=args.requested_at)
