"""
Files API endpoints for JARVIS AI
Handles file operations, search, and management
"""

from flask import Blueprint, request, jsonify, g
from ...services.file_service import file_service
from ...services.system_service import system_service
from ...core.logging import get_logger
from ...core.exceptions import ValidationError, FileNotFoundError, SystemError
from ...core.security import input_validator
from ..middleware import rate_limit, validate_json_input

logger = get_logger(__name__)

# Create blueprint
files_bp = Blueprint('files', __name__, url_prefix='/api/v1/files')


@files_bp.route('/search', methods=['POST'])
@rate_limit('file_search')
@validate_json_input(['query'])
def search_files():
    """Search for files and folders"""
    try:
        data = request.get_json()
        query = data.get('query', '').strip()
        file_type = data.get('file_type')
        max_results = int(data.get('max_results', 50))
        search_locations = data.get('search_locations')

        if not query:
            raise ValidationError("Search query is required", field="query")

        # Validate parameters
        if max_results < 1 or max_results > 1000:
            raise ValidationError("max_results must be between 1 and 1000")

        results = file_service.search_files(
            query=query,
            file_type=file_type,
            max_results=max_results,
            search_locations=search_locations
        )

        return jsonify({
            'success': True,
            'data': {
                'query': query,
                'file_type': file_type,
                'results': results,
                'count': len(results),
                'searched_locations': search_locations or file_service.search_locations
            }
        })
    except Exception as e:
        logger.error(f"File search failed: {str(e)}")
        return jsonify({
            'success': False,
            'error': {
                'error_code': 'FILE_SEARCH_ERROR',
                'message': 'Failed to search files'
            }
        }), 500


@files_bp.route('/<path:file_path>/info', methods=['GET'])
@rate_limit()
def get_file_info(file_path):
    """Get detailed information about a specific file"""
    try:
        # Validate file path
        validated_path = input_validator.validate_file_path(file_path)

        info = file_service.get_file_info(validated_path)
        if not info:
            raise FileNotFoundError(f"File not found: {file_path}", path=file_path)

        return jsonify({
            'success': True,
            'data': info
        })
    except (ValidationError, FileNotFoundError) as e:
        return jsonify({
            'success': False,
            'error': e.to_dict()
        }), 404
    except Exception as e:
        logger.error(f"Failed to get file info: {str(e)}")
        return jsonify({
            'success': False,
            'error': {
                'error_code': 'FILE_INFO_ERROR',
                'message': 'Failed to get file information'
            }
        }), 500


@files_bp.route('/<path:file_path>/open', methods=['POST'])
@rate_limit()
def open_file(file_path):
    """Open file or folder with default application"""
    try:
        # Validate file path
        validated_path = input_validator.validate_file_path(file_path)

        success = system_service.open_file(validated_path)

        return jsonify({
            'success': success,
            'data': {
                'file_path': validated_path,
                'opened': success
            }
        })
    except (ValidationError, FileNotFoundError) as e:
        return jsonify({
            'success': False,
            'error': e.to_dict()
        }), 404
    except Exception as e:
        logger.error(f"Failed to open file: {str(e)}")
        return jsonify({
            'success': False,
            'error': {
                'error_code': 'FILE_OPEN_ERROR',
                'message': 'Failed to open file'
            }
        }), 500


@files_bp.route('/<path:file_path>/read', methods=['GET'])
@rate_limit()
def read_file(file_path):
    """Read file contents"""
    try:
        # Validate file path
        validated_path = input_validator.validate_file_path(file_path)

        # Get query parameters
        encoding = request.args.get('encoding', 'utf-8')
        max_size = int(request.args.get('max_size', 10240))  # 10KB default

        content = file_service.read_file(validated_path, encoding, max_size)

        return jsonify({
            'success': True,
            'data': {
                'file_path': validated_path,
                'content': content,
                'encoding': encoding,
                'size': len(content),
                'truncated': max_size is not None
            }
        })
    except (ValidationError, FileNotFoundError) as e:
        return jsonify({
            'success': False,
            'error': e.to_dict()
        }), 404
    except Exception as e:
        logger.error(f"Failed to read file: {str(e)}")
        return jsonify({
            'success': False,
            'error': {
                'error_code': 'FILE_READ_ERROR',
                'message': 'Failed to read file'
            }
        }), 500


