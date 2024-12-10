#!/bin/bash

export PYTHONUNBUFFERED=1

nohup python3 manage.py runserver localhost:8000 &