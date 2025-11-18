#!/usr/bin/env bash
# run.sh - start TrueWater GUI in a venv
set -e


if [ -f env/bin/activate ]; then
source env/bin/activate
fi


python3 gui_app.py