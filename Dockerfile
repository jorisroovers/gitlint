# User-facing Dockerfile. For development, see Dockerfile.dev and ./run_tests.sh -h

# To lint your current working directory:
# docker run --ulimit nofile=1024 -v $(pwd):/repo jorisroovers/gitlint

# With arguments:
# docker --ulimit nofile=1024 run -v $(pwd):/repo jorisroovers/gitlint --debug --ignore T1

# NOTE: --ulimit is required to work around a limitation in Docker
# Details: https://github.com/jorisroovers/gitlint/issues/129

FROM python:3.11.0-alpine
ARG GITLINT_VERSION

RUN apk add git
RUN pip install gitlint==$GITLINT_VERSION

ENTRYPOINT ["gitlint", "--target", "/repo"]
