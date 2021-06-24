# PlatIAgro Projects

[![.github/workflows/ci.yml](https://github.com/platiagro/projects/actions/workflows/ci.yml/badge.svg)](https://github.com/platiagro/projects/actions/workflows/ci.yml)
[![Quality Gate Status](https://sonarcloud.io/api/project_badges/measure?project=platiagro_projects&metric=alert_status)](https://sonarcloud.io/dashboard?id=platiagro_projects)
[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)

## Requirements

You may start the server locally or using a docker container, the requirements for each setup are listed below.

### Local

- [Python 3.7](https://www.python.org/downloads/)

### Docker

- [Docker CE](https://www.docker.com/get-docker)

## Quick Start

Make sure you have all requirements installed on your computer. Then, you may start the server using either a [Docker container](#run-using-docker) or in your [local machine](#run-local).

### Run using Docker

Export these environment variables:

```bash
export MINIO_ENDPOINT=localhost:9000
export MINIO_ACCESS_KEY=minio
export MINIO_SECRET_KEY=minio123
export MYSQL_DB_HOST=mysql
export MYSQL_DB_NAME=platiagro
export MYSQL_DB_USER=root
export MYSQL_DB_PASSWORD=
export JUPYTER_ENDPOINT=http://localhost:8888
export KF_PIPELINES_ENDPOINT=127.0.0.1:31380/pipeline
export KF_PIPELINES_NAMESPACE=anonymous
```

(Optional) Start a MinIO instance:

```bash
docker run -d -p 9000:9000 \
  --name minio \
  --env "MINIO_ACCESS_KEY=$MINIO_ACCESS_KEY" \
  --env "MINIO_SECRET_KEY=$MINIO_SECRET_KEY" \
  minio/minio:RELEASE.2018-02-09T22-40-05Z \
  server /data
```

(Optional) Start a MySQL server instance:

```bash
docker run -d -p 3306:3306 \
  --name mysql \
  --env "MYSQL_DATABASE=$MYSQL_DB_NAME" \
  --env "MYSQL_ROOT_PASSWORD=$MYSQL_DB_PASSWORD" \
  --env "MYSQL_ALLOW_EMPTY_PASSWORD=yes" \
  mysql:8.0.3
```

(Optional) Start a Jupyter Notebook instance:

```bash
docker run -d -p 8888:8888 \
  --name jupyter \
  jupyter/base-notebook \
  start-notebook.sh --NotebookApp.token=''
```

Then, build a docker image that launches the API server:

```bash
docker build -t platiagro/projects:0.2.0 .
```

Finally, start the API server:

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
  --env "JUPYTER_ENDPOINT=$JUPYTER_ENDPOINT" \
  platiagro/projects:0.2.0
```

### Run Local:

Export these environment variables:

```bash
export MINIO_ENDPOINT=localhost:9000
export MINIO_ACCESS_KEY=minio
export MINIO_SECRET_KEY=minio123
export MYSQL_DB_HOST=localhost
export MYSQL_DB_NAME=platiagro
export MYSQL_DB_USER=root
export MYSQL_DB_PASSWORD=
export JUPYTER_ENDPOINT=http://localhost:8888
export KF_PIPELINES_ENDPOINT=127.0.0.1:31380/pipeline
export KF_PIPELINES_NAMESPACE=anonymous
```

(Optional) Create a virtualenv:

```bash
virtualenv -p python3 venv
. venv/bin/activate
```

Install Python modules:

```bash
pip install .
```

(Optional) Initialize database:

```bash
platiagro-init-db
```
(Optional) For config SMTP parameters:

```bash
export MAIL_USERNAME=
export MAIL_PASSWORD=
export MAIL_SENDER_ADDRESS=
export MAIL_SERVER=
```

Then, start the API server:

```bash
uvicorn projects.api:app
```

Arguments:

```bash
usage: uvicorn projects.api:app [-h] [--host TEXT] [--port INTEGER] [--workers INTEGER]
Datasets API
optional arguments:
  -h, --help         show this help message and exit
  --host TEXT        Bind socket to this host (default: 127.0.0.1)
  --port INTEGER     Port for HTTP server (default: 8000)
  --workers INTEGER  Number of worker processes.
environment variables:
  ENABLE_CORS          whether to enable CORS headers for all responses.
```

## Testing

Install the testing requirements:

```bash
pip install .[testing]
```

Export these environment variables:

```bash
export MINIO_ENDPOINT=localhost:9000
export MINIO_ACCESS_KEY=minio
export MINIO_SECRET_KEY=minio123
export MYSQL_DB_HOST=localhost
export MYSQL_DB_NAME=platiagro
export MYSQL_DB_USER=root
export MYSQL_DB_PASSWORD=
export JUPYTER_ENDPOINT=http://localhost:8888
export KF_PIPELINES_ENDPOINT=localhost:5000
export KF_PIPELINES_NAMESPACE=anonymous
```

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
