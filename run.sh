#!/bin/bash

# Move to the root directory of the project
cd "$(dirname "$0")"
uvicorn app.main:app --reload

