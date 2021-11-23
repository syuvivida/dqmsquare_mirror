#!/bin/bash

service=$1

sudo mkdir -p /cephfs/testbed/dqmsquare_mirror/tmp/
sudo mkdir -p /cephfs/testbed/dqmsquare_mirror/log/
chmod +rwx /cephfs/testbed/dqmsquare_mirror

if [ $service = "robber" ] ; then
  sudo ./dqmsquare_cert.sh
  python3 dqmsquare_robber.py
fi

if [ $service = "robber_oldruns" ] ; then
  sudo ./dqmsquare_cert.sh
  python3 dqmsquare_robber_oldruns.py
fi

if [ $service = "parser" ] ; then
  python3 dqmsquare_parser.py         
fi

if [ $service = "server" ] ; then
  python3 dqmsquare_server.py
fi



