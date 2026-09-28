#!/usr/bin/env bash
set -e
echo "Running Backend Pytest Test Suite..."
cd backend
pytest -v
cd ..
