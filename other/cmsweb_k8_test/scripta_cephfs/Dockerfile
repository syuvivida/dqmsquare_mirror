FROM cmssw/cmsweb:20210628
MAINTAINER P.~Mandrik petr.mandrik@cern.ch

# add environment

# pass env variable to the build
ARG CMSK8S
ENV CMSK8S=$CMSK8S
COPY script_A.py script_A.py
COPY run.sh run.sh
CMD ["run.sh"]

