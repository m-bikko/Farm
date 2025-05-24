# Farm Assistant Deployment Instructions

This guide provides instructions for deploying the Farm Assistant application on a Google VM running Ubuntu 22.04 at http://35.228.230.53:5006/.

## Prerequisites

- Google VM instance with Ubuntu 22.04
- Root access to the VM

## Quick Deployment

For a quick deployment, follow these steps:

1. **Transfer project files to the VM**

   From your local machine:
   ```bash
   scp -r /Users/marbik/Desktop/claude\ projects/KIMEP\ hackathon/* username@35.228.230.53:~/farm-assistant/
   ```

2. **Connect to the VM and run the deployment script**

   ```bash
   ssh username@35.228.230.53
   cd ~/farm-assistant
   chmod +x deploy.sh
   sudo ./deploy.sh
   ```

   The script will:
   - Install Docker and Docker Compose if needed
   - Copy files to the appropriate location
   - Build and start the Docker containers
   - Offer to seed the database with sample data

3. **Access the application**

   Open a web browser and navigate to: http://35.228.230.53:5006/

## Manual Deployment Steps

If you prefer to deploy manually or if the script encounters issues, follow these steps:

### 1. Install Docker and Docker Compose

```bash
# Update system packages
sudo apt update
sudo apt upgrade -y

# Install required packages
sudo apt install -y apt-transport-https ca-certificates curl software-properties-common

# Add Docker repository
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg
echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

# Install Docker
sudo apt update
sudo apt install -y docker-ce docker-ce-cli containerd.io

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/download/v2.20.0/docker-compose-linux-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
```

### 2. Set Up the Project

```bash
# Create project directory
sudo mkdir -p /farm-assistant
sudo chown -R $(whoami):$(whoami) /farm-assistant

# Copy project files
cp -r ~/farm-assistant/* /farm-assistant/
cd /farm-assistant
```

### 3. Start the Application

```bash
# Build and start containers
sudo docker-compose up -d --build

# Seed the database (optional)
sudo docker exec -it $(sudo docker ps -qf "name=farm-assistant") python seed_db.py
```

## Managing the Application

### View Logs

```bash
cd /farm-assistant
sudo docker-compose logs -f
```

### Stop the Application

```bash
cd /farm-assistant
sudo docker-compose down
```

### Restart the Application

```bash
cd /farm-assistant
sudo docker-compose restart
```

### Update the Application

To update the application with new files:

```bash
# Copy new files to the VM
scp -r /path/to/updated/files/* username@35.228.230.53:~/updated-files/

# On the VM, update the application
sudo cp -r ~/updated-files/* /farm-assistant/
cd /farm-assistant
sudo docker-compose down
sudo docker-compose up -d --build
```

## Troubleshooting

### Check Container Status

```bash
sudo docker ps
```

### Check Container Logs

```bash
cd /farm-assistant
sudo docker-compose logs -f
```

### Access Container Shell

```bash
sudo docker exec -it $(sudo docker ps -qf "name=farm-assistant") bash
```

### Check if the Port is in Use

```bash
sudo lsof -i :5006
```

### Restart from Scratch

If you need to completely reset the application:

```bash
cd /farm-assistant
sudo docker-compose down
sudo rm -rf /farm-assistant/app/instance/*
sudo docker-compose up -d --build
```

## Security Notes

- The Google Generative AI API key is hardcoded in the docker-compose.yml file. In a production environment, you should use more secure methods for managing secrets.
- Consider setting up HTTPS for secure communication.
- Regularly update the application and dependencies for security patches.