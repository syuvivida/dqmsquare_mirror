FROM python:2-alpine
MAINTAINER P.~Mandrik petr.mandrik@cern.ch

# add environment

# pass env variable to the build
ARG CMSK8S
ENV CMSK8S=$CMSK8S
COPY script_A.py script_A.py
CMD ["python", "script_A.py"]

