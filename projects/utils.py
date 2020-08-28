# -*- coding: utf-8 -*-
import re
from string import Template

JUPYTER_OUTPUT = Template("""{
    "cellType":  $cell_type,
    "executionCount": $count,
    "output": {
        "errorName": $type,
        "errorValue": $value,
        "traceback": $traceback,
    }
}""")


def remove_ansi_escapes(traceback):
    compiler = re.compile(r'(\x9B|\x1B\[)[0-?]*[ -\/]*[@-~]')
    return [compiler.sub('', line) for line in traceback]


def to_camel_case(snake_str):
    components = snake_str.split("_")
    # We capitalize the first letter of each component except the first one
    # with the 'title' method and join them together.
    return components[0] + "".join(x.title() for x in components[1:])


def to_snake_case(name):
    name = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
    return re.sub('([a-z0-9])([A-Z])', r'\1_\2', name).lower()
