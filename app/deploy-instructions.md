# Deployment Instructions for Farm Assistant

This document provides detailed instructions on how to deploy the Farm Assistant application on a Google Cloud VM instance running Ubuntu 22.04.

## Prerequisites

- Google Cloud VM instance with Ubuntu 22.04
- External IP: http://35.228.230.53:5006/
- Google API key for the Gemini AI model

## Deployment Steps

### 1. Connect to the VM Instance

Connect to your VM instance using SSH:

```bash
ssh username@35.228.230.53
```

Replace `username` with your VM username.

### 2. Update the System

Update the package lists and upgrade the installed packages:

```bash
sudo apt update
sudo apt upgrade -y
```

### 3. Install Docker and Docker Compose

Install Docker:

```bash
# Install required packages
sudo apt install -y apt-transport-https ca-certificates curl software-properties-common

# Add Docker's official GPG key
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg

# Add Docker repository
echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

# Update package list and install Docker
sudo apt update
sudo apt install -y docker-ce docker-ce-cli containerd.io

# Add your user to the docker group to avoid using sudo
sudo usermod -aG docker $USER
```

Install Docker Compose:

```bash
# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/download/v2.20.0/docker-compose-linux-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
```

Verify installations:

```bash
# Verify Docker installation
docker --version

# Verify Docker Compose installation
docker-compose --version
```

**Note**: After adding your user to the docker group, you might need to log out and log back in for the changes to take effect.

### 4. Create a Project Directory

Create a directory for the project:

```bash
mkdir -p ~/farm-assistant
cd ~/farm-assistant
```

### 5. Transfer the Project Files

#### Option 1: Transfer from your local machine using SCP

From your local machine, navigate to the project directory and run:

```bash
scp -r /Users/marbik/Desktop/claude\ projects/KIMEP\ hackathon/app/* username@35.228.230.53:~/farm-assistant/
```

Replace `username` with your VM username.

#### Option 2: Clone from Git repository (if available)

If you've pushed the project to a Git repository, you can clone it directly on the VM:

```bash
git clone https://your-git-repo-url.git .
```

### 6. Configure the Environment Variables

Create a .env file with your Google API key:

```bash
cd ~/farm-assistant
cp .env.example .env
nano .env  # or use any other text editor like vim
```

Update the API key values in the .env file:

```
GOOGLE_API_KEY=your_actual_google_api_key
GOOGLE_GENERATIVE_AI_API_KEY=your_actual_google_generative_ai_api_key
```

### 7. Build and Start the Docker Containers

Run Docker Compose to build and start the application:

```bash
cd ~/farm-assistant
docker-compose up -d --build
```

The `-d` flag runs the containers in detached mode (in the background).

### 8. Initialize the Database (if needed)

If you need to seed the database with initial data, you can access the container and run the seed script:

```bash
# Access the running container
docker exec -it farm-assistant_farm-assistant_1 bash

# Inside the container, run the seed script
python seed_db.py

# Exit the container
exit
```

### 9. Configure Firewall Rules (if needed)

If your VM has a firewall enabled, make sure port 5006 is allowed:

```bash
sudo ufw allow 5006/tcp
sudo ufw status
```

### 10. Verify the Deployment

Open a web browser and navigate to:

```
http://35.228.230.53:5006/
```

You should see the Farm Assistant application running.

## Maintenance and Monitoring

### View Container Logs

To view logs from your containers:

```bash
docker-compose logs -f
```

### Stop the Application

To stop the running containers:

```bash
cd ~/farm-assistant
docker-compose down
```

### Update the Application

To update the application with new changes:

1. Transfer the updated files to the VM
2. Rebuild and restart the containers:

```bash
cd ~/farm-assistant
docker-compose down
docker-compose up -d --build
```

### Persistent Data

The database is stored in a Docker volume mapped to the `./instance` directory, so your data will persist even if you rebuild the containers.

## Troubleshooting

### Check Container Status

```bash
docker ps
```

### Check Container Logs

```bash
docker-compose logs -f
```

### Access Container Shell

```bash
docker exec -it farm-assistant_farm-assistant_1 bash
```

### Check Network Configuration

```bash
docker network ls
docker network inspect farm-assistant_default
```

### Restart Containers

```bash
docker-compose restart
```

### Full Reset

If you need to completely reset the application:

```bash
docker-compose down
docker volume prune  # This will remove all unused volumes, including the database
docker-compose up -d --build
```

Note: This will delete all data in the database.

## Security Considerations

1. Secure your API keys and never expose them publicly
2. Set up SSL/TLS for HTTPS access (using Nginx or a similar reverse proxy)
3. Configure proper firewall rules to restrict access as needed
4. Regularly update your application and dependencies