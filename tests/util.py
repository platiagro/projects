# -*- coding: utf-8 -*-
from datetime import datetime
from unittest import mock
from kfp_server_api.rest import ApiException
import json

import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from projects.database import DB_TENANT, Base
from projects import models

MOCK_SET_USER_NAMESPACE = mock.MagicMock()
MOCK_RUNS = mock.MagicMock()
MOCK_RUN_ID = "4546465"
MOCK_RUN = mock.MagicMock(id=MOCK_RUN_ID)
MOCK_LIST_RUNS = mock.MagicMock(
    return_value=mock.MagicMock(runs=[MOCK_RUN], next_page_token=None)
)
MOCK_WORKFLOW_MANIFEST = open(
    "tests/resources/deployment_mock_manifest.json", "r"
).read()
MOCK_NOT_GET_RUN = mock.MagicMock(
    runs=mock.MagicMock(terminate_run=mock.MagicMock(side_effect=ApiException()))
)
MOCK_GET_RUN = mock.MagicMock(
    return_value=mock.MagicMock(
        run=mock.MagicMock(id="uuid-1", created_at=datetime.utcnow()),
        pipeline_runtime=mock.MagicMock(workflow_manifest=MOCK_WORKFLOW_MANIFEST),
    )
)
MOCK_CREATE_RUN_FROM_PIPELINE_FUNC = mock.MagicMock()
MOCK_RUN_PIPELINE = mock.MagicMock(return_value=mock.MagicMock(id="uuid-1"))
MOCK_GET_EXPERIMENT = mock.MagicMock(return_value=mock.MagicMock(id="uuid-1"))
MOCK_CREATE_EXPERIMENT = mock.MagicMock(return_value=mock.MagicMock(id="uuid-1"))
MOCK_DELETE_EXPERIMENT = mock.MagicMock()
MOCK_EXPERIMENTS = mock.MagicMock(delete_experiment=MOCK_DELETE_EXPERIMENT)
MOCK_KFP_CLIENT = mock.MagicMock(
    set_user_namespace=MOCK_SET_USER_NAMESPACE,
    runs=MOCK_RUNS,
    list_runs=MOCK_LIST_RUNS,
    get_run=MOCK_GET_RUN,
    create_run_from_pipeline_func=MOCK_CREATE_RUN_FROM_PIPELINE_FUNC,
    run_pipeline=MOCK_RUN_PIPELINE,
    get_experiment=MOCK_GET_EXPERIMENT,
    create_experiment=MOCK_CREATE_EXPERIMENT,
    experiments=MOCK_EXPERIMENTS,
)

MOCK_STREAM = mock.MagicMock(
    is_open=mock.MagicMock(side_effect=[True, False]),
    read_stdout=mock.MagicMock(
        return_value=("Z2l0aHViLmNvbS9wbGF0aWFncm8vcHJvamVjdHM=")
    ),
)

MOCK_POD = mock.MagicMock(
    metadata=mock.MagicMock(name="server-0", namespace="anonymous"),
    status=mock.MagicMock(
        phase="Running",
        container_statuses=[mock.MagicMock(state=mock.MagicMock(running=True))],
    ),
)

MOCK_POD.spec = mock.MagicMock(
    volumes=[mock.MagicMock(name=mock.ANY)],
)

MOCK_CORE_V1_API = mock.MagicMock(
    read_namespaced_persistent_volume_claim=mock.MagicMock(
        side_effect=lambda name, namespace: mock.MagicMock(
            api_version="v1",
            kind="PersistentVolumeClaim",
            metadata=mock.MagicMock(
                name=f"vol-{name}",
                namespace=namespace,
            ),
            status=mock.MagicMock(phase="Bound"),
        )
    ),
    read_namespaced_pod=mock.MagicMock(
        side_effect=lambda name, namespace, **kwargs: MOCK_POD
    ),
    connect_get_namespaced_pod_exec=mock.MagicMock(
        __self__=mock.MagicMock(api_client=mock.MagicMock()),
        side_effect=lambda **kwargs: mock.MagicMock(
            is_open=mock.MagicMock(return_value=False),
            close=mock.MagicMock(),
        ),
    ),
    read_namespaced_service=mock.MagicMock(
        side_effect=lambda name, namespace: mock.MagicMock(
            api_version="v1",
            metadata=mock.MagicMock(
                name=name,
                namespace=namespace,
            ),
            status=mock.MagicMock(
                load_balancer=mock.MagicMock(
                    ingress=[
                        mock.MagicMock(ip="10.10.10.10:8000", hostname="anonymous")
                    ]
                )
            ),
        ),
    ),
    create_namespaced_persistent_volume_clain=mock.MagicMock(
        side_effect=lambda name, namespace: mock.MagicMock(
            api_version="v1",
            kind="PersistentVolumeClaim",
            metadata=mock.MagicMock(
                name=f"vol-{name}",
                namespace=namespace,
            ),
            status=mock.MagicMock(phase="Bound"),
        )
    ),
)


