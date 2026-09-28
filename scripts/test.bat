@echo off
echo Running Backend Pytest Test Suite...
cd backend
call pytest -v
cd ..
