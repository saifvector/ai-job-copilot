@echo off
echo ===========================================
echo  Running Monorepo Linters (Frontend + Backend)
echo ===========================================

echo [1/2] Checking Frontend (ESLint + TypeScript)...
call npm run lint --workspace=frontend
call npm run type-check --workspace=frontend

echo [2/2] Checking Backend (Ruff + Black + Mypy)...
cd backend
call ruff check .
call black --check .
call mypy .
cd ..

echo Linting check complete!
