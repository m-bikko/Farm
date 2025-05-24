#!/bin/bash

# This script fixes the Farm Assistant deployment issue with gunicorn
# Run this on your Google VM to fix the deployment

# Colors for better readability
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}===== Farm Assistant Deployment Fix =====${NC}"

# Check if running as root
if [ "$EUID" -ne 0 ]; then
  echo -e "${YELLOW}Please run as root (use sudo)${NC}"
  exit 1
fi

# Go to the farm directory
cd /farm-assistant || cd ~/farm-assistant || cd ~/farm || cd /farm || cd ~/Farm || cd /Farm

# Stop any running containers
echo -e "${YELLOW}Stopping any running containers...${NC}"
docker-compose down

# Update the requirements.txt file
echo -e "${YELLOW}Updating requirements.txt with gunicorn...${NC}"
cat > requirements.txt << EOL
flask==2.3.3
flask-sqlalchemy==3.1.1
python-dotenv==1.0.0
google-generativeai==0.3.1
json5==0.9.14
gunicorn==21.2.0
werkzeug==2.3.7
EOL

# Update the Dockerfile
echo -e "${YELLOW}Updating Dockerfile to use python -m gunicorn...${NC}"
sed -i 's/CMD \["gunicorn"/CMD \["python", "-m", "gunicorn"/g' Dockerfile

# Build and start containers
echo -e "${YELLOW}Rebuilding and starting containers...${NC}"
docker-compose up -d --build

# Check if containers are running
sleep 5
if [ $(docker ps -q | wc -l) -ge 1 ]; then
  echo -e "${GREEN}Farm Assistant is now running at http://35.228.230.53:5006/${NC}"
  echo -e "${GREEN}Fix completed successfully!${NC}"
else
  echo -e "${YELLOW}Something went wrong. Checking logs...${NC}"
  docker-compose logs
fi