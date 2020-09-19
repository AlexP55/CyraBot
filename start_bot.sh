#!/bin/sh
PID=$(/usr/bin/pgrep python3)
if [ "$PID" != "" ]
then
  echo "Bot is already running"
else
  mkdir -p log
  nohup python3 -u cyra.py >> ./log/`date +%s`.txt &
fi
