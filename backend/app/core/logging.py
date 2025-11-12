"""
Logging configuration for JARVIS AI
Provides structured logging with both JSON and text formats
"""

import logging
import logging.handlers
import sys
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional
from .config import config


class JSONFormatter(logging.Formatter):
    """Custom JSON formatter for structured logging"""

    def format(self, record: logging.LogRecord) -> str:
        """Format log record as JSON"""
        log_entry = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }

        # Add exception info if present
        if record.exc_info:
            log_entry["exception"] = self.formatException(record.exc_info)

        # Add extra fields
        for key, value in record.__dict__.items():
            if key not in ["name", "msg", "args", "levelname", "levelno",
                          "pathname", "filename", "module", "lineno", "funcName",
                          "created", "msecs", "relativeCreated", "thread",
                          "threadName", "processName", "process", "getMessage",
                          "exc_info", "exc_text", "stack_info"]:
                log_entry["extra"] = log_entry.get("extra", {})
                log_entry["extra"][key] = value

        return json.dumps(log_entry)


class ColoredFormatter(logging.Formatter):
    """Colored formatter for console output"""

    # ANSI color codes
    COLORS = {
        "DEBUG": "\033[36m",    # Cyan
        "INFO": "\033[32m",     # Green
        "WARNING": "\033[33m",  # Yellow
        "ERROR": "\033[31m",    # Red
        "CRITICAL": "\033[35m", # Magenta
        "RESET": "\033[0m"      # Reset
    }

    def format(self, record: logging.LogRecord) -> str:
        """Format log record with colors"""
        color = self.COLORS.get(record.levelname, self.COLORS["RESET"])
        reset = self.COLORS["RESET"]

        # Format the message
        formatted = super().format(record)

        # Add color to level name
        formatted = formatted.replace(
            f"[{record.levelname}]",
            f"[{color}{record.levelname}{reset}]"
        )

        return formatted


class ContextFilter(logging.Filter):
    """Add context information to log records"""

    def filter(self, record: logging.LogRecord) -> bool:
        """Add context information to log record"""
        # Add user ID if available (for future authentication)
        record.user_id = getattr(record, "user_id", "anonymous")

        # Add request ID if available
        record.request_id = getattr(record, "request_id", "no-request")

        # Add session ID if available
        record.session_id = getattr(record, "session_id", "no-session")

        return True


