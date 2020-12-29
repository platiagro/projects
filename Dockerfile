FROM python:3.7-buster

LABEL maintainer="fabiol@cpqd.com.br"

# Stamps the commit SHA into the labels and ENV vars
ARG BRANCH="master"
ARG COMMIT=""
LABEL branch=${BRANCH}
LABEL commit=${COMMIT}
ENV COMMIT=${COMMIT}
ENV BRANCH=${BRANCH}

RUN apt-get update && \
    apt-get install wget unzip jq && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

COPY ./requirements.txt /app/requirements.txt

RUN pip install -r /app/requirements.txt

COPY ./projects /app/projects
COPY ./setup.py /app/setup.py

RUN pip install /app/

RUN wget https://github.com/platiagro/tasks/archive/main.zip && \
    unzip main.zip && \
    mv tasks-main/tasks /tasks && \
    rm -rf main.zip tasks-main/

COPY ./tasks_config.json /tasks/config.json
COPY ./artifacts_config.json /artifacts/config.json

RUN jq -c ".[]" /artifacts/config.json | while read a; do \
    URL=$(echo $a | jq -r .url); \
    FILE_PATH=$(echo $a | jq -r .file_name); \
    wget -O "$FILE_PATH" "$URL"; \
    done

WORKDIR /app/

EXPOSE 8080

ENTRYPOINT ["python", "-m", "projects.api.main"]
CMD ["--init-db", "--tasks-config", "/tasks/config.json", "--artifacts-config", "/artifacts/config.json"]
