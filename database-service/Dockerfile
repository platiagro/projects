FROM mysql:5.7

RUN	mkdir /usr/sql
RUN	chmod 644 /usr/sql

COPY ./db.sql /docker-entrypoint-initdb.d/