#!/bin/bash

echo "🚀 Starting AI-Based Security Log Analyzer Setup..."

# Step 1: Set up Python virtual environment
if [ ! -d "venv" ]; then
  echo "📦 Creating Python virtual environment..."
  python3 -m venv venv
fi

echo "🟢 Activating virtual environment..."
source venv/bin/activate

# Step 2: Install backend dependencies
echo "📥 Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Step 3: Start backend
echo "🚀 Starting FastAPI backend at http://localhost:8000..."
cd backend_api
uvicorn main:app --reload &
cd ..

# Step 4: Install frontend and run
echo "📦 Installing frontend dependencies..."
cd frontend_dashboard
npm install

echo "🎯 Starting React frontend at http://localhost:5173..."
npm run dev