def mock_get_namespaced_custom_object(plural, **kwargs):
    if plural == "gateways":
        return {"spec": {"servers": [{}]}}
    elif plural == "notebooks":
        return {
            "spec": {
                "template": {
                    "spec": {
                        "containers": [{"volumeMounts": [{"mountPath": ""}]}],
                        "volumes": [{"name": ""}],
                    }
                }
            }
        }


MOCK_CUSTOM_OBJECTS_API = mock.MagicMock(
    list_namespaced_custom_object=mock.MagicMock(),
    get_namespaced_custom_object=mock.MagicMock(
        side_effect=mock_get_namespaced_custom_object
    ),
    patch_namespaced_custom_object=mock.MagicMock(),
)

MOCK_POST_PREDICTION = mock.MagicMock(
    status_code=200,
    _content=json.dumps(
        {
            "data": {
                "names": [
                    "SepalLengthCm",
                    "SepalWidthCm",
                    "PetalLengthCm",
                    "PetalWidthCm",
                    "Species",
                ],
                "ndarray": [
                    [5.1, 3.5, 1.4, 0.2, "Iris-setosa"],
                    [4.9, 3.0, 1.4, 0.2, "Iris-setosa"],
                    [4.7, 3.2, 1.3, 0.2, "Iris-setosa"],
                    [4.6, 3.1, 1.5, 0.2, "Iris-setosa"],
                ],
            }
        }
    ),
)

IRIS_DATASET_NAME = "iris.csv"

IRIS_DATA = (
    "SepalLengthCm,SepalWidthCm,PetalLengthCm,PetalWidthCm,Species\n"
    "5.1,3.5,1.4,0.2,Iris-setosa\n"
    "4.9,3.0,1.4,0.2,Iris-setosa\n"
    "4.7,3.2,1.3,0.2,Iris-setosa\n"
    "4.6,3.1,1.5,0.2,Iris-setosa\n"
)

IRIS_COLUMNS = [
    "SepalLengthCm",
    "SepalWidthCm",
    "PetalLengthCm",
    "PetalWidthCm",
    "Species",
]

IRIS_HEADERLESS_COLUMNS = [
    "col0",
    "col1",
    "col2",
    "col3",
    "col4",
]

IRIS_FEATURETYPES = [
    "Numerical",
    "Numerical",
    "Numerical",
    "Numerical",
    "Categorical",
]

IRIS_DATA_ARRAY = [
    [5.1, 3.5, 1.4, 0.2, "Iris-setosa"],
    [4.9, 3.0, 1.4, 0.2, "Iris-setosa"],
    [4.7, 3.2, 1.3, 0.2, "Iris-setosa"],
    [4.6, 3.1, 1.5, 0.2, "Iris-setosa"],
]


def mock_load_dataset(page_size, **kwargs):
    return IRIS_HEADERLESS_DATAFRAME.iloc[:page_size]


IRIS_DATAFRAME = pd.DataFrame(IRIS_DATA_ARRAY, columns=IRIS_COLUMNS)
IRIS_HEADERLESS_DATAFRAME = pd.DataFrame(
    IRIS_DATA_ARRAY, columns=IRIS_HEADERLESS_COLUMNS
)

