"""  
Power state monitoring module
Tracks device power events: startup, shutdown, sleep, wake, battery
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
        self.last_battery_status = None
        self.has_battery = self._check_battery()
        
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
    
    def _check_battery(self):
        """Check if device has a battery"""
        try:
            battery = psutil.sensors_battery()
            return battery is not None
        except Exception:
            return False
    
    def _monitor_battery(self):
        """Monitor battery status and log events"""
        if not self.has_battery:
            return
        
        try:
            battery = psutil.sensors_battery()
            if battery is None:
                return
            
            percent = battery.percent
            plugged = battery.power_plugged
            
            # Check for battery events
            if self.last_battery_status:
                last_percent, last_plugged = self.last_battery_status
                
                # Battery charging started
                if not last_plugged and plugged:
                    self.db.log_power_event('BATTERY_CHARGING', f'Battery charging started at {percent}%')
                    self.logger.info(f"🔌 Battery charging started at {percent}%")
                
                # Battery unplugged
                elif last_plugged and not plugged:
                    self.db.log_power_event('BATTERY_UNPLUGGED', f'Running on battery at {percent}%')
                    self.logger.info(f"🔋 Running on battery at {percent}%")
                
                # Battery full
                if plugged and percent == 100 and last_percent < 100:
                    self.db.log_power_event('BATTERY_FULL', 'Battery fully charged')
                    self.logger.info("✅ Battery fully charged")
                
                # Battery low
                if not plugged and percent <= 20 and last_percent > 20:
                    self.db.log_power_event('BATTERY_LOW', f'Battery low: {percent}%')
                    self.logger.warning(f"⚠️ Battery low: {percent}%")
                
                # Battery critical
                if not plugged and percent <= 10 and last_percent > 10:
                    self.db.log_power_event('BATTERY_CRITICAL', f'Battery critical: {percent}%')
                    self.logger.warning(f"🚨 Battery critical: {percent}%")
            
            # Update last status
            self.last_battery_status = (percent, plugged)
            
        except Exception as e:
            self.logger.error(f"Error monitoring battery: {e}")
    
    def _monitor_loop(self):
        """Main monitoring loop"""
        last_check = datetime.now()
        check_interval = 60  # Check every minute
        
        while self.running:
            try:
                current_time = datetime.now()
                
                # Check for system wake from sleep
                # If there's a large gap between checks, system was likely asleep
                time_diff = (current_time - last_check).total_seconds()
                if time_diff > (check_interval + 60):  # More than expected interval + 1 min buffer
                    sleep_duration = time_diff - check_interval
                    self.logger.info(f"⏰ System wake detected. Was offline for {sleep_duration:.0f} seconds")
                    self.db.log_power_event('WAKE', f'System was offline for {sleep_duration:.0f} seconds')
                    self.db.log_power_event('SLEEP', f'Duration: {sleep_duration:.0f} seconds', )
                
                # Monitor battery
                if self.has_battery:
                    self._monitor_battery()
                
                last_check = current_time
                time.sleep(check_interval)
                
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