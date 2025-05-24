#!/bin/bash

# Simple one-command setup script for Google VM
# Run this script on your VM to set up Farm Assistant

# Make sure script is run as root
if [ "$EUID" -ne 0 ]; then
  echo "Please run as root (use sudo)"
  exit 1
fi

# Set color variables
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}Starting Farm Assistant setup on Google VM...${NC}"

# Update system
echo -e "${YELLOW}Updating system packages...${NC}"
apt update && apt upgrade -y

# Install Docker
echo -e "${YELLOW}Installing Docker...${NC}"
apt install -y apt-transport-https ca-certificates curl software-properties-common
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg
echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | tee /etc/apt/sources.list.d/docker.list > /dev/null
apt update
apt install -y docker-ce docker-ce-cli containerd.io

# Install Docker Compose
echo -e "${YELLOW}Installing Docker Compose...${NC}"
curl -L "https://github.com/docker/compose/releases/download/v2.20.0/docker-compose-linux-$(uname -m)" -o /usr/local/bin/docker-compose
chmod +x /usr/local/bin/docker-compose

# Create directory structure
echo -e "${YELLOW}Creating directory structure...${NC}"
mkdir -p /farm-assistant
mkdir -p /data/instance

# Copy project files (assumes they're in the current directory)
echo -e "${YELLOW}Copying project files...${NC}"
cp -r . /farm-assistant/
cd /farm-assistant

# Set up environment file
echo -e "${YELLOW}Setting up environment file...${NC}"
if [ ! -f .env ]; then
  cat > .env << EOL
GOOGLE_API_KEY=your_google_api_key_here
GOOGLE_GENERATIVE_AI_API_KEY=your_google_generative_ai_api_key_here
EOL
  echo -e "${RED}Important: Edit .env file with your actual API keys before continuing${NC}"
  echo -e "${YELLOW}Press Enter when ready to continue...${NC}"
  read
fi

# Build and start containers
echo -e "${YELLOW}Building and starting containers...${NC}"
docker-compose up -d --build

# Check if everything is running
if [ $(docker ps -q | wc -l) -ge 2 ]; then
  echo -e "${GREEN}Farm Assistant is now running at http://35.228.230.53:5006/${NC}"
  echo -e "${GREEN}Setup completed successfully!${NC}"
  
  # Ask about seeding the database
  echo -e "${YELLOW}Do you want to seed the database with sample data? (y/n)${NC}"
  read -r answer
  if [[ "$answer" =~ ^[Yy]$ ]]; then
    docker exec -it $(docker ps -qf "name=farm-assistant") python seed_db.py
    echo -e "${GREEN}Database seeded successfully!${NC}"
  fi
else
  echo -e "${RED}Something went wrong. Check logs with: docker-compose logs${NC}"
fi

echo -e "${YELLOW}-------------------${NC}"
echo -e "${YELLOW}Useful commands:${NC}"
echo -e "${GREEN}View logs:${NC} docker-compose logs -f"
echo -e "${GREEN}Stop application:${NC} docker-compose down"
echo -e "${GREEN}Restart application:${NC} docker-compose restart"
echo -e "${GREEN}Access container shell:${NC} docker exec -it \$(docker ps -qf \"name=farm-assistant\") bash"