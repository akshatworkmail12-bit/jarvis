"""
File Service for JARVIS AI
Handles file operations, management, and utilities
"""

import os
import shutil
import glob
import json
import time
from pathlib import Path
from typing import Dict, Any, List, Optional, Union
from datetime import datetime
from ..core.config import config
from ..core.logging import get_logger
from ..core.exceptions import FileNotFoundError, SystemError, ValidationError

logger = get_logger(__name__)


class FileService:
    """Service for file operations and management"""

    def __init__(self):
        self.search_locations = config.search_locations
        logger.info("File service initialized")

    def search_files(self, query: str, file_type: str = None,
                    max_results: int = 50, search_locations: List[str] = None) -> List[Dict[str, Any]]:
        """Search for files and folders"""
        if not query:
            raise ValidationError("Search query cannot be empty", field="query")

        locations = search_locations or self.search_locations
        results = []
        search_pattern = f"*{query}*"

        logger.info(f"Searching files: {query} (max: {max_results})")

        try:
            for location in locations:
                if not os.path.exists(location):
                    logger.debug(f"Location does not exist: {location}")
                    continue

                logger.debug(f"Scanning location: {location}")

                # Build search pattern
                if file_type:
                    pattern = os.path.join(location, '**', f"*{query}*.{file_type}")
                else:
                    pattern = os.path.join(location, '**', f"*{query}*")

                try:
                    matches = glob.glob(pattern, recursive=True)
                    for match in matches:
                        if len(results) >= max_results:
                            break

                        try:
                            result = self._create_file_info(match)
                            if result:
                                results.append(result)
                        except Exception as e:
                            logger.debug(f"Error processing file {match}: {e}")
                            continue

                except Exception as e:
                    logger.debug(f"Error scanning {location}: {e}")
                    continue

                if len(results) >= max_results:
                    break

            # Sort results (folders first, then alphabetically)
            results.sort(key=lambda x: (x['type'] != 'folder', x['name'].lower()))

            logger.info(f"Found {len(results)} search results")
            return results

        except Exception as e:
            logger.error(f"File search failed: {e}")
            raise SystemError(f"File search failed: {str(e)}",
                            operation="search_files", target=query)

    def _create_file_info(self, file_path: str) -> Optional[Dict[str, Any]]:
        """Create detailed file information dictionary"""
        try:
            if not os.path.exists(file_path):
                return None

            stat_info = os.stat(file_path)

            base_info = {
                'path': file_path,
                'name': os.path.basename(file_path),
                'parent': os.path.dirname(file_path),
                'size': stat_info.st_size,
                'created': datetime.fromtimestamp(stat_info.st_ctime).isoformat(),
                'modified': datetime.fromtimestamp(stat_info.st_mtime).isoformat(),
                'accessed': datetime.fromtimestamp(stat_info.st_atime).isoformat(),
            }

            if os.path.isfile(file_path):
                base_info.update({
                    'type': 'file',
                    'extension': os.path.splitext(file_path)[1].lower(),
                    'size_human': self._format_size(stat_info.st_size),
                })

                # Add file type information
                ext = base_info['extension']
                base_info['category'] = self._get_file_category(ext)

            elif os.path.isdir(file_path):
                base_info.update({
                    'type': 'folder',
                    'item_count': len([f for f in os.listdir(file_path)]) if os.path.isdir(file_path) else 0,
                })

            return base_info

        except Exception as e:
            logger.debug(f"Error creating file info for {file_path}: {e}")
            return None

    def _get_file_category(self, extension: str) -> str:
        """Get file category based on extension"""
        categories = {
            'images': ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp', '.svg', '.ico'],
            'documents': ['.pdf', '.doc', '.docx', '.txt', '.rtf', '.odt', '.md'],
            'spreadsheets': ['.xls', '.xlsx', '.csv', '.ods'],
            'presentations': ['.ppt', '.pptx', '.odp'],
            'archives': ['.zip', '.rar', '.7z', '.tar', '.gz', '.bz2'],
            'code': ['.py', '.js', '.html', '.css', '.json', '.xml', '.yaml', '.yml', '.java', '.cpp', '.c'],
            'media': ['.mp4', '.avi', '.mov', '.wmv', '.flv', '.webm', '.mp3', '.wav', '.flac', '.aac'],
            'executables': ['.exe', '.msi', '.deb', '.rpm', '.dmg', '.app'],
        }

        for category, extensions in categories.items():
            if extension.lower() in extensions:
                return category

        return 'other'

    def _format_size(self, size_bytes: int) -> str:
        """Format file size in human readable format"""
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if size_bytes < 1024.0:
                return f"{size_bytes:.1f} {unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.1f} PB"

    def get_file_info(self, file_path: str) -> Optional[Dict[str, Any]]:
        """Get detailed information about a specific file"""
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}", path=file_path)

        return self._create_file_info(file_path)

    def read_file(self, file_path: str, encoding: str = 'utf-8',
                 max_size: int = 10 * 1024 * 1024) -> str:
        """Read file contents safely"""
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}", path=file_path)

        try:
            file_size = os.path.getsize(file_path)
            if file_size > max_size:
                raise ValidationError(f"File too large: {file_size} bytes (max: {max_size})")

            with open(file_path, 'r', encoding=encoding, errors='ignore') as f:
                content = f.read()

            logger.info(f"Read file: {file_path} ({len(content)} chars)")
            return content

        except Exception as e:
            logger.error(f"Failed to read file {file_path}: {e}")
            raise SystemError(f"Failed to read file: {str(e)}",
                            operation="read_file", target=file_path)

    def write_file(self, file_path: str, content: str,
                  encoding: str = 'utf-8', backup: bool = True) -> bool:
        """Write content to file safely"""
        try:
            # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(file_path), exist_ok=True)

            # Create backup if file exists and backup is enabled
            if backup and os.path.exists(file_path):
                backup_path = f"{file_path}.backup.{int(time.time())}"
                shutil.copy2(file_path, backup_path)
                logger.debug(f"Created backup: {backup_path}")

            with open(file_path, 'w', encoding=encoding) as f:
                f.write(content)

            logger.info(f"Wrote file: {file_path} ({len(content)} chars)")
            return True

        except Exception as e:
            logger.error(f"Failed to write file {file_path}: {e}")
            raise SystemError(f"Failed to write file: {str(e)}",
                            operation="write_file", target=file_path)

    def create_directory(self, dir_path: str) -> bool:
        """Create directory and parent directories if needed"""
        try:
            os.makedirs(dir_path, exist_ok=True)
            logger.info(f"Created directory: {dir_path}")
            return True

        except Exception as e:
            logger.error(f"Failed to create directory {dir_path}: {e}")
            raise SystemError(f"Failed to create directory: {str(e)}",
                            operation="create_directory", target=dir_path)

    def delete_file(self, file_path: str, permanent: bool = False) -> bool:
        """Delete file or directory"""
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Path not found: {file_path}", path=file_path)

        try:
            if not permanent:
                # Move to recycle bin (implementation depends on OS)
                if self._move_to_recycle_bin(file_path):
                    logger.info(f"Moved to recycle bin: {file_path}")
                    return True
                else:
                    # Fallback to permanent deletion
                    logger.warning("Recycle bin not available, deleting permanently")
                    permanent = True

            if permanent:
                if os.path.isfile(file_path):
                    os.remove(file_path)
                elif os.path.isdir(file_path):
                    shutil.rmtree(file_path)
                logger.info(f"Deleted permanently: {file_path}")

            return True

        except Exception as e:
            logger.error(f"Failed to delete file {file_path}: {e}")
            raise SystemError(f"Failed to delete file: {str(e)}",
                            operation="delete_file", target=file_path)

    def _move_to_recycle_bin(self, file_path: str) -> bool:
        """Move file to recycle bin (OS-specific implementation)"""
        try:
            import send2trash
            send2trash.send2trash(file_path)
            return True
        except ImportError:
            # send2trash not available
            return False
        except Exception as e:
            logger.debug(f"Recycle bin operation failed: {e}")
            return False

    def copy_file(self, source_path: str, dest_path: str) -> bool:
        """Copy file or directory"""
        if not os.path.exists(source_path):
            raise FileNotFoundError(f"Source not found: {source_path}", path=source_path)

        try:
            # Create destination directory if needed
            os.makedirs(os.path.dirname(dest_path), exist_ok=True)

            if os.path.isfile(source_path):
                shutil.copy2(source_path, dest_path)
            elif os.path.isdir(source_path):
                shutil.copytree(source_path, dest_path, dirs_exist_ok=True)

            logger.info(f"Copied: {source_path} -> {dest_path}")
            return True

        except Exception as e:
            logger.error(f"Failed to copy file {source_path}: {e}")
            raise SystemError(f"Failed to copy file: {str(e)}",
                            operation="copy_file", target=source_path)

    def move_file(self, source_path: str, dest_path: str) -> bool:
        """Move file or directory"""
        if not os.path.exists(source_path):
            raise FileNotFoundError(f"Source not found: {source_path}", path=source_path)

        try:
            # Create destination directory if needed
            os.makedirs(os.path.dirname(dest_path), exist_ok=True)

            shutil.move(source_path, dest_path)
            logger.info(f"Moved: {source_path} -> {dest_path}")
            return True

        except Exception as e:
            logger.error(f"Failed to move file {source_path}: {e}")
            raise SystemError(f"Failed to move file: {str(e)}",
                            operation="move_file", target=source_path)

    def list_directory(self, dir_path: str, show_hidden: bool = False) -> List[Dict[str, Any]]:
        """List contents of directory"""
        if not os.path.exists(dir_path):
            raise FileNotFoundError(f"Directory not found: {dir_path}", path=dir_path)

        if not os.path.isdir(dir_path):
            raise ValidationError(f"Path is not a directory: {dir_path}", field="dir_path")

        try:
            items = []
            for item in os.listdir(dir_path):
                if not show_hidden and item.startswith('.'):
                    continue

                item_path = os.path.join(dir_path, item)
                file_info = self._create_file_info(item_path)
                if file_info:
                    items.append(file_info)

            # Sort: folders first, then files, both alphabetically
            items.sort(key=lambda x: (x['type'] != 'folder', x['name'].lower()))

            logger.info(f"Listed directory: {dir_path} ({len(items)} items)")
            return items

        except Exception as e:
            logger.error(f"Failed to list directory {dir_path}: {e}")
            raise SystemError(f"Failed to list directory: {str(e)}",
                            operation="list_directory", target=dir_path)

    def get_disk_usage(self, path: str = None) -> Dict[str, Any]:
        """Get disk usage information"""
        if not path:
            path = os.path.expanduser('~')

        try:
            usage = shutil.disk_usage(path)
            total = usage.total
            used = usage.used
            free = usage.free

            return {
                'path': path,
                'total_bytes': total,
                'used_bytes': used,
                'free_bytes': free,
                'total_human': self._format_size(total),
                'used_human': self._format_size(used),
                'free_human': self._format_size(free),
                'usage_percent': round((used / total) * 100, 2) if total > 0 else 0
            }

        except Exception as e:
            logger.error(f"Failed to get disk usage for {path}: {e}")
            raise SystemError(f"Failed to get disk usage: {str(e)}",
                            operation="disk_usage", target=path)

    def find_duplicates(self, directory: str, min_size: int = 1024) -> List[List[str]]:
        """Find duplicate files in directory"""
        if not os.path.exists(directory):
            raise FileNotFoundError(f"Directory not found: {directory}", path=directory)

        try:
            file_hashes = {}
            duplicates = []

            for root, dirs, files in os.walk(directory):
                for file in files:
                    file_path = os.path.join(root, file)
                    try:
                        # Skip small files
                        if os.path.getsize(file_path) < min_size:
                            continue

                        # Calculate file hash
                        file_hash = self._calculate_file_hash(file_path)
                        if file_hash in file_hashes:
                            file_hashes[file_hash].append(file_path)
                        else:
                            file_hashes[file_hash] = [file_path]

                    except Exception as e:
                        logger.debug(f"Error processing file {file_path}: {e}")
                        continue

            # Collect duplicates
            for hash_val, file_list in file_hashes.items():
                if len(file_list) > 1:
                    duplicates.append(file_list)

            logger.info(f"Found {len(duplicates)} groups of duplicates in {directory}")
            return duplicates

        except Exception as e:
            logger.error(f"Failed to find duplicates in {directory}: {e}")
            raise SystemError(f"Failed to find duplicates: {str(e)}",
                            operation="find_duplicates", target=directory)

    def _calculate_file_hash(self, file_path: str, algorithm: str = 'md5') -> str:
        """Calculate file hash"""
        import hashlib

        hash_obj = hashlib.new(algorithm)
        with open(file_path, 'rb') as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_obj.update(chunk)
        return hash_obj.hexdigest()

    def cleanup_temp_files(self, temp_dirs: List[str] = None) -> Dict[str, Any]:
        """Clean up temporary files"""
        if not temp_dirs:
            temp_dirs = [
                os.path.expanduser('~/AppData/Local/Temp') if os.name == 'nt' else '/tmp',
                os.path.expanduser('~/.cache'),
            ]

        cleaned_files = []
        errors = []

        for temp_dir in temp_dirs:
            if not os.path.exists(temp_dir):
                continue

            try:
                for item in os.listdir(temp_dir):
                    item_path = os.path.join(temp_dir, item)
                    try:
                        # Only delete files older than 24 hours
                        if os.path.isfile(item_path):
                            file_age = time.time() - os.path.getmtime(item_path)
                            if file_age > 24 * 3600:  # 24 hours
                                os.remove(item_path)
                                cleaned_files.append(item_path)
                    except Exception as e:
                        errors.append(f"Failed to delete {item_path}: {str(e)}")

            except Exception as e:
                errors.append(f"Failed to clean {temp_dir}: {str(e)}")

        result = {
            'cleaned_files': cleaned_files,
            'cleaned_count': len(cleaned_files),
            'errors': errors
        }

        logger.info(f"Cleaned {len(cleaned_files)} temporary files")
        return result

    def get_file_service_status(self) -> Dict[str, Any]:
        """Get file service status"""
        try:
            return {
                "search_locations": self.search_locations,
                "total_search_locations": len(self.search_locations),
                "features": {
                    "file_search": True,
                    "file_operations": True,
                    "duplicate_detection": True,
                    "disk_usage": True,
                    "temp_cleanup": True
                },
                "supported_file_types": [
                    "images", "documents", "spreadsheets", "presentations",
                    "archives", "code", "media", "executables"
                ]
            }

        except Exception as e:
            logger.error(f"Failed to get file service status: {e}")
            return {"error": str(e)}


# Global file service instance
file_service = FileService()