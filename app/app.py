import os
import json
from datetime import datetime, timedelta
from flask import Flask, request, jsonify, render_template, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv
from models.models import db, Animal, FeedingLog, HealthRecord, Alert
from services.gemini_service import gemini_service

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///farm_assistant.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = os.urandom(24)

db.init_app(app)

# Helper function to parse date strings
def parse_date(date_str):
    try:
        return datetime.strptime(date_str, '%Y-%m-%d').date()
    except ValueError:
        return None

# Routes for web interface
@app.route('/')
def dashboard():
    active_alerts = Alert.query.filter_by(acknowledged=False).order_by(Alert.timestamp.desc()).all()
    return render_template('dashboard.html', alerts=active_alerts, Animal=Animal)

@app.route('/animals')
def animals_list():
    animals = Animal.query.all()
    return render_template('animals.html', animals=animals)

@app.route('/animals/new', methods=['GET', 'POST'])
def new_animal():
    if request.method == 'POST':
        try:
            animal = Animal(
                animal_tag_id=request.form['animal_tag_id'],
                species=request.form['species'],
                breed=request.form['breed'],
                birth_date=parse_date(request.form['birth_date']),
                notes=request.form['notes']
            )
            db.session.add(animal)
            db.session.commit()
            flash('Animal added successfully!', 'success')
            return redirect(url_for('animals_list'))
        except Exception as e:
            flash(f'Error adding animal: {str(e)}', 'danger')
            return render_template('animal_form.html')
    
    return render_template('animal_form.html')

@app.route('/animals/<animal_tag_id>')
def animal_detail(animal_tag_id):
    animal = Animal.query.filter_by(animal_tag_id=animal_tag_id).first_or_404()
    feeding_logs = FeedingLog.query.filter_by(animal_id=animal.id).order_by(FeedingLog.timestamp.desc()).all()
    health_records = HealthRecord.query.filter_by(animal_id=animal.id).order_by(HealthRecord.timestamp.desc()).all()
    
    today = datetime.utcnow().date()
    
    return render_template('animal_detail.html', 
                           animal=animal, 
                           feeding_logs=feeding_logs, 
                           health_records=health_records,
                           today=today)

@app.route('/animals/<animal_tag_id>/add_feeding', methods=['POST'])
def add_feeding(animal_tag_id):
    animal = Animal.query.filter_by(animal_tag_id=animal_tag_id).first_or_404()
    
    try:
        feeding_log = FeedingLog(
            animal_id=animal.id,
            feed_type=request.form['feed_type'],
            quantity_kg=float(request.form['quantity_kg']),
            notes=request.form['notes']
        )
        db.session.add(feeding_log)
        db.session.commit()
        flash('Feeding log added successfully!', 'success')
    except Exception as e:
        flash(f'Error adding feeding log: {str(e)}', 'danger')
    
    return redirect(url_for('animal_detail', animal_tag_id=animal_tag_id))

@app.route('/animals/<animal_tag_id>/add_health', methods=['POST'])
def add_health(animal_tag_id):
    animal = Animal.query.filter_by(animal_tag_id=animal_tag_id).first_or_404()
    
    try:
        health_record = HealthRecord(
            animal_id=animal.id,
            weight_kg=float(request.form['weight_kg']) if request.form.get('weight_kg') else None,
            temperature_celsius=float(request.form['temperature_celsius']) if request.form.get('temperature_celsius') else None,
            behavior_observation=request.form['behavior_observation'],
            notes=request.form['notes']
        )
        db.session.add(health_record)
        db.session.commit()
        flash('Health record added successfully!', 'success')
    except Exception as e:
        flash(f'Error adding health record: {str(e)}', 'danger')
    
    return redirect(url_for('animal_detail', animal_tag_id=animal_tag_id))

@app.route('/alerts/<int:alert_id>/acknowledge', methods=['POST'])
def acknowledge_alert(alert_id):
    alert = Alert.query.get_or_404(alert_id)
    alert.acknowledged = True
    db.session.commit()
    flash('Alert acknowledged!', 'success')
    return redirect(url_for('dashboard'))

