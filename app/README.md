# Farm Assistant - AI-powered Livestock Feeding & Monitoring Assistant

A web application that helps farm managers track feeding routines, animal health data, and uses AI to generate feeding suggestions, detect anomalies, and provide health summaries.

## Features

- Animal management and tracking
- Feeding logs and health records
- AI-powered feeding plan generation
- Anomaly detection in health records
- Health summary generation
- Responsive, animated UI

## Tech Stack

- **Backend**: Flask, SQLAlchemy, SQLite
- **Frontend**: HTML, CSS, JavaScript
- **AI Integration**: Google Generative AI (Gemini)
- **Deployment**: Docker, Docker Compose, Nginx

## Quick Start (Local Development)

1. Clone this repository
2. Create a `.env` file with your Google API key (see `.env.example`)
3. Run the following commands:

```bash
# Install dependencies
pip install -r requirements.txt

# Initialize the database and add sample data
python seed_db.py

# Start the application
python app.py
```

The application will be available at http://localhost:5000

## Docker Deployment

1. Create a `.env` file with your Google API key (see `.env.example`)
2. Run the deployment script:

```bash
./run-docker.sh
```

The application will be available at http://35.228.230.53:5006/

## Detailed Deployment Instructions

For detailed instructions on deploying to a Google Cloud VM instance, see [deploy-instructions.md](deploy-instructions.md).

## Project Structure

```
farm-assistant/
├── app.py                # Main Flask application
├── models/               # Database models
│   ├── __init__.py
│   └── models.py         # SQLAlchemy models
├── services/             # Service modules
│   ├── __init__.py
│   └── gemini_service.py # Google Gemini API integration
├── static/               # Static assets
│   ├── css/
│   │   └── style.css     # Main stylesheet
│   └── js/
│       └── main.js       # JavaScript functionality
├── templates/            # Jinja2 HTML templates
│   ├── animal_detail.html
│   ├── animal_form.html
│   ├── animals.html
│   ├── anomalies.html
│   ├── base.html
│   ├── dashboard.html
│   ├── feeding_plan.html
│   └── health_summary.html
├── seed_db.py            # Database seeding script
├── Dockerfile            # Docker configuration
├── docker-compose.yml    # Docker Compose configuration
├── nginx/                # Nginx configuration
│   └── farm-assistant.conf
├── requirements.txt      # Python dependencies
└── .env.example          # Example environment variables
```

## License

This project is licensed under the MIT License.