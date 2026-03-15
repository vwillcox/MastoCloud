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

# Run the wordcloud generator, passing all arguments through
python -m mastocloud.main "$@"

# Deactivate venv
deactivate
