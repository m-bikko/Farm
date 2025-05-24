#!/bin/bash

# Go to project directory
cd "$(dirname "$0")"

# Define the port number
PORT=5006

# Check if port is already in use and kill the process if it is
if lsof -i :$PORT > /dev/null; then
    echo "Port $PORT is already in use. Killing the process..."
    # Get PID of process using the port and kill it
    PID=$(lsof -t -i:$PORT)
    kill -9 $PID
    echo "Process $PID killed"
    sleep 1
fi

# Check if virtual environment exists, create if it doesn't
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install requirements
echo "Installing dependencies..."
pip install -r requirements.txt

# Set the API key environment variable if not already set
if [ -z "$GOOGLE_GENERATIVE_AI_API_KEY" ]; then
    echo "Setting up environment variables..."
    export GOOGLE_GENERATIVE_AI_API_KEY="AIzaSyA7zgkfPqewfQsGhQi7L8OYVxsiZuOguSU"
fi

# Go to app directory
cd app

# Make sure services directory exists
mkdir -p services

# Check if database exists, seed if it doesn't
if [ ! -f "farm_assistant.db" ]; then
    echo "Initializing database..."
    python seed_db.py
fi

# Run the application
echo "Starting Farm Assistant application..."
echo "Open http://localhost:$PORT in your browser"
python app.py