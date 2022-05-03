# PlatIAgro Projects

[![.github/workflows/ci.yml](https://github.com/platiagro/projects/actions/workflows/ci.yml/badge.svg)](https://github.com/platiagro/projects/actions/workflows/ci.yml)
[![Quality Gate Status](https://sonarcloud.io/api/project_badges/measure?project=platiagro_projects&metric=alert_status)](https://sonarcloud.io/dashboard?id=platiagro_projects)
[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)

## Requirements

You may start the server locally or using a docker container, the requirements for each setup are listed below.

### Local

- [Python 3.8](https://www.python.org/downloads/)

### Docker

- [Docker CE](https://www.docker.com/get-docker)

## Projects API

Install requirements:

```bash
pip install .
```

Then, start the API server:

```bash
uvicorn projects.api.main:app
```

Arguments:

```bash
usage: uvicorn projects.api.main:app [-h] [--host TEXT] [--port INTEGER] [--workers INTEGER]
Projects API
optional arguments:
  -h, --help         show this help message and exit.
  --host TEXT        Bind socket to this host (default: 127.0.0.1).
  --port INTEGER     Port for HTTP server (default: 8000).
  --workers INTEGER  Number of worker processes.
environment variables:
  ENABLE_CORS                   whether to enable CORS headers for all responses.
  MINIO_ENDPOINT                hostname of a MinIO service (default: minio-service.platiagro:9000).
  MINIO_ACCESS_KEY              access key (aka user ID) of your account in MinIO service (default: minio).
  MINIO_SECRET_KEY              secret key (aka password) of your account in MinIO service (default: minio123).
  MYSQL_DB_HOST                 hostname of a MySQL service. If not set, the in-cluster address will be used (default: mysql.platiagro).
  MYSQL_DB_NAME                 name of a database in MySQL service (default: platiagro).
  MYSQL_DB_USER                 username to access the database specified by the MYSQL_DB_NAME variable (default: root).
  MYSQL_DB_PASSWORD             password to access the database specified by the MYSQL_DB_NAME variable (default: platiagro).
  JUPYTER_ENDPOINT              hostname of a Jupyter service (default: http://server.anonymous:80/notebook/anonymous/server).
  KF_PIPELINES_ENDPOINT         hostname to use to talk to Kubeflow Pipelines (default: the in-cluster service DNS name will be used).
  INGRESS_HOST_PORT             istio ingress host and post (default: the in-cluster host or ip will be used)
  MAIL_SERVER                   hostname of a smtp service (default: ).
  MAIL_USERNAME                 username of a smtp service (default: ).
  MAIL_PASSWORD                 password of a smtp service (default: ).
  MAIL_SENDER_ADDRESS           sender address for emails sent by the smtp service (default: ).
  SELDON_REST_TIMEOUT           response timeout in milliseconds for seldondeployments (default: 60000)
  SELDON_LOGGER_ENDPOINT        logger service URL that receives seldondeployment responses (default: http://projects.platiagro:8080)
  BROKER_URL                    monitoring broker service URL (default: http://broker-ingress.knative-eventing.svc.cluster.local/anonymous/default)
  TASK_DEFAULT_EXPERIMENT_IMAGE docker image used in a new task when none is specified (default: platiagro/platiagro-experiment-image:0.3.1)
  TASK_DEFAULT_MEMORY_REQUEST   amount of memory a new task requests when none is specified (default: 2Gi)
  TASK_DEFAULT_MEMORY_LIMIT     amount of memory a new task is limited to when none is specified (default: 2Gi)
  TASK_DEFAULT_CPU_REQUEST      amount of CPU a new task requests when none is specified (default: 100Mi)
  TASK_DEFAULT_CPU_LIMIT        amount of CPU a new task is limited to when none is specified (default: 1000Mi)
  TASK_NVIDIA_VISIBLE_DEVICES   which GPUs will be made accessible inside the task container. Possible values: 0,1,2...,none,all. (default: none)
```

**Using Docker**

```bash
docker build -t platiagro/projects:0.3.1-SNAPSHOT -f Dockerfile .
```

Example:

```bash
docker run -it -p 8080:8080 \
  --name projects \
  --env "MINIO_ENDPOINT=$MINIO_ENDPOINT" \
  --env "MINIO_ACCESS_KEY=$MINIO_ACCESS_KEY" \
  --env "MINIO_SECRET_KEY=$MINIO_SECRET_KEY" \
  --env "MYSQL_DB_HOST=$MYSQL_DB_HOST" \
  --env "MYSQL_DB_NAME=$MYSQL_DB_NAME" \
  --env "MYSQL_DB_USER=$MYSQL_DB_USER" \
  --env "MYSQL_DB_PASSWORD=$MYSQL_DB_PASSWORD" \
  --env "KF_PIPELINES_ENDPOINT=$KF_PIPELINES_ENDPOINT" \
  platiagro/projects:0.3.1-SNAPSHOT
```

## Persistence Agent

Start the Persistence Agent:

```bash
python -m projects.agent.main:app
```

Arguments:

```bash
usage: main.py [-h] [--debug] [--log-level [{NOTSET,DEBUG,INFO,WARNING,ERROR,CRITICAL}]]

Persistence Agent

optional arguments:
  -h, --help            show this help message and exit
  --debug               Enable debug
  --log-level [{NOTSET,DEBUG,INFO,WARNING,ERROR,CRITICAL}]
                        Sets log level to logging
```

**Using Docker**

```bash
docker build -t platiagro/persistence-agent:0.3.1-SNAPSHOT -f Dockerfile.persistenceagent .
```

```bash
docker run -it \
  -v $HOME/.kube:/root/.kube \
  --name persistence-agent \
  --env "MYSQL_DB_HOST=$MYSQL_DB_HOST" \
  --env "MYSQL_DB_NAME=$MYSQL_DB_NAME" \
  --env "MYSQL_DB_USER=$MYSQL_DB_USER" \
  --env "MYSQL_DB_PASSWORD=$MYSQL_DB_PASSWORD" \
  platiagro/persistence-agent:0.3.1-SNAPSHOT
```

## Testing

Install the testing requirements:

```bash
pip install .[testing]
```

Export environment variables.

Use the following command to run all tests:

```bash
pytest
```

Use the following command to run lint:

```bash
flake8 --max-line-length 127 projects/
```

## API

See the [PlatIAgro Projects API doc](https://platiagro.github.io/projects/) for API specification.
