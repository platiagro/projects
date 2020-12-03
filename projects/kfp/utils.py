# -*- coding: utf-8 -*-
"""Utility functions."""

import ast
import base64


def convert_parameter_value_to_correct_type(value):
    """
    Convert boolean and null JSON values to Python format.

    Parameters
    ----------
    value : str

    Returns
    -------
    str or None
    """
    if value == 'null':
        value = None
    elif value == 'true':
        value = True
    elif value == 'false':
        value = False
    else:
        try:
            # try to convert string to correct type
            value = ast.literal_eval(value)
        except Exception:
            pass
    return value


def format_operator_parameters(parameters):
    """
    Format operator parameters to human-readable.

    Parameters
    ----------
    parameters : list

    Returns
    -------
    dict
    """
    params = {}
    for parameter in parameters:
        if parameter != "" and parameter != "{}":
            parameter_slited = parameter.split(':')
            key = parameter_slited[0]
            value = parameter_slited[1].strip()
            if value.startswith('- '):
                params[key] = get_parameter_list_values(value)
            else:
                params[key] = convert_parameter_value_to_correct_type(value)
    return params


def get_parameter_list_values(value):
    """
    Retrieves a list of parameters values.

    Parameters
    ----------
    value : str

    Returns
    -------
    list
    """
    parameter_list_values = []
    list_values = value.split('-')
    for list_value in list_values:
        # Remove "from list_value and replace with empty
        list_value = list_value.replace('"', '')
        if list_value != "":
            """unicode_escape Encoding suitable as the contents of a Unicode literal in ASCII-encoded Python"""
            list_value = list_value.replace("\\/", "/").encode().decode('unicode_escape')
            parameter_list_values.append(list_value.strip())
    return parameter_list_values


def get_operator_parameters(workflow_manifest, operator):
    """
    retrieves all parameters associated with an operator.

    Parameters:
    ----------
    workflow_manifest : ?
    operator : str

    Returns
    -------
    list
    """
    templates = workflow_manifest['spec']['templates']
    for template in templates:
        name = template['name']
        if name == operator and 'container' in template and 'args' in template['container']:
            args = template['container']['args']
            for arg in args:
                if 'papermill' in arg:
                    # split the arg and get base64 parameters in fifth position
                    splited_arg = arg.split()
                    base64_parameters = splited_arg[4].replace(';', '')
                    # decode base64 parameters
                    parameters = base64.b64decode(base64_parameters).decode()
                    # replace \n- to make list parameter to be in same line
                    parameters = parameters.replace('\n-', '-').split('\n')
                    return format_operator_parameters(parameters)


def search_for_pod_name(details: dict, operator_id: str):
    """
    Get operator pod name.

    Parameters
    ----------
    details : dict
        Workflow manifest from pipeline runtime.
    operator_id : str

    Returns:
        dict: id and status of pod
    """
    try:
        if 'nodes' in details['status']:
            for node in [*details['status']['nodes'].values()]:
                if node['displayName'] == operator_id:
                    return {'name': node['id'], 'status': node['phase'], 'message': node['message']}
    except KeyError:
        pass
