#!/bin/sh
mkdir -p log
output=./log/`date +%s`.txt
python3 -u cyra.py > $output 2>&1
