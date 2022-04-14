FROM node:14-alpine

RUN apk update && apk add openssh && service sshd start

EXPOSE 22