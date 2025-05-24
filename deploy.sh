#!/bin/bash

# Farm Assistant Deployment Script for Google VM
# For use with Ubuntu 22.04 at http://35.228.230.53:5006/

# Colors for better readability
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}===== Farm Assistant Deployment Script =====${NC}"
echo -e "${GREEN}This script will set up the Farm Assistant application on your VM.${NC}"
echo -e "${GREEN}Target: http://35.228.230.53:5006/${NC}"
echo ""

# Check if running as root
if [ "$EUID" -ne 0 ]; then
  echo -e "${YELLOW}Please run as root (use sudo)${NC}"
  exit 1
fi

# Update system packages
echo -e "${YELLOW}Updating system packages...${NC}"
apt update && apt upgrade -y

# Install Docker if not already installed
if ! command -v docker &> /dev/null; then
  echo -e "${YELLOW}Installing Docker...${NC}"
  apt install -y apt-transport-https ca-certificates curl software-properties-common
  curl -fsSL https://download.docker.com/linux/ubuntu/gpg | gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg
  echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | tee /etc/apt/sources.list.d/docker.list > /dev/null
  apt update
  apt install -y docker-ce docker-ce-cli containerd.io
  systemctl enable docker
  systemctl start docker
  echo -e "${GREEN}Docker installed successfully!${NC}"
else
  echo -e "${GREEN}Docker is already installed.${NC}"
fi

# Install Docker Compose if not already installed
if ! command -v docker-compose &> /dev/null; then
  echo -e "${YELLOW}Installing Docker Compose...${NC}"
  curl -L "https://github.com/docker/compose/releases/download/v2.20.0/docker-compose-linux-$(uname -m)" -o /usr/local/bin/docker-compose
  chmod +x /usr/local/bin/docker-compose
  echo -e "${GREEN}Docker Compose installed successfully!${NC}"
else
  echo -e "${GREEN}Docker Compose is already installed.${NC}"
fi

# Create farm-assistant directory
mkdir -p /farm-assistant
cd /farm-assistant

# Check if this is a first-time setup or an update
if [ -f "docker-compose.yml" ]; then
  echo -e "${YELLOW}Updating existing installation...${NC}"
  # Stop running containers
  docker-compose down
else
  echo -e "${YELLOW}Setting up new installation...${NC}"
fi

# Copy all files from the current directory to /farm-assistant
echo -e "${YELLOW}Copying application files...${NC}"
cp -r * /farm-assistant/
chown -R $(logname):$(logname) /farm-assistant

# Build and start containers
echo -e "${YELLOW}Building and starting containers...${NC}"
cd /farm-assistant
docker-compose up -d --build

# Check if containers are running
if [ $(docker ps -q | wc -l) -ge 1 ]; then
  echo -e "${GREEN}Farm Assistant is now running at http://35.228.230.53:5006/${NC}"
  
  # Ask if user wants to seed the database
  echo -e "${YELLOW}Do you want to seed the database with sample data? (y/n)${NC}"
  read -r answer
  if [[ "$answer" =~ ^[Yy]$ ]]; then
    echo -e "${YELLOW}Seeding database...${NC}"
    docker exec -it $(docker ps -qf "name=farm-assistant") python seed_db.py
    echo -e "${GREEN}Database seeded successfully!${NC}"
  fi
  
  echo -e "${GREEN}Deployment completed successfully!${NC}"
else
  echo -e "${YELLOW}Something went wrong. Checking logs...${NC}"
  docker-compose logs
fi

echo ""
echo -e "${GREEN}===== Useful Commands =====${NC}"
echo "View logs: docker-compose logs -f"
echo "Stop application: docker-compose down"
echo "Restart application: docker-compose restart"
echo "Access shell: docker exec -it \$(docker ps -qf \"name=farm-assistant\") bash"