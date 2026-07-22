#!/usr/bin/env bash
set -euo pipefail

# Update pip and install dependencies (Render also installs requirements automatically,
# but running here ensures the environment is ready during build hook)
python -m pip install --upgrade pip
pip install -r requirements.txt

# Run migrations and collect static files
python manage.py migrate --noinput
python manage.py collectstatic --noinput
