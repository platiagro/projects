# -*- coding: utf-8 -*-
from string import Template

SELDON_DEPLOYMENT = Template("""{
    "apiVersion": "machinelearning.seldon.io/v1alpha2",
    "kind": "SeldonDeployment",
    "metadata": {
        "labels": {
            "app": "seldon"
        },
        "name": "$experimentId",
        "deploymentName": "$deploymentName",
        "namespace": "$namespace"
    },
    "spec": {
        "annotations": {
            "deployment_version": "v1",
            "seldon.io/rest-read-timeout": "60000",
            "seldon.io/rest-connection-timeout": "60000",
            "seldon.io/grpc-read-timeout": "60000",
            "seldon.io/engine-separate-pod": "true"
        },
        "name": "$experimentId",
        "resources": {
            "requests": {
                "memory": "2G"
            }
        },
        "predictors": [
            {
                "componentSpecs": [$componentSpecs
                ],
                "graph": $graph,
                "labels": {
                    "version": "v1"
                },
                "name": "model",
                "replicas": 1,
                "svcOrchSpec": {
                    "env": [
                        {
                            "name": "SELDON_LOG_LEVEL",
                            "value": "DEBUG"
                        }
                    ]
                }
            }
        ]
    }
}
""")

COMPONENT_SPEC = Template("""
{
    "spec": {
        "containers": [
            {
                "image": "platiagro/platiagro-deployment-image:0.2.0",
                "name": "$operatorId",
                "securityContext": {
                    "allowPrivilegeEscalation": false,
                    "runAsUser": 0
                },
                "env": [
                    {
                        "name": "EXPERIMENT_ID",
                        "value": "$experimentId"
                    },
                    {
                        "name": "OPERATOR_ID",
                        "value": "$operatorId"
                    },
                    {
                        "name": "PARAMETERS",
                        "value": "$parameters"
                    }
                ],
                "volumeMounts": [
                    {
                        "name": "workspace",
                        "mountPath": "/app"
                    }
                ]
            }
        ],
        "volumes": [
            {
                "name": "workspace",
                "persistentVolumeClaim": {
                    "claimName": "{{workflow.name}}-$operatorId"
                }
            }
        ]
    }
}""")

GRAPH = Template("""{
    "name": "$name",
    "type": "MODEL",
    "endpoint": {
        "type": "REST"
    },
    "children": [
        $children
    ]$logger
}""")

LOGGER = Template(""",
    "logger": {
        "url": "http://pipelines.kubeflow/seldon/logger/$experimentId",
        "mode": "all"
    }""")

POD_DEPLOYMENT_VOLUME = Template("""
{
    "apiVersion": "v1",
    "kind": "PersistentVolumeClaim",
    "metadata": {
        "name": "{{workflow.name}}-$operatorId",
        "namespace": "$namespace"
    },
    "spec": {
        "accessModes": ["ReadWriteOnce"],
        "resources": {
            "requests": {
                "storage": "50Mi"
            }
        }
    }
}""")

POD_DEPLOYMENT = Template("""
{
    "apiVersion": "v1",
    "kind": "Pod",
    "metadata": {
        "annotations":{
            "sidecar.istio.io/inject": "false"
        },
        "name": "{{workflow.name}}-$operatorId",
        "namespace": "$namespace"
    },
    "spec": {
        "containers": [
            {
                "image": "platiagro/platiagro-notebook-image:0.2.0",
                "name": "export-notebook",
                "command": ["sh", "-c"],
                "args": [
                    "papermill $notebookPath output.ipynb --log-level DEBUG; \
                     status=$status; \
                     bash upload-to-jupyter.sh $experimentId $operatorId Deployment.ipynb; \
                     touch -t 197001010000 Model.py; \
                     exit $statusEnv"
                ],
                "volumeMounts": [
                    {
                        "name": "workspace",
                        "mountPath": "/home/jovyan"
                    }
                ],
                "resources": {
                    "requests": {
                        "memory": "2G"
                    }
                },
                "env": [
                    {
                        "name": "EXPERIMENT_ID",
                        "value": "$experimentId"
                    },
                    {
                        "name": "OPERATOR_ID",
                        "value": "$operatorId"
                    }
                ]
            }
        ],
        "volumes": [
            {
                "name": "workspace",
                "persistentVolumeClaim": {
                    "claimName": "{{workflow.name}}-$operatorId"
                }
            }
        ],
        "restartPolicy": "Never"
    }
}""")
