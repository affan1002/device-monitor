#!/usr/bin/env python3
"""
Device Monitor Server - Main Application
Flask server for centralized device monitoring
"""

from flask import Flask, render_template, jsonify
from flask_cors import CORS
import sys
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from server.config.settings import config
from server.models.database import db, Device, SystemStat, PowerEvent
from server.api.routes import api

def create_app():
    """Create and configure the Flask application"""
    app = Flask(__name__,
                template_folder='dashboard/templates',
                static_folder='dashboard/static')
    
    # Load configuration
    app.config['SECRET_KEY'] = config.SECRET_KEY
    app.config['SQLALCHEMY_DATABASE_URI'] = config.SQLALCHEMY_DATABASE_URI
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = config.SQLALCHEMY_TRACK_MODIFICATIONS
    
    # Initialize extensions
    db.init_app(app)
    CORS(app)  # Enable CORS for API access
    
    # Register blueprints
    app.register_blueprint(api)
    
    # Create database tables
    with app.app_context():
        db.create_all()
        print("✅ Database initialized successfully")
    
    # Dashboard routes
    @app.route('/')
    def index():
        """Main dashboard page"""
        return render_template('index.html')
    
    @app.route('/devices')
    def devices():
        """Devices management page"""
        return render_template('devices.html')
    
    @app.route('/reports')
    def reports():
        """Reports page"""
        return render_template('reports.html')
    
    # Dashboard API endpoints (for frontend)
    @app.route('/dashboard/api/stats')
    def dashboard_stats():
        """Get overall statistics for dashboard"""
        try:
            total_devices = Device.query.count()
            active_devices = Device.query.filter_by(is_active=True).count()
            total_events = PowerEvent.query.count()
            
            # Get latest stats across all devices
            latest_stats = db.session.query(
                db.func.avg(SystemStat.cpu_percent).label('avg_cpu'),
                db.func.avg(SystemStat.memory_percent).label('avg_memory'),
                db.func.avg(SystemStat.disk_percent).label('avg_disk')
            ).first()
            
            return jsonify({
                'total_devices': total_devices,
                'active_devices': active_devices,
                'total_events': total_events,
                'avg_cpu': round(latest_stats.avg_cpu, 1) if latest_stats.avg_cpu else 0,
                'avg_memory': round(latest_stats.avg_memory, 1) if latest_stats.avg_memory else 0,
                'avg_disk': round(latest_stats.avg_disk, 1) if latest_stats.avg_disk else 0
            }), 200
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    # Error handlers
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({'error': 'Not found'}), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        return jsonify({'error': 'Internal server error'}), 500
    
    return app

def main():
    """Main function to run the server"""
    app = create_app()
    
    print("=" * 80)
    print("🚀 Device Monitor Server Starting...")
    print("=" * 80)
    print(f"📡 Server running on: http://{config.HOST}:{config.PORT}")
    print(f"📊 Dashboard: http://localhost:{config.PORT}")
    print(f"🔌 API: http://localhost:{config.PORT}/api/v1")
    print(f"🗄️  Database: {config.DATABASE_TYPE}")
    print("=" * 80)
    print("Press Ctrl+C to stop the server")
    print("=" * 80)
    
    app.run(
        host=config.HOST,
        port=config.PORT,
        debug=config.DEBUG
    )

if __name__ == '__main__':
    main()
