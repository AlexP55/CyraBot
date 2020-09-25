#!/bin/sh
if [ -z "$1" ] ; then
  echo "No Args"
  #No input argument passed -> kill all base_bot instances
  sudo pkill -9 -f cyra.py
  #wait for all processes to end
  PID=$(/usr/bin/pgrep -f cyra.py)
  while [ "$PID" != "" ];do
    sleep 1
    sudo pkill -9 -f cyra.py
    PID=$(/usr/bin/pgrep -f cyra.py)
  done
else
  #kill only the process with the given pid (arg 1 passed to script)
  sudo kill -9 $1
fi
