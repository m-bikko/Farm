# AI-Powered Livestock Feeding & Monitoring Assistant

A Minimum Viable Product (MVP) for a web application that assists farmers in optimizing livestock care. The application tracks feeding routines, animal health data, and uses AI prompts to generate feeding suggestions, detect anomalies, and provide health summaries.

## Technologies Used

- **Backend**: Python with Flask
- **Database**: SQLite with SQLAlchemy ORM
- **Frontend**: HTML, CSS, and vanilla JavaScript
- **AI Integration**: Google Generative AI (Gemini)

## Features

- Register and manage livestock animals
- Record feeding logs and health data
- AI-powered tools:
  - Generate optimized feeding plans
  - Detect anomalies in health and feeding patterns
  - Create comprehensive health summaries
- Alert system for health and feeding issues

## Setup Instructions

### 1. Clone the repository

```bash
git clone <repository-url>
cd <repository-directory>
```

### 2. Set up a virtual environment (recommended)

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Set up the Google API Key

You need to set the `GOOGLE_API_KEY` environment variable with your Google Generative AI API key:

On Linux/macOS:
```bash
export GOOGLE_API_KEY="your_api_key_here"
```

On Windows:
```bash
set GOOGLE_API_KEY=your_api_key_here
```

Alternatively, you can create a `.env` file in the project root with the following content:
```
GOOGLE_API_KEY=your_api_key_here
```

### 5. Initialize the database and seed with sample data

```bash
cd app
python seed_db.py
```

### 6. Run the application

```bash
python app.py
```

The application will be available at http://127.0.0.1:5000/

## API Endpoints

### Animals

- `GET /api/animals`: List all animals
- `POST /api/animals`: Add a new animal
- `GET /api/animals/<animal_tag_id>`: Get details of a specific animal
- `PUT /api/animals/<animal_tag_id>`: Update animal details
- `DELETE /api/animals/<animal_tag_id>`: Delete an animal

### Feeding Logs

- `GET /api/animals/<animal_tag_id>/feeding_logs`: List feeding logs for an animal
- `POST /api/animals/<animal_tag_id>/feeding_logs`: Add a feeding log for an animal

### Health Records

- `GET /api/animals/<animal_tag_id>/health_records`: List health records for an animal
- `POST /api/animals/<animal_tag_id>/health_records`: Add a health record for an animal

### Alerts

- `GET /api/alerts`: List all active (non-acknowledged) alerts
- `POST /api/alerts/<alert_id>/acknowledge`: Mark an alert as acknowledged

### AI Interaction

- `POST /api/ai/generate_feeding_plan/<animal_tag_id>`: Generate a feeding plan
- `POST /api/ai/detect_anomalies/<animal_tag_id>`: Detect health or feeding anomalies
- `GET /api/ai/health_summary/<animal_tag_id>`: Generate a health summary

## Project Structure

```
app/
├── app.py              # Main Flask application
├── models/
│   └── models.py       # SQLAlchemy data models
├── static/
│   ├── css/
│   │   └── style.css   # CSS styles
│   └── js/
│       └── main.js     # Client-side JavaScript
├── templates/          # Jinja2 HTML templates
│   ├── base.html
│   ├── dashboard.html
│   ├── animals.html
│   └── ...
└── seed_db.py          # Database seeding script
```

## Data Models

- **Animal**: Basic information about livestock animals
- **FeedingLog**: Records of animal feeding events
- **HealthRecord**: Animal health measurements and observations
- **Alert**: System notifications about potential issues

## Future Improvements

- Mobile responsiveness for field use
- Image/video analysis for visual health checks
- Integration with IoT sensors for automated data collection
- More sophisticated anomaly detection algorithms
- User roles and permissions system
- Email or SMS notifications for critical alerts