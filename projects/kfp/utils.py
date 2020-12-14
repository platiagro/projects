# -*- coding: utf-8 -*-
"""Utility functions."""
import base64
from projects.utils import convert_json_values


def get_operator_parameters(workflow_manifest, operator):
    """
    Retrieves all parameters associated with an operator.

    Parameters:
    ----------
    workflow_manifest : ?
    operator : str

    Returns
    -------
    list
    """
    templates = workflow_manifest["spec"]["templates"]

    for template in templates:
        name = template["name"]
        if name == operator and "container" in template and "args" in template["container"]:
            args = template["container"]["args"]
            for arg in args:
                if "papermill" in arg:
                    # split the arg and get base64 parameters in fifth position
                    splited_arg = arg.split()
                    base64_parameters = splited_arg[4].replace(';', '')
                    # decode base64 parameters
                    parameters = base64.b64decode(base64_parameters).decode()
                    # replace \n- to make list parameter to be in same line
                    parameters = parameters.replace('\n-', '-').split('\n')
                    return format_operator_parameters(parameters)


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
                params[key] = convert_json_values(value)
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


def remove_non_deployable_operators(operators):
    """
    Removes operators that are not part of the deployment pipeline.
    If the non-deployable operator is dependent on another operator, it will be
    removed from that operator's dependency list.

    Parameters
    ----------
    operators : list
        Original pipeline operators.

    Returns
    -------
    list
        A list of all deployable operators.
    """
    deployable_operators = [operator for operator in operators if operator["notebookPath"]]
    non_deployable_operators = list()

    for operator in operators:
        if operator["notebookPath"] is None:
            # checks if the non-deployable operator has dependency
            if operator["dependencies"]:
                dependency = operator["dependencies"]

                # looks for who has the non-deployable operator as dependency
                # and assign the dependency of the non-deployable operator to this operator
                for op in deployable_operators:
                    if operator["operatorId"] in op["dependencies"]:
                        op["dependencies"] = dependency

            non_deployable_operators.append(operator["operatorId"])

    for operator in deployable_operators:
        dependencies = set(operator["dependencies"])
        operator["dependencies"] = list(dependencies - set(non_deployable_operators))

    return deployable_operators
