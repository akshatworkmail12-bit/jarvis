"""
JARVIS AI Backend - Main Application Entry Point
Professional modular architecture with API versioning and comprehensive services
"""

import os
from flask import Flask
from flask_cors import CORS
from .core.config import config
from .core.logging import get_logger, log_system_event
from .api.middleware import setup_middleware
from .api.v1 import commands_bp, system_bp, files_bp, media_bp

# Initialize logger
logger = get_logger(__name__)


def create_app(env_file: str = None):
    """Application factory pattern"""
    # Create Flask app
    app = Flask(__name__)

    # Load configuration
    if env_file:
        config.env_file = env_file
        config.reload()

    # Configure app
    app.config['DEBUG'] = config.api.debug
    app.config['SECRET_KEY'] = config.security.jwt_secret

    # Setup CORS
    CORS(app, origins=config.api.cors_origins)

    # Setup middleware
    setup_middleware(app)

    # Register API blueprints
    app.register_blueprint(commands_bp)
    app.register_blueprint(system_bp)
    app.register_blueprint(files_bp)
    app.register_blueprint(media_bp)

    # Root endpoint
    @app.route('/')
    def index():
        return {
            'name': 'JARVIS AI Backend',
            'version': '2.0.0',
            'status': 'running',
            'api_version': 'v1',
            'endpoints': {
                'commands': '/api/v1/commands',
                'system': '/api/v1/system',
                'files': '/api/v1/files',
                'media': '/api/v1/media'
            }
        }

    # Health check endpoint
    @app.route('/health')
    def health_check():
        return {
            'status': 'healthy',
            'services': {
                'ai': 'operational',
                'voice': 'operational',
                'vision': 'operational',
                'system': 'operational',
                'files': 'operational',
                'media': 'operational'
            }
        }

    # API documentation endpoint
    @app.route('/api/docs')
    def api_docs():
        return {
            'title': 'JARVIS AI API Documentation',
            'version': 'v1',
            'base_url': '/api/v1',
            'endpoints': {
                'commands': {
                    'execute': 'POST /api/v1/commands/execute',
                    'interpret': 'POST /api/v1/commands/interpret',
                    'history': 'GET /api/v1/commands/history',
                    'suggest': 'POST /api/v1/commands/suggest'
                },
                'system': {
                    'info': 'GET /api/v1/system/info',
                    'applications': 'GET /api/v1/system/applications',
                    'screen_capture': 'GET /api/v1/system/screen/capture',
                    'screen_analyze': 'POST /api/v1/system/screen/analyze',
                    'keyboard_type': 'POST /api/v1/system/keyboard/type',
                    'keyboard_press': 'POST /api/v1/system/keyboard/press',
                    'status': 'GET /api/v1/system/status'
                },
                'files': {
                    'search': 'POST /api/v1/files/search',
                    'info': 'GET /api/v1/files/<path>/info',
                    'open': 'POST /api/v1/files/<path>/open',
                    'read': 'GET /api/v1/files/<path>/read',
                    'write': 'POST /api/v1/files/<path>/write',
                    'list': 'GET /api/v1/files/<path>/list',
                    'delete': 'DELETE /api/v1/files/<path>/delete',
                    'disk_usage': 'GET /api/v1/files/disk-usage'
                },
                'media': {
                    'web_search': 'POST /api/v1/media/web/search',
                    'youtube_search': 'POST /api/v1/media/youtube/search',
                    'youtube_play': 'POST /api/v1/media/youtube/play',
                    'website_open': 'POST /api/v1/media/website/open',
                    'status': 'GET /api/v1/media/status'
                }
            }
        }

    return app


def main():
    """Main entry point for running the application"""
    import argparse

    parser = argparse.ArgumentParser(description='JARVIS AI Backend Server')
    parser.add_argument('--host', default=config.api.host, help='Host to bind to')
    parser.add_argument('--port', type=int, default=config.api.port, help='Port to bind to')
    parser.add_argument('--debug', action='store_true', help='Enable debug mode')
    parser.add_argument('--env', help='Environment file path')
    args = parser.parse_args()

    # Override config with command line arguments
    if args.debug:
        config.api.debug = True

    # Create app
    app = create_app(args.env)

    # Log startup
    log_system_event('application_startup', {
        'host': args.host,
        'port': args.port,
        'debug': config.api.debug,
        'environment': 'development' if config.api.debug else 'production'
    })

    print("\n" + "="*70)
    print("🤖 JARVIS AI Backend - Professional Modular Architecture")
    print("="*70)
    print("\n⚙️ Configuration:")
    print(f"   • Environment: {config.system.os_type}")
    print(f"   • API Host: {args.host}")
    print(f"   • API Port: {args.port}")
    print(f"   • Debug Mode: {config.api.debug}")
    print(f"   • LLM Provider: {config.llm.provider}")
    print(f"   • Voice Enabled: {config.voice.enabled}")
    print(f"   • Search Locations: {len(config.search_locations)}")
    print("\n✅ Features Active:")
    print("   • Modular Architecture")
    print("   • API Versioning (v1)")
    print("   • Command Processing")
    print("   • Screen Vision & Analysis")
    print("   • Voice Recognition & TTS")
    print("   • File Management")
    print("   • YouTube Integration")
    print("   • System Automation")
    print("   • Security & Rate Limiting")
    print("   • Comprehensive Logging")
    print("   • Error Handling")
    print("\n🌐 API Endpoints:")
    print("   • Commands: /api/v1/commands/*")
    print("   • System: /api/v1/system/*")
    print("   • Files: /api/v1/files/*")
    print("   • Media: /api/v1/media/*")
    print("   • Docs: /api/docs")
    print("   • Health: /health")
    print(f"\n🚀 Server starting on http://{args.host}:{args.port}")
    print("="*70 + "\n")

    # Run the app
    app.run(
        host=args.host,
        port=args.port,
        debug=config.api.debug,
        use_reloader=False  # Prevent reloader issues with services
    )


if __name__ == '__main__':
    main()