MOCK_UUID_1, MOCK_UUID_2, MOCK_UUID_3, MOCK_UUID_4, MOCK_UUID_5 = (
    "uuid-1",
    "uuid-2",
    "uuid-3",
    "uuid-4",
    "uuid-5",
)
MOCK_PROJECT_NAME_1, MOCK_PROJECT_NAME_2, MOCK_PROJECT_NAME_3, MOCK_PROJECT_NAME_4 = (
    "project-1",
    "project-2",
    "project-3",
    "project-4",
)
MOCK_EXPERIMENT_NAME_1, MOCK_EXPERIMENT_NAME_2 = "experiment-1", "experiment-2"
MOCK_DEPLOYMENT_NAME_1, MOCK_DEPLOYMENT_NAME_2 = "deployment-1", "deployment-2"
(
    MOCK_TASK_NAME_1,
    MOCK_TASK_NAME_2,
    MOCK_TASK_NAME_3,
    MOCK_TASK_NAME_4,
    MOCK_TASK_NAME_5,
) = (
    "task-1",
    "task-2",
    "task-3",
    "task-4",
    "task-5",
)
MOCK_TEMPLATE_NAME_1, MOCK_TEMPLATE_NAME_2 = "template-1", "template-2"
(
    MOCK_CREATED_AT_1,
    MOCK_CREATED_AT_2,
    MOCK_CREATED_AT_3,
    MOCK_CREATED_AT_4,
    MOCK_CREATED_AT_5,
) = (
    datetime.utcnow(),
    datetime.utcnow(),
    datetime.utcnow(),
    datetime.utcnow(),
    datetime.utcnow(),
)
(
    MOCK_UPDATED_AT_1,
    MOCK_UPDATED_AT_2,
    MOCK_UPDATED_AT_3,
    MOCK_UPDATED_AT_4,
    MOCK_UPDATED_AT_5,
) = (
    datetime.utcnow(),
    datetime.utcnow(),
    datetime.utcnow(),
    datetime.utcnow(),
    datetime.utcnow(),
)

MOCK_OPERATOR_1 = {
    "uuid": MOCK_UUID_1,
    "name": MOCK_TASK_NAME_1,
    "taskId": MOCK_UUID_1,
    "task": {
        "name": MOCK_TASK_NAME_1,
        "tags": [],
        "parameters": [],
    },
    "dependencies": [],
    "parameters": {"dataset": IRIS_DATASET_NAME},
    "experimentId": MOCK_UUID_1,
    "deploymentId": None,
    "positionX": 0,
    "positionY": 0,
    "createdAt": MOCK_CREATED_AT_1.isoformat(),
    "updatedAt": MOCK_UPDATED_AT_1.isoformat(),
    "status": "Unset",
    "statusMessage": None,
}

MOCK_OPERATOR_2 = {
    "uuid": MOCK_UUID_2,
    "name": MOCK_TASK_NAME_1,
    "taskId": MOCK_UUID_1,
    "task": {
        "name": MOCK_TASK_NAME_1,
        "tags": [],
        "parameters": [],
    },
    "dependencies": [],
    "parameters": {},
    "experimentId": None,
    "deploymentId": MOCK_UUID_1,
    "positionX": 0,
    "positionY": 0,
    "createdAt": MOCK_CREATED_AT_2.isoformat(),
    "updatedAt": MOCK_UPDATED_AT_2.isoformat(),
    "status": "Unset",
    "statusMessage": None,
}

MOCK_OPERATOR_3 = {
    "uuid": MOCK_UUID_3,
    "name": MOCK_TASK_NAME_1,
    "taskId": MOCK_UUID_1,
    "task": {
        "name": MOCK_TASK_NAME_1,
        "tags": [],
        "parameters": [],
    },
    "dependencies": [],
    "parameters": {},
    "experimentId": None,
    "deploymentId": MOCK_UUID_2,
    "positionX": 0,
    "positionY": 0,
    "createdAt": MOCK_CREATED_AT_3.isoformat(),
    "updatedAt": MOCK_UPDATED_AT_3.isoformat(),
    "status": "Unset",
    "statusMessage": None,
}

MOCK_OPERATOR_4 = {
    "uuid": MOCK_UUID_4,
    "name": MOCK_TASK_NAME_1,
    "taskId": MOCK_UUID_1,
    "task": {
        "name": MOCK_TASK_NAME_1,
        "tags": [],
        "parameters": [],
    },
    "dependencies": [MOCK_UUID_1],
    "parameters": {},
    "experimentId": MOCK_UUID_1,
    "deploymentId": None,
    "positionX": 0,
    "positionY": 0,
    "createdAt": MOCK_CREATED_AT_1.isoformat(),
    "updatedAt": MOCK_UPDATED_AT_1.isoformat(),
    "status": "Unset",
    "statusMessage": None,
}

MOCK_EXPERIMENT_1 = {
    "createdAt": MOCK_CREATED_AT_1.isoformat(),
    "isActive": True,
    "name": MOCK_EXPERIMENT_NAME_1,
    "position": 0,
    "projectId": MOCK_UUID_1,
    "operators": [MOCK_OPERATOR_1, MOCK_OPERATOR_4],
    "updatedAt": MOCK_UPDATED_AT_1.isoformat(),
    "uuid": MOCK_UUID_1,
}

