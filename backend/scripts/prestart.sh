#! /usr/bin/env bash

set -e
set -x

echo "Prestart: skipping complex initialization as backend1 handles it internally."
# alembic upgrade head # Enable this if you add migrations to backend1
