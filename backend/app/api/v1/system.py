"""
System API endpoints for JARVIS AI
Handles system information, automation, and control
"""

from flask import Blueprint, request, jsonify, g
from ...services.system_service import system_service
from ...services.vision_service import vision_service
from ...core.logging import get_logger
from ...core.exceptions import ValidationError, SystemError
from ...core.security import input_validator
from ..middleware import rate_limit, validate_json_input

logger = get_logger(__name__)

# Create blueprint
system_bp = Blueprint('system', __name__, url_prefix='/api/v1/system')


@system_bp.route('/info', methods=['GET'])
@rate_limit()
def get_system_info():
    """Get comprehensive system information"""
    try:
        info = system_service.get_system_info()
        return jsonify({
            'success': True,
            'data': info
        })
    except Exception as e:
        logger.error(f"Failed to get system info: {str(e)}")
        return jsonify({
            'success': False,
            'error': {
                'error_code': 'SYSTEM_INFO_ERROR',
                'message': 'Failed to retrieve system information'
            }
        }), 500


@system_bp.route('/applications', methods=['GET'])
@rate_limit()
def get_installed_applications():
    """Get list of installed applications"""
    try:
        apps = system_service.get_installed_apps()
        return jsonify({
            'success': True,
            'data': {
                'applications': apps,
                'count': len(apps)
            }
        })
    except Exception as e:
        logger.error(f"Failed to get applications: {str(e)}")
        return jsonify({
            'success': False,
            'error': {
                'error_code': 'APPS_LIST_ERROR',
                'message': 'Failed to retrieve applications'
            }
        }), 500


@system_bp.route('/applications/<app_name>/open', methods=['POST'])
@rate_limit()
def open_application(app_name):
    """Open a specific application"""
    try:
        data = request.get_json() or {}
        executable_hints = data.get('executable_hints', [])

        if not app_name:
            raise ValidationError("Application name is required")

        success = system_service.open_application(app_name, executable_hints)

        return jsonify({
            'success': success,
            'data': {
                'app_name': app_name,
                'opened': success
            }
        })
    except Exception as e:
        logger.error(f"Failed to open application {app_name}: {str(e)}")
        return jsonify({
            'success': False,
            'error': {
                'error_code': 'APP_OPEN_ERROR',
                'message': f'Failed to open application: {str(e)}'
            }
        }), 500


@system_bp.route('/folders/open', methods=['POST'])
@rate_limit()
@validate_json_input(['folder_name'])
def open_folder():
    """Open a folder"""
    try:
        data = request.get_json()
        folder_name = data.get('folder_name', '').strip()
        folder_paths = data.get('folder_paths', [])

        if not folder_name:
            raise ValidationError("Folder name is required")

        success = system_service.open_folder(folder_name, folder_paths)

        return jsonify({
            'success': success,
            'data': {
                'folder_name': folder_name,
                'opened': success
            }
        })
    except Exception as e:
        logger.error(f"Failed to open folder: {str(e)}")
        return jsonify({
            'success': False,
            'error': {
                'error_code': 'FOLDER_OPEN_ERROR',
                'message': f'Failed to open folder: {str(e)}'
            }
        }), 500


@system_bp.route('/screen/capture', methods=['GET'])
@rate_limit()
def capture_screen():
    """Capture current screen"""
    try:
        # Get optional region parameters
        region = None
        if request.args.get('x') and request.args.get('y') and request.args.get('width') and request.args.get('height'):
            try:
                x = int(request.args.get('x'))
                y = int(request.args.get('y'))
                width = int(request.args.get('width'))
                height = int(request.args.get('height'))
                region = (x, y, width, height)
            except ValueError:
                pass  # Invalid region parameters, ignore

        screenshot = vision_service.capture_screen(region)
        if not screenshot:
            raise SystemError("Failed to capture screen", operation="screen_capture")

        # Convert to base64 for JSON response
        img_base64 = vision_service.capture_screen_to_base64(region)

        return jsonify({
            'success': True,
            'data': {
                'screenshot': img_base64,
                'region': region,
                'timestamp': vision_service.get_screen_info().get('timestamp')
            }
        })
    except Exception as e:
        logger.error(f"Screen capture failed: {str(e)}")
        return jsonify({
            'success': False,
            'error': {
                'error_code': 'SCREEN_CAPTURE_ERROR',
                'message': 'Failed to capture screen'
            }
        }), 500