MOCK_EXPERIMENT_2 = {
    "createdAt": MOCK_CREATED_AT_2.isoformat(),
    "isActive": False,
    "name": MOCK_EXPERIMENT_NAME_2,
    "position": 1,
    "projectId": MOCK_UUID_1,
    "operators": [],
    "updatedAt": MOCK_UPDATED_AT_2.isoformat(),
    "uuid": MOCK_UUID_2,
}

MOCK_DEPLOYMENT_1 = {
    "createdAt": MOCK_CREATED_AT_1.isoformat(),
    "deployedAt": None,
    "experimentId": MOCK_UUID_1,
    "isActive": True,
    "name": MOCK_DEPLOYMENT_NAME_1,
    "position": 0,
    "projectId": MOCK_UUID_1,
    "operators": [MOCK_OPERATOR_2],
    "status": "Pending",
    "updatedAt": MOCK_UPDATED_AT_1.isoformat(),
    "url": None,
    "uuid": MOCK_UUID_1,
}

MOCK_DEPLOYMENT_2 = {
    "createdAt": MOCK_CREATED_AT_2.isoformat(),
    "deployedAt": None,
    "experimentId": MOCK_UUID_1,
    "isActive": False,
    "name": MOCK_DEPLOYMENT_NAME_2,
    "position": 1,
    "projectId": MOCK_UUID_1,
    "operators": [MOCK_OPERATOR_3],
    "status": "Pending",
    "updatedAt": MOCK_UPDATED_AT_2.isoformat(),
    "url": None,
    "uuid": MOCK_UUID_2,
}

MOCK_PROJECT_1 = {
    "createdAt": MOCK_CREATED_AT_1.isoformat(),
    "deployments": [MOCK_DEPLOYMENT_1, MOCK_DEPLOYMENT_2],
    "description": None,
    "experiments": [MOCK_EXPERIMENT_1, MOCK_EXPERIMENT_2],
    "hasDeployment": False,
    "hasExperiment": True,
    "hasPreDeployment": True,
    "name": MOCK_PROJECT_NAME_1,
    "updatedAt": MOCK_UPDATED_AT_1.isoformat(),
    "uuid": MOCK_UUID_1,
}

MOCK_PROJECT_2 = {
    "createdAt": MOCK_CREATED_AT_2.isoformat(),
    "deployments": [],
    "description": None,
    "experiments": [],
    "hasDeployment": False,
    "hasExperiment": False,
    "hasPreDeployment": False,
    "name": MOCK_PROJECT_NAME_2,
    "updatedAt": MOCK_UPDATED_AT_2.isoformat(),
    "uuid": MOCK_UUID_2,
}

MOCK_PROJECT_3 = {
    "createdAt": MOCK_CREATED_AT_3.isoformat(),
    "deployments": [],
    "description": None,
    "experiments": [],
    "hasDeployment": False,
    "hasExperiment": False,
    "hasPreDeployment": False,
    "name": MOCK_PROJECT_NAME_3,
    "updatedAt": MOCK_UPDATED_AT_3.isoformat(),
    "uuid": MOCK_UUID_3,
}

MOCK_COMPARISON_1 = {
    "activeTab": "1",
    "createdAt": MOCK_CREATED_AT_1.isoformat(),
    "experimentId": MOCK_UUID_1,
    "layout": {"x": 0, "y": 0, "w": 0, "h": 0},
    "operatorId": MOCK_UUID_1,
    "projectId": MOCK_UUID_1,
    "runId": MOCK_UUID_1,
    "updatedAt": MOCK_UPDATED_AT_1.isoformat(),
    "uuid": MOCK_UUID_1,
}

MOCK_PROJECT_LIST = {
    "projects": [
        MOCK_PROJECT_1,
        MOCK_PROJECT_2,
        MOCK_PROJECT_3,
    ],
    "total": 3,
}

MOCK_PROJECT_LIST_SORTED_BY_NAME_DESC = {
    "projects": MOCK_PROJECT_LIST["projects"][::-1],
    "total": 3,
}

MOCK_EXPERIMENT_LIST = {
    "experiments": [
        MOCK_EXPERIMENT_1,
        MOCK_EXPERIMENT_2,
    ],
    "total": 2,
}

MOCK_DEPLOYMENT_LIST = {
    "deployments": [
        MOCK_DEPLOYMENT_1,
        MOCK_DEPLOYMENT_2,
    ],
    "total": 2,
}

