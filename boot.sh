#!/bin/sh
mkdir -p log
python3 -u cyra.py >> ./log/`date +%s`.txt
