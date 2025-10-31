#!/bin/bash

# Run script for Medical AI Assistant

echo "🏥 Medical AI Assistant - Starting Services"
echo "============================================"

# Check if .env file exists
if [ ! -f .env ]; then
    echo "⚠️  Warning: .env file not found"
    echo "Please create a .env file with your GROQ_API_KEY"
    exit 1
fi

# Check if patient database exists
if [ ! -f patient_database.db ]; then
    echo "📊 Setting up patient database..."
    python setup.py
fi

# Start FastAPI backend in background
echo "🚀 Starting FastAPI backend on port 8000..."
python api.py &
API_PID=$!

# Wait for API to start
sleep 3

# Start Streamlit frontend
echo "🌐 Starting Streamlit frontend on port 8501..."
streamlit run app.py

# Cleanup on exit
trap "kill $API_PID" EXIT

