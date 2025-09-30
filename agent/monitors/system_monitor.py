"""
System statistics monitoring module
Tracks CPU, memory, disk usage and other system metrics
"""

import psutil
import threading
import time
from datetime import datetime

class SystemMonitor:
    def __init__(self, database, logger, interval=300):
        """
        Initialize system monitor
        :param interval: Monitoring interval in seconds (default: 5 minutes)
        """
        self.db = database
        self.logger = logger
        self.interval = interval
        self.running = False
        self.monitor_thread = None
    
    def start(self):
        """Start system monitoring"""
        self.running = True
        self.logger.info(f"System monitor started. Interval: {self.interval}s")
        
        # Log initial stats
        self._collect_stats()
        
        # Start monitoring thread
        self.monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self.monitor_thread.start()
    
    def _monitor_loop(self):
        """Main monitoring loop"""
        while self.running:
            try:
                time.sleep(self.interval)
                if self.running:
                    self._collect_stats()
            except Exception as e:
                self.logger.error(f"Error in system monitoring loop: {e}")
                time.sleep(60)
    
    def _collect_stats(self):
        """Collect and log system statistics"""
        try:
            # Get CPU usage (average over 1 second)
            cpu_percent = psutil.cpu_percent(interval=1)
            
            # Get memory usage
            memory = psutil.virtual_memory()
            memory_percent = memory.percent
            
            # Get disk usage
            disk = psutil.disk_usage('/')
            disk_percent = disk.percent
            
            # Get uptime
            uptime = time.time() - psutil.boot_time()
            
            # Log to database
            self.db.log_system_stats(
                cpu_percent=cpu_percent,
                memory_percent=memory_percent,
                disk_percent=disk_percent,
                uptime=int(uptime)
            )
            
            self.logger.debug(
                f"Stats - CPU: {cpu_percent}%, Memory: {memory_percent}%, "
                f"Disk: {disk_percent}%, Uptime: {uptime:.0f}s"
            )
            
        except Exception as e:
            self.logger.error(f"Error collecting system stats: {e}")
    
    def get_current_stats(self):
        """Get current system statistics without logging"""
        return {
            'cpu_percent': psutil.cpu_percent(interval=1),
            'memory_percent': psutil.virtual_memory().percent,
            'disk_percent': psutil.disk_usage('/').percent,
            'uptime': time.time() - psutil.boot_time(),
            'timestamp': datetime.now().isoformat()
        }
    
    def stop(self):
        """Stop system monitoring"""
        self.running = False
        self.logger.info("System monitor stopped")
        
        if self.monitor_thread:
            self.monitor_thread.join(timeout=2)