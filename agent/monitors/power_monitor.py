"""
Power state monitoring module
Tracks device power events: startup, shutdown, sleep, wake
"""

import psutil
import platform
import threading
import time
from datetime import datetime

class PowerMonitor:
    def __init__(self, database, logger):
        self.db = database
        self.logger = logger
        self.running = False
        self.monitor_thread = None
        self.boot_time = None
        
    def start(self):
        """Start power monitoring"""
        self.running = True
        self.boot_time = datetime.fromtimestamp(psutil.boot_time())
        
        # Log system startup event
        self.db.log_power_event('STARTUP', f'System booted at {self.boot_time}')
        self.logger.info(f"Power monitor started. Boot time: {self.boot_time}")
        
        # Start monitoring thread
        self.monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self.monitor_thread.start()
    
    def _monitor_loop(self):
        """Main monitoring loop"""
        last_check = datetime.now()
        
        while self.running:
            try:
                current_time = datetime.now()
                
                # Check for system wake from sleep
                # If there's a large gap between checks, system was likely asleep
                time_diff = (current_time - last_check).total_seconds()
                if time_diff > 120:  # More than 2 minutes gap
                    self.logger.info(f"System wake detected. Was offline for {time_diff:.0f} seconds")
                    self.db.log_power_event('WAKE', f'System was offline for {time_diff:.0f} seconds')
                
                last_check = current_time
                time.sleep(60)  # Check every minute
                
            except Exception as e:
                self.logger.error(f"Error in power monitoring loop: {e}")
                time.sleep(60)
    
    def get_uptime(self):
        """Get system uptime in seconds"""
        return time.time() - psutil.boot_time()
    
    def stop(self):
        """Stop power monitoring"""
        self.running = False
        
        # Log shutdown event
        uptime = self.get_uptime()
        self.db.log_power_event('SHUTDOWN', f'System uptime: {uptime:.0f} seconds')
        self.logger.info("Power monitor stopped")
        
        if self.monitor_thread:
            self.monitor_thread.join(timeout=2)