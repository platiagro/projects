# -*- coding: utf-8 -*-
from string import Template

SELDON_DEPLOYMENT = Template("""{
    "apiVersion": "machinelearning.seldon.io/v1",
    "kind": "SeldonDeployment",
    "metadata": {
        "labels": {
            "app": "seldon",
            "projectId": "$projectId"
        },
        "name": "$deploymentId",
        "namespace": "$namespace"
    },
    "spec": {
        "annotations": {
            "deployment_version": "v1",
            "prometheus.io/scrape": "false",
            "seldon.io/rest-timeout": "$restTimeout",
            "seldon.io/executor": "true"
        },
        "name": "$deploymentId",
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
                            "value": "INFO"
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
                    },
                    {
                        "name": "TASK_NAME",
                        "value": "$taskName"
                    },
                    {
                        "name": "NVIDIA_VISIBLE_DEVICES",
                        "value": "$nvidiaVisibleDevices"
                    }
                ],
                "livenessProbe": {
                    "failureThreshold": 3,
                    "initialDelaySeconds": $initialDelaySeconds,
                    "periodSeconds": 5,
                    "successThreshold": 1,
                    "tcpSocket": {
                        "port": "http"
                    },
                    "timeoutSeconds": 1
                },
                "readinessProbe": {
                    "failureThreshold": 3,
                    "initialDelaySeconds": $initialDelaySeconds,
                    "periodSeconds": 5,
                    "successThreshold": 1,
                    "tcpSocket": {
                        "port": "http"
                    },
                    "timeoutSeconds": 1
                },
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
    ]
} """)


MONITORING_SERVICE = Template("""{
    "apiVersion": "serving.knative.dev/v1alpha1",
    "kind": "Service",
    "metadata": {
        "name": "$name",
        "namespace": "$namespace"
    },
    "spec": {
        "template": {
            "metadata": {
                "annotations": {
                    "autoscaling.knative.dev/minScale": "1"
                }
            },
            "spec": {
                "containers": [
                    {
                        "image": "platiagro/platiagro-monitoring-image:0.2.0",
                        "ports": [
                            {
                                "containerPort": 5000
                            }
                        ],
                        "env": [
                            {
                                "name": "MONITORING_ID",
                                "value": "$monitoringId"
                            },
                            {
                                "name": "EXPERIMENT_ID",
                                "value": "$experimentId"
                            },
                            {
                                "name": "DEPLOYMENT_ID",
                                "value": "$deploymentId"
                            },
                            {
                                "name": "RUN_ID",
                                "value": "$runId"
                            }
                        ],
                        "volumeMounts": [
                            {
                                "name": "configmap",
                                "mountPath": "/task"
                            }
                        ]
                    }
                ],
                "volumes": [
                    {
                        "name": "configmap",
                        "configmap": {
                            "name": "$configMap"
                        }
                    }
                ]
            }
        }
    }
} """)


MONITORING_TRIGGER = Template("""{
    "apiVersion": "eventing.knative.dev/v1alpha1",
    "kind": "Trigger",
    "metadata": {
        "name": "$name",
        "namespace": "$namespace"
    },
    "spec": {
        "broker": "default",
        "filter": {
            "attributes": {
                "type": "deployment.$deploymentId"
            }
        },
        "subscriber": {
            "ref": {
                "apiVersion": "serving.knative.dev/v1alpha1",
                "kind": "Service",
                "name": "$service"
            },
            "uri": "/api/v1.0/predictions"
        }
    }
} """)
