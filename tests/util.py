# -*- coding: utf-8 -*-
from datetime import datetime

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from projects.database import DB_TENANT, Base
from projects import models

MOCK_UUID_1, MOCK_UUID_2, MOCK_UUID_3 = "uuid-1", "uuid-2", "uuid-3"
MOCK_PROJECT_NAME_1, MOCK_PROJECT_NAME_2, MOCK_PROJECT_NAME_3 = (
    "project-1",
    "project-2",
    "project-3",
)
MOCK_TASK_NAME_1, MOCK_TASK_NAME_2, MOCK_TASK_NAME_3 = (
    "task-1",
    "task-2",
    "task-3",
)
MOCK_CREATED_AT_1, MOCK_CREATED_AT_2, MOCK_CREATED_AT_3 = (
    datetime.utcnow(),
    datetime.utcnow(),
    datetime.utcnow(),
)
MOCK_UPDATED_AT_1, MOCK_UPDATED_AT_2, MOCK_UPDATED_AT_3 = (
    datetime.utcnow(),
    datetime.utcnow(),
    datetime.utcnow(),
)

MOCK_PROJECT_1 = {
    "createdAt": MOCK_CREATED_AT_1.isoformat(),
    "deployments": [],
    "description": None,
    "experiments": [],
    "hasDeployment": False,
    "hasExperiment": False,
    "hasPreDeployment": False,
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

MOCK_TASK_1 = {
    "arguments": None,
    "category": "DEFAULT",
    "commands": None,
    "cpuLimit": models.task.TASK_DEFAULT_CPU_LIMIT,
    "cpuRequest": models.task.TASK_DEFAULT_CPU_REQUEST,
    "createdAt": MOCK_CREATED_AT_1.isoformat(),
    "dataIn": None,
    "dataOut": None,
    "description": None,
    "docs": None,
    "hasNotebook": False,
    "image": models.task.TASK_DEFAULT_EXPERIMENT_IMAGE,
    "memoryLimit": models.task.TASK_DEFAULT_MEMORY_LIMIT,
    "memoryRequest": models.task.TASK_DEFAULT_MEMORY_REQUEST,
    "name": MOCK_TASK_NAME_1,
    "parameters": [],
    "readinessProbeInitialDelaySeconds": models.task.TASK_DEFAULT_READINESS_INITIAL_DELAY_SECONDS,
    "tags": None,
    "updatedAt": MOCK_UPDATED_AT_1.isoformat(),
    "uuid": MOCK_UUID_1,
}

MOCK_TASK_2 = {
    "arguments": None,
    "category": "DEFAULT",
    "commands": None,
    "cpuLimit": models.task.TASK_DEFAULT_CPU_LIMIT,
    "cpuRequest": models.task.TASK_DEFAULT_CPU_REQUEST,
    "createdAt": MOCK_CREATED_AT_2.isoformat(),
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
    "tags": None,
    "updatedAt": MOCK_UPDATED_AT_2.isoformat(),
    "uuid": MOCK_UUID_2,
}

MOCK_TASK_3 = {
    "arguments": None,
    "category": "DEFAULT",
    "commands": None,
    "cpuLimit": models.task.TASK_DEFAULT_CPU_LIMIT,
    "cpuRequest": models.task.TASK_DEFAULT_CPU_REQUEST,
    "createdAt": MOCK_CREATED_AT_3.isoformat(),
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
    "tags": None,
    "updatedAt": MOCK_UPDATED_AT_3.isoformat(),
    "uuid": MOCK_UUID_3,
}

MOCK_TASK_LIST = {
    "tasks": [
        MOCK_TASK_1,
        MOCK_TASK_2,
        MOCK_TASK_3,
    ],
    "total": 3,
}

MOCK_TASK_LIST_SORTED_BY_NAME_DESC = {
    "tasks": MOCK_TASK_LIST["tasks"][::-1],
    "total": 3,
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


def create_mock_projects():
    """
    Inserts some mock projects into test database.
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
    session.commit()
    session.close()


def create_mock_tasks():
    """
    Inserts some mock tasks into test database.
    """
    session = TestingSessionLocal()
    objects = [
        models.Task(
            uuid=MOCK_UUID_1,
            name=MOCK_TASK_NAME_1,
            category="DEFAULT",
            created_at=MOCK_CREATED_AT_1,
            updated_at=MOCK_UPDATED_AT_1,
        ),
        models.Task(
            uuid=MOCK_UUID_2,
            name=MOCK_TASK_NAME_2,
            category="DEFAULT",
            created_at=MOCK_CREATED_AT_2,
            updated_at=MOCK_UPDATED_AT_2,
        ),
        models.Task(
            uuid=MOCK_UUID_3,
            name=MOCK_TASK_NAME_3,
            category="DEFAULT",
            created_at=MOCK_CREATED_AT_3,
            updated_at=MOCK_UPDATED_AT_3,
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
    session.query(models.Experiment).delete()
    session.query(models.Project).delete()
    session.query(models.Template).delete()
    session.query(models.Task).delete()
    session.commit()
    session.close()
