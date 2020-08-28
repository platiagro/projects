# -*- coding: utf-8 -*-
from json import dumps, loads
from unittest import TestCase

import requests

from projects.api.main import app
from projects.controllers.utils import uuid_alpha

from projects.jupyter import JUPYTER_ENDPOINT, COOKIES, HEADERS

OPERATOR_ID = str(uuid_alpha())
WRONG_OPERATOR_ID = str(uuid_alpha())
PROJECT_ID = str(uuid_alpha())
EXPERIMENT_ID = str(uuid_alpha())
SAMPLE_NOTEBOOK = '{ "cells": [ { "cell_type": "markdown", "metadata": { "tags": [ "papermill-error-cell-tag" ] }, "source": [ "<span style=\\"color:red; font-family:Helvetica Neue, Helvetica, Arial, sans-serif; font-size:2em;\\">An Exception was encountered at \'<a href=\\"#papermill-error-cell\\">In [1]</a>\'.</span>" ] }, { "cell_type": "markdown", "metadata": { "tags": [ "papermill-error-cell-tag" ] }, "source": [ "<span id=\\"papermill-error-cell\\" style=\\"color:red; font-family:Helvetica Neue, Helvetica, Arial, sans-serif; font-size:2em;\\">Execution using papermill encountered an exception here and stopped:</span>" ] }, { "cell_type": "code", "execution_count": 1, "metadata": { "execution": { "iopub.execute_input": "2020-08-28T22:06:45.857336Z", "iopub.status.busy": "2020-08-28T22:06:45.856220Z", "iopub.status.idle": "2020-08-28T22:06:45.981091Z", "shell.execute_reply": "2020-08-28T22:06:45.980093Z" }, "papermill": { "duration": 0.155491, "end_time": "2020-08-28T22:06:45.981506", "exception": true, "start_time": "2020-08-28T22:06:45.826015", "status": "failed" }, "tags": [] }, "outputs": [ { "ename": "NameError", "evalue": "name \'lorem_ipsum\' is not defined", "output_type": "error", "traceback": [ "\\u001b[0;31m---------------------------------------------------------------------------\\u001b[0m", "\\u001b[0;31mNameError\\u001b[0m Traceback (most recent call last)", "\\u001b[0;32m<ipython-input-1-ef1ec8b9335b>\\u001b[0m in \\u001b[0;36m<module>\\u001b[0;34m\\u001b[0m\\n\\u001b[0;32m----> 1\\u001b[0;31m \\u001b[0mprint\\u001b[0m\\u001b[0;34m(\\u001b[0m\\u001b[0mlorem_ipsum\\u001b[0m\\u001b[0;34m)\\u001b[0m\\u001b[0;34m\\u001b[0m\\u001b[0;34m\\u001b[0m\\u001b[0m\\n\\u001b[0m", "\\u001b[0;31mNameError\\u001b[0m: name \'lorem_ipsum\' is not defined" ] } ], "source": [ "print(lorem_ipsum)" ] } ], "metadata": { "celltoolbar": "Tags", "experiment_id": "a7170734-ca2b-4294-b9eb-6ef849672d11", "kernelspec": { "display_name": "Python 3", "language": "python", "name": "python3" }, "language_info": { "codemirror_mode": { "name": "ipython", "version": 3 }, "file_extension": ".py", "mimetype": "text/x-python", "name": "python", "nbconvert_exporter": "python", "pygments_lexer": "ipython3", "version": "3.7.8" }, "operator_id": "bb01c6b5-edda-41ba-bae2-65df6b8d1a29", "papermill": { "duration": 2.356765, "end_time": "2020-08-28T22:06:46.517405", "environment_variables": {}, "exception": true, "input_path": "s3://anonymous/tasks/fb874d84-92c3-4fd0-ae58-ceb74fdc558a/Experiment.ipynb", "output_path": "output.ipynb", "parameters": {}, "start_time": "2020-08-28T22:06:44.160640", "version": "2.1.1" }, "task_id": "fb874d84-92c3-4fd0-ae58-ceb74fdc558a" }, "nbformat": 4, "nbformat_minor": 4 }'


class TestOperators(TestCase):

    def setUp(self):
        self.maxDiff = None

        session = requests.Session()
        session.cookies.update(COOKIES)
        session.headers.update(HEADERS)
        session.hooks = {
            "response": lambda r, *args, **kwargs: r.raise_for_status(),
        }

        session.put(
            url=f"{JUPYTER_ENDPOINT}/api/contents/experiments",
            data=dumps({"type": "directory", "content": None}),
        )

        session.put(
            url=f"{JUPYTER_ENDPOINT}/api/contents/experiments/{EXPERIMENT_ID}",
            data=dumps({"type": "directory", "content": None}),
        )

        session.put(
            url=f"{JUPYTER_ENDPOINT}/api/contents/experiments/{EXPERIMENT_ID}/operators",
            data=dumps({"type": "directory", "content": None}),
        )

        session.put(
            url=f"{JUPYTER_ENDPOINT}/api/contents/experiments/{EXPERIMENT_ID}/operators/{OPERATOR_ID}",
            data=dumps({"type": "directory", "content": None}),
        )

        session.put(
            url=f"{JUPYTER_ENDPOINT}/api/contents/experiments/{EXPERIMENT_ID}/operators/{OPERATOR_ID}/Experiment.ipynb",
            data=dumps({"type": "notebook", "content": loads(SAMPLE_NOTEBOOK)}),
        )

    def test_get_logs(self):
        with app.test_client() as c:
            rv = c.get(f"/projects/{PROJECT_ID}/experiments/{EXPERIMENT_ID}/operators/{OPERATOR_ID}/logs")
            result = rv.get_json()

            expected = {
                "cellType": "code",
                "executionCount": 1,
                "output": {
                    "errorName": "NameError",
                    "errorValue": "name 'lorem_ipsum' is not defined",
                    "traceback": [
                        "---------------------------------------------------------------------------",
                        "NameError Traceback (most recent call last)",
                        "<ipython-input-1-ef1ec8b9335b> in <module>",
                        "----> 1 print(lorem_ipsum)",
                        "",
                        "NameError: name 'lorem_ipsum' is not defined"
                    ]
                }
            }

            self.assertEqual(rv.status_code, 200)
            self.assertDictEqual(result, expected)

            rv = c.get(f"/projects/{PROJECT_ID}/experiments/{EXPERIMENT_ID}/operators/{WRONG_OPERATOR_ID}/logs")
            result = rv.get_json()

            expected = {"message": "The specified notebook does not exist"}

            self.assertEqual(rv.status_code, 404)
            self.assertDictEqual(result, expected)
