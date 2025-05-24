import os
import sys
import random
from datetime import datetime, timedelta
from flask import Flask
from models.models import db, Animal, FeedingLog, HealthRecord, Alert

# Create a Flask app context for database operations
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///farm_assistant.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

# Sample data
species_breeds = {
    'Cow': ['Holstein', 'Angus', 'Jersey', 'Hereford', 'Simmental'],
    'Pig': ['Yorkshire', 'Duroc', 'Hampshire', 'Berkshire', 'Landrace'],
    'Chicken': ['Leghorn', 'Rhode Island Red', 'Plymouth Rock', 'Orpington', 'Wyandotte'],
    'Sheep': ['Merino', 'Suffolk', 'Dorper', 'Romney', 'Corriedale'],
    'Goat': ['Boer', 'Alpine', 'Nubian', 'Saanen', 'Angora']
}

feed_types = {
    'Cow': ['Hay', 'Silage', 'Grain Mix', 'Pasture', 'Corn Silage'],
    'Pig': ['Corn Feed', 'Soybean Meal', 'Wheat Bran', 'Commercial Pellets', 'Kitchen Scraps'],
    'Chicken': ['Layer Feed', 'Scratch Grains', 'Crumbles', 'Mash', 'Pellets'],
    'Sheep': ['Hay', 'Pasture', 'Grain Mix', 'Alfalfa', 'Pellets'],
    'Goat': ['Hay', 'Brush', 'Grain Mix', 'Alfalfa', 'Mineral Blocks']
}

behaviors = ['Active', 'Normal', 'Lethargic', 'Not eating', 'Agitated', 'Distressed', 'Calm']

# Utility functions
def random_date(start_date, end_date):
    time_between = end_date - start_date
    days_between = time_between.days
    random_days = random.randrange(days_between)
    return start_date + timedelta(days=random_days)

def create_sample_feeding_logs(animal, num_logs=30, days_range=60):
    """Create sample feeding logs for an animal over the specified days range."""
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=days_range)
    
    # Create a set of dates for the logs (one per day on average)
    dates = set()
    while len(dates) < num_logs:
        date = random_date(start_date, end_date)
        dates.add(date)
    
    # Sort dates to ensure chronological order
    sorted_dates = sorted(list(dates))
    
    logs = []
    for date in sorted_dates:
        # Some animals will have a pattern of consistent feeding
        feed_type = random.choice(feed_types[animal.species])
        
        # Quantity varies by species
        if animal.species == 'Cow':
            quantity = round(random.uniform(15.0, 25.0), 1)
        elif animal.species == 'Pig':
            quantity = round(random.uniform(3.0, 8.0), 1)
        elif animal.species == 'Chicken':
            quantity = round(random.uniform(0.1, 0.3), 1)
        elif animal.species == 'Sheep':
            quantity = round(random.uniform(2.0, 5.0), 1)
        elif animal.species == 'Goat':
            quantity = round(random.uniform(2.0, 4.0), 1)
        else:
            quantity = round(random.uniform(1.0, 10.0), 1)
        
        # Create abnormal patterns for some animals (for anomaly detection testing)
        if animal.animal_tag_id == 'COW-002' and date > (end_date - timedelta(days=7)):
            # Sudden decrease in food intake for COW-002 in the last week
            quantity = round(quantity * 0.7, 1)
            notes = "Seems less interested in food"
        elif animal.animal_tag_id == 'PIG-001' and date > (end_date - timedelta(days=5)):
            # Change in feed type for PIG-001 in the last 5 days
            feed_type = "New Commercial Feed"
            notes = "Switched to new feed brand"
        else:
            notes = None
        
        log = FeedingLog(
            animal_id=animal.id,
            timestamp=date,
            feed_type=feed_type,
            quantity_kg=quantity,
            notes=notes
        )
        logs.append(log)
    
    return logs

