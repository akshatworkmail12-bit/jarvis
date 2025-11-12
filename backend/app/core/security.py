"""
Security utilities for JARVIS AI
Handles input validation, sanitization, and security checks
"""

import re
import html
import hashlib
import secrets
from typing import Dict, Any, List, Optional
from pathlib import Path
import os
from .exceptions import ValidationError, SecurityError
from .config import config


class InputValidator:
    """Validates and sanitizes user input"""

    # Dangerous patterns to check for
    DANGEROUS_PATTERNS = [
        r'<script[^>]*>.*?</script>',  # Script tags
        r'javascript:',                # JavaScript URLs
        r'on\w+\s*=',                 # Event handlers
        r'eval\s*\(',                 # eval() calls
        r'exec\s*\(',                 # exec() calls
        r'__import__\s*\(',           # Python imports
        r'subprocess\s*\(',           # Subprocess calls
        r'os\.system\s*\(',           # OS system calls
    ]

    # Allowed file extensions for file operations
    ALLOWED_FILE_EXTENSIONS = {
        'images': ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp'],
        'documents': ['.pdf', '.doc', '.docx', '.txt', '.rtf', '.odt'],
        'spreadsheets': ['.xls', '.xlsx', '.csv', '.ods'],
        'presentations': ['.ppt', '.pptx', '.odp'],
        'archives': ['.zip', '.rar', '.7z', '.tar', '.gz'],
        'code': ['.py', '.js', '.html', '.css', '.json', '.xml', '.yaml', '.yml'],
        'media': ['.mp4', '.avi', '.mov', '.mp3', '.wav', '.flac'],
    }

    # Rate limiting configuration
    RATE_LIMITS = {
        'command': {'max_requests': 60, 'window_seconds': 60},      # 60 commands per minute
        'api_request': {'max_requests': 1000, 'window_seconds': 3600},  # 1000 requests per hour
        'file_search': {'max_requests': 20, 'window_seconds': 60},     # 20 searches per minute
    }

    @classmethod
    def sanitize_input(cls, input_text: str) -> str:
        """Sanitize user input by removing dangerous content"""
        if not isinstance(input_text, str):
            raise ValidationError("Input must be a string")

        # HTML escape
        sanitized = html.escape(input_text)

        # Remove dangerous patterns
        for pattern in cls.DANGEROUS_PATTERNS:
            sanitized = re.sub(pattern, '', sanitized, flags=re.IGNORECASE | re.DOTALL)

        # Normalize whitespace
        sanitized = ' '.join(sanitized.split())

        return sanitized.strip()

    @classmethod
    def validate_command(cls, command: str) -> str:
        """Validate and sanitize user command"""
        if not command:
            raise ValidationError("Command cannot be empty", field="command")

        if len(command) > 10000:  # 10KB limit
            raise ValidationError("Command too long", field="command")

        # Check for suspicious patterns
        suspicious_patterns = [
            r'\.\./',          # Path traversal
            r'\\x[0-9a-f]{2}', # Hex encoded characters
            r'%[0-9a-f]{2}',   # URL encoded characters
        ]

        for pattern in suspicious_patterns:
            if re.search(pattern, command, re.IGNORECASE):
                raise ValidationError("Command contains suspicious patterns", field="command")

        return cls.sanitize_input(command)

    @classmethod
    def validate_file_path(cls, file_path: str) -> str:
        """Validate file path for security"""
        if not file_path:
            raise ValidationError("File path cannot be empty")

        # Normalize path
        normalized_path = os.path.normpath(file_path)

        # Check for path traversal
        if '..' in normalized_path or normalized_path.startswith('/'):
            raise ValidationError("Invalid file path", field="file_path")

        # Check for dangerous characters
        dangerous_chars = ['<', '>', '|', '"', '*', '?']
        if any(char in normalized_path for char in dangerous_chars):
            raise ValidationError("File path contains invalid characters", field="file_path")

        return normalized_path

    @classmethod
    def validate_file_extension(cls, file_path: str, category: str = None) -> bool:
        """Validate file extension"""
        if not file_path:
            return False

        file_ext = Path(file_path).suffix.lower()

        if category and category in cls.ALLOWED_FILE_EXTENSIONS:
            return file_ext in cls.ALLOWED_FILE_EXTENSIONS[category]

        # Check all categories if no specific category provided
        all_extensions = []
        for extensions in cls.ALLOWED_FILE_EXTENSIONS.values():
            all_extensions.extend(extensions)

        return file_ext in all_extensions

    @classmethod
    def validate_url(cls, url: str) -> str:
        """Validate and normalize URL"""
        if not url:
            raise ValidationError("URL cannot be empty")

        # Basic URL pattern
        url_pattern = re.compile(
            r'^https?://'  # http:// or https://
            r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # domain
            r'localhost|'  # localhost
            r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # IP
            r'(?::\d+)?'  # optional port
            r'(?:/?|[/?]\S+)$', re.IGNORECASE)

        if not url_pattern.match(url):
            raise ValidationError("Invalid URL format", field="url")

        return url


