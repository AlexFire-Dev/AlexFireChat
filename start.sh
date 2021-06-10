#!/usr/bin/env bash

python3 manage.py collectstatic --clear
python3 manage.py migrate

daphne AlexFireChat.asgi:application