#!/usr/bin/env bash
set -e

echo "==================================================="
echo " AI Job Copilot - Local Environment Setup (Phase 1)"
echo "==================================================="

echo "[1/4] Copying environment configurations..."
[ ! -f .env ] && cp .env.example .env && echo "Created root .env"
[ ! -f backend/.env ] && cp backend/.env.example backend/.env && echo "Created backend/.env"
[ ! -f frontend/.env.local ] && cp frontend/.env.example frontend/.env.local && echo "Created frontend/.env.local"

echo ""
echo "[2/4] Setting up Python virtual environment..."
cd backend
if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo "Python venv created at backend/venv"
fi
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
pip install -r requirements-dev.txt
cd ..

echo ""
echo "[3/4] Installing Node dependencies..."
npm install

echo ""
echo "[4/4] Setup complete!"
echo "Run: docker compose up --build"
echo "Or run local servers: ./scripts/dev.sh"
echo "==================================================="
