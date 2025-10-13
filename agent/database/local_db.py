"""
Local SQLite database management for storing device monitoring data
"""

import sqlite3
import logging
from datetime import datetime
from pathlib import Path

class LocalDatabase:
    def __init__(self, db_path='agent_data.db'):
        """Initialize database connection"""
        self.db_path = db_path
        self.connection = None
        self.logger = logging.getLogger(__name__)
        self._init_database()
    
    def _init_database(self):
        """Create database and tables if they don't exist"""
        try:
            self.connection = sqlite3.connect(self.db_path, check_same_thread=False)
            self.connection.row_factory = sqlite3.Row
            cursor = self.connection.cursor()
            
            # Create power_events table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS power_events (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    event_type TEXT NOT NULL,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    details TEXT,
                    synced INTEGER DEFAULT 0
                )
            ''')
            
            # Create session_events table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS session_events (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_type TEXT NOT NULL,
                    start_time DATETIME,
                    end_time DATETIME,
                    duration INTEGER,
                    username TEXT,
                    synced INTEGER DEFAULT 0
                )
            ''')
            
            # Create system_stats table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS system_stats (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    cpu_percent REAL,
                    memory_percent REAL,
                    disk_percent REAL,
                    uptime INTEGER,
                    synced INTEGER DEFAULT 0
                )
            ''')
            
            # Create screenshots table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS screenshots (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    filename TEXT NOT NULL,
                    filepath TEXT NOT NULL,
                    filesize REAL,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    synced INTEGER DEFAULT 0
                )
            ''')
            
            self.connection.commit()
            self.logger.info("Database initialized successfully")
            
        except sqlite3.Error as e:
            self.logger.error(f"Database initialization error: {e}")
            raise
    
    def log_power_event(self, event_type, details=''):
        """Log a power-related event"""
        try:
            cursor = self.connection.cursor()
            cursor.execute('''
                INSERT INTO power_events (event_type, details, timestamp)
                VALUES (?, ?, ?)
            ''', (event_type, details, datetime.now()))
            self.connection.commit()
            self.logger.info(f"Logged power event: {event_type}")
            return cursor.lastrowid
        except sqlite3.Error as e:
            self.logger.error(f"Error logging power event: {e}")
            return None
    
    def log_session_event(self, session_type, start_time, end_time=None, duration=None, username=''):
        """Log a session event (login/logout)"""
        try:
            cursor = self.connection.cursor()
            cursor.execute('''
                INSERT INTO session_events (session_type, start_time, end_time, duration, username)
                VALUES (?, ?, ?, ?, ?)
            ''', (session_type, start_time, end_time, duration, username))
            self.connection.commit()
            self.logger.info(f"Logged session event: {session_type}")
            return cursor.lastrowid
        except sqlite3.Error as e:
            self.logger.error(f"Error logging session event: {e}")
            return None
    
    def log_system_stats(self, cpu_percent, memory_percent, disk_percent, uptime):
        """Log current system statistics"""
        try:
            cursor = self.connection.cursor()
            cursor.execute('''
                INSERT INTO system_stats (cpu_percent, memory_percent, disk_percent, uptime)
                VALUES (?, ?, ?, ?)
            ''', (cpu_percent, memory_percent, disk_percent, uptime))
            self.connection.commit()
            return cursor.lastrowid
        except sqlite3.Error as e:
            self.logger.error(f"Error logging system stats: {e}")
            return None
    
    def get_unsynced_events(self):
        """Retrieve all events that haven't been synced to the server"""
        try:
            cursor = self.connection.cursor()
            
            # Get power events
            cursor.execute('SELECT * FROM power_events WHERE synced = 0')
            power_events = [dict(row) for row in cursor.fetchall()]
            
            # Get session events
            cursor.execute('SELECT * FROM session_events WHERE synced = 0')
            session_events = [dict(row) for row in cursor.fetchall()]
            
            # Get system stats
            cursor.execute('SELECT * FROM system_stats WHERE synced = 0')
            system_stats = [dict(row) for row in cursor.fetchall()]
            
            return {
                'power_events': power_events,
                'session_events': session_events,
                'system_stats': system_stats
            }
        except sqlite3.Error as e:
            self.logger.error(f"Error retrieving unsynced events: {e}")
            return None
    
    def mark_as_synced(self, table_name, event_ids):
        """Mark events as synced to the server"""
        try:
            cursor = self.connection.cursor()
            placeholders = ','.join('?' * len(event_ids))
            query = f'UPDATE {table_name} SET synced = 1 WHERE id IN ({placeholders})'
            cursor.execute(query, event_ids)
            self.connection.commit()
            self.logger.info(f"Marked {len(event_ids)} events as synced in {table_name}")
            return True
        except sqlite3.Error as e:
            self.logger.error(f"Error marking events as synced: {e}")
            return False
    
    def get_recent_stats(self, limit=10):
        """Get recent system statistics"""
        try:
            cursor = self.connection.cursor()
            cursor.execute('''
                SELECT * FROM system_stats 
                ORDER BY timestamp DESC 
                LIMIT ?
            ''', (limit,))
            return [dict(row) for row in cursor.fetchall()]
        except sqlite3.Error as e:
            self.logger.error(f"Error retrieving recent stats: {e}")
            return []
    
    def log_screenshot(self, filename, filepath, filesize):
        """Log a screenshot capture"""
        try:
            cursor = self.connection.cursor()
            cursor.execute('''
                INSERT INTO screenshots (filename, filepath, filesize, timestamp)
                VALUES (?, ?, ?, ?)
            ''', (filename, filepath, filesize, datetime.now()))
            self.connection.commit()
            return cursor.lastrowid
        except sqlite3.Error as e:
            self.logger.error(f"Error logging screenshot: {e}")
            return None
    
    def get_screenshots(self):
        """Get all screenshots"""
        try:
            cursor = self.connection.cursor()
            cursor.execute('SELECT * FROM screenshots ORDER BY timestamp DESC')
            return [dict(row) for row in cursor.fetchall()]
        except sqlite3.Error as e:
            self.logger.error(f"Error retrieving screenshots: {e}")
            return []
    
    def delete_screenshot(self, screenshot_id):
        """Delete a screenshot from database"""
        try:
            cursor = self.connection.cursor()
            cursor.execute('DELETE FROM screenshots WHERE id = ?', (screenshot_id,))
            self.connection.commit()
            return True
        except sqlite3.Error as e:
            self.logger.error(f"Error deleting screenshot: {e}")
            return False
    
    def close(self):
        """Close database connection"""
        if self.connection:
            self.connection.close()
            self.logger.info("Database connection closed")