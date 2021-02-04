# -*- coding: utf-8 -*-
from string import Template

SELDON_DEPLOYMENT = Template("""{
    "apiVersion": "machinelearning.seldon.io/v1alpha2",
    "kind": "SeldonDeployment",
    "metadata": {
        "labels": {
            "app": "seldon",
            "projectId": "$projectId"
        },
        "name": "$deploymentId",
        "deploymentId": "$deploymentId",
        "namespace": "$namespace"
    },
    "spec": {
        "annotations": {
            "deployment_version": "v1",
            "prometheus.io/scrape": "false",
            "seldon.io/rest-timeout": "$restTimeout",
            "seldon.io/grpc-timeout": "$grpcTimeout",
            "seldon.io/executor": "true"
        },
        "name": "$deploymentId",
        "predictors": [
            {
                "componentSpecs": [$componentSpecs
                ],
                "annotations": {
                    "tasks": "$tasks"
                },
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
                "image": "$image",
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
                    }
                ],
                "volumeMounts": [
                    {
                        "name": "workspace",
                        "mountPath": "/app"
                    }
                ],
                "resources": {
                    "requests": {
                        "memory": "$memoryRequest"
                    },
                    "limits": {
                        "memory": "$memoryLimit"
                    }
                }
            }
        ],
        "volumes": [
            {
                "name": "workspace",
                "persistentVolumeClaim": {
                    "claimName": "vol-task-$taskId"
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
    ],
    "logger": {
        "mode": "response",
        "url": "http://logger.anonymous"
    }
}""")
