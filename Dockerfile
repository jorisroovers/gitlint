# User-facing Dockerfile. For development, see Dockerfile.dev and ./run_tests.sh -h

# To lint your current working directory:
# docker run -v $(pwd):/repo jorisroovers/gitlint

# With arguments:
# docker run -v $(pwd):/repo jorisroovers/gitlint --debug --ignore T1

FROM python:3.8-alpine
ARG GITLINT_VERSION

RUN apk add git
RUN pip install gitlint==$GITLINT_VERSION

ENTRYPOINT ["gitlint", "--target", "/repo"]
