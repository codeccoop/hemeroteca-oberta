FROM node:14-alpine

RUN apk update && apk add openssh

EXPOSE 22