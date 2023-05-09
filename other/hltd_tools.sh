#!/bin/bash
# P.S.~Mandrik, IHEP, https://github.com/pmandrik

me=`basename "$0"`
echo $me $1

# via dqmpro
if [ $1 == "restart_playback" ] ; then
  for host in "dqmrubu-c2a06-03-01.cms"  "dqmfu-c2b01-45-01.cms"  "dqmfu-c2b02-45-01.cms"; do
    echo $host
    ssh $host sudo -i /sbin/service hltd restart
  done
fi

if [ $1 == "restart_production" ] ; then
  for host in "dqmrubu-c2a06-01-01.cms"  "dqmfu-c2b03-45-01.cms"  "dqmfu-c2b04-45-01.cms"; do
    echo $host
    ssh $host sudo -i /sbin/service hltd restart
  done;
fi
