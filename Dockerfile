FROM python:3.6-buster

RUN apt-get update && \
    apt-get install wget unzip && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

COPY ./requirements.txt /app/requirements.txt

RUN pip install -r /app/requirements.txt

COPY ./projects /app/projects
COPY ./setup.py /app/setup.py

RUN pip install /app/

RUN wget https://github.com/platiagro/tasks/archive/main.zip && \
    unzip main.zip && \
    mv tasks-main/tasks /samples && \
    mv tasks-main/config.json /samples && \
    rm -rf main.zip tasks-main/

WORKDIR /app/

EXPOSE 8080

ENTRYPOINT ["python", "-m", "projects.api.main"]
CMD ["--init-db", "--samples-config", "/samples/config.json"]