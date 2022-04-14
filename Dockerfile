FROM jenkins/agent:latest-jdk11

WORKDIR /home/jenkins

RUN apt update && apt install -y nodejs

EXPOSE 22