#!/bin/bash

export PYTHONUNBUFFERED=1

nohup python3 src/manage.py runserver localhost:8000 &