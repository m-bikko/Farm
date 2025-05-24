#!/bin/bash

# Set up environment variables if .env file exists
if [ -f .env ]; then
  export $(cat .env | xargs)
fi

# Create instance directory if it doesn't exist
mkdir -p instance

# Build and start the containers
docker-compose up -d --build

# Seed the database if needed
echo "Do you want to seed the database with initial data? (y/n)"
read -r answer
if [[ "$answer" =~ ^[Yy]$ ]]; then
  docker exec -it $(docker ps -qf "name=farm-assistant") python seed_db.py
  echo "Database seeded successfully!"
fi

echo "Farm Assistant is now running at http://35.228.230.53:5006/"
echo "To view logs: docker-compose logs -f"
echo "To stop the application: docker-compose down"