@files_bp.route('/<path:file_path>/write', methods=['POST'])
@rate_limit()
@validate_json_input(['content'])
def write_file(file_path):
    """Write content to file"""
    try:
        data = request.get_json()
        content = data.get('content', '')
        encoding = data.get('encoding', 'utf-8')
        backup = bool(data.get('backup', True))

        # Validate file path
        validated_path = input_validator.validate_file_path(file_path)

        success = file_service.write_file(validated_path, content, encoding, backup)

        return jsonify({
            'success': success,
            'data': {
                'file_path': validated_path,
                'content_length': len(content),
                'encoding': encoding,
                'backup_created': backup,
                'written': success
            }
        })
    except ValidationError as e:
        return jsonify({
            'success': False,
            'error': e.to_dict()
        }), 400
    except Exception as e:
        logger.error(f"Failed to write file: {str(e)}")
        return jsonify({
            'success': False,
            'error': {
                'error_code': 'FILE_WRITE_ERROR',
                'message': 'Failed to write file'
            }
        }), 500


@files_bp.route('/<path:dir_path>/list', methods=['GET'])
@rate_limit()
def list_directory(dir_path):
    """List contents of directory"""
    try:
        # Validate directory path
        validated_path = input_validator.validate_file_path(dir_path)

        # Get query parameters
        show_hidden = request.args.get('show_hidden', 'false').lower() == 'true'

        items = file_service.list_directory(validated_path, show_hidden)

        return jsonify({
            'success': True,
            'data': {
                'directory_path': validated_path,
                'items': items,
                'count': len(items),
                'show_hidden': show_hidden
            }
        })
    except (ValidationError, FileNotFoundError) as e:
        return jsonify({
            'success': False,
            'error': e.to_dict()
        }), 404
    except Exception as e:
        logger.error(f"Failed to list directory: {str(e)}")
        return jsonify({
            'success': False,
            'error': {
                'error_code': 'DIRECTORY_LIST_ERROR',
                'message': 'Failed to list directory'
            }
        }), 500


@files_bp.route('/<path:dir_path>/create', methods=['POST'])
@rate_limit()
def create_directory(dir_path):
    """Create directory"""
    try:
        # Validate directory path
        validated_path = input_validator.validate_file_path(dir_path)

        success = file_service.create_directory(validated_path)

        return jsonify({
            'success': success,
            'data': {
                'directory_path': validated_path,
                'created': success
            }
        })
    except ValidationError as e:
        return jsonify({
            'success': False,
            'error': e.to_dict()
        }), 400
    except Exception as e:
        logger.error(f"Failed to create directory: {str(e)}")
        return jsonify({
            'success': False,
            'error': {
                'error_code': 'DIRECTORY_CREATE_ERROR',
                'message': 'Failed to create directory'
            }
        }), 500


@files_bp.route('/<path:file_path>/copy', methods=['POST'])
@rate_limit()
@validate_json_input(['destination'])
def copy_file(file_path):
    """Copy file or directory"""
    try:
        data = request.get_json()
        destination = data.get('destination', '').strip()

        if not destination:
            raise ValidationError("Destination is required", field="destination")

        # Validate paths
        validated_source = input_validator.validate_file_path(file_path)
        validated_dest = input_validator.validate_file_path(destination)

        success = file_service.copy_file(validated_source, validated_dest)

        return jsonify({
            'success': success,
            'data': {
                'source': validated_source,
                'destination': validated_dest,
                'copied': success
            }
        })
    except ValidationError as e:
        return jsonify({
            'success': False,
            'error': e.to_dict()
        }), 400
    except FileNotFoundError as e:
        return jsonify({
            'success': False,
            'error': e.to_dict()
        }), 404
    except Exception as e:
        logger.error(f"Failed to copy file: {str(e)}")
        return jsonify({
            'success': False,
            'error': {
                'error_code': 'FILE_COPY_ERROR',
                'message': 'Failed to copy file'
            }
        }), 500


