"""
Database models for the device monitoring server
"""

from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class Device(db.Model):
    """Device model - represents monitored devices"""
    __tablename__ = 'devices'
    
    id = db.Column(db.Integer, primary_key=True)
    device_id = db.Column(db.String(100), unique=True, nullable=False)
    hostname = db.Column(db.String(200), nullable=False)
    platform = db.Column(db.String(50))
    platform_version = db.Column(db.String(100))
    last_seen = db.Column(db.DateTime, default=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    power_events = db.relationship('PowerEvent', backref='device', lazy=True, cascade='all, delete-orphan')
    system_stats = db.relationship('SystemStat', backref='device', lazy=True, cascade='all, delete-orphan')
    session_events = db.relationship('SessionEvent', backref='device', lazy=True, cascade='all, delete-orphan')
    
    def to_dict(self):
        """Convert device to dictionary"""
        return {
            'id': self.id,
            'device_id': self.device_id,
            'hostname': self.hostname,
            'platform': self.platform,
            'platform_version': self.platform_version,
            'last_seen': self.last_seen.isoformat() if self.last_seen else None,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class PowerEvent(db.Model):
    """Power event model - stores power state changes"""
    __tablename__ = 'power_events'
    
    id = db.Column(db.Integer, primary_key=True)
    device_id = db.Column(db.Integer, db.ForeignKey('devices.id'), nullable=False)
    event_type = db.Column(db.String(50), nullable=False)  # STARTUP, SHUTDOWN, SLEEP, WAKE
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    details = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        """Convert power event to dictionary"""
        return {
            'id': self.id,
            'device_id': self.device_id,
            'event_type': self.event_type,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None,
            'details': self.details,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class SystemStat(db.Model):
    """System statistics model - stores system metrics"""
    __tablename__ = 'system_stats'
    
    id = db.Column(db.Integer, primary_key=True)
    device_id = db.Column(db.Integer, db.ForeignKey('devices.id'), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    cpu_percent = db.Column(db.Float)
    memory_percent = db.Column(db.Float)
    disk_percent = db.Column(db.Float)
    uptime = db.Column(db.Integer)  # in seconds
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        """Convert system stat to dictionary"""
        return {
            'id': self.id,
            'device_id': self.device_id,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None,
            'cpu_percent': self.cpu_percent,
            'memory_percent': self.memory_percent,
            'disk_percent': self.disk_percent,
            'uptime': self.uptime,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class SessionEvent(db.Model):
    """Session event model - stores login/logout events"""
    __tablename__ = 'session_events'
    
    id = db.Column(db.Integer, primary_key=True)
    device_id = db.Column(db.Integer, db.ForeignKey('devices.id'), nullable=False)
    session_type = db.Column(db.String(50), nullable=False)  # LOGIN, LOGOUT
    start_time = db.Column(db.DateTime)
    end_time = db.Column(db.DateTime)
    duration = db.Column(db.Integer)  # in seconds
    username = db.Column(db.String(200))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        """Convert session event to dictionary"""
        return {
            'id': self.id,
            'device_id': self.device_id,
            'session_type': self.session_type,
            'start_time': self.start_time.isoformat() if self.start_time else None,
            'end_time': self.end_time.isoformat() if self.end_time else None,
            'duration': self.duration,
            'username': self.username,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