class RateLimiter:
    """Simple in-memory rate limiter"""

    def __init__(self):
        self.requests = {}  # {identifier: [(timestamp, count), ...]}

    def is_allowed(self, identifier: str, limit_type: str) -> bool:
        """Check if request is allowed based on rate limits"""
        if limit_type not in self.RATE_LIMITS:
            return True

        limit_config = self.RATE_LIMITS[limit_type]
        max_requests = limit_config['max_requests']
        window_seconds = limit_config['window_seconds']

        import time
        current_time = time.time()
        window_start = current_time - window_seconds

        # Clean old requests
        if identifier in self.requests:
            self.requests[identifier] = [
                (timestamp, count) for timestamp, count in self.requests[identifier]
                if timestamp > window_start
            ]
        else:
            self.requests[identifier] = []

        # Count current requests
        current_count = sum(count for _, count in self.requests[identifier])

        if current_count >= max_requests:
            return False

        # Add current request
        self.requests[identifier].append((current_time, 1))

        return True

    def get_remaining_requests(self, identifier: str, limit_type: str) -> int:
        """Get remaining requests for identifier"""
        if limit_type not in self.RATE_LIMITS:
            return float('inf')

        limit_config = self.RATE_LIMITS[limit_type]
        max_requests = limit_config['max_requests']
        window_seconds = limit_config['window_seconds']

        import time
        current_time = time.time()
        window_start = current_time - window_seconds

        # Clean old requests
        if identifier in self.requests:
            self.requests[identifier] = [
                (timestamp, count) for timestamp, count in self.requests[identifier]
                if timestamp > window_start
            ]
        else:
            self.requests[identifier] = []

        current_count = sum(count for _, count in self.requests[identifier])
        return max(0, max_requests - current_count)


class SecurityUtils:
    """Security utility functions"""

    @staticmethod
    def generate_secure_token(length: int = 32) -> str:
        """Generate a cryptographically secure random token"""
        return secrets.token_urlsafe(length)

    @staticmethod
    def hash_password(password: str, salt: str = None) -> tuple[str, str]:
        """Hash password with salt"""
        if salt is None:
            salt = secrets.token_hex(16)

        # Combine password and salt
        password_salt = f"{password}{salt}".encode('utf-8')

        # Hash with SHA-256
        hash_obj = hashlib.sha256(password_salt)
        password_hash = hash_obj.hexdigest()

        return password_hash, salt

    @staticmethod
    def verify_password(password: str, salt: str, stored_hash: str) -> bool:
        """Verify password against stored hash"""
        password_hash, _ = SecurityUtils.hash_password(password, salt)
        return password_hash == stored_hash

    @staticmethod
    def validate_api_key(api_key: str) -> bool:
        """Validate API key format"""
        if not api_key:
            return False

        # Check for common patterns
        patterns = [
            r'^sk-[A-Za-z0-9]{48}$',      # OpenAI API key pattern
            r'^sk-or-v1-[A-Za-z0-9]{48}$', # OpenRouter API key pattern
        ]

        return any(re.match(pattern, api_key) for pattern in patterns)

    @staticmethod
    def mask_sensitive_data(data: str, mask_char: str = '*', visible_chars: int = 4) -> str:
        """Mask sensitive data for logging"""
        if len(data) <= visible_chars:
            return mask_char * len(data)

        return data[:visible_chars] + mask_char * (len(data) - visible_chars)

    @staticmethod
    def check_path_security(file_path: str, allowed_directories: List[str] = None) -> bool:
        """Check if file path is secure"""
        if allowed_directories is None:
            # Default to user directory and common safe locations
            allowed_directories = config.search_locations

        # Normalize path
        normalized_path = os.path.abspath(file_path)

        # Check if path is within allowed directories
        for allowed_dir in allowed_directories:
            allowed_abs = os.path.abspath(allowed_dir)
            if normalized_path.startswith(allowed_abs):
                return True

        return False

    @staticmethod
    def sanitize_filename(filename: str) -> str:
        """Sanitize filename to prevent directory traversal"""
        if not filename:
            return "unnamed"

        # Remove path separators
        filename = os.path.basename(filename)

        # Remove dangerous characters
        dangerous_chars = ['<', '>', ':', '"', '|', '?', '*', '/', '\\']
        for char in dangerous_chars:
            filename = filename.replace(char, '_')

        # Limit length
        if len(filename) > 255:
            name, ext = os.path.splitext(filename)
            filename = name[:255-len(ext)] + ext

        return filename


# Global instances
input_validator = InputValidator()
rate_limiter = RateLimiter()