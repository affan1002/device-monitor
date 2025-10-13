"""
Server synchronization module
Sends collected data from agent to central server
"""

import requests
import logging
from datetime import datetime
import socket
import platform
from pathlib import Path

class ServerSync:
    def __init__(self, database, server_url, api_key, device_id):
        """
        Initialize server sync
        :param database: Local database instance
        :param server_url: Server URL (e.g., http://localhost:5000)
        :param api_key: API key for authentication
        :param device_id: Unique device identifier
        """
        self.db = database
        self.server_url = server_url.rstrip('/')
        self.api_key = api_key
        self.device_id = device_id
        self.logger = logging.getLogger(__name__)
        self.api_base_url = f"{self.server_url}/api/v1"
        
    def register_device(self):
        """Register this device with the server"""
        try:
            url = f"{self.api_base_url}/devices/register"
            
            # Get system information
            data = {
                'device_id': self.device_id,
                'hostname': socket.gethostname(),
                'platform': platform.system(),
                'platform_version': platform.version()
            }
            
            headers = {
                'Content-Type': 'application/json',
                'X-API-Key': self.api_key
            }
            
            response = requests.post(url, json=data, headers=headers, timeout=10)
            
            if response.status_code == 200:
                self.logger.info(f"✅ Device registered successfully: {self.device_id}")
                return True
            else:
                self.logger.error(f"❌ Device registration failed: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            self.logger.error(f"Error registering device: {e}")
            return False
    
    def sync_power_events(self):
        """Sync unsynced power events to server"""
        try:
            # Get unsynced events
            unsynced_data = self.db.get_unsynced_events()
            power_events = unsynced_data.get('power_events', [])
            
            if not power_events:
                return True
            
            url = f"{self.api_base_url}/devices/{self.device_id}/power_events"
            
            # Format events for server
            events_data = []
            for event in power_events:
                events_data.append({
                    'event_type': event['event_type'],
                    'timestamp': event['timestamp'],
                    'details': event.get('details', '')
                })
            
            headers = {
                'Content-Type': 'application/json',
                'X-API-Key': self.api_key
            }
            
            response = requests.post(
                url,
                json={'events': events_data},
                headers=headers,
                timeout=10
            )
            
            if response.status_code == 200:
                # Mark events as synced
                event_ids = [e['id'] for e in power_events]
                self.db.mark_as_synced('power_events', event_ids)
                self.logger.info(f"✅ Synced {len(events_data)} power events")
                return True
            else:
                self.logger.error(f"Failed to sync power events: {response.status_code}")
                return False
                
        except Exception as e:
            self.logger.error(f"Error syncing power events: {e}")
            return False
    
    def sync_system_stats(self):
        """Sync unsynced system statistics to server"""
        try:
            # Get unsynced stats
            unsynced_data = self.db.get_unsynced_events()
            system_stats = unsynced_data.get('system_stats', [])
            
            if not system_stats:
                return True
            
            url = f"{self.api_base_url}/devices/{self.device_id}/system_stats"
            
            # Format stats for server
            stats_data = []
            for stat in system_stats:
                stats_data.append({
                    'timestamp': stat['timestamp'],
                    'cpu_percent': stat['cpu_percent'],
                    'memory_percent': stat['memory_percent'],
                    'disk_percent': stat['disk_percent'],
                    'uptime': stat['uptime']
                })
            
            headers = {
                'Content-Type': 'application/json',
                'X-API-Key': self.api_key
            }
            
            response = requests.post(
                url,
                json={'stats': stats_data},
                headers=headers,
                timeout=10
            )
            
            if response.status_code == 200:
                # Mark stats as synced
                stat_ids = [s['id'] for s in system_stats]
                self.db.mark_as_synced('system_stats', stat_ids)
                self.logger.info(f"✅ Synced {len(stats_data)} system stats")
                return True
            else:
                self.logger.error(f"Failed to sync system stats: {response.status_code}")
                return False
                
        except Exception as e:
            self.logger.error(f"Error syncing system stats: {e}")
            return False
    
    def sync_all(self):
        """Sync all unsynced data to server"""
        try:
            self.logger.info("🔄 Starting data synchronization...")
            
            # Register/update device
            self.register_device()
            
            # Sync power events
            self.sync_power_events()
            
            # Sync system stats
            self.sync_system_stats()
            
            # Sync screenshots
            self.sync_screenshots()
            
            self.logger.info("✅ Synchronization complete")
            return True
            
        except Exception as e:
            self.logger.error(f"Error during synchronization: {e}")
            return False
    
    def sync_screenshots(self):
        """Sync screenshots to server"""
        try:
            # Get unsynced screenshots
            screenshots = self.db.get_screenshots()
            
            for screenshot in screenshots:
                if screenshot.get('synced') == 0:
                    # Read screenshot file
                    filepath = screenshot['filepath']
                    
                    if not Path(filepath).exists():
                        self.logger.warning(f"Screenshot file not found: {filepath}")
                        continue
                    
                    url = f"{self.api_base_url}/devices/{self.device_id}/screenshots"
                    
                    headers = {
                        'X-API-Key': self.api_key
                    }
                    
                    # Upload file
                    with open(filepath, 'rb') as f:
                        files = {'file': (screenshot['filename'], f, 'image/jpeg')}
                        response = requests.post(url, files=files, headers=headers, timeout=30)
                    
                    if response.status_code == 200:
                        self.logger.info(f"📸 Synced screenshot: {screenshot['filename']}")
                        # Note: We don't mark as synced because we manage screenshots locally
                    else:
                        self.logger.error(f"Failed to sync screenshot: {response.status_code}")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error syncing screenshots: {e}")
            return False
    
    def test_connection(self):
        """Test connection to server"""
        try:
            url = f"{self.api_base_url}/health"
            response = requests.get(url, timeout=5)
            
            if response.status_code == 200:
                self.logger.info(f"✅ Server connection successful: {self.server_url}")
                return True
            else:
                self.logger.error(f"❌ Server health check failed: {response.status_code}")
                return False
                
        except requests.exceptions.ConnectionError:
            self.logger.error(f"❌ Cannot connect to server at {self.server_url}")
            return False
        except Exception as e:
            self.logger.error(f"Error testing connection: {e}")
            return False
