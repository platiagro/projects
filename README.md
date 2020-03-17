# PlatIAgro Projects

[![Build Status](https://travis-ci.com/platiagro/projects.svg)](https://travis-ci.com/platiagro/projects)
[![codecov](https://codecov.io/gh/platiagro/projects/branch/master/graph/badge.svg)](https://codecov.io/gh/platiagro/projects)
[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![Gitter](https://badges.gitter.im/platiagro/community.svg)](https://gitter.im/platiagro/community?utm_source=badge&utm_medium=badge&utm_campaign=pr-badge)
[![Known Vulnerabilities](https://snyk.io/test/github/platiagro/projects/badge.svg?targetFile=requirements.txt)](https://snyk.io/test/github/platiagro/projects?targetFile=requirements.txt)

## Requirements

You may start the server locally or using a docker container, the requirements for each setup are listed below.

### Local

- [Python 3.6](https://www.python.org/downloads/)

### Docker

- [Docker CE](https://www.docker.com/get-docker)

## Quick Start

Make sure you have all requirements installed on your computer. Then, you may start the server using either a [Docker container](#run-using-docker) or in your [local machine](#run-local).

### Run using Docker

Export these environment variables:

```bash
export MINIO_ENDPOINT=play.min.io
export MINIO_ACCESS_KEY=Q3AM3UQ867SPQQA43P2F
export MINIO_SECRET_KEY=zuf+tfteSlswRu7BJ86wekitnifILbZam1KYY3TG
export MYSQL_DB_HOST=localhost
export MYSQL_DB_NAME=platiagro
export MYSQL_DB_USER=root
export MYSQL_DB_PASSWORD=
export JUPYTER_ENDPOINT=http://localhost:8888
```

(Optional) Start a MySQL server instance:

```bash
docker run -d -p 3306:3306 \
  --name mysql \
  --env "MYSQL_DATABASE=$MYSQL_DB_NAME" \
  --env "MYSQL_ROOT_PASSWORD=$MYSQL_DB_PASSWORD" \
  --env "MYSQL_ALLOW_EMPTY_PASSWORD=yes" \
  mysql:8
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
docker build -t platiagro/projects:0.0.2 .
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
  platiagro/projects:0.0.2
```

### Run Local:

Export these environment variables:

```bash
export MINIO_ENDPOINT=play.min.io
export MINIO_ACCESS_KEY=Q3AM3UQ867SPQQA43P2F
export MINIO_SECRET_KEY=zuf+tfteSlswRu7BJ86wekitnifILbZam1KYY3TG
export MYSQL_DB_HOST=localhost
export MYSQL_DB_NAME=platiagro
export MYSQL_DB_USER=root
export MYSQL_DB_PASSWORD=
export JUPYTER_ENDPOINT=http://localhost:8888
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

Then, start the API server:

```bash
python -m projects.api.main
```

## Testing

Install the testing requirements:

```bash
pip install .[testing]
```

Export these environment variables:

```bash
export MINIO_ENDPOINT=play.min.io
export MINIO_ACCESS_KEY=Q3AM3UQ867SPQQA43P2F
export MINIO_SECRET_KEY=zuf+tfteSlswRu7BJ86wekitnifILbZam1KYY3TG
export MYSQL_DB_HOST=localhost
export MYSQL_DB_NAME=platiagro
export MYSQL_DB_USER=root
export MYSQL_DB_PASSWORD=
export JUPYTER_ENDPOINT=http://localhost:8888
```

Use the following command to run all tests:

```bash
pytest
```

## API

API Reference with examples.

### Components

**Lists components:** <br>
method: GET <br>
url: /components

```bash
curl -X GET \
  http://localhost:8080/components
```

Expected Output:

```json
[{"createdAt":"2000-01-01T00:00:00","description":"long foo","inferenceNotebookPath":"minio://anonymous/components/6814cdae-d88d-4c4d-bfb6-9ea6d6086dc4/Inference.ipynb","isDefault":false,"name":"foo","params":[],"trainingNotebookPath":"minio://anonymous/components/6814cdae-d88d-4c4d-bfb6-9ea6d6086dc4/Training.ipynb","updatedAt":"2000-01-01T00:00:00","uuid":"6814cdae-d88d-4c4d-bfb6-9ea6d6086dc4"}]
```

**Creates a component:** <br>
method: POST <br>
url: /components

```bash
curl -X POST \
  http://localhost:8080/components \
  -d '{"name":"foo"}'
```

Expected Output:

```json
{"createdAt":"2000-01-01T00:00:00","description":"long foo","inferenceNotebookPath":"minio://anonymous/components/6814cdae-d88d-4c4d-bfb6-9ea6d6086dc4/Inference.ipynb","isDefault":false,"name":"foo","params":[],"trainingNotebookPath":"minio://anonymous/components/6814cdae-d88d-4c4d-bfb6-9ea6d6086dc4/Training.ipynb","updatedAt":"2000-01-01T00:00:00","uuid":"6814cdae-d88d-4c4d-bfb6-9ea6d6086dc4"}
```

**Details a component** <br>
method: GET <br>
url: /components/:uuid

```bash
curl -X GET \
  http://localhost:8080/components/6814cdae-d88d-4c4d-bfb6-9ea6d6086dc4
```

Expected Output:

```json
{"createdAt":"2000-01-01T00:00:00","description":"long foo","inferenceNotebookPath":"minio://anonymous/components/6814cdae-d88d-4c4d-bfb6-9ea6d6086dc4/Inference.ipynb","isDefault":false,"name":"foo","params":[],"trainingNotebookPath":"minio://anonymous/components/6814cdae-d88d-4c4d-bfb6-9ea6d6086dc4/Training.ipynb","updatedAt":"2000-01-01T00:00:00","uuid":"6814cdae-d88d-4c4d-bfb6-9ea6d6086dc4"}
```

**Updates a component:** <br>
method: PATCH <br>
url: /components/:uuid

```bash
curl -X PATCH \
  http://localhost:8080/components/6814cdae-d88d-4c4d-bfb6-9ea6d6086dc4 \
  -d '{"name":"bar"}'
```

Expected Output:

```json
{"createdAt":"2000-01-01T00:00:00","description":"long foo","inferenceNotebookPath":"minio://anonymous/components/6814cdae-d88d-4c4d-bfb6-9ea6d6086dc4/Inference.ipynb","isDefault":false,"name":"bar","params":[],"trainingNotebookPath":"minio://anonymous/components/6814cdae-d88d-4c4d-bfb6-9ea6d6086dc4/Training.ipynb","updatedAt":"2000-01-01T00:00:00","uuid":"6814cdae-d88d-4c4d-bfb6-9ea6d6086dc4"}
```

### Projects

**Lists projects:** <br>
method: GET <br>
url: /projects

```bash
curl -X GET \
  http://localhost:8080/projects
```

Expected Output:

```json
[{"createdAt":"2000-01-01T00:00:00","experiments":[],"name":"foo","updatedAt":"2000-01-01T00:00:00","uuid":"cc07c929-85d5-4939-b59c-790e540f207f"}]
```

**Creates a project:** <br>
method: POST <br>
url: /projects

```bash
curl -X POST \
  http://localhost:8080/projects \
  -d '{"name":"foo"}'
```

Expected Output:

```json
{"createdAt":"2000-01-01T00:00:00","experiments":[],"name":"foo","updatedAt":"2000-01-01T00:00:00","uuid":"cc07c929-85d5-4939-b59c-790e540f207f"}
```

**Details a project** <br>
method: GET <br>
url: /projects/:uuid

```bash
curl -X GET \
  http://localhost:8080/projects/cc07c929-85d5-4939-b59c-790e540f207f
```

Expected Output:

```json
{"createdAt":"2000-01-01T00:00:00","experiments":[],"name":"foo","updatedAt":"2000-01-01T00:00:00","uuid":"cc07c929-85d5-4939-b59c-790e540f207f"}
```

**Updates a project:** <br>
method: PATCH <br>
url: /projects/:uuid

```bash
curl -X PATCH \
  http://localhost:8080/projects/cc07c929-85d5-4939-b59c-790e540f207f \
  -d '{"name":"bar"}'
```

Expected Output:

```json
{"createdAt":"2000-01-01T00:00:00","experiments":[],"name":"bar","updatedAt":"2000-01-01T00:00:00","uuid":"cc07c929-85d5-4939-b59c-790e540f207f"}
```

### Experiments

**Lists experiments:** <br>
method: GET <br>
url: /projects/:project_id/experiments

```bash
curl -X GET \
  http://localhost:8080/projects/cc07c929-85d5-4939-b59c-790e540f207f/experiments
```

Expected Output:

```json
[{"createdAt":"2000-01-01T00:00:00","dataset":"iris","name":"foo","operators":[],"position":0,"projectId":"cc07c929-85d5-4939-b59c-790e540f207f","target":"col4","updatedAt":"2000-01-01T00:00:00","uuid":"2b42d7b7-3a32-4678-b59e-91b2ad9e1fcf"}]
```

**Creates an experiment:** <br>
method: POST <br>
url: /projects/:project_id/experiments

```bash
curl -X POST \
  http://localhost:8080/projects/cc07c929-85d5-4939-b59c-790e540f207f/experiments \
  -d '{"dataset":"iris","name":"foo","position":0,"target":"col4"}'
```

Expected Output:

```json
{"createdAt":"2000-01-01T00:00:00","dataset":"iris","name":"foo","operators":[],"position":0,"projectId":"cc07c929-85d5-4939-b59c-790e540f207f","target":"col4","updatedAt":"2000-01-01T00:00:00","uuid":"2b42d7b7-3a32-4678-b59e-91b2ad9e1fcf"}
```

**Details an experiment** <br>
method: GET <br>
url: /projects/:project_id/experiments/:uuid

```bash
curl -X GET \
  http://localhost:8080/projects/cc07c929-85d5-4939-b59c-790e540f207f/experiments/2b42d7b7-3a32-4678-b59e-91b2ad9e1fcf
```

Expected Output:

```json
{"createdAt":"2000-01-01T00:00:00","dataset":"iris","name":"foo","operators":[],"position":0,"projectId":"cc07c929-85d5-4939-b59c-790e540f207f","target":"col4","updatedAt":"2000-01-01T00:00:00","uuid":"2b42d7b7-3a32-4678-b59e-91b2ad9e1fcf"}
```

**Updates an experiment:** <br>
method: PATCH <br>
url: /projects/:project_id/experiments/:uuid

```bash
curl -X PATCH \
  http://localhost:8080/projects/cc07c929-85d5-4939-b59c-790e540f207f/experiments/2b42d7b7-3a32-4678-b59e-91b2ad9e1fcf \
  -d '{"name":"bar"}'
```

Expected Output:

```json
{"createdAt":"2000-01-01T00:00:00","dataset":"iris","name":"bar","operators":[],"position":0,"projectId":"cc07c929-85d5-4939-b59c-790e540f207f","target":"col4","updatedAt":"2000-01-01T00:00:00","uuid":"2b42d7b7-3a32-4678-b59e-91b2ad9e1fcf"}
```

### Operators

**Lists operators:** <br>
method: GET <br>
url: /projects/:project_id/experiments/:experiment_id/operators

```bash
curl -X GET \
  http://localhost:8080/projects/cc07c929-85d5-4939-b59c-790e540f207f/experiments/2b42d7b7-3a32-4678-b59e-91b2ad9e1fcf/operators
```

Expected Output:

```json
[{"componentId":"6814cdae-d88d-4c4d-bfb6-9ea6d6086dc4","createdAt":"2000-01-01T00:00:00","experimentId":"2b42d7b7-3a32-4678-b59e-91b2ad9e1fcf","position":0,"updatedAt":"2000-01-01T00:00:00","uuid":"e2b1870f-d699-4c7d-bcc4-5828728d1235"}]
```

**Creates an operator:** <br>
method: POST <br>
url: /projects/:project_id/experiments/:experiment_id/operators

```bash
curl -X POST \
  http://localhost:8080/projects/cc07c929-85d5-4939-b59c-790e540f207f/experiments/2b42d7b7-3a32-4678-b59e-91b2ad9e1fcf/operators \
  -d '{"componentId":"6814cdae-d88d-4c4d-bfb6-9ea6d6086dc4","position":0}'
```

Expected Output:

```json
{"componentId":"6814cdae-d88d-4c4d-bfb6-9ea6d6086dc4","createdAt":"2000-01-01T00:00:00","experimentId":"2b42d7b7-3a32-4678-b59e-91b2ad9e1fcf","position":0,"updatedAt":"2000-01-01T00:00:00","uuid":"e2b1870f-d699-4c7d-bcc4-5828728d1235"}
```

**Deletes an operator:** <br>
method: DELETE <br>
url: /projects/:project_id/experiments/:experiment_id/operators/:uuid

```bash
curl -X DELETE \
  http://localhost:8080/projects/cc07c929-85d5-4939-b59c-790e540f207f/experiments/2b42d7b7-3a32-4678-b59e-91b2ad9e1fcf/operators/6814cdae-d88d-4c4d-bfb6-9ea6d6086dc4
```

Expected Output:

```json
{"message":"Operator deleted"}
```

### Figures

**Lists figures:** <br>
method: GET <br>
url: /projects/:project_id/experiments/:experiment_id/operators/:operator_id/figures

```bash
curl -X GET \
  http://localhost:8080/projects/cc07c929-85d5-4939-b59c-790e540f207f/experiments/2b42d7b7-3a32-4678-b59e-91b2ad9e1fcf/operators/2b457c55-2e2c-485a-a1c3-db4492dace33/figures
```

Expected Output:

```json
["data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAMAAAAC6CAIAAAB3B9X3AAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsMAAA7DAcdvqGQAAAG6SURBVHhe7dIxAQAADMOg+TfdicgLGrhBIBCJQCQCkQhEIhCJQCQCkQhEIhCJQCQCkQhEIhCJQCQCkQhEIhCJQCQCkQhEIhCJQCQCkQhEIhCJQCQCkQhEIhCJQCQCkQhEIhCJQCQCkQhEIhCJQCQCkQhEIhCJQCQCkQhEIhCJQCQCkQhEIhCJQCQCkQhEIhCJQCQCkQhEIhCJQCQCkQhEIhCJQCQCkQhEIhCJQCQCkQhEIhCJQCQCkQhEIhCJQCQCkQhEIhCJQCQCkQhEIhCJQCQCkQhEIhCJQCQCkQhEIhCJQCQCkQhEIhCJQCQCkQhEIhCJQCQCkQhEIhCJQCQCkQhEIhCJQCQCkQhEIhCJQCQCkQhEIhCJQCQCkQhEIhCJQCQCkQhEIhCJQCQCkQhEIhCJQCQCkQhEIhCJQCQCkQhEIhCJQCQCkQhEIhCJQCQCkQhEIhCJQCQCkQhEIhCJQCQCkQhEIhCJQCQCkQhEIhCJQCQCkQhEIhCJQCQCkQhEIhCJQCQCkQhEIhCJQCQCkQhEIhCJQCQCkQhEIhCJQCQCkQhEIhCJQCQCkQhEIhCJQCQCkQhEIhDB9ho69eEGiUHfAAAAAElFTkSuQmCC"]
```