class Logger:
    """Centralized logger for JARVIS AI"""

    def __init__(self):
        self.loggers = {}
        self.setup_logging()

    def setup_logging(self):
        """Setup logging configuration"""
        # Create logs directory if file logging is enabled
        if config.logging.file_path:
            log_file = Path(config.logging.file_path)
            log_file.parent.mkdir(parents=True, exist_ok=True)

        # Configure root logger
        root_logger = logging.getLogger()
        root_logger.setLevel(getattr(logging, config.logging.level.upper()))

        # Clear existing handlers
        root_logger.handlers.clear()

        # Console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(getattr(logging, config.logging.level.upper()))

        if config.logging.format.lower() == "json":
            console_formatter = JSONFormatter()
        else:
            console_formatter = ColoredFormatter(
                fmt="[{asctime}] [{levelname}] [{name}] {message}",
                datefmt="%Y-%m-%d %H:%M:%S",
                style="{"
            )

        console_handler.setFormatter(console_formatter)
        console_handler.addFilter(ContextFilter())
        root_logger.addHandler(console_handler)

        # File handler (if configured)
        if config.logging.file_path:
            file_handler = logging.handlers.RotatingFileHandler(
                filename=config.logging.file_path,
                maxBytes=10 * 1024 * 1024,  # 10MB
                backupCount=5,
                encoding="utf-8"
            )
            file_handler.setLevel(getattr(logging, config.logging.level.upper()))

            # Always use JSON format for file logging
            file_formatter = JSONFormatter()
            file_handler.setFormatter(file_formatter)
            file_handler.addFilter(ContextFilter())
            root_logger.addHandler(file_handler)

        # Configure specific loggers
        self._configure_specific_loggers()

    def _configure_specific_loggers(self):
        """Configure specific module loggers"""
        # Suppress noisy third-party loggers
        noisy_loggers = [
            "urllib3.connectionpool",
            "requests.packages.urllib3",
            "werkzeug",
            "flask",
            "PIL",
            "matplotlib",
        ]

        for logger_name in noisy_loggers:
            logger = logging.getLogger(logger_name)
            logger.setLevel(logging.WARNING)

        # Configure application loggers
        app_loggers = [
            "jarvis",
            "jarvis.ai",
            "jarvis.voice",
            "jarvis.vision",
            "jarvis.system",
            "jarvis.api",
        ]

        for logger_name in app_loggers:
            logger = logging.getLogger(logger_name)
            logger.setLevel(getattr(logging, config.logging.level.upper()))

    def get_logger(self, name: str) -> logging.Logger:
        """Get or create a logger with the given name"""
        if name not in self.loggers:
            self.loggers[name] = logging.getLogger(name)
        return self.loggers[name]

    def log_command(self, command: str, result: Dict[str, Any], user_id: str = None):
        """Log command execution"""
        logger = self.get_logger("jarvis.commands")

        log_data = {
            "command": command,
            "success": result.get("success", False),
            "action": result.get("action", "unknown"),
            "response_length": len(result.get("response", "")),
            "execution_time": result.get("execution_time"),
        }

        if user_id:
            log_data["user_id"] = user_id

        if result.get("success"):
            logger.info(f"Command executed successfully", extra=log_data)
        else:
            logger.error(f"Command execution failed", extra=log_data)

    def log_api_request(self, endpoint: str, method: str,
                       status_code: int, duration: float,
                       user_id: str = None, request_id: str = None):
        """Log API request"""
        logger = self.get_logger("jarvis.api")

        log_data = {
            "endpoint": endpoint,
            "method": method,
            "status_code": status_code,
            "duration_ms": round(duration * 1000, 2),
            "request_id": request_id,
        }

        if user_id:
            log_data["user_id"] = user_id

        if 200 <= status_code < 400:
            logger.info(f"API request successful", extra=log_data)
        else:
            logger.warning(f"API request failed", extra=log_data)

    def log_error(self, error: Exception, context: Dict[str, Any] = None):
        """Log error with context"""
        logger = self.get_logger("jarvis.errors")

        log_data = {
            "error_type": type(error).__name__,
            "error_message": str(error),
        }

        # Add error details if it's a JarvisException
        if hasattr(error, 'error_code'):
            log_data["error_code"] = error.error_code
            log_data["error_details"] = error.details

        if context:
            log_data["context"] = context

        logger.error(f"Error occurred: {str(error)}", extra=log_data, exc_info=True)

    def log_system_event(self, event_type: str, details: Dict[str, Any]):
        """Log system events"""
        logger = self.get_logger("jarvis.system")

        log_data = {
            "event_type": event_type,
            "details": details,
        }

        logger.info(f"System event: {event_type}", extra=log_data)


# Global logger instance
logger_manager = Logger()

# Convenience functions
def get_logger(name: str = None) -> logging.Logger:
    """Get logger instance"""
    if name:
        return logger_manager.get_logger(name)
    return logger_manager.get_logger("jarvis")


def log_command(command: str, result: Dict[str, Any], user_id: str = None):
    """Log command execution"""
    logger_manager.log_command(command, result, user_id)


def log_api_request(endpoint: str, method: str, status_code: int,
                   duration: float, user_id: str = None, request_id: str = None):
    """Log API request"""
    logger_manager.log_api_request(endpoint, method, status_code, duration, user_id, request_id)


def log_error(error: Exception, context: Dict[str, Any] = None):
    """Log error with context"""
    logger_manager.log_error(error, context)


def log_system_event(event_type: str, details: Dict[str, Any]):
    """Log system event"""
    logger_manager.log_system_event(event_type, details)