# Note: development using the local Dockerfile is still work-in-progress
# Getting started: http://jorisroovers.github.io/gitlint/contributing/
ARG python_version_dotted

FROM python:${python_version_dotted}-stretch

RUN apt-get update
# software-properties-common contains 'add-apt-repository'
RUN apt-get install -y git silversearcher-ag jq curl

ADD . /gitlint
WORKDIR /gitlint

RUN pip install --ignore-requires-python -r requirements.txt
RUN pip install --ignore-requires-python -r test-requirements.txt

CMD ["/bin/bash"]
