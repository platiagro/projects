import argparse
import logging
parser = argparse.ArgumentParser()

parser.add_argument(
    "--log-level",
     nargs="?",
     choices=["NOTSET","DEBUG","INFO","WARNING","ERROR","CRITICAL"],
     default="NOTSET",
     const="NOTSET",
     help="Sets log level to logging",
     )

args = parser.parse_args()
print(args)

logging.basicConfig(level="INFO")


logging.info("Hello World")
