FROM registry.cern.ch/cmsweb/cmsweb:20210914-stable
MAINTAINER P.~Mandrik petr.mandrik@cern.ch

# add environment

# pass env variable to the build
ARG CMSK8S
ENV CMSK8S=$CMSK8S
COPY script_A.py script_A.py
COPY run.sh run.sh

RUN mkdir -p /cephfs/testbed/confdb-logs

CMD ["run.sh"]