# AI-related routes
@app.route('/animals/<animal_tag_id>/feeding_plan')
def generate_feeding_plan(animal_tag_id):
    animal = Animal.query.filter_by(animal_tag_id=animal_tag_id).first_or_404()
    
    # Get recent feeding history (last 7 days)
    seven_days_ago = datetime.utcnow() - timedelta(days=7)
    feeding_logs = FeedingLog.query.filter(
        FeedingLog.animal_id == animal.id,
        FeedingLog.timestamp >= seven_days_ago
    ).order_by(FeedingLog.timestamp).all()
    
    # Prepare data for AI prompt
    feeding_history = []
    for log in feeding_logs:
        feeding_history.append(f"- {log.timestamp.strftime('%Y-%m-%d')}: {log.feed_type}, {log.quantity_kg} kg")
    
    # Get most recent health record for weight
    latest_health = HealthRecord.query.filter_by(animal_id=animal.id).order_by(HealthRecord.timestamp.desc()).first()
    weight_kg = latest_health.weight_kg if latest_health and latest_health.weight_kg else "Unknown"
    
    # Calculate age
    if animal.birth_date:
        today = datetime.utcnow().date()
        age_days = (today - animal.birth_date).days
        age_years = age_days / 365
        age = f"{age_years:.1f} years ({age_days} days)"
    else:
        age = "Unknown"
    
    # Available feed types (from all recorded feedings for simplicity)
    available_feeds = db.session.query(FeedingLog.feed_type).distinct().all()
    available_feed_types = [feed[0] for feed in available_feeds]
    
    # Use the Gemini service to generate the feeding plan
    result = gemini_service.generate_feeding_plan(
        animal_tag_id=animal.animal_tag_id,
        species=animal.species,
        breed=animal.breed,
        age=age,
        weight_kg=weight_kg,
        feeding_history=feeding_history,
        available_feed_types=available_feed_types
    )
    
    # Check if we got a valid response or error
    if "error" in result:
        return render_template('feeding_plan.html', animal=animal, raw_response=result.get("raw_response", str(result)))
    else:
        return render_template('feeding_plan.html', animal=animal, plan=result)

@app.route('/animals/<animal_tag_id>/detect_anomalies')
def detect_anomalies(animal_tag_id):
    animal = Animal.query.filter_by(animal_tag_id=animal_tag_id).first_or_404()
    
    # Get recent data (last 14 days)
    fourteen_days_ago = datetime.utcnow() - timedelta(days=14)
    
    feeding_logs = FeedingLog.query.filter(
        FeedingLog.animal_id == animal.id,
        FeedingLog.timestamp >= fourteen_days_ago
    ).order_by(FeedingLog.timestamp).all()
    
    health_records = HealthRecord.query.filter(
        HealthRecord.animal_id == animal.id,
        HealthRecord.timestamp >= fourteen_days_ago
    ).order_by(HealthRecord.timestamp).all()
    
    # Prepare data for AI prompt
    feeding_history = []
    for log in feeding_logs:
        feeding_history.append(f"- {log.timestamp.strftime('%Y-%m-%d')}: {log.feed_type}, {log.quantity_kg} kg, Notes: {log.notes or 'None'}")
    
    health_history = []
    for record in health_records:
        health_history.append(f"- {record.timestamp.strftime('%Y-%m-%d')}: Weight {record.weight_kg or 'N/A'} kg, Temp {record.temperature_celsius or 'N/A'} C, Behavior: {record.behavior_observation}, Notes: {record.notes or 'None'}")
    
    # Calculate age
    if animal.birth_date:
        today = datetime.utcnow().date()
        age_days = (today - animal.birth_date).days
        age_years = age_days / 365
        age = f"{age_years:.1f} years ({age_days} days)"
    else:
        age = "Unknown"
    
    # Use the Gemini service to detect anomalies
    result = gemini_service.detect_anomalies(
        animal_tag_id=animal.animal_tag_id,
        species=animal.species,
        breed=animal.breed,
        age=age,
        feeding_history=feeding_history,
        health_history=health_history
    )
    
    # Check if we got a valid response or error
    if "error" in result:
        return render_template('anomalies.html', animal=animal, raw_response=result.get("raw_response", str(result)))
    else:
        # If anomalies detected, create alerts
        if result.get('anomalies_detected') and len(result['anomalies_detected']) > 0:
            for anomaly in result['anomalies_detected']:
                alert = Alert(
                    animal_id=animal.id,
                    message=f"{anomaly['description']} Potential cause: {anomaly['potential_cause']}",
                    severity=anomaly['severity'],
                    source="AI Anomaly Detection"
                )
                db.session.add(alert)
            db.session.commit()
            flash('Anomalies detected! Alerts have been created.', 'warning')
            
        return render_template('anomalies.html', animal=animal, anomalies=result)

