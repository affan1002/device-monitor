"""
Configuration settings for the Device Monitor Agent
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Settings:
    def __init__(self):
        # Database settings
        self.DATABASE_PATH = os.getenv('DATABASE_PATH', 'agent_data.db')
        
        # Server settings
        self.SERVER_HOST = os.getenv('SERVER_HOST', 'localhost')
        self.SERVER_PORT = int(os.getenv('SERVER_PORT', 5000))
        self.API_KEY = os.getenv('API_KEY', 'dev-key-123')
        
        # Agent settings
        self.AGENT_ID = os.getenv('AGENT_ID', 'device-001')
        self.REPORT_INTERVAL = int(os.getenv('REPORT_INTERVAL', 300))  # 5 minutes
        self.DEBUG = os.getenv('DEBUG', 'True').lower() == 'true'
        
        # Logging settings
        self.LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
        self.LOG_FILE = os.getenv('LOG_FILE', 'agent.log')
        
    def get_database_url(self):
        """Get the full database file path"""
        return str(Path(__file__).parent.parent / self.DATABASE_PATH)