@files_bp.route('/<path:file_path>/move', methods=['POST'])
@rate_limit()
@validate_json_input(['destination'])
def move_file(file_path):
    """Move file or directory"""
    try:
        data = request.get_json()
        destination = data.get('destination', '').strip()

        if not destination:
            raise ValidationError("Destination is required", field="destination")

        # Validate paths
        validated_source = input_validator.validate_file_path(file_path)
        validated_dest = input_validator.validate_file_path(destination)

        success = file_service.move_file(validated_source, validated_dest)

        return jsonify({
            'success': success,
            'data': {
                'source': validated_source,
                'destination': validated_dest,
                'moved': success
            }
        })
    except ValidationError as e:
        return jsonify({
            'success': False,
            'error': e.to_dict()
        }), 400
    except FileNotFoundError as e:
        return jsonify({
            'success': False,
            'error': e.to_dict()
        }), 404
    except Exception as e:
        logger.error(f"Failed to move file: {str(e)}")
        return jsonify({
            'success': False,
            'error': {
                'error_code': 'FILE_MOVE_ERROR',
                'message': 'Failed to move file'
            }
        }), 500


@files_bp.route('/<path:file_path>/delete', methods=['DELETE'])
@rate_limit()
def delete_file(file_path):
    """Delete file or directory"""
    try:
        # Get query parameters
        permanent = request.args.get('permanent', 'false').lower() == 'true'

        # Validate file path
        validated_path = input_validator.validate_file_path(file_path)

        success = file_service.delete_file(validated_path, permanent)

        return jsonify({
            'success': success,
            'data': {
                'file_path': validated_path,
                'permanent_delete': permanent,
                'deleted': success
            }
        })
    except (ValidationError, FileNotFoundError) as e:
        return jsonify({
            'success': False,
            'error': e.to_dict()
        }), 404
    except Exception as e:
        logger.error(f"Failed to delete file: {str(e)}")
        return jsonify({
            'success': False,
            'error': {
                'error_code': 'FILE_DELETE_ERROR',
                'message': 'Failed to delete file'
            }
        }), 500


@files_bp.route('/disk-usage', methods=['GET'])
@rate_limit()
def get_disk_usage():
    """Get disk usage information"""
    try:
        path = request.args.get('path', '')
        usage = file_service.get_disk_usage(path if path else None)

        return jsonify({
            'success': True,
            'data': usage
        })
    except Exception as e:
        logger.error(f"Failed to get disk usage: {str(e)}")
        return jsonify({
            'success': False,
            'error': {
                'error_code': 'DISK_USAGE_ERROR',
                'message': 'Failed to get disk usage'
            }
        }), 500


@files_bp.route('/duplicates', methods=['POST'])
@rate_limit()
@validate_json_input(['directory'])
def find_duplicates():
    """Find duplicate files in directory"""
    try:
        data = request.get_json()
        directory = data.get('directory', '').strip()
        min_size = int(data.get('min_size', 1024))

        if not directory:
            raise ValidationError("Directory is required", field="directory")

        # Validate directory path
        validated_path = input_validator.validate_file_path(directory)

        duplicates = file_service.find_duplicates(validated_path, min_size)

        return jsonify({
            'success': True,
            'data': {
                'directory': validated_path,
                'min_size': min_size,
                'duplicate_groups': duplicates,
                'total_duplicates': sum(len(group) for group in duplicates)
            }
        })
    except ValidationError as e:
        return jsonify({
            'success': False,
            'error': e.to_dict()
        }), 400
    except Exception as e:
        logger.error(f"Failed to find duplicates: {str(e)}")
        return jsonify({
            'success': False,
            'error': {
                'error_code': 'DUPLICATES_SEARCH_ERROR',
                'message': 'Failed to find duplicates'
            }
        }), 500


@files_bp.route('/cleanup', methods=['POST'])
@rate_limit()
def cleanup_temp_files():
    """Clean up temporary files"""
    try:
        data = request.get_json() or {}
        temp_dirs = data.get('temp_dirs')

        result = file_service.cleanup_temp_files(temp_dirs)

        return jsonify({
            'success': True,
            'data': result
        })
    except Exception as e:
        logger.error(f"Failed to cleanup temp files: {str(e)}")
        return jsonify({
            'success': False,
            'error': {
                'error_code': 'TEMP_CLEANUP_ERROR',
                'message': 'Failed to cleanup temporary files'
            }
        }), 500


@files_bp.route('/status', methods=['GET'])
@rate_limit()
def get_file_service_status():
    """Get file service status and capabilities"""
    try:
        status = file_service.get_file_service_status()

        return jsonify({
            'success': True,
            'data': status
        })
    except Exception as e:
        logger.error(f"Failed to get file service status: {str(e)}")
        return jsonify({
            'success': False,
            'error': {
                'error_code': 'FILE_SERVICE_STATUS_ERROR',
                'message': 'Failed to get file service status'
            }
        }), 500