#!/usr/bin/env bash
set -e

echo "==========================================="
echo " Running Monorepo Linters (Frontend + Backend)"
echo "==========================================="

echo "[1/2] Checking Frontend (ESLint + TypeScript)..."
npm run lint --workspace=frontend
npm run type-check --workspace=frontend

echo "[2/2] Checking Backend (Ruff + Black + Mypy)..."
cd backend
ruff check .
black --check .
mypy .
cd ..

echo "Linting check complete!"
