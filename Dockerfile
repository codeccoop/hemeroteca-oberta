FROM jenkins/agent:latest

WORKDIR /opt/builds

RUN 'apt update && apt -y dist-upgrade && apt install nodejs'

EXPOSE 22