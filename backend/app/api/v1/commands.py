"""
Command API endpoints for JARVIS AI
Handles command processing and execution
"""

import time
from flask import Blueprint, request, jsonify, g
from ...services.ai_service import ai_service
from ...services.voice_service import voice_service
from ...services.vision_service import vision_service
from ...services.system_service import system_service
from ...services.media_service import media_service
from ...services.file_service import file_service
from ...core.security import input_validator, rate_limiter
from ...core.logging import get_logger, log_command
from ...core.exceptions import ValidationError, CommandError
from ..middleware import rate_limit, validate_json_input

logger = get_logger(__name__)

# Create blueprint
commands_bp = Blueprint('commands', __name__, url_prefix='/api/v1/commands')


@commands_bp.route('/execute', methods=['POST'])
@rate_limit('command')
@validate_json_input(['command'])
def execute_command():
    """Execute a user command"""
    start_time = time.time()
    data = request.get_json()
    command = data.get('command', '').strip()
    user_id = data.get('user_id', 'anonymous')

    try:
        # Validate command
        if not command:
            raise ValidationError("Command cannot be empty", field="command")

        command = input_validator.validate_command(command)

        # Interpret command using AI service
        context = {
            'detected_apps': list(system_service.installed_apps_cache.keys())[:50],
            'system_status': system_service.get_system_info(),
            'last_actions': data.get('last_actions', [])
        }

        interpretation = ai_service.interpret_command(command, context)

        if not interpretation:
            raise CommandError("Failed to interpret command", command=command)

        logger.info(f"Command interpretation: {interpretation.get('action', 'UNKNOWN')}")

        # Execute the command based on interpretation
        result = _execute_interpreted_command(interpretation, command)

        # Add execution time
        result['execution_time'] = round(time.time() - start_time, 2)

        # Log command execution
        log_command(command, result, user_id)

        # Speak response if voice is enabled
        if result.get('success') and result.get('response') and voice_service.is_enabled:
            voice_service.speak(result['response'], blocking=False)

        return jsonify({
            'success': True,
            'data': result,
            'interpretation': {
                'action': interpretation.get('action'),
                'target': interpretation.get('target'),
                'reasoning': interpretation.get('reasoning')
            }
        })

    except (ValidationError, CommandError) as e:
        logger.warning(f"Command validation error: {str(e)}")
        return jsonify({
            'success': False,
            'error': e.to_dict()
        }), 400

    except Exception as e:
        logger.error(f"Command execution failed: {str(e)}")
        return jsonify({
            'success': False,
            'error': {
                'error_code': 'COMMAND_EXECUTION_ERROR',
                'message': 'Failed to execute command',
                'details': {'command': command[:100]}
            }
        }), 500


