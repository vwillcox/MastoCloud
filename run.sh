#!/usr/bin/env bash
set -e

VENV_DIR=".venv"

# Create venv if it doesn't exist
if [ ! -d "$VENV_DIR" ]; then
    echo "Creating virtual environment..."
    python3 -m venv "$VENV_DIR"
fi

# Activate and install dependencies
source "$VENV_DIR/bin/activate"
pip install --quiet -r requirements.txt

# Launch web interface or CLI depending on args
if [ "$1" = "--web" ]; then
    python web.py
else
    python -m mastocloud.main "$@"
fi

# Deactivate venv
deactivate
