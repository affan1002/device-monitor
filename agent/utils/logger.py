"""  
Logging configuration for the Device Monitor Agent
"""

import logging
import sys
from pathlib import Path
from datetime import datetime
import pytz

# IST Timezone
IST = pytz.timezone('Asia/Kolkata')

class ISTFormatter(logging.Formatter):
    """Custom formatter to use IST timezone"""
    
    def formatTime(self, record, datefmt=None):
        # Convert to IST
        dt = datetime.fromtimestamp(record.created, IST)
        if datefmt:
            return dt.strftime(datefmt)
        return dt.strftime('%Y-%m-%d %H:%M:%S')

def setup_logger(name='DeviceMonitor', log_file='agent.log', level=logging.INFO):
    """
    Setup logger with both file and console handlers using IST timezone
    """
    # Create logger
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    # Create formatters with IST
    detailed_formatter = ISTFormatter(
        '%(asctime)s IST - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    simple_formatter = ISTFormatter(
        '%(levelname)s: %(message)s'
    )
    
    # File handler
    log_path = Path(__file__).parent.parent / log_file
    file_handler = logging.FileHandler(log_path)
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(detailed_formatter)
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(simple_formatter)
    
    # Add handlers to logger
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    return logger