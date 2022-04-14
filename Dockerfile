FROM jenkins/agent:latest

WORKDIR /opt/builds

RUN 'sudo apt update && sudo apt -y dist-upgrade && sudo apt install nodejs'

EXPOSE 22