def create_sample_health_records(animal, num_records=10, days_range=60):
    """Create sample health records for an animal over the specified days range."""
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=days_range)
    
    # Create a set of dates for the records
    dates = set()
    while len(dates) < num_records:
        date = random_date(start_date, end_date)
        dates.add(date)
    
    # Sort dates to ensure chronological order
    sorted_dates = sorted(list(dates))
    
    records = []
    
    # Initialize normal weight ranges based on species
    if animal.species == 'Cow':
        base_weight = random.uniform(450, 700)
        temp_range = (38.0, 39.2)
    elif animal.species == 'Pig':
        base_weight = random.uniform(80, 150)
        temp_range = (38.0, 39.0)
    elif animal.species == 'Chicken':
        base_weight = random.uniform(1.5, 3.5)
        temp_range = (40.5, 41.5)
    elif animal.species == 'Sheep':
        base_weight = random.uniform(45, 85)
        temp_range = (38.5, 39.5)
    elif animal.species == 'Goat':
        base_weight = random.uniform(35, 70)
        temp_range = (38.5, 39.5)
    else:
        base_weight = random.uniform(50, 200)
        temp_range = (38.0, 39.5)
    
    # Create health progression
    for i, date in enumerate(sorted_dates):
        # Weight increases slightly over time (unless there's a problem)
        if animal.animal_tag_id == 'COW-002' and date > (end_date - timedelta(days=10)):
            # Weight loss for COW-002 in the last 10 days
            weight = base_weight - (i * 5)
            behavior = 'Lethargic' if random.random() < 0.7 else 'Not eating'
            notes = "Appears to be losing weight despite regular feeding"
            temp = random.uniform(39.5, 40.2)  # Slightly elevated temperature
        elif animal.animal_tag_id == 'PIG-001' and date > (end_date - timedelta(days=7)):
            # Abnormal behavior for PIG-001 in the last week
            weight = base_weight + (i * 0.2)  # Minimal weight gain
            behavior = 'Agitated' if random.random() < 0.6 else 'Distressed'
            notes = "Showing unusual agitation, possibly due to feed change"
            temp = random.uniform(temp_range[0] - 0.2, temp_range[1] + 0.5)
        elif animal.animal_tag_id == 'CHICKEN-003' and date > (end_date - timedelta(days=5)):
            # Chicken with temp issues
            weight = base_weight - (i * 0.1)
            behavior = 'Lethargic'
            notes = "Not as active as usual, keeping to itself"
            temp = random.uniform(41.8, 42.5)  # Elevated temperature
        else:
            # Normal health progression
            weight_gain = i * (0.5 if animal.species == 'Chicken' else 2.0)
            weight = base_weight + weight_gain
            behavior = random.choice(behaviors)
            notes = None
            temp = random.uniform(temp_range[0], temp_range[1])
        
        # Some records may not have weight or temperature measurements
        if random.random() < 0.2:  # 20% chance of missing weight
            weight = None
        if random.random() < 0.3:  # 30% chance of missing temperature
            temp = None
            
        record = HealthRecord(
            animal_id=animal.id,
            timestamp=date,
            weight_kg=weight,
            temperature_celsius=temp,
            behavior_observation=behavior,
            notes=notes
        )
        records.append(record)
    
    return records

def create_sample_alerts(animals):
    """Create a few sample alerts."""
    alerts = []
    
    # Find the animal with ID COW-002 (which we've set up with abnormalities)
    cow_002 = next((a for a in animals if a.animal_tag_id == 'COW-002'), None)
    if cow_002:
        alerts.append(Alert(
            animal_id=cow_002.id,
            message="Weight loss detected: 5% decrease over the past week",
            severity="Medium",
            source="AI Anomaly Detection",
            acknowledged=False
        ))
        
        alerts.append(Alert(
            animal_id=cow_002.id,
            message="Decreased food intake: 30% reduction in the last 3 days",
            severity="High",
            source="AI Anomaly Detection",
            acknowledged=False
        ))
    
    # Find the animal with ID PIG-001
    pig_001 = next((a for a in animals if a.animal_tag_id == 'PIG-001'), None)
    if pig_001:
        alerts.append(Alert(
            animal_id=pig_001.id,
            message="Unusual behavior observed following feed change",
            severity="Low",
            source="AI Health Summary",
            acknowledged=False
        ))
    
    # General farm alert
    alerts.append(Alert(
        animal_id=None,
        message="Routine veterinary check scheduled for next week",
        severity="Low",
        source="Manual",
        acknowledged=False
    ))
    
    return alerts

