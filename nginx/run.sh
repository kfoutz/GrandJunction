#!/usr/bin/env bash
set -e

export FLASK_APP=manage.py
export FLASK_ENV=development

flask db upgrade || true
flask run --host=0.0.0.0 --port=5000    