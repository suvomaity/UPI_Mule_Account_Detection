#!/bin/bash

# Start backend
echo "🚀 Starting backend on port 8000..."
cd backend
pip install -q -r requirements.txt
python -m uvicorn app:app --host 0.0.0.0 --port 8000 &
BACKEND_PID=$!
cd ..

# Wait for backend to start
sleep 3

# Start frontend
echo "🚀 Starting frontend on port 5000..."
cd frontend
npm install -q
PORT=5000 npm run dev &
FRONTEND_PID=$!
cd ..

# Keep services running
wait
