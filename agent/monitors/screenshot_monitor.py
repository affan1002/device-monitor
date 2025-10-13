"""
Screenshot monitoring module
Captures screenshots periodically and manages storage
"""

import pyscreenshot as ImageGrab
from PIL import Image
import io
import time
import threading
import logging
import random
from datetime import datetime
from pathlib import Path

class ScreenshotMonitor:
    def __init__(self, database, logger, interval=300, max_screenshots=3):
        """
        Initialize screenshot monitor
        :param database: Local database instance
        :param logger: Logger instance
        :param interval: Base screenshot interval in seconds (not used with random mode)
        :param max_screenshots: Maximum number of screenshots to keep (default: 3)
        """
        self.db = database
        self.logger = logger
        self.interval = interval
        self.max_screenshots = max_screenshots
        self.running = False
        self.monitor_thread = None
        self.screenshot_dir = Path(__file__).parent.parent / "screenshots"
        self.screenshot_dir.mkdir(exist_ok=True)
        # Random interval range: 3 to 5 minutes
        self.min_interval = 180  # 3 minutes
        self.max_interval = 300  # 5 minutes
        
    def start(self):
        """Start screenshot monitoring"""
        self.running = True
        self.logger.info(f"[SCREENSHOT] Monitor started. Random interval: 3-5 minutes, Max: {self.max_screenshots}")
        
        # Take initial screenshot
        self._capture_screenshot()
        
        # Start monitoring thread
        self.monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self.monitor_thread.start()
    
    def _monitor_loop(self):
        """Main monitoring loop"""
        while self.running:
            try:
                # Generate random interval between 3 and 5 minutes
                next_interval = random.randint(self.min_interval, self.max_interval)
                minutes = next_interval / 60
                self.logger.info(f"[SCREENSHOT] Next capture in {minutes:.1f} minutes")
                
                time.sleep(next_interval)
                
                if self.running:
                    self._capture_screenshot()
            except Exception as e:
                self.logger.error(f"Error in screenshot monitoring loop: {e}")
                time.sleep(60)
    
    def _capture_screenshot(self):
        """Capture a screenshot and save it"""
        try:
            # Capture screenshot
            screenshot = ImageGrab.grab()
            
            # Generate filename with timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"screenshot_{timestamp}.jpg"
            filepath = self.screenshot_dir / filename
            
            # Compress and save (quality=60 for good balance)
            screenshot = screenshot.convert('RGB')  # Convert to RGB
            screenshot.save(filepath, 'JPEG', quality=60, optimize=True)
            
            # Get file size
            file_size = filepath.stat().st_size / 1024  # KB
            
            self.logger.info(f"[SCREENSHOT] Captured: {filename} ({file_size:.1f} KB)")
            
            # Store in database
            self.db.log_screenshot(filename, str(filepath), file_size)
            
            # Clean up old screenshots
            self._cleanup_old_screenshots()
            
        except Exception as e:
            self.logger.error(f"Error capturing screenshot: {e}")
    
    def _cleanup_old_screenshots(self):
        """Keep only the latest N screenshots, delete older ones"""
        try:
            # Get all screenshots from database
            screenshots = self.db.get_screenshots()
            
            if len(screenshots) > self.max_screenshots:
                # Sort by timestamp (oldest first)
                screenshots.sort(key=lambda x: x['timestamp'])
                
                # Delete oldest screenshots
                screenshots_to_delete = screenshots[:-self.max_screenshots]
                
                for screenshot in screenshots_to_delete:
                    # Delete file
                    filepath = Path(screenshot['filepath'])
                    if filepath.exists():
                        filepath.unlink()
                        self.logger.info(f"[SCREENSHOT] Deleted old: {screenshot['filename']}")
                    
                    # Delete from database
                    self.db.delete_screenshot(screenshot['id'])
            
        except Exception as e:
            self.logger.error(f"Error cleaning up screenshots: {e}")
    
    def get_screenshot_bytes(self, filepath):
        """Get screenshot as bytes for sending to server"""
        try:
            with open(filepath, 'rb') as f:
                return f.read()
        except Exception as e:
            self.logger.error(f"Error reading screenshot file: {e}")
            return None
    
    def stop(self):
        """Stop screenshot monitoring"""
        self.running = False
        self.logger.info("[SCREENSHOT] Monitor stopped")
        
        if self.monitor_thread:
            self.monitor_thread.join(timeout=2)
