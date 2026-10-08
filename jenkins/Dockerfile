# Jenkins with Python 3, the Docker CLI and the pipeline plugins pre-installed,
# so the candidate can focus on the Jenkinsfile.
# FROM jenkins/jenkins:lts-jdk17

# USER root
# RUN apt-get update \
#  && apt-get install -y --no-install-recommends python3 python3-venv docker.io curl \
#  && rm -rf /var/lib/apt/lists/*

# USER jenkins
# RUN jenkins-plugin-cli --plugins \
#     workflow-aggregator \
#     git \
#     junit \
#     pipeline-stage-view \
#     docker-workflow

#----------------------------------------------------------------------------------------------#
    # Update from 1st test

FROM docker:cli AS docker-cli

FROM jenkins/jenkins:lts-jdk17

USER root

COPY --from=docker-cli /usr/local/bin/docker /usr/local/bin/docker

RUN apt-get update \
 && apt-get install -y --no-install-recommends \
    python3 \
    python3-pip \
    python3-venv \
    curl \
 && rm -rf /var/lib/apt/lists/*

RUN pip3 install --break-system-packages flake8 pytest

RUN docker --version

USER jenkins

RUN jenkins-plugin-cli --plugins \
    workflow-aggregator \
    git \
    junit \
    pipeline-stage-view \
    docker-workflow