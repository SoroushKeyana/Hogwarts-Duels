#!/usr/bin/env bash
set -o errexit

# install dependencies (Render will usually run pip based on requirements.txt; keep this to be safe)
pip install -r requirements.txt

# collect static files (no interactive prompts)
python manage.py collectstatic --no-input

# apply migrations
python manage.py migrate