MOCK_OPERATOR_LIST = {
    "operators": [
        MOCK_OPERATOR_1,
        MOCK_OPERATOR_4,
    ],
    "total": 2,
}
# {
# 'createdAt': mock.ANY,
# 'operators': {
#     'deployment': {
#         'parameters': {},
#         'status': 'Succeeded'
#     },
#     MOCK_UUID_3: {
#         'parameters': {
#             'dataset': None,
#             'features_to_filter': ['Vibracao1']
#         },
#         'status': 'Succeeded',
#         'taskId': MOCK_UUID_2
#     },
# },
# 'uuid': 'uuid-1'
# }
MOCK_DEPLOYMENT_RUN_LIST = {
    "runs": [
        {
            "createdAt": mock.ANY,
            "operators": {
                "deployment": {"parameters": {}, "status": "Succeeded"},
                "f08ccfda-9206-4f26-8326-ad666b1761e7": {
                    "parameters": {
                        "dataset": None,
                        "features_to_filter": ["Vibracao1"],
                    },
                    "status": "Succeeded",
                    "taskId": "f298de51-cfc1-4bc9-8ebd-0959d74d7b91",
                },
            },
            "uuid": "uuid-1",
        }
    ],
    "total": 1,
}

MOCK_COMPARISON_LIST = {
    "comparisons": [
        MOCK_COMPARISON_1,
    ],
    "total": 1,
}

MOCK_TASK_1 = {
    "arguments": None,
    "category": "DEFAULT",
    "commands": None,
    "cpuLimit": models.task.TASK_DEFAULT_CPU_LIMIT,
    "cpuRequest": models.task.TASK_DEFAULT_CPU_REQUEST,
    "createdAt": mock.ANY,
    "dataIn": None,
    "dataOut": None,
    "description": None,
    "docs": None,
    "hasNotebook": True,
    "image": models.task.TASK_DEFAULT_EXPERIMENT_IMAGE,
    "memoryLimit": models.task.TASK_DEFAULT_MEMORY_LIMIT,
    "memoryRequest": models.task.TASK_DEFAULT_MEMORY_REQUEST,
    "name": MOCK_TASK_NAME_1,
    "parameters": [],
    "readinessProbeInitialDelaySeconds": models.task.TASK_DEFAULT_READINESS_INITIAL_DELAY_SECONDS,
    "tags": [],
    "updatedAt": mock.ANY,
    "uuid": MOCK_UUID_1,
}

MOCK_TASK_2 = {
    "arguments": None,
    "category": "DEFAULT",
    "commands": None,
    "cpuLimit": models.task.TASK_DEFAULT_CPU_LIMIT,
    "cpuRequest": models.task.TASK_DEFAULT_CPU_REQUEST,
    "createdAt": mock.ANY,
    "dataIn": None,
    "dataOut": None,
    "description": None,
    "docs": None,
    "hasNotebook": False,
    "image": models.task.TASK_DEFAULT_EXPERIMENT_IMAGE,
    "memoryLimit": models.task.TASK_DEFAULT_MEMORY_LIMIT,
    "memoryRequest": models.task.TASK_DEFAULT_MEMORY_REQUEST,
    "name": MOCK_TASK_NAME_2,
    "parameters": [],
    "readinessProbeInitialDelaySeconds": models.task.TASK_DEFAULT_READINESS_INITIAL_DELAY_SECONDS,
    "tags": [],
    "updatedAt": mock.ANY,
    "uuid": MOCK_UUID_2,
}

MOCK_TASK_3 = {
    "arguments": None,
    "category": "DEFAULT",
    "commands": None,
    "cpuLimit": models.task.TASK_DEFAULT_CPU_LIMIT,
    "cpuRequest": models.task.TASK_DEFAULT_CPU_REQUEST,
    "createdAt": mock.ANY,
    "dataIn": None,
    "dataOut": None,
    "description": None,
    "docs": None,
    "hasNotebook": False,
    "image": models.task.TASK_DEFAULT_EXPERIMENT_IMAGE,
    "memoryLimit": models.task.TASK_DEFAULT_MEMORY_LIMIT,
    "memoryRequest": models.task.TASK_DEFAULT_MEMORY_REQUEST,
    "name": MOCK_TASK_NAME_3,
    "parameters": [],
    "readinessProbeInitialDelaySeconds": models.task.TASK_DEFAULT_READINESS_INITIAL_DELAY_SECONDS,
    "tags": [],
    "updatedAt": mock.ANY,
    "uuid": MOCK_UUID_3,
}

