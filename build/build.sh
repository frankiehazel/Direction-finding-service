#!/bin/bash

# Exit in case of error
set -e

# Install dependencies from requirements.txt
pip install -r requirements.txt

chmod +x build.sh