#!/bin/sh
exec gunicorn -b :80 --access-logfile - --error-logfile - permapol:app
