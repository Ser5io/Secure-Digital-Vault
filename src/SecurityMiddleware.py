from flask import request, jsonify
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

# Initialize limiter with the Sliding Window Counter strategy
# This strategy is more accurate than fixed window as it smoothens out 
# bursts at the edges of time windows.
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["100 per 15 minutes"],
    strategy="sliding-window-counter",
    storage_uri="memory://",
)

def setup_security(app):
    """
    Apply security configurations and rate limiting to the Flask app.
    """
    # Initialize the limiter with the app
    limiter.init_app(app)

    # 1. Request Size Limiting
    # Restrict maximum payload size to 5MB to prevent memory exhaustion attacks
    app.config['MAX_CONTENT_LENGTH'] = 5 * 1024 * 1024

    # 2. Custom error handler for rate limits
    @app.errorhandler(429)
    def ratelimit_handler(e):
        return jsonify({
            "status": "error",
            "message": "Too many requests. Please try again later.",
            "retry_after": e.description
        }), 429

    # 3. Request size error handler
    @app.errorhandler(413)
    def request_entity_too_large(e):
        return jsonify({
            "status": "error",
            "message": "File too large. Maximum size is 5MB."
        }), 413

def get_limiter():
    """Return the initialized limiter instance for use in other modules."""
    return limiter
