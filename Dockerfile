FROM node:16-alpine

WORKDIR /opt/builds

RUN 'apk update && apk add openssh'
RUN 'servie ssh start'
RUN 'apk add openjdk11'

EXPOSE 22