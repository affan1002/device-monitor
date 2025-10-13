"""
API routes for device monitoring server
"""

from flask import Blueprint, request, jsonify, send_file
from datetime import datetime
from pathlib import Path
import os
from werkzeug.utils import secure_filename
from server.models.database import db, Device, PowerEvent, SystemStat, SessionEvent, Screenshot
from server.api.auth import require_api_key

api = Blueprint('api', __name__, url_prefix='/api/v1')

@api.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.utcnow().isoformat()
    }), 200

@api.route('/devices/register', methods=['POST'])
@require_api_key
def register_device():
    """Register a new device or update existing device"""
    try:
        data = request.get_json()
        
        # Required fields
        device_id = data.get('device_id')
        hostname = data.get('hostname')
        
        if not device_id or not hostname:
            return jsonify({'error': 'device_id and hostname are required'}), 400
        
        # Check if device exists
        device = Device.query.filter_by(device_id=device_id).first()
        
        if device:
            # Update existing device
            device.hostname = hostname
            device.platform = data.get('platform')
            device.platform_version = data.get('platform_version')
            device.last_seen = datetime.utcnow()
            device.is_active = True
        else:
            # Create new device
            device = Device(
                device_id=device_id,
                hostname=hostname,
                platform=data.get('platform'),
                platform_version=data.get('platform_version'),
                last_seen=datetime.utcnow(),
                is_active=True
            )
            db.session.add(device)
        
        db.session.commit()
        
        return jsonify({
            'message': 'Device registered successfully',
            'device': device.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@api.route('/devices/<device_id>/power_events', methods=['POST'])
@require_api_key
def submit_power_events(device_id):
    """Submit power events from a device"""
    try:
        data = request.get_json()
        events = data.get('events', [])
        
        # Find device
        device = Device.query.filter_by(device_id=device_id).first()
        if not device:
            return jsonify({'error': 'Device not found'}), 404
        
        # Update last seen
        device.last_seen = datetime.utcnow()
        
        # Add power events
        for event_data in events:
            power_event = PowerEvent(
                device_id=device.id,
                event_type=event_data.get('event_type'),
                timestamp=datetime.fromisoformat(event_data.get('timestamp')) if event_data.get('timestamp') else datetime.utcnow(),
                details=event_data.get('details')
            )
            db.session.add(power_event)
        
        db.session.commit()
        
        return jsonify({
            'message': f'{len(events)} power events submitted successfully'
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@api.route('/devices/<device_id>/system_stats', methods=['POST'])
@require_api_key
def submit_system_stats(device_id):
    """Submit system statistics from a device"""
    try:
        data = request.get_json()
        stats = data.get('stats', [])
        
        # Find device
        device = Device.query.filter_by(device_id=device_id).first()
        if not device:
            return jsonify({'error': 'Device not found'}), 404
        
        # Update last seen
        device.last_seen = datetime.utcnow()
        
        # Add system stats
        for stat_data in stats:
            system_stat = SystemStat(
                device_id=device.id,
                timestamp=datetime.fromisoformat(stat_data.get('timestamp')) if stat_data.get('timestamp') else datetime.utcnow(),
                cpu_percent=stat_data.get('cpu_percent'),
                memory_percent=stat_data.get('memory_percent'),
                disk_percent=stat_data.get('disk_percent'),
                uptime=stat_data.get('uptime')
            )
            db.session.add(system_stat)
        
        db.session.commit()
        
        return jsonify({
            'message': f'{len(stats)} system stats submitted successfully'
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@api.route('/devices', methods=['GET'])
def get_devices():
    """Get all devices"""
    try:
        devices = Device.query.order_by(Device.last_seen.desc()).all()
        return jsonify({
            'devices': [device.to_dict() for device in devices],
            'total': len(devices)
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api.route('/devices/<device_id>', methods=['GET'])
def get_device(device_id):
    """Get a specific device"""
    try:
        device = Device.query.filter_by(device_id=device_id).first()
        if not device:
            return jsonify({'error': 'Device not found'}), 404
        
        return jsonify({'device': device.to_dict()}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api.route('/devices/<device_id>/stats', methods=['GET'])
def get_device_stats(device_id):
    """Get system statistics for a device"""
    try:
        device = Device.query.filter_by(device_id=device_id).first()
        if not device:
            return jsonify({'error': 'Device not found'}), 404
        
        # Get query parameters
        limit = request.args.get('limit', 50, type=int)
        
        # Get recent stats
        stats = SystemStat.query.filter_by(device_id=device.id)\
            .order_by(SystemStat.timestamp.desc())\
            .limit(limit)\
            .all()
        
        return jsonify({
            'device_id': device_id,
            'stats': [stat.to_dict() for stat in stats],
            'total': len(stats)
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api.route('/devices/<device_id>/power_events', methods=['GET'])
def get_power_events(device_id):
    """Get power events for a device"""
    try:
        device = Device.query.filter_by(device_id=device_id).first()
        if not device:
            return jsonify({'error': 'Device not found'}), 404
        
        # Get query parameters
        limit = request.args.get('limit', 50, type=int)
        
        # Get recent events
        events = PowerEvent.query.filter_by(device_id=device.id)\
            .order_by(PowerEvent.timestamp.desc())\
            .limit(limit)\
            .all()
        
        return jsonify({
            'device_id': device_id,
            'events': [event.to_dict() for event in events],
            'total': len(events)
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api.route('/devices/<device_id>/screenshots', methods=['POST'])
@require_api_key
def upload_screenshot(device_id):
    """Upload a screenshot from a device"""
    try:
        # Find device
        device = Device.query.filter_by(device_id=device_id).first()
        if not device:
            return jsonify({'error': 'Device not found'}), 404
        
        # Check if file is present
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'Empty filename'}), 400
        
        # Secure the filename and save
        filename = secure_filename(file.filename)
        
        # Create screenshots directory if not exists
        screenshot_dir = Path(__file__).parent.parent / 'screenshots'
        screenshot_dir.mkdir(exist_ok=True)
        
        # Save file
        filepath = screenshot_dir / filename
        file.save(str(filepath))
        
        # Get file size in KB
        filesize = filepath.stat().st_size / 1024
        
        # Add to database
        screenshot = Screenshot(
            device_id=device.id,
            filename=filename,
            filesize=filesize,
            timestamp=datetime.utcnow()
        )
        db.session.add(screenshot)
        
        # Keep only 3 screenshots per device
        screenshots = Screenshot.query.filter_by(device_id=device.id)\
            .order_by(Screenshot.timestamp.desc())\
            .all()
        
        if len(screenshots) > 3:
            # Delete oldest screenshots
            for old_screenshot in screenshots[3:]:
                # Delete file
                old_filepath = screenshot_dir / old_screenshot.filename
                if old_filepath.exists():
                    old_filepath.unlink()
                # Delete from database
                db.session.delete(old_screenshot)
        
        db.session.commit()
        
        return jsonify({
            'message': 'Screenshot uploaded successfully',
            'screenshot': screenshot.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@api.route('/devices/<device_id>/screenshots', methods=['GET'])
def get_screenshots(device_id):
    """Get screenshots for a device"""
    try:
        device = Device.query.filter_by(device_id=device_id).first()
        if not device:
            return jsonify({'error': 'Device not found'}), 404
        
        # Get recent screenshots (max 3)
        screenshots = Screenshot.query.filter_by(device_id=device.id)\
            .order_by(Screenshot.timestamp.desc())\
            .limit(3)\
            .all()
        
        return jsonify({
            'device_id': device_id,
            'screenshots': [screenshot.to_dict() for screenshot in screenshots],
            'total': len(screenshots)
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api.route('/screenshots/<filename>', methods=['GET'])
def get_screenshot_file(filename):
    """Serve a screenshot file"""
    try:
        screenshot_dir = Path(__file__).parent.parent / 'screenshots'
        filepath = screenshot_dir / secure_filename(filename)
        
        if not filepath.exists():
            return jsonify({'error': 'Screenshot not found'}), 404
        
        return send_file(str(filepath), mimetype='image/jpeg')
    except Exception as e:
        return jsonify({'error': str(e)}), 500
