#!/bin/bash

service=$1

sudo mkdir -p /cephfs/testbed/dqmsquare_mirror/tmp/
sudo mkdir -p /cephfs/testbed/dqmsquare_mirror/log/
sudo find /cephfs/testbed/dqmsquare_mirror -type d -exec chmod 777 {} \;

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



