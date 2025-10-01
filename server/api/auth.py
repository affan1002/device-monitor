"""
API authentication middleware
"""

from functools import wraps
from flask import request, jsonify
from server.config.settings import config

def require_api_key(f):
    """Decorator to require API key for endpoint access"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Get API key from header
        api_key = request.headers.get('X-API-Key') or request.headers.get('Authorization')
        
        if not api_key:
            return jsonify({'error': 'API key required'}), 401
        
        # Remove 'Bearer ' prefix if present
        if api_key.startswith('Bearer '):
            api_key = api_key[7:]
        
        # Validate API key
        if api_key != config.API_KEY:
            return jsonify({'error': 'Invalid API key'}), 403
        
        return f(*args, **kwargs)
    
    return decorated_function