@system_bp.route('/screen/analyze', methods=['POST'])
@rate_limit()
@validate_json_input(['query'])
def analyze_screen():
    """Analyze screen content with AI"""
    try:
        data = request.get_json()
        query = data.get('query', '').strip()
        region = data.get('region')

        if not query:
            raise ValidationError("Query is required", field="query")

        # Validate region if provided
        screen_region = None
        if region and all(key in region for key in ['x', 'y', 'width', 'height']):
            screen_region = (
                int(region['x']), int(region['y']),
                int(region['width']), int(region['height'])
            )

        result = vision_service.analyze_screen(query, screen_region)

        return jsonify({
            'success': True,
            'data': {
                'query': query,
                'analysis': result,
                'region': screen_region
            }
        })
    except Exception as e:
        logger.error(f"Screen analysis failed: {str(e)}")
        return jsonify({
            'success': False,
            'error': {
                'error_code': 'SCREEN_ANALYSIS_ERROR',
                'message': 'Failed to analyze screen'
            }
        }), 500


@system_bp.route('/screen/click', methods=['POST'])
@rate_limit()
@validate_json_input(['x', 'y'])
def click_screen():
    """Click at specific screen position"""
    try:
        data = request.get_json()
        x = float(data.get('x'))
        y = float(data.get('y'))
        duration = float(data.get('duration', 0.5))

        # Validate coordinates
        if not (0 <= x <= 100 and 0 <= y <= 100):
            raise ValidationError("Coordinates must be between 0 and 100 (percentages)")

        success = vision_service.click_position(x, y, duration)

        return jsonify({
            'success': success,
            'data': {
                'x_percent': x,
                'y_percent': y,
                'duration': duration,
                'clicked': success
            }
        })
    except Exception as e:
        logger.error(f"Screen click failed: {str(e)}")
        return jsonify({
            'success': False,
            'error': {
                'error_code': 'SCREEN_CLICK_ERROR',
                'message': 'Failed to click screen position'
            }
        }), 500


@system_bp.route('/screen/scroll', methods=['POST'])
@rate_limit()
@validate_json_input(['direction'])
def scroll_screen():
    """Scroll screen in specified direction"""
    try:
        data = request.get_json()
        direction = data.get('direction', 'down')
        amount = int(data.get('amount', 3))
        x = data.get('x')
        y = data.get('y')

        # Validate direction
        if direction not in ['up', 'down', 'left', 'right']:
            raise ValidationError("Direction must be: up, down, left, or right")

        success = vision_service.scroll_screen(direction, amount, x, y)

        return jsonify({
            'success': success,
            'data': {
                'direction': direction,
                'amount': amount,
                'position': {'x': x, 'y': y} if x and y else None,
                'scrolled': success
            }
        })
    except Exception as e:
        logger.error(f"Screen scroll failed: {str(e)}")
        return jsonify({
            'success': False,
            'error': {
                'error_code': 'SCREEN_SCROLL_ERROR',
                'message': 'Failed to scroll screen'
            }
        }), 500


