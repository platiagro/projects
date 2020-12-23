# -*- coding: utf-8 -*-
"""Utility functions."""


def remove_non_deployable_operators(operators):
    """
    Removes operators that are not part of the deployment pipeline.

    Parameters
    ----------
    operators : list
        Original pipeline operators.

    Returns
    -------
    list
        A list of all deployable operators.

    Notes
    -----
    If the non-deployable operator is dependent on another operator, it will be
    removed from that operator's dependency list.
    """
    deployable_operators = [operator for operator in operators if operator["notebookPath"]]
    non_deployable_operators = get_non_deployable_operators(operators, deployable_operators)

    for operator in deployable_operators:
        dependencies = set(operator["dependencies"])
        operator["dependencies"] = list(dependencies - set(non_deployable_operators))

    return deployable_operators


def get_non_deployable_operators(operators, deployable_operators):
    """
    Get all non deployable operators from a deployment run.

    Parameters
    ----------
    operators : list
    deployable_operators : list

    Returns
    -------
    list
        A list of non deployable operators.
    """
    non_deployable_operators = []
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

    return non_deployable_operators
