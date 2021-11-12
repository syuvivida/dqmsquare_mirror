#!/bin/bash

wdir=__PDQM__

service=$1
cd $wdir

if [ $service = "robber" ] ; then
  ./dqmsquare_cert.sh
  python3 dqmsquare_robber.py         
fi

if [ $service = "robber_oldruns" ] ; then
  python3 dqmsquare_robber_oldruns.py
fi

if [ $service = "parser" ] ; then
  python3 dqmsquare_parser.py         
fi

if [ $service = "server" ] ; then
  python3 dqmsquare_server.py
fi


 
