FROM registry.cern.ch/cmsweb/cmsweb:20210914-stable
MAINTAINER P.~Mandrik petr.mandrik@cern.ch

RUN yum install -y firefox nano python3

COPY * dqmsquare_mirror
WORKDIR dqmsquare_mirror
RUN python3 -m pip install -r requirements
RUN ./dqmsquare_deploy.sh k8

RUN mkdir -p /cephfs/testbed/dqmsquare_mirror/

CMD ["/bin/bash"]

