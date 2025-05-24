#!/bin/bash

# Update system packages
echo "Updating system packages..."
sudo apt update
sudo apt upgrade -y

# Install required packages
echo "Installing required packages..."
sudo apt install -y apt-transport-https ca-certificates curl software-properties-common

# Install Docker if not already installed
if ! command -v docker &> /dev/null; then
  echo "Installing Docker..."
  curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg
  echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
  sudo apt update
  sudo apt install -y docker-ce docker-ce-cli containerd.io
  sudo systemctl enable docker
  sudo systemctl start docker
  sudo usermod -aG docker $USER
  echo "Docker installed successfully!"
else
  echo "Docker is already installed."
fi

# Install Docker Compose if not already installed
if ! command -v docker-compose &> /dev/null; then
  echo "Installing Docker Compose..."
  sudo curl -L "https://github.com/docker/compose/releases/download/v2.20.0/docker-compose-linux-$(uname -m)" -o /usr/local/bin/docker-compose
  sudo chmod +x /usr/local/bin/docker-compose
  echo "Docker Compose installed successfully!"
else
  echo "Docker Compose is already installed."
fi

# Create necessary directories
echo "Creating necessary directories..."
sudo mkdir -p /farm-assistant
sudo mkdir -p /data/instance
sudo chown -R $USER:$USER /farm-assistant
sudo chown -R $USER:$USER /data

# Create .env file if it doesn't exist
if [ ! -f /farm-assistant/.env ]; then
  echo "Creating .env file..."
  cat > /farm-assistant/.env << EOL
GOOGLE_API_KEY=your_google_api_key_here
GOOGLE_GENERATIVE_AI_API_KEY=your_google_generative_ai_api_key_here
EOL
  echo "Please edit /farm-assistant/.env and add your Google API keys"
fi

# Copy all project files to root directory
echo "Copying project files to /farm-assistant..."
cd "$(dirname "$0")"
sudo cp -r ./* /farm-assistant/
sudo chown -R $USER:$USER /farm-assistant

# Build and start the Docker containers
echo "Building and starting Docker containers..."
cd /farm-assistant
sudo docker-compose up -d --build

# Seed the database if needed
echo "Do you want to seed the database with initial data? (y/n)"
read -r answer
if [[ "$answer" =~ ^[Yy]$ ]]; then
  sudo docker exec -it $(sudo docker ps -qf "name=farm-assistant") python seed_db.py
  echo "Database seeded successfully!"
fi

echo "Farm Assistant is now running at http://35.228.230.53:5006/"
echo "To view logs: sudo docker-compose logs -f"
echo "To stop the application: sudo docker-compose down"

echo "Setup complete! You may need to log out and log back in for Docker to work without sudo."