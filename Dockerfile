FROM jenkins/agent:latest

WORKDIR /opt/builds

RUN apt update && apt install -y nodejs

EXPOSE 22