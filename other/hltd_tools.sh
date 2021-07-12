#!/bin/bash
# P.S.~Mandrik, IHEP, https://github.com/pmandrik

me=`basename "$0"`
echo $me $1

# via dqmpro
if [ $1 == "restart_playback" ] ; then
  for host in "bu-c2f11-09-01.cms"  "fu-c2f11-11-01.cms"  "fu-c2f11-11-02.cms"  "fu-c2f11-11-03.cms"  "fu-c2f11-11-04.cms"; do
    echo $host
    ssh $host sudo -i /sbin/service hltd restart
  done
fi

if [ $1 == "restart_production" ] ; then
  for host in "bu-c2f11-09-01.cms"  "fu-c2f11-11-01.cms"  "fu-c2f11-11-02.cms"  "fu-c2f11-11-03.cms"  "fu-c2f11-11-04.cms"; do
    echo $host
    ssh $host sudo -i /sbin/service hltd restart
  done;
fi
