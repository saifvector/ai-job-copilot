@echo off
echo ===================================================
echo  AI Job Copilot - Local Environment Setup (Phase 1)
echo ===================================================

echo [1/4] Setting up root and backend environment files...
if not exist ".env" (
    copy ".env.example" ".env"
    echo Created root .env
)
if not exist "backend\.env" (
    copy "backend\.env.example" "backend\.env"
    echo Created backend\.env
)
if not exist "frontend\.env.local" (
    copy "frontend\.env.example" "frontend\.env.local"
    echo Created frontend\.env.local
)

echo.
echo [2/4] Setting up Python virtual environment for Backend...
cd backend
if not exist "venv" (
    python -m venv venv
    echo Python venv created at backend\venv
)
call venv\Scripts\activate.bat
python -m pip install --upgrade pip
pip install -r requirements.txt
pip install -r requirements-dev.txt
cd ..

echo.
echo [3/4] Installing Node dependencies for Frontend & Database...
call npm install

echo.
echo [4/4] Setup complete!
echo To launch with Docker: docker compose up --build
echo To launch locally: scripts\dev.bat
echo ===================================================