def _execute_interpreted_command(interpretation: dict, original_command: str) -> dict:
    """Execute command based on AI interpretation"""
    action = interpretation.get('action', 'CONVERSATION')
    target = interpretation.get('target', '')
    ai_response = interpretation.get('response', '')
    params = interpretation.get('params', {})
    executable_hints = interpretation.get('executable_hints', [])
    folder_paths = interpretation.get('folder_paths', [])

    try:
        if action == "CONVERSATION":
            response = ai_service.generate_conversation_response(original_command)
            return {
                'success': True,
                'response': response,
                'action': 'conversation',
                'data': {'type': 'chat_response'}
            }

        elif action == "OPEN_APP":
            success = system_service.open_application(target, executable_hints)
            return {
                'success': success,
                'response': ai_response if success else f"Couldn't find {target}",
                'action': 'open_app',
                'data': {'app_name': target}
            }

        elif action == "OPEN_FOLDER":
            success = system_service.open_folder(target, folder_paths)
            return {
                'success': success,
                'response': ai_response if success else f"Couldn't find {target} folder",
                'action': 'open_folder',
                'data': {'folder_name': target}
            }

        elif action == "SEARCH_WEB":
            success = system_service.search_web(target)
            return {
                'success': success,
                'response': ai_response,
                'action': 'search_web',
                'data': {'query': target}
            }

        elif action == "SEARCH_YOUTUBE":
            success = system_service.search_youtube(target)
            return {
                'success': success,
                'response': ai_response,
                'action': 'search_youtube',
                'data': {'query': target}
            }

        elif action == "PLAY_YOUTUBE":
            success = media_service.play_youtube_video(target)
            return {
                'success': success,
                'response': ai_response if success else f"Couldn't play {target}",
                'action': 'play_youtube',
                'data': {'video_query': target}
            }

        elif action == "OPEN_WEBSITE":
            url = system_service.open_website(target)
            return {
                'success': True,
                'response': ai_response,
                'action': 'open_website',
                'data': {'website': target, 'url': url}
            }

        elif action == "TYPE_TEXT":
            success = system_service.type_text(target)
            return {
                'success': success,
                'response': ai_response if success else "Failed to type text",
                'action': 'type_text',
                'data': {'text': target}
            }

        elif action == "PRESS_KEY":
            key = params.get('key', target)
            success = system_service.press_key(key)
            return {
                'success': success,
                'response': ai_response if success else "Failed to press key",
                'action': 'press_key',
                'data': {'key': key}
            }

        elif action == "SCROLL":
            direction = params.get('direction', target) or 'down'
            amount = params.get('amount', 3)
            success = vision_service.scroll_screen(direction, amount)
            return {
                'success': success,
                'response': ai_response if success else "Failed to scroll",
                'action': 'scroll',
                'data': {'direction': direction, 'amount': amount}
            }

        elif action == "SEARCH_FILES":
            file_type = params.get('file_type', None)
            results = file_service.search_files(target, file_type)
            return {
                'success': len(results) > 0,
                'response': ai_response or f"Found {len(results)} results",
                'action': 'search_files',
                'data': {
                    'query': target,
                    'file_type': file_type,
                    'results': results,
                    'count': len(results)
                }
            }

        elif action == "OPEN_FILE":
            # Handle file opening by index or direct path
            if target.isdigit():
                # This would need context from previous search - simplified for now
                return {
                    'success': False,
                    'response': "Cannot open file by index via API",
                    'action': 'open_file'
                }
            else:
                results = file_service.search_files(target)
                if results:
                    success = system_service.open_file(results[0]['path'])
                    return {
                        'success': success,
                        'response': f"Opening {results[0]['name']}",
                        'action': 'open_file',
                        'data': {'file': results[0]}
                    }
                else:
                    return {
                        'success': False,
                        'response': "File not found",
                        'action': 'open_file'
                    }

        elif action == "SCREEN_CLICK":
            # Analyze screen first to find click target
            vision_result = vision_service.analyze_screen(original_command)
            if vision_result and vision_result.get('action') == 'CLICK':
                pos = vision_result.get('approximate_position', {})
                if pos and 'x' in pos and 'y' in pos:
                    success = vision_service.click_position(pos['x'], pos['y'])
                    return {
                        'success': success,
                        'response': vision_result.get('response', 'Clicked'),
                        'action': 'screen_click',
                        'data': {
                            'position': pos,
                            'confidence': vision_result.get('confidence')
                        }
                    }

            return {
                'success': False,
                'response': "Couldn't identify click target",
                'action': 'screen_click'
            }

        elif action == "SCREEN_ANALYZE":
            vision_result = vision_service.analyze_screen(original_command)
            if vision_result:
                return {
                    'success': True,
                    'response': vision_result.get('response', 'Screen analyzed'),
                    'action': 'screen_analyze',
                    'data': {
                        'analysis': vision_result,
                        'screenshot_available': True
                    }
                }

            return {
                'success': False,
                'response': "Couldn't analyze screen",
                'action': 'screen_analyze'
            }

        elif action == "SYSTEM_COMMAND":
            success = system_service.execute_system_command(target)
            return {
                'success': success,
                'response': ai_response if success else "System command failed",
                'action': 'system_command',
                'data': {'command': target}
            }

        else:
            return {
                'success': False,
                'response': "Unknown action",
                'action': action
            }

    except Exception as e:
        logger.error(f"Command execution error for {action}: {str(e)}")
        return {
            'success': False,
            'response': f"Error executing {action}: {str(e)}",
            'action': action,
            'error': str(e)
        }


@commands_bp.route('/interpret', methods=['POST'])
@rate_limit()
@validate_json_input(['command'])
def interpret_command():
    """Interpret command without executing"""
    data = request.get_json()
    command = data.get('command', '').strip()

    try:
        command = input_validator.validate_command(command)

        context = {
            'detected_apps': list(system_service.installed_apps_cache.keys())[:50],
            'system_status': system_service.get_system_info()
        }

        interpretation = ai_service.interpret_command(command, context)

        return jsonify({
            'success': True,
            'data': {
                'command': command,
                'interpretation': interpretation,
                'context_used': {
                    'apps_count': len(context['detected_apps']),
                    'system_type': context['system_status']['os']
                }
            }
        })

    except Exception as e:
        logger.error(f"Command interpretation failed: {str(e)}")
        return jsonify({
            'success': False,
            'error': {
                'error_code': 'INTERPRETATION_ERROR',
                'message': 'Failed to interpret command',
                'details': {'command': command[:100]}
            }
        }), 500


@commands_bp.route('/history', methods=['GET'])
@rate_limit()
def get_command_history():
    """Get recent command history (placeholder)"""
    # In a real implementation, this would pull from a database
    return jsonify({
        'success': True,
        'data': {
            'history': [],
            'message': 'Command history not yet implemented'
        }
    })


@commands_bp.route('/suggest', methods=['POST'])
@rate_limit()
@validate_json_input(['partial_command'])
def get_command_suggestions():
    """Get command suggestions based on partial input"""
    data = request.get_json()
    partial = data.get('partial_command', '').strip().lower()

    try:
        # Simple suggestion logic - can be enhanced with ML
        suggestions = []

        if 'open' in partial:
            suggestions.extend([
                'open chrome', 'open notepad', 'open calculator',
                'open folder', 'open file'
            ])

        if 'play' in partial:
            suggestions.extend([
                'play music', 'play video', 'play youtube'
            ])

        if 'search' in partial:
            suggestions.extend([
                'search web', 'search files', 'search youtube'
            ])

        if 'type' in partial:
            suggestions.extend([
                'type hello', 'type message'
            ])

        # Filter suggestions that match the partial command
        filtered_suggestions = [
            s for s in suggestions
            if partial in s.lower()
        ][:5]  # Limit to 5 suggestions

        return jsonify({
            'success': True,
            'data': {
                'partial_command': partial,
                'suggestions': filtered_suggestions
            }
        })

    except Exception as e:
        logger.error(f"Command suggestions failed: {str(e)}")
        return jsonify({
            'success': False,
            'error': {
                'error_code': 'SUGGESTION_ERROR',
                'message': 'Failed to get suggestions'
            }
        }), 500