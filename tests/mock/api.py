import json
import multiprocessing
from datetime import datetime

from flask import Flask, jsonify, request


def start_mock_api():
    """
    Starts a Mock REST API to replace KFP in a separate process.

    Returns
    -------
    multiprocessing.Process
    """
    app = Flask(__name__)

    with open("tests/mock/run-experiment.json") as f:
        app.config["RUN_EXPERIMENT"] = json.load(f)

    with open("tests/mock/run-deployment.json") as f:
        app.config["RUN_DEPLOYMENT"] = json.load(f)

    with open("tests/mock/experiment.json") as f:
        app.config["EXPERIMENT"] = json.load(f)

    def get_healthz():
        return jsonify({
            "apiServerReady": True,
        })

    def get_runs():
        print("get_runs")
        return jsonify({
            "runs": sorted([
                app.config["RUN_EXPERIMENT"]["run"],
                app.config["RUN_DEPLOYMENT"]["run"],
            ], key=lambda x: x["created_at"], reverse=True),
            "total_size": 2,
        })

    def post_runs():
        workflow_manifest = request.get_json(force=True).get("pipeline_spec").get("workflow_manifest")
        run_name = json.loads(workflow_manifest).get("metadata").get("generateName")
        if run_name.startswith("experiment-"):
            app.config["RUN_EXPERIMENT"]["run"]["created_at"] = datetime.utcnow().isoformat()
            app.config["RUN_EXPERIMENT"]["run"]["finished_at"] = datetime.utcnow().isoformat()
            return jsonify(app.config["RUN_EXPERIMENT"])
        elif run_name.startswith("deployment-"):
            deployment_id = run_name[len("deployment-"):-1]

            workflow_manifest = app.config["RUN_DEPLOYMENT"]["run"]["pipeline_spec"]["workflow_manifest"]
            run_name = json.loads(workflow_manifest).get("metadata").get("generateName")
            old_deployment_id = run_name[len("deployment-"):-1]

            RUN_STR = json.dumps(app.config["RUN_DEPLOYMENT"])
            RUN_STR = RUN_STR.replace(old_deployment_id, deployment_id)
            app.config["RUN_DEPLOYMENT"] = json.loads(RUN_STR)

            app.config["RUN_DEPLOYMENT"]["run"]["created_at"] = datetime.utcnow().isoformat()
            app.config["RUN_DEPLOYMENT"]["run"]["finished_at"] = datetime.utcnow().isoformat()
            return jsonify(app.config["RUN_DEPLOYMENT"])
        else:
            return jsonify({"error": f""}), 500

    def get_run(run_id):
        print("get_run")
        if run_id == app.config["RUN_EXPERIMENT"]["run"]["id"]:
            return jsonify(app.config["RUN_EXPERIMENT"])
        elif run_id == app.config["RUN_DEPLOYMENT"]["run"]["id"]:
            return jsonify(app.config["RUN_DEPLOYMENT"])
        else:
            return jsonify({"error": f"Run {run_id} not found."}), 404

    def delete_run(run_id):
        print("delete_run")
        return jsonify({})

    def post_retry(run_id):
        return jsonify({})

    def post_terminate(run_id):
        return jsonify({})

    def get_experiments():
        print("get_experiments")
        return jsonify({
            "experiments": [app.config["EXPERIMENT"]],
            "total_size": 1,
        })

    def post_experiment():
        print("post_experiment")
        experiment_name = request.get_json(force=True).get("name")
        RUN_STR = json.dumps(app.config["RUN_EXPERIMENT"])
        RUN_STR = RUN_STR.replace(app.config["EXPERIMENT"]["name"], experiment_name)
        app.config["RUN_EXPERIMENT"] = json.loads(RUN_STR)

        RUN_STR = json.dumps(app.config["RUN_DEPLOYMENT"])
        RUN_STR = RUN_STR.replace(app.config["EXPERIMENT"]["name"], experiment_name)
        app.config["RUN_DEPLOYMENT"] = json.loads(RUN_STR)

        app.config["EXPERIMENT"]["name"] = experiment_name
        return jsonify(app.config["EXPERIMENT"])

    def get_experiment(experiment_id):
        print("get_experiment")
        if experiment_id != app.config["EXPERIMENT"]["id"]:
            return jsonify({"error": f"Experiment {experiment_id} not found."}), 404
        return jsonify(app.config["EXPERIMENT"])

    def delete_experiment(experiment_id):
        return jsonify({})

    # KFP API
    app.add_url_rule("/apis/v1beta1/healthz", view_func=get_healthz, methods=["GET"])
    app.add_url_rule("/apis/v1beta1/runs", view_func=get_runs, methods=["GET"])
    app.add_url_rule("/apis/v1beta1/runs", view_func=post_runs, methods=["POST"])
    app.add_url_rule("/apis/v1beta1/runs/<run_id>", view_func=get_run, methods=["GET"])
    app.add_url_rule("/apis/v1beta1/runs/<run_id>", view_func=delete_run, methods=["DELETE"])
    app.add_url_rule("/apis/v1beta1/runs/<run_id>/retry", view_func=post_retry, methods=["POST"])
    app.add_url_rule("/apis/v1beta1/runs/<run_id>/terminate", view_func=post_terminate, methods=["POST"])
    app.add_url_rule("/apis/v1beta1/experiments", view_func=get_experiments, methods=["GET"])
    app.add_url_rule("/apis/v1beta1/experiments", view_func=post_experiment, methods=["POST"])
    app.add_url_rule("/apis/v1beta1/experiments/<experiment_id>", view_func=get_experiment, methods=["GET"])
    app.add_url_rule("/apis/v1beta1/experiments/<experiment_id>", view_func=delete_experiment, methods=["DELETE"])

    proc = multiprocessing.Process(target=app.run, args=())
    proc.start()
    return proc
