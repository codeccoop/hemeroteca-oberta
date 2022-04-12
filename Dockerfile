FROM node:16-alpine

WORKDIR /usr/src/app

RUN 'apk update && apk add openssh'
RUN 'servie ssh start'
