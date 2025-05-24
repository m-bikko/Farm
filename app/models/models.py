from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class Animal(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    animal_tag_id = db.Column(db.String(20), unique=True, nullable=False)
    species = db.Column(db.String(50), nullable=False)
    breed = db.Column(db.String(50))
    birth_date = db.Column(db.Date, nullable=False)
    notes = db.Column(db.Text)
    
    feeding_logs = db.relationship('FeedingLog', backref='animal', lazy=True, cascade="all, delete-orphan")
    health_records = db.relationship('HealthRecord', backref='animal', lazy=True, cascade="all, delete-orphan")
    alerts = db.relationship('Alert', backref='animal', lazy=True, cascade="all, delete-orphan")
    
    def to_dict(self):
        return {
            'id': self.id,
            'animal_tag_id': self.animal_tag_id,
            'species': self.species,
            'breed': self.breed,
            'birth_date': self.birth_date.isoformat() if self.birth_date else None,
            'notes': self.notes
        }


class FeedingLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    animal_id = db.Column(db.Integer, db.ForeignKey('animal.id'), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    feed_type = db.Column(db.String(50), nullable=False)
    quantity_kg = db.Column(db.Float, nullable=False)
    notes = db.Column(db.Text)
    
    def to_dict(self):
        return {
            'id': self.id,
            'animal_id': self.animal_id,
            'timestamp': self.timestamp.isoformat(),
            'feed_type': self.feed_type,
            'quantity_kg': self.quantity_kg,
            'notes': self.notes
        }


class HealthRecord(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    animal_id = db.Column(db.Integer, db.ForeignKey('animal.id'), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    weight_kg = db.Column(db.Float)
    temperature_celsius = db.Column(db.Float)
    behavior_observation = db.Column(db.Text, nullable=False)
    notes = db.Column(db.Text)
    
    def to_dict(self):
        return {
            'id': self.id,
            'animal_id': self.animal_id,
            'timestamp': self.timestamp.isoformat(),
            'weight_kg': self.weight_kg,
            'temperature_celsius': self.temperature_celsius,
            'behavior_observation': self.behavior_observation,
            'notes': self.notes
        }


class Alert(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    animal_id = db.Column(db.Integer, db.ForeignKey('animal.id'), nullable=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    message = db.Column(db.Text, nullable=False)
    severity = db.Column(db.String(20), nullable=False)
    source = db.Column(db.String(50), nullable=False)
    acknowledged = db.Column(db.Boolean, default=False, nullable=False)
    
    def to_dict(self):
        return {
            'id': self.id,
            'animal_id': self.animal_id,
            'timestamp': self.timestamp.isoformat(),
            'message': self.message,
            'severity': self.severity,
            'source': self.source,
            'acknowledged': self.acknowledged
        }