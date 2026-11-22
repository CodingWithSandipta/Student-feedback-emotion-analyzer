#!/bin/bash
# Student Feedback Emotion Analyzer - Linux/macOS Startup Script

set -e

echo ""
echo "============================================================"
echo "  Student Feedback Emotion Analyzer - Project Startup"
echo "  AI-Based Bi-LSTM Emotion Classification System"
echo "============================================================"
echo ""

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$SCRIPT_DIR"
BACKEND_DIR="$PROJECT_DIR/backend"
FRONTEND_DIR="$PROJECT_DIR/frontend"

# Check Python
if ! command -v python3 &>/dev/null; then
    echo "[ERROR] Python 3 not found. Install from https://python.org"
    exit 1
fi

# Check Node.js
if ! command -v node &>/dev/null; then
    echo "[ERROR] Node.js not found. Install from https://nodejs.org"
    exit 1
fi

echo "[OK] Python 3 and Node.js found."
echo ""

# Setup virtual environment
if [ ! -d "$BACKEND_DIR/venv" ]; then
    echo "[INFO] Creating virtual environment..."
    python3 -m venv "$BACKEND_DIR/venv"
    echo "[OK] Virtual environment created."
fi

# Install backend requirements
echo "[INFO] Installing backend requirements..."
source "$BACKEND_DIR/venv/bin/activate"
pip install -r "$BACKEND_DIR/requirements.txt" -q
echo "[OK] Backend requirements installed."
echo ""

# Check model
if [ ! -f "$BACKEND_DIR/models/bilstm_emotion_model.keras" ]; then
    echo "============================================================"
    echo "  MODEL NOT FOUND"
    echo "============================================================"
    echo ""
    echo "  Train the model first:"
    echo "    cd $BACKEND_DIR"
    echo "    source venv/bin/activate"
    echo "    python train_model.py"
    echo ""
    echo "  Predictions will not work until training is complete."
    echo "  Continuing startup anyway..."
    echo ""
else
    echo "[OK] Model artifacts found."
fi

# Install frontend dependencies
if [ ! -d "$FRONTEND_DIR/node_modules" ]; then
    echo "[INFO] Installing frontend dependencies..."
    cd "$FRONTEND_DIR" && npm install --silent
    echo "[OK] Frontend dependencies installed."
fi

echo ""
echo "============================================================"
echo "  Starting Application"
echo "============================================================"
echo ""
echo "  Backend API  : http://localhost:5000"
echo "  Frontend App : http://localhost:5173"
echo ""

# Start backend
cd "$BACKEND_DIR"
source venv/bin/activate
python app.py &
BACKEND_PID=$!
echo "[OK] Backend started (PID: $BACKEND_PID)"

sleep 2

# Start frontend
cd "$FRONTEND_DIR"
npm run dev &
FRONTEND_PID=$!
echo "[OK] Frontend started (PID: $FRONTEND_PID)"

echo ""
echo "  Open: http://localhost:5173"
echo ""
echo "  Press Ctrl+C to stop both servers."

# Cleanup on exit
trap "echo 'Stopping...'; kill $BACKEND_PID $FRONTEND_PID 2>/dev/null; exit 0" INT TERM

wait
