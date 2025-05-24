# Root Deployment Instructions for Farm Assistant

This document provides simplified instructions for deploying the Farm Assistant application directly from the root directory on your Google Cloud VM instance.

## Prerequisites

- Google Cloud VM instance with Ubuntu 22.04
- External IP: http://35.228.230.53:5006/
- Google API key for the Gemini AI model
- Root or sudo access on the VM

## Deployment Steps

### 1. Connect to the VM Instance

Connect to your VM instance using SSH:

```bash
ssh username@35.228.230.53
```

Replace `username` with your VM username.

### 2. Transfer the Project Files

From your local machine, navigate to the project directory and run:

```bash
scp -r /Users/marbik/Desktop/claude\ projects/KIMEP\ hackathon/app/* username@35.228.230.53:~/farm-temp/
```

Replace `username` with your VM username. This will create a temporary directory to hold the files.

### 3. Run the Deployment Script

SSH into your VM and run the deployment script:

```bash
cd ~/farm-temp
chmod +x deploy-root.sh
sudo ./deploy-root.sh
```

This script will:
- Update the system
- Install Docker and Docker Compose if needed
- Create the necessary directories in the root filesystem
- Copy all project files to /farm-assistant
- Create an .env file if it doesn't exist
- Build and start the Docker containers
- Offer to seed the database with initial data

### 4. Configure Your API Keys

After running the deployment script, edit the .env file to add your Google API keys:

```bash
sudo nano /farm-assistant/.env
```

Update the API key values:

```
GOOGLE_API_KEY=your_actual_google_api_key
GOOGLE_GENERATIVE_AI_API_KEY=your_actual_google_generative_ai_api_key
```

Save and exit (Ctrl+X, then Y, then Enter).

### 5. Restart the Application

Restart the application to apply the API key changes:

```bash
cd /farm-assistant
sudo docker-compose down
sudo docker-compose up -d
```

### 6. Verify the Deployment

Open a web browser and navigate to:

```
http://35.228.230.53:5006/
```

You should see the Farm Assistant application running.

## Managing the Application

### View Container Logs

To view logs from your containers:

```bash
cd /farm-assistant
sudo docker-compose logs -f
```

### Stop the Application

To stop the running containers:

```bash
cd /farm-assistant
sudo docker-compose down
```

### Start the Application

To start the application:

```bash
cd /farm-assistant
sudo docker-compose up -d
```

### Update the Application

To update the application with new changes:

1. Transfer the updated files to the VM
2. Copy them to the /farm-assistant directory
3. Rebuild and restart the containers:

```bash
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

### Restart Containers

```bash
cd /farm-assistant
sudo docker-compose restart
```

### Full Reset

If you need to completely reset the application:

```bash
cd /farm-assistant
sudo docker-compose down
sudo rm -rf /data/instance/*
sudo docker-compose up -d --build
```

Note: This will delete all data in the database.