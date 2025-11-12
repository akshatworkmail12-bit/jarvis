"""
Custom exceptions for JARVIS AI
Provides structured error handling for different types of failures
"""


class JarvisException(Exception):
    """Base exception for all JARVIS errors"""

    def __init__(self, message: str, error_code: str = None, details: dict = None):
        self.message = message
        self.error_code = error_code or "UNKNOWN_ERROR"
        self.details = details or {}
        super().__init__(self.message)

    def to_dict(self) -> dict:
        """Convert exception to dictionary for API responses"""
        return {
            "error": self.error_code,
            "message": self.message,
            "details": self.details
        }


class ConfigurationError(JarvisException):
    """Raised when there's a configuration problem"""

    def __init__(self, message: str, config_key: str = None):
        details = {"config_key": config_key} if config_key else {}
        super().__init__(message, "CONFIG_ERROR", details)


class LLMError(JarvisException):
    """Raised when LLM operations fail"""

    def __init__(self, message: str, provider: str = None, model: str = None):
        details = {}
        if provider:
            details["provider"] = provider
        if model:
            details["model"] = model
        super().__init__(message, "LLM_ERROR", details)


class VoiceError(JarvisException):
    """Raised when voice operations fail"""

    def __init__(self, message: str, operation: str = None):
        details = {"operation": operation} if operation else {}
        super().__init__(message, "VOICE_ERROR", details)


class VisionError(JarvisException):
    """Raised when vision/analysis operations fail"""

    def __init__(self, message: str, operation: str = None):
        details = {"operation": operation} if operation else {}
        super().__init__(message, "VISION_ERROR", details)


class SystemError(JarvisException):
    """Raised when system operations fail"""

    def __init__(self, message: str, operation: str = None, target: str = None):
        details = {}
        if operation:
            details["operation"] = operation
        if target:
            details["target"] = target
        super().__init__(message, "SYSTEM_ERROR", details)


class FileNotFoundError(JarvisException):
    """Raised when files or folders cannot be found"""

    def __init__(self, message: str, path: str = None):
        details = {"path": path} if path else {}
        super().__init__(message, "FILE_NOT_FOUND", details)


class ApplicationError(JarvisException):
    """Raised when application operations fail"""

    def __init__(self, message: str, app_name: str = None, hint: str = None):
        details = {"app_name": app_name} if app_name else {}
        if hint:
            details["hint"] = hint
        super().__init__(message, "APPLICATION_ERROR", details)


class CommandError(JarvisException):
    """Raised when command processing fails"""

    def __init__(self, message: str, command: str = None, action: str = None):
        details = {}
        if command:
            details["command"] = command
        if action:
            details["action"] = action
        super().__init__(message, "COMMAND_ERROR", details)


class APIError(JarvisException):
    """Raised when API operations fail"""

    def __init__(self, message: str, endpoint: str = None, status_code: int = None):
        details = {}
        if endpoint:
            details["endpoint"] = endpoint
        if status_code:
            details["status_code"] = status_code
        super().__init__(message, "API_ERROR", details)


class AuthenticationError(JarvisException):
    """Raised when authentication fails"""

    def __init__(self, message: str = "Authentication failed"):
        super().__init__(message, "AUTH_ERROR")


class PermissionError(JarvisException):
    """Raised when permission is denied"""

    def __init__(self, message: str, resource: str = None):
        details = {"resource": resource} if resource else {}
        super().__init__(message, "PERMISSION_ERROR", details)


class ValidationError(JarvisException):
    """Raised when input validation fails"""

    def __init__(self, message: str, field: str = None, value: str = None):
        details = {}
        if field:
            details["field"] = field
        if value:
            details["value"] = value
        super().__init__(message, "VALIDATION_ERROR", details)


class ExtensionError(JarvisException):
    """Raised when extension operations fail"""

    def __init__(self, message: str, extension_name: str = None, operation: str = None):
        details = {}
        if extension_name:
            details["extension_name"] = extension_name
        if operation:
            details["operation"] = operation
        super().__init__(message, "EXTENSION_ERROR", details)


class RateLimitError(JarvisException):
    """Raised when rate limits are exceeded"""

    def __init__(self, message: str, limit: int = None, reset_time: int = None):
        details = {}
        if limit:
            details["limit"] = limit
        if reset_time:
            details["reset_time"] = reset_time
        super().__init__(message, "RATE_LIMIT_ERROR", details)