@system_bp.route('/keyboard/type', methods=['POST'])
@rate_limit()
@validate_json_input(['text'])
def type_text():
    """Type text using keyboard"""
    try:
        data = request.get_json()
        text = data.get('text', '').strip()
        interval = float(data.get('interval', 0.05))

        if not text:
            raise ValidationError("Text is required", field="text")

        # Validate text length
        if len(text) > 10000:
            raise ValidationError("Text too long (max 10000 characters)")

        success = system_service.type_text(text, interval)

        return jsonify({
            'success': success,
            'data': {
                'text': text[:100] + '...' if len(text) > 100 else text,
                'interval': interval,
                'typed': success,
                'character_count': len(text)
            }
        })
    except Exception as e:
        logger.error(f"Type text failed: {str(e)}")
        return jsonify({
            'success': False,
            'error': {
                'error_code': 'TYPE_TEXT_ERROR',
                'message': 'Failed to type text'
            }
        }), 500


@system_bp.route('/keyboard/press', methods=['POST'])
@rate_limit()
@validate_json_input(['key'])
def press_key():
    """Press keyboard key or key combination"""
    try:
        data = request.get_json()
        key = data.get('key', '').strip()

        if not key:
            raise ValidationError("Key is required", field="key")

        success = system_service.press_key(key)

        return jsonify({
            'success': success,
            'data': {
                'key': key,
                'pressed': success
            }
        })
    except Exception as e:
        logger.error(f"Press key failed: {str(e)}")
        return jsonify({
            'success': False,
            'error': {
                'error_code': 'PRESS_KEY_ERROR',
                'message': 'Failed to press key'
            }
        }), 500


@system_bp.route('/execute', methods=['POST'])
@rate_limit()
@validate_json_input(['command'])
def execute_system_command():
    """Execute system command (with safety checks)"""
    try:
        data = request.get_json()
        command = data.get('command', '').strip()

        if not command:
            raise ValidationError("Command is required", field="command")

        success = system_service.execute_system_command(command)

        return jsonify({
            'success': success,
            'data': {
                'command': command,
                'executed': success
            }
        })
    except Exception as e:
        logger.error(f"System command execution failed: {str(e)}")
        return jsonify({
            'success': False,
            'error': {
                'error_code': 'SYSTEM_COMMAND_ERROR',
                'message': 'Failed to execute system command'
            }
        }), 500


@system_bp.route('/status', methods=['GET'])
@rate_limit()
def get_system_status():
    """Get current system status and capabilities"""
    try:
        system_info = system_service.get_system_info()
        screen_info = vision_service.get_screen_info()
        vision_status = vision_service.test_vision_capabilities()

        return jsonify({
            'success': True,
            'data': {
                'system': system_info,
                'screen': screen_info,
                'vision': vision_status,
                'capabilities': {
                    'screen_capture': vision_status.get('screen_capture', False),
                    'ai_analysis': vision_status.get('ai_analysis', False),
                    'clicking': vision_status.get('clicking', False),
                    'scrolling': vision_status.get('scrolling', False),
                    'typing': True,
                    'keyboard': True,
                    'app_management': True,
                    'file_operations': True
                },
                'status': 'operational'
            }
        })
    except Exception as e:
        logger.error(f"Failed to get system status: {str(e)}")
        return jsonify({
            'success': False,
            'error': {
                'error_code': 'SYSTEM_STATUS_ERROR',
                'message': 'Failed to retrieve system status'
            }
        }), 500


@system_bp.route('/test', methods=['GET'])
@rate_limit()
def test_system_functionality():
    """Test various system functionalities"""
    try:
        tests = {
            'screen_capture': vision_service.test_vision_capabilities(),
            'system_info': system_service.get_system_info(),
            'api_response': True
        }

        all_tests_passed = all([
            tests['screen_capture'].get('success', False),
            tests['system_info'].get('os') is not None,
            tests['api_response']
        ])

        return jsonify({
            'success': True,
            'data': {
                'tests': tests,
                'all_passed': all_tests_passed,
                'timestamp': vision_service.get_screen_info().get('timestamp')
            }
        })
    except Exception as e:
        logger.error(f"System functionality test failed: {str(e)}")
        return jsonify({
            'success': False,
            'error': {
                'error_code': 'SYSTEM_TEST_ERROR',
                'message': 'System functionality test failed'
            }
        }), 500