@app.route('/animals/<animal_tag_id>/health_summary')
def health_summary(animal_tag_id):
    animal = Animal.query.filter_by(animal_tag_id=animal_tag_id).first_or_404()
    
    # Get all feeding logs and health records
    feeding_logs = FeedingLog.query.filter_by(animal_id=animal.id).order_by(FeedingLog.timestamp).all()
    health_records = HealthRecord.query.filter_by(animal_id=animal.id).order_by(HealthRecord.timestamp).all()
    
    # Prepare data for AI prompt
    feeding_history = []
    for log in feeding_logs:
        feeding_history.append(f"- {log.timestamp.strftime('%Y-%m-%d')}: {log.feed_type}, {log.quantity_kg} kg, Notes: {log.notes or 'None'}")
    
    health_history = []
    for record in health_records:
        health_history.append(f"- {record.timestamp.strftime('%Y-%m-%d')}: Weight {record.weight_kg or 'N/A'} kg, Temp {record.temperature_celsius or 'N/A'} C, Behavior: {record.behavior_observation}, Notes: {record.notes or 'None'}")
    
    # Calculate age
    if animal.birth_date:
        today = datetime.utcnow().date()
        age_days = (today - animal.birth_date).days
        age_years = age_days / 365
        age = f"{age_years:.1f} years ({age_days} days)"
    else:
        age = "Unknown"
    
    # Find earliest and latest dates for summary period
    earliest_date = None
    latest_date = datetime.utcnow().date()
    
    if feeding_logs or health_records:
        dates = []
        if feeding_logs:
            dates.extend([log.timestamp.date() for log in feeding_logs])
        if health_records:
            dates.extend([record.timestamp.date() for record in health_records])
        
        if dates:
            earliest_date = min(dates)
    
    # Use the Gemini service to generate health summary
    result = gemini_service.generate_health_summary(
        animal_tag_id=animal.animal_tag_id,
        species=animal.species,
        breed=animal.breed,
        age=age,
        feeding_history=feeding_history,
        health_history=health_history,
        summary_period_start=earliest_date.isoformat() if earliest_date else 'N/A',
        summary_period_end=latest_date.isoformat()
    )
    
    # Check if we got a valid response or error
    if "error" in result:
        return render_template('health_summary.html', animal=animal, raw_response=result.get("raw_response", str(result)))
    else:
        return render_template('health_summary.html', animal=animal, summary=result)

# API Endpoints
@app.route('/api/animals', methods=['GET'])
def api_get_animals():
    animals = Animal.query.all()
    return jsonify([animal.to_dict() for animal in animals])

