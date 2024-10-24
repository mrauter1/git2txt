#!/bin/bash

SCRIPT_DIR=$(dirname "$(readlink -f "$0" || realpath "$0")")
python3 "$SCRIPT_DIR/install.py"
