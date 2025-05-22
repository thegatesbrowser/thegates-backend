#!/bin/bash
# run: 'source setup_venv.sh' or ''. setup_venv.sh'

VENV_DIR=venv

if [ ! -d "$VENV_DIR" ]; then
    echo "Creating virutal environment $VENV_DIR"
    python -m venv $VENV_DIR
fi

source "$VENV_DIR/bin/activate"
pip install django plotly requests mixpanel meilisearch ua_parser