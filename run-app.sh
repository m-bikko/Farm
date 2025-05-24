#!/bin/bash

# Simple run script for Flask application directly (without Docker)
# Use this if Docker deployment is problematic

# Colors for better readability
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}===== Farm Assistant Direct Run Script =====${NC}"

# Install required packages if needed
if ! command -v pip3 &> /dev/null; then
  echo -e "${YELLOW}Installing pip3...${NC}"
  sudo apt update
  sudo apt install -y python3-pip
fi

# Go to app directory
cd "$(dirname "$0")/app" || exit

# Install dependencies
echo -e "${YELLOW}Installing dependencies...${NC}"
pip3 install -r ../requirements.txt

# Set API key environment variable
export GOOGLE_GENERATIVE_AI_API_KEY=AIzaSyA7zgkfPqewfQsGhQi7L8OYVxsiZuOguSU

# Run the application
echo -e "${GREEN}Starting Farm Assistant on port 5006...${NC}"
echo -e "${GREEN}Access at: http://35.228.230.53:5006/${NC}"
python3 -m flask run --host=0.0.0.0 --port=5006