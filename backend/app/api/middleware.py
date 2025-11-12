"""
API Middleware for JARVIS AI
Handles authentication, rate limiting, and request processing
"""

import time
import uuid
from functools import wraps
from flask import request, jsonify, g
from ..core.security import rate_limiter, input_validator
from ..core.logging import log_api_request
from ..core.exceptions import AuthenticationError, RateLimitError, ValidationError

# Request context storage
request_context = {}


def rate_limit(limit_type: str = 'api_request'):
    """Rate limiting middleware decorator"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Get client identifier (IP address for now)
            client_id = request.environ.get('HTTP_X_FORWARDED_FOR', request.remote_addr)

            if not rate_limiter.is_allowed(client_id, limit_type):
                remaining = rate_limiter.get_remaining_requests(client_id, limit_type)
                raise RateLimitError(
                    f"Rate limit exceeded. {remaining} requests remaining.",
                    limit=rate_limiter.RATE_LIMITS[limit_type]['max_requests'],
                    reset_time=int(time.time()) + 60
                )

            return f(*args, **kwargs)
        return decorated_function
    return decorator


def validate_json_input(required_fields: list = None):
    """Validate JSON input middleware"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not request.is_json:
                raise ValidationError("Request must be JSON")

            data = request.get_json()
            if data is None:
                raise ValidationError("Invalid JSON data")

            if required_fields:
                missing_fields = [field for field in required_fields if field not in data]
                if missing_fields:
                    raise ValidationError(f"Missing required fields: {', '.join(missing_fields)}")

            # Sanitize input data
            if isinstance(data, dict):
                for key, value in data.items():
                    if isinstance(value, str):
                        data[key] = input_validator.sanitize_input(value)

            return f(*args, **kwargs)
        return decorated_function
    return decorator


def request_context_middleware():
    """Set up request context for logging and tracking"""
    g.request_id = str(uuid.uuid4())
    g.start_time = time.time()
    g.client_ip = request.environ.get('HTTP_X_FORWARDED_FOR', request.remote_addr)
    g.user_agent = request.headers.get('User-Agent', 'Unknown')

    # Store in global context for error handling
    request_context[g.request_id] = {
        'client_ip': g.client_ip,
        'user_agent': g.user_agent,
        'method': request.method,
        'endpoint': request.endpoint,
        'path': request.path,
        'start_time': g.start_time
    }


def log_response(response):
    """Log API response"""
    try:
        if hasattr(g, 'start_time') and hasattr(g, 'request_id'):
            duration = time.time() - g.start_time

            # Log the API request
            log_api_request(
                endpoint=request.path,
                method=request.method,
                status_code=response.status_code,
                duration=duration,
                request_id=g.request_id
            )

            # Add request ID to response headers
            response.headers['X-Request-ID'] = g.request_id

    except Exception as e:
        # Don't let logging errors break the response
        pass

    return response


def cors_middleware():
    """CORS middleware for cross-origin requests"""
    # Handle preflight requests
    if request.method == 'OPTIONS':
        response = jsonify({'status': 'ok'})
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization,X-Requested-With')
        response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
        response.headers.add('Access-Control-Max-Age', '86400')
        return response


def error_handler(app):
    """Global error handler for the Flask app"""

    @app.errorhandler(ValidationError)
    def handle_validation_error(e):
        return jsonify({
            'success': False,
            'error': e.to_dict()
        }), 400

    @app.errorhandler(AuthenticationError)
    def handle_auth_error(e):
        return jsonify({
            'success': False,
            'error': e.to_dict()
        }), 401

    @app.errorhandler(RateLimitError)
    def handle_rate_limit_error(e):
        return jsonify({
            'success': False,
            'error': e.to_dict()
        }), 429

    @app.errorhandler(Exception)
    def handle_general_error(e):
        # Log unexpected errors
        from ..core.logging import log_error
        log_error(e, {
            'endpoint': request.path,
            'method': request.method,
            'request_id': getattr(g, 'request_id', None)
        })

        return jsonify({
            'success': False,
            'error': {
                'error_code': 'INTERNAL_SERVER_ERROR',
                'message': 'An unexpected error occurred',
                'details': {}
            }
        }), 500


def setup_middleware(app):
    """Set up all middleware for the Flask app"""

    # Request context middleware
    @app.before_request
    def before_request():
        request_context_middleware()
        cors_middleware()

    # Response logging middleware
    @app.after_request
    def after_request(response):
        return log_response(response)

    # Error handlers
    error_handler(app)