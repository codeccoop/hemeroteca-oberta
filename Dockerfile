FROM node:14-alpine

WORKDIR /home/jenkins

RUN apt update && apt install -y nodejs

EXPOSE 22