@app.route('/api/animals', methods=['POST'])
def api_add_animal():
    data = request.json
    
    try:
        animal = Animal(
            animal_tag_id=data['animal_tag_id'],
            species=data['species'],
            breed=data.get('breed'),
            birth_date=parse_date(data['birth_date']),
            notes=data.get('notes')
        )
        db.session.add(animal)
        db.session.commit()
        return jsonify(animal.to_dict()), 201
    except KeyError as e:
        return jsonify({'error': f'Missing required field: {str(e)}'}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/animals/<animal_tag_id>', methods=['GET'])
def api_get_animal(animal_tag_id):
    animal = Animal.query.filter_by(animal_tag_id=animal_tag_id).first()
    if not animal:
        return jsonify({'error': 'Animal not found'}), 404
    return jsonify(animal.to_dict())

@app.route('/api/animals/<animal_tag_id>', methods=['PUT'])
def api_update_animal(animal_tag_id):
    animal = Animal.query.filter_by(animal_tag_id=animal_tag_id).first()
    if not animal:
        return jsonify({'error': 'Animal not found'}), 404
    
    data = request.json
    
    if 'animal_tag_id' in data:
        animal.animal_tag_id = data['animal_tag_id']
    if 'species' in data:
        animal.species = data['species']
    if 'breed' in data:
        animal.breed = data['breed']
    if 'birth_date' in data:
        animal.birth_date = parse_date(data['birth_date'])
    if 'notes' in data:
        animal.notes = data['notes']
    
    db.session.commit()
    return jsonify(animal.to_dict())

@app.route('/api/animals/<animal_tag_id>', methods=['DELETE'])
def api_delete_animal(animal_tag_id):
    animal = Animal.query.filter_by(animal_tag_id=animal_tag_id).first()
    if not animal:
        return jsonify({'error': 'Animal not found'}), 404
    
    db.session.delete(animal)
    db.session.commit()
    return jsonify({'message': f'Animal {animal_tag_id} deleted successfully'})

@app.route('/api/animals/<animal_tag_id>/feeding_logs', methods=['GET'])
def api_get_feeding_logs(animal_tag_id):
    animal = Animal.query.filter_by(animal_tag_id=animal_tag_id).first()
    if not animal:
        return jsonify({'error': 'Animal not found'}), 404
    
    logs = FeedingLog.query.filter_by(animal_id=animal.id).all()
    return jsonify([log.to_dict() for log in logs])

@app.route('/api/animals/<animal_tag_id>/feeding_logs', methods=['POST'])
def api_add_feeding_log(animal_tag_id):
    animal = Animal.query.filter_by(animal_tag_id=animal_tag_id).first()
    if not animal:
        return jsonify({'error': 'Animal not found'}), 404
    
    data = request.json
    
    try:
        feeding_log = FeedingLog(
            animal_id=animal.id,
            feed_type=data['feed_type'],
            quantity_kg=float(data['quantity_kg']),
            notes=data.get('notes')
        )
        db.session.add(feeding_log)
        db.session.commit()
        return jsonify(feeding_log.to_dict()), 201
    except KeyError as e:
        return jsonify({'error': f'Missing required field: {str(e)}'}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/animals/<animal_tag_id>/health_records', methods=['GET'])
def api_get_health_records(animal_tag_id):
    animal = Animal.query.filter_by(animal_tag_id=animal_tag_id).first()
    if not animal:
        return jsonify({'error': 'Animal not found'}), 404
    
    records = HealthRecord.query.filter_by(animal_id=animal.id).all()
    return jsonify([record.to_dict() for record in records])

@app.route('/api/animals/<animal_tag_id>/health_records', methods=['POST'])
def api_add_health_record(animal_tag_id):
    animal = Animal.query.filter_by(animal_tag_id=animal_tag_id).first()
    if not animal:
        return jsonify({'error': 'Animal not found'}), 404
    
    data = request.json
    
    try:
        health_record = HealthRecord(
            animal_id=animal.id,
            weight_kg=float(data['weight_kg']) if 'weight_kg' in data else None,
            temperature_celsius=float(data['temperature_celsius']) if 'temperature_celsius' in data else None,
            behavior_observation=data['behavior_observation'],
            notes=data.get('notes')
        )
        db.session.add(health_record)
        db.session.commit()
        return jsonify(health_record.to_dict()), 201
    except KeyError as e:
        return jsonify({'error': f'Missing required field: {str(e)}'}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/alerts', methods=['GET'])
def api_get_alerts():
    active_only = request.args.get('active_only', 'true').lower() == 'true'
    
    if active_only:
        alerts = Alert.query.filter_by(acknowledged=False).all()
    else:
        alerts = Alert.query.all()
    
    return jsonify([alert.to_dict() for alert in alerts])

@app.route('/api/alerts/<int:alert_id>/acknowledge', methods=['POST'])
def api_acknowledge_alert(alert_id):
    alert = Alert.query.get(alert_id)
    if not alert:
        return jsonify({'error': 'Alert not found'}), 404
    
    alert.acknowledged = True
    db.session.commit()
    return jsonify({'message': f'Alert {alert_id} acknowledged successfully'})

@app.route('/api/ai/generate_feeding_plan/<animal_tag_id>', methods=['POST'])
def api_generate_feeding_plan(animal_tag_id):
    animal = Animal.query.filter_by(animal_tag_id=animal_tag_id).first()
    if not animal:
        return jsonify({'error': 'Animal not found'}), 404
    
    # Similar logic as the web route
    seven_days_ago = datetime.utcnow() - timedelta(days=7)
    feeding_logs = FeedingLog.query.filter(
        FeedingLog.animal_id == animal.id,
        FeedingLog.timestamp >= seven_days_ago
    ).order_by(FeedingLog.timestamp).all()
    
    feeding_history = []
    for log in feeding_logs:
        feeding_history.append(f"- {log.timestamp.strftime('%Y-%m-%d')}: {log.feed_type}, {log.quantity_kg} kg")
    
    latest_health = HealthRecord.query.filter_by(animal_id=animal.id).order_by(HealthRecord.timestamp.desc()).first()
    weight_kg = latest_health.weight_kg if latest_health and latest_health.weight_kg else "Unknown"
    
    if animal.birth_date:
        today = datetime.utcnow().date()
        age_days = (today - animal.birth_date).days
        age_years = age_days / 365
        age = f"{age_years:.1f} years ({age_days} days)"
    else:
        age = "Unknown"
    
    available_feeds = db.session.query(FeedingLog.feed_type).distinct().all()
    available_feed_types = [feed[0] for feed in available_feeds]
    
    # Use the Gemini service to generate the feeding plan
    result = gemini_service.generate_feeding_plan(
        animal_tag_id=animal.animal_tag_id,
        species=animal.species,
        breed=animal.breed,
        age=age,
        weight_kg=weight_kg,
        feeding_history=feeding_history,
        available_feed_types=available_feed_types
    )
    
    # Check if we got a valid response or error
    if "error" in result and "raw_response" in result:
        return jsonify({'error': 'Failed to parse AI response', 'raw_response': result["raw_response"]}), 500
    elif "error" in result:
        return jsonify(result), 500
    else:
        return jsonify(result)

@app.route('/api/ai/detect_anomalies/<animal_tag_id>', methods=['POST'])
def api_detect_anomalies(animal_tag_id):
    animal = Animal.query.filter_by(animal_tag_id=animal_tag_id).first()
    if not animal:
        return jsonify({'error': 'Animal not found'}), 404
    
    # Similar logic as the web route
    fourteen_days_ago = datetime.utcnow() - timedelta(days=14)
    
    feeding_logs = FeedingLog.query.filter(
        FeedingLog.animal_id == animal.id,
        FeedingLog.timestamp >= fourteen_days_ago
    ).order_by(FeedingLog.timestamp).all()
    
    health_records = HealthRecord.query.filter(
        HealthRecord.animal_id == animal.id,
        HealthRecord.timestamp >= fourteen_days_ago
    ).order_by(HealthRecord.timestamp).all()
    
    feeding_history = []
    for log in feeding_logs:
        feeding_history.append(f"- {log.timestamp.strftime('%Y-%m-%d')}: {log.feed_type}, {log.quantity_kg} kg, Notes: {log.notes or 'None'}")
    
    health_history = []
    for record in health_records:
        health_history.append(f"- {record.timestamp.strftime('%Y-%m-%d')}: Weight {record.weight_kg or 'N/A'} kg, Temp {record.temperature_celsius or 'N/A'} C, Behavior: {record.behavior_observation}, Notes: {record.notes or 'None'}")
    
    if animal.birth_date:
        today = datetime.utcnow().date()
        age_days = (today - animal.birth_date).days
        age_years = age_days / 365
        age = f"{age_years:.1f} years ({age_days} days)"
    else:
        age = "Unknown"
    
    # Use the Gemini service to detect anomalies
    result = gemini_service.detect_anomalies(
        animal_tag_id=animal.animal_tag_id,
        species=animal.species,
        breed=animal.breed,
        age=age,
        feeding_history=feeding_history,
        health_history=health_history
    )
    
    # Check if we got a valid response or error
    if "error" in result and "raw_response" in result:
        return jsonify({'error': 'Failed to parse AI response', 'raw_response': result["raw_response"]}), 500
    elif "error" in result:
        return jsonify(result), 500
    else:
        # If anomalies detected, create alerts
        if result.get('anomalies_detected') and len(result['anomalies_detected']) > 0:
            for anomaly in result['anomalies_detected']:
                alert = Alert(
                    animal_id=animal.id,
                    message=f"{anomaly['description']} Potential cause: {anomaly['potential_cause']}",
                    severity=anomaly['severity'],
                    source="AI Anomaly Detection"
                )
                db.session.add(alert)
            db.session.commit()
            
        return jsonify(result)

@app.route('/api/ai/health_summary/<animal_tag_id>', methods=['GET'])
def api_health_summary(animal_tag_id):
    animal = Animal.query.filter_by(animal_tag_id=animal_tag_id).first()
    if not animal:
        return jsonify({'error': 'Animal not found'}), 404
    
    # Similar logic as the web route
    feeding_logs = FeedingLog.query.filter_by(animal_id=animal.id).order_by(FeedingLog.timestamp).all()
    health_records = HealthRecord.query.filter_by(animal_id=animal.id).order_by(HealthRecord.timestamp).all()
    
    feeding_history = []
    for log in feeding_logs:
        feeding_history.append(f"- {log.timestamp.strftime('%Y-%m-%d')}: {log.feed_type}, {log.quantity_kg} kg, Notes: {log.notes or 'None'}")
    
    health_history = []
    for record in health_records:
        health_history.append(f"- {record.timestamp.strftime('%Y-%m-%d')}: Weight {record.weight_kg or 'N/A'} kg, Temp {record.temperature_celsius or 'N/A'} C, Behavior: {record.behavior_observation}, Notes: {record.notes or 'None'}")
    
    if animal.birth_date:
        today = datetime.utcnow().date()
        age_days = (today - animal.birth_date).days
        age_years = age_days / 365
        age = f"{age_years:.1f} years ({age_days} days)"
    else:
        age = "Unknown"
    
    earliest_date = None
    latest_date = datetime.utcnow().date()
    
    if feeding_logs or health_records:
        dates = []
        if feeding_logs:
            dates.extend([log.timestamp.date() for log in feeding_logs])
        if health_records:
            dates.extend([record.timestamp.date() for record in health_records])
        
        if dates:
            earliest_date = min(dates)
    
    # Use the Gemini service to generate health summary
    result = gemini_service.generate_health_summary(
        animal_tag_id=animal.animal_tag_id,
        species=animal.species,
        breed=animal.breed,
        age=age,
        feeding_history=feeding_history,
        health_history=health_history,
        summary_period_start=earliest_date.isoformat() if earliest_date else 'N/A',
        summary_period_end=latest_date.isoformat()
    )
    
    # Check if we got a valid response or error
    if "error" in result and "raw_response" in result:
        return jsonify({'error': 'Failed to parse AI response', 'raw_response': result["raw_response"]}), 500
    elif "error" in result:
        return jsonify(result), 500
    else:
        return jsonify(result)

# Database initialization
with app.app_context():
    db.create_all()

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=False, host='0.0.0.0', port=5006)