MOCK_TASK_4 = {
    "arguments": None,
    "category": "DEFAULT",
    "commands": None,
    "cpuLimit": models.task.TASK_DEFAULT_CPU_LIMIT,
    "cpuRequest": models.task.TASK_DEFAULT_CPU_REQUEST,
    "createdAt": mock.ANY,
    "dataIn": None,
    "dataOut": None,
    "description": None,
    "docs": None,
    "hasNotebook": False,
    "image": models.task.TASK_DEFAULT_EXPERIMENT_IMAGE,
    "memoryLimit": models.task.TASK_DEFAULT_MEMORY_LIMIT,
    "memoryRequest": models.task.TASK_DEFAULT_MEMORY_REQUEST,
    "name": MOCK_TASK_NAME_4,
    "parameters": [],
    "readinessProbeInitialDelaySeconds": models.task.TASK_DEFAULT_READINESS_INITIAL_DELAY_SECONDS,
    "tags": [],
    "updatedAt": mock.ANY,
    "uuid": MOCK_UUID_4,
}

MOCK_TASK_5 = {
    "arguments": None,
    "category": "DEFAULT",
    "commands": None,
    "cpuLimit": models.task.TASK_DEFAULT_CPU_LIMIT,
    "cpuRequest": models.task.TASK_DEFAULT_CPU_REQUEST,
    "createdAt": mock.ANY,
    "dataIn": None,
    "dataOut": None,
    "description": None,
    "docs": None,
    "hasNotebook": False,
    "image": models.task.TASK_DEFAULT_EXPERIMENT_IMAGE,
    "memoryLimit": models.task.TASK_DEFAULT_MEMORY_LIMIT,
    "memoryRequest": models.task.TASK_DEFAULT_MEMORY_REQUEST,
    "name": MOCK_TASK_NAME_5,
    "parameters": [],
    "readinessProbeInitialDelaySeconds": models.task.TASK_DEFAULT_READINESS_INITIAL_DELAY_SECONDS,
    "tags": [],
    "updatedAt": mock.ANY,
    "uuid": MOCK_UUID_5,
}

MOCK_TASK_LIST = {
    "tasks": [
        MOCK_TASK_1,
        MOCK_TASK_2,
        MOCK_TASK_3,
        MOCK_TASK_4,
        MOCK_TASK_5,
    ],
    "total": 5,
}

MOCK_TASK_LIST_SORTED_BY_NAME_DESC = {
    "tasks": MOCK_TASK_LIST["tasks"][::-1],
    "total": 5,
}

MOCK_TEMPLATE_1 = {
    "uuid": MOCK_UUID_1,
    "name": MOCK_TEMPLATE_NAME_1,
    "tasks": [
        {
            "uuid": MOCK_UUID_1,
            "task_id": MOCK_UUID_1,
            "dependencies": [],
            "position_x": 0.0,
            "position_y": 0.0,
        }
    ],
    "experimentId": MOCK_UUID_1,
    "deploymentId": None,
    "createdAt": MOCK_CREATED_AT_1.isoformat(),
    "updatedAt": MOCK_UPDATED_AT_1.isoformat(),
}

MOCK_TEMPLATE_2 = {
    "uuid": MOCK_UUID_2,
    "name": MOCK_TEMPLATE_NAME_2,
    "tasks": [
        {
            "uuid": MOCK_UUID_2,
            "task_id": MOCK_UUID_1,
            "dependencies": [],
            "position_x": 0.0,
            "position_y": 0.0,
        }
    ],
    "experimentId": None,
    "deploymentId": MOCK_UUID_1,
    "createdAt": MOCK_CREATED_AT_2.isoformat(),
    "updatedAt": MOCK_UPDATED_AT_2.isoformat(),
}

MOCK_TEMPLATE_LIST = {
    "templates": [
        MOCK_TEMPLATE_1,
        MOCK_TEMPLATE_2,
    ],
    "total": 2,
}

MOCK_NOTEBOOK = {
    "cells": [
        {
            "cell_type": "markdown",
            "metadata": {},
            "source": [
                "# Nova Tarefa - Experimento\n",
                "\n",
                "Preencha aqui com detalhes sobre a tarefa.<br>\n",
                "### **Em caso de dúvidas, consulte os [tutoriais da PlatIAgro](https://platiagro.github.io/tutorials/).**",
            ],
        }
    ],
    "metadata": {
        "celltoolbar": "Tags",
        "kernelspec": {
            "display_name": "Python 3",
            "language": "python",
            "name": "python3",
        },
        "language_info": {
            "codemirror_mode": {"name": "ipython", "version": 3},
            "file_extension": ".py",
            "mimetype": "text/x-python",
            "name": "python",
            "nbconvert_exporter": "python",
            "pygments_lexer": "ipython3",
            "version": "3.7.8",
        },
    },
    "nbformat": 4,
    "nbformat_minor": 4,
}

SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)


def override_session_scope():
    """
    Provide a transactional scope around a series of operations.
    """
    try:
        session = TestingSessionLocal()
        yield session
    finally:
        session.close()


def create_mocks():
    """
    Inserts some mock records into test database.
    """
    session = TestingSessionLocal()
    objects = [
        models.Project(
            uuid=MOCK_UUID_1,
            name=MOCK_PROJECT_NAME_1,
            created_at=MOCK_CREATED_AT_1,
            updated_at=MOCK_UPDATED_AT_1,
            tenant=DB_TENANT,
        ),
        models.Project(
            uuid=MOCK_UUID_2,
            name=MOCK_PROJECT_NAME_2,
            created_at=MOCK_CREATED_AT_2,
            updated_at=MOCK_UPDATED_AT_2,
            tenant=DB_TENANT,
        ),
        models.Project(
            uuid=MOCK_UUID_3,
            name=MOCK_PROJECT_NAME_3,
            created_at=MOCK_CREATED_AT_3,
            updated_at=MOCK_UPDATED_AT_3,
            tenant=DB_TENANT,
        ),
    ]
    session.bulk_save_objects(objects)
    session.flush()
    objects = [
        models.Task(
            uuid=MOCK_UUID_1,
            name=MOCK_TASK_NAME_1,
            category="DEFAULT",
            tags=[],
            experiment_notebook_path="Experiment.ipynb",
            deployment_notebook_path="Deployment.ipynb",
            created_at=MOCK_CREATED_AT_1,
            updated_at=MOCK_UPDATED_AT_1,
        ),
        models.Task(
            uuid=MOCK_UUID_2,
            name=MOCK_TASK_NAME_2,
            category="DEFAULT",
            tags=[],
            created_at=MOCK_CREATED_AT_2,
            updated_at=MOCK_UPDATED_AT_2,
        ),
        models.Task(
            uuid=MOCK_UUID_3,
            name=MOCK_TASK_NAME_3,
            category="DEFAULT",
            tags=[],
            created_at=MOCK_CREATED_AT_3,
            updated_at=MOCK_UPDATED_AT_3,
        ),
        models.Task(
            uuid=MOCK_UUID_4,
            name=MOCK_TASK_NAME_4,
            category="DEFAULT",
            tags=[],
            created_at=MOCK_CREATED_AT_4,
            updated_at=MOCK_UPDATED_AT_4,
        ),
        models.Task(
            uuid=MOCK_UUID_5,
            name=MOCK_TASK_NAME_5,
            category="DEFAULT",
            tags=[],
            created_at=MOCK_CREATED_AT_4,
            updated_at=MOCK_UPDATED_AT_4,
        ),
    ]
    session.bulk_save_objects(objects)
    session.flush()
    objects = [
        models.Experiment(
            uuid=MOCK_UUID_1,
            name=MOCK_EXPERIMENT_NAME_1,
            project_id=MOCK_UUID_1,
            position=0,
            is_active=True,
            created_at=MOCK_CREATED_AT_1,
            updated_at=MOCK_UPDATED_AT_1,
        ),
        models.Experiment(
            uuid=MOCK_UUID_2,
            name=MOCK_EXPERIMENT_NAME_2,
            project_id=MOCK_UUID_1,
            position=1,
            is_active=False,
            created_at=MOCK_CREATED_AT_2,
            updated_at=MOCK_UPDATED_AT_2,
        ),
    ]
    session.bulk_save_objects(objects)
    session.flush()
    objects = [
        models.Deployment(
            uuid=MOCK_UUID_1,
            name=MOCK_DEPLOYMENT_NAME_1,
            project_id=MOCK_UUID_1,
            experiment_id=MOCK_UUID_1,
            position=0,
            is_active=True,
            status="Pending",
            created_at=MOCK_CREATED_AT_1,
            updated_at=MOCK_UPDATED_AT_1,
        ),
        models.Deployment(
            uuid=MOCK_UUID_2,
            name=MOCK_DEPLOYMENT_NAME_2,
            project_id=MOCK_UUID_1,
            experiment_id=MOCK_UUID_1,
            is_active=False,
            position=1,
            status="Pending",
            created_at=MOCK_CREATED_AT_2,
            updated_at=MOCK_UPDATED_AT_2,
        ),
    ]
    session.bulk_save_objects(objects)
    session.flush()
    objects = [
        models.Operator(
            uuid=MOCK_UUID_1,
            experiment_id=MOCK_UUID_1,
            task_id=MOCK_UUID_1,
            dependencies=[],
            parameters={"dataset": IRIS_DATASET_NAME},
            status="Unset",
            position_x=0,
            position_y=0,
            created_at=MOCK_CREATED_AT_1,
            updated_at=MOCK_UPDATED_AT_1,
        ),
        models.Operator(
            uuid=MOCK_UUID_2,
            deployment_id=MOCK_UUID_1,
            task_id=MOCK_UUID_1,
            dependencies=[],
            parameters={},
            status="Unset",
            position_x=0,
            position_y=0,
            created_at=MOCK_CREATED_AT_2,
            updated_at=MOCK_UPDATED_AT_2,
        ),
        models.Operator(
            uuid=MOCK_UUID_3,
            deployment_id=MOCK_UUID_2,
            task_id=MOCK_UUID_1,
            dependencies=[],
            parameters={},
            status="Unset",
            position_x=0,
            position_y=0,
            created_at=MOCK_CREATED_AT_3,
            updated_at=MOCK_UPDATED_AT_3,
        ),
        models.Operator(
            uuid=MOCK_UUID_4,
            experiment_id=MOCK_UUID_1,
            task_id=MOCK_UUID_1,
            dependencies=[MOCK_UUID_1],
            parameters={},
            status="Unset",
            position_x=0,
            position_y=0,
            created_at=MOCK_CREATED_AT_1,
            updated_at=MOCK_UPDATED_AT_1,
        ),
    ]
    session.bulk_save_objects(objects)
    session.flush()
    objects = [
        models.Template(
            uuid=MOCK_UUID_1,
            name=MOCK_TEMPLATE_NAME_1,
            tasks=[
                {
                    "uuid": MOCK_UUID_1,
                    "task_id": MOCK_UUID_1,
                    "dependencies": [],
                    "position_x": 0.0,
                    "position_y": 0.0,
                }
            ],
            experiment_id=MOCK_UUID_1,
            deployment_id=None,
            created_at=MOCK_CREATED_AT_1,
            updated_at=MOCK_UPDATED_AT_1,
            tenant=DB_TENANT,
        ),
        models.Template(
            uuid=MOCK_UUID_2,
            name=MOCK_TEMPLATE_NAME_2,
            tasks=[
                {
                    "uuid": MOCK_UUID_2,
                    "task_id": MOCK_UUID_1,
                    "dependencies": [],
                    "position_x": 0.0,
                    "position_y": 0.0,
                }
            ],
            experiment_id=None,
            deployment_id=MOCK_UUID_1,
            created_at=MOCK_CREATED_AT_2,
            updated_at=MOCK_UPDATED_AT_2,
            tenant=DB_TENANT,
        ),
    ]
    session.bulk_save_objects(objects)
    session.flush()
    objects = [
        models.Comparison(
            uuid=MOCK_UUID_1,
            project_id=MOCK_UUID_1,
            experiment_id=MOCK_UUID_1,
            operator_id=MOCK_UUID_1,
            active_tab="1",
            run_id=MOCK_UUID_1,
            layout={"x": 0, "y": 0, "w": 0, "h": 0},
            created_at=MOCK_CREATED_AT_1,
            updated_at=MOCK_UPDATED_AT_1,
        ),
    ]
    session.bulk_save_objects(objects)
    session.commit()
    session.close()


def delete_mocks():
    """
    Deletes mock records from test database.
    """
    session = TestingSessionLocal()
    session.query(models.Comparison).delete()
    session.query(models.Operator).delete()
    session.query(models.Deployment).delete()
    session.query(models.Experiment).delete()
    session.query(models.Project).delete()
    session.query(models.Template).delete()
    session.query(models.Task).delete()
    session.commit()
    session.close()


FILE_NOT_FOUND_ERROR = FileNotFoundError("The specified dataset does not exist")
SAMPLE_NOTEBOOK = '{"cells": [{"cell_type": "code","execution_count": null,"metadata": {"tags": ["parameters"]},"outputs":[],"source":["shuffle = True #@param {type: \\"boolean\\"}"]}],"metadata": {"kernelspec": {"display_name": "Python 3","language": "python","name": "python3"},"language_info": {"codemirror_mode": {"name": "ipython","version": 3},"file_extension": ".py","mimetype": "text/x-python","name": "python","nbconvert_exporter": "python","pygments_lexer": "ipython3","version": "3.6.9"}},"nbformat": 4,"nbformat_minor": 4}'
CONTENT_DISPOSITION = "attachment; filename=results.zip"
CONTENT_TYPE = "application/x-zip-compressed"
