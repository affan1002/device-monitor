#!/usr/bin/env python3
"""
Device Monitor Agent - Main Entry Point
Monitors device power states and system events
"""

import sys
import time
import signal
import logging
from pathlib import Path

# Add the project root to Python path
sys.path.append(str(Path(__file__).parent.parent))

from agent.config.settings import Settings
from agent.monitors.power_monitor import PowerMonitor
from agent.monitors.system_monitor import SystemMonitor
from agent.database.local_db import LocalDatabase
from agent.utils.logger import setup_logger

class DeviceMonitorAgent:
    def __init__(self):
        self.settings = Settings()
        self.logger = setup_logger()
        self.db = LocalDatabase()
        self.power_monitor = PowerMonitor(self.db, self.logger)
        self.system_monitor = SystemMonitor(self.db, self.logger)
        self.running = False
        
    def start(self):
        """Start the monitoring agent"""
        self.logger.info("Starting Device Monitor Agent...")
        self.running = True
        
        # Register signal handlers for graceful shutdown
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
        
        try:
            self.power_monitor.start()
            self.system_monitor.start()
            
            # Main loop
            while self.running:
                time.sleep(1)
                
        except Exception as e:
            self.logger.error(f"Error in main loop: {e}")
        finally:
            self.stop()
    
    def stop(self):
        """Stop the monitoring agent"""
        self.logger.info("Stopping Device Monitor Agent...")
        self.running = False
        
        if hasattr(self, 'power_monitor'):
            self.power_monitor.stop()
        if hasattr(self, 'system_monitor'):
            self.system_monitor.stop()
        
        self.logger.info("Agent stopped successfully")
    
    def _signal_handler(self, signum, frame):
        """Handle shutdown signals"""
        self.logger.info(f"Received signal {signum}, shutting down...")
        self.stop()

if __name__ == "__main__":
    agent = DeviceMonitorAgent()
    try:
        agent.start()
    except KeyboardInterrupt:
        print("\nShutdown requested by user")
    except Exception as e:
        print(f"Fatal error: {e}")
    finally:
        agent.stop()