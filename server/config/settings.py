"""
Server configuration settings
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class ServerConfig:
    """Server configuration class"""
    
    def __init__(self):
        # Flask settings
        self.SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
        self.DEBUG = os.getenv('DEBUG', 'True').lower() == 'true'
        
        # Server settings
        self.HOST = os.getenv('SERVER_HOST', '0.0.0.0')
        self.PORT = int(os.getenv('SERVER_PORT', 5000))
        
        # Database settings
        self.DATABASE_TYPE = os.getenv('DATABASE_TYPE', 'sqlite')
        self.DATABASE_PATH = os.getenv('DATABASE_PATH', 'server_data.db')
        self.SQLALCHEMY_DATABASE_URI = self._get_database_uri()
        self.SQLALCHEMY_TRACK_MODIFICATIONS = False
        
        # API settings
        self.API_KEY = os.getenv('API_KEY', 'dev-key-123')
        self.API_VERSION = 'v1'
        
        # Dashboard settings
        self.ITEMS_PER_PAGE = 20
        self.CHART_DATA_POINTS = 50
        
    def _get_database_uri(self):
        """Get database URI based on type"""
        if self.DATABASE_TYPE == 'sqlite':
            db_path = Path(__file__).parent.parent / self.DATABASE_PATH
            return f'sqlite:///{db_path}'
        elif self.DATABASE_TYPE == 'postgresql':
            user = os.getenv('DB_USER', 'postgres')
            password = os.getenv('DB_PASSWORD', '')
            host = os.getenv('DB_HOST', 'localhost')
            port = os.getenv('DB_PORT', '5432')
            name = os.getenv('DB_NAME', 'device_monitor')
            return f'postgresql://{user}:{password}@{host}:{port}/{name}'
        else:
            raise ValueError(f"Unsupported database type: {self.DATABASE_TYPE}")

config = ServerConfig()
