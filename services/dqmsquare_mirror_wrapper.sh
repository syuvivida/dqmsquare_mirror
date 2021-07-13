#!/bin/bash

wdir=__PDQM__

service=$1
cd $wdir

if [ $service = "robber" ] ; then
  ./dqmsquare_robber         
fi

if [ $service = "robber_oldruns" ] ; then
  ./dqmsquare_robber_oldruns
fi

if [ $service = "parser" ] ; then
  ./dqmsquare_parser         
fi

if [ $service = "server" ] ; then
  python dqmsquare_server.py
fi


 
