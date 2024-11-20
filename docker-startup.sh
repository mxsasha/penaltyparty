#!/bin/sh

./manage.py migrate
gunicorn --bind :8000 --workers 2 penaltyparty.wsgi:application
