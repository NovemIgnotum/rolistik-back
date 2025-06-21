#!/bin/bash
export DATABASE_URL="mongodb://myuser:mypassword@localhost:27017/servitor-dev"
export PYTHONPATH=$(pwd)
pytest