def seed_database():
    """Seed the database with sample data."""
    # Create sample animals
    animals = [
        Animal(animal_tag_id='COW-001', species='Cow', breed='Holstein', 
               birth_date=datetime(2022, 3, 15).date(), notes="First calf born June 2023"),
        Animal(animal_tag_id='COW-002', species='Cow', breed='Jersey', 
               birth_date=datetime(2021, 8, 10).date(), notes="High milk producer"),
        Animal(animal_tag_id='COW-003', species='Cow', breed='Angus', 
               birth_date=datetime(2022, 5, 22).date(), notes=None),
        Animal(animal_tag_id='PIG-001', species='Pig', breed='Yorkshire', 
               birth_date=datetime(2023, 1, 5).date(), notes="Breeding sow"),
        Animal(animal_tag_id='PIG-002', species='Pig', breed='Duroc', 
               birth_date=datetime(2023, 2, 18).date(), notes=None),
        Animal(animal_tag_id='CHICKEN-001', species='Chicken', breed='Leghorn', 
               birth_date=datetime(2023, 4, 10).date(), notes="Egg layer"),
        Animal(animal_tag_id='CHICKEN-002', species='Chicken', breed='Rhode Island Red', 
               birth_date=datetime(2023, 4, 12).date(), notes="Egg layer"),
        Animal(animal_tag_id='CHICKEN-003', species='Chicken', breed='Plymouth Rock', 
               birth_date=datetime(2023, 3, 28).date(), notes="Broiler"),
        Animal(animal_tag_id='SHEEP-001', species='Sheep', breed='Merino', 
               birth_date=datetime(2022, 2, 14).date(), notes="Wool producer"),
        Animal(animal_tag_id='GOAT-001', species='Goat', breed='Boer', 
               birth_date=datetime(2022, 9, 5).date(), notes=None),
    ]
    
    # Add animals to session
    for animal in animals:
        db.session.add(animal)
    
    # Need to flush to get IDs assigned
    db.session.flush()
    
    # Create feeding logs and health records for each animal
    for animal in animals:
        # Create more logs for some animals, fewer for others
        num_feeding_logs = random.randint(20, 40)
        feeding_logs = create_sample_feeding_logs(animal, num_logs=num_feeding_logs)
        for log in feeding_logs:
            db.session.add(log)
        
        num_health_records = random.randint(5, 15)
        health_records = create_sample_health_records(animal, num_records=num_health_records)
        for record in health_records:
            db.session.add(record)
    
    # Create sample alerts
    alerts = create_sample_alerts(animals)
    for alert in alerts:
        db.session.add(alert)
    
    # Commit all changes
    db.session.commit()
    
    print(f"Database seeded with {len(animals)} animals, {num_feeding_logs * len(animals)} feeding logs, " +
          f"{num_health_records * len(animals)} health records, and {len(alerts)} alerts.")

def main():
    with app.app_context():
        # Create tables
        db.create_all()
        
        # Check if database is already populated
        animal_count = Animal.query.count()
        if animal_count > 0:
            print(f"Database already contains {animal_count} animals.")
            choice = input("Do you want to clear the database and re-seed it? (y/n): ")
            if choice.lower() == 'y':
                # Drop all tables and recreate
                db.drop_all()
                db.create_all()
                seed_database()
            else:
                print("Seeding canceled.")
        else:
            seed_database()

if __name__ == "__main__":
    main()