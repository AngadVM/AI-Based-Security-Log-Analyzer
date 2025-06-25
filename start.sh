#!/bin/bash

echo "Starting backend on http://localhost:8000"
source venv/bin/activate
uvicorn backend_api.main:app --reload &

echo "Starting frontend on http://localhost:5173"
cd frontend_dashboard
npm run dev

