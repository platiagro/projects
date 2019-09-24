FROM node:lts-alpine

RUN npm install -g knex && \
    apk add netcat-openbsd;

COPY wait-for.sh /opt/wait-for.sh
RUN ["chmod", "+x", "/opt/wait-for.sh"]