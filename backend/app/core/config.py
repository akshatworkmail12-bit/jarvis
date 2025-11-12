"""
Configuration management for JARVIS AI
Uses Pydantic for validation and environment variable handling
"""

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional, Dict, Any
import os
from pathlib import Path


class LLMConfig(BaseSettings):
    """LLM configuration settings"""
    model_config = SettingsConfigDict(
        env_file=".env",
        env_prefix="LLM_",
        case_sensitive=False,
        extra="ignore"
    )

    provider: str = Field(default="openrouter", description="LLM provider", alias="PROVIDER")
    api_key: str = Field(..., description="API key for LLM service", alias="API_KEY")
    api_base: str = Field(default="https://openrouter.ai/api/v1", description="API base URL", alias="API_BASE")
    model: str = Field(default="openai/gpt-oss-20b:free", description="Text model name", alias="MODEL")
    vision_model: str = Field(default="gpt-4o", description="Vision model name", alias="VISION_MODEL")
    enable_reasoning: bool = Field(default=True, description="Enable reasoning for compatible models", alias="ENABLE_REASONING")
    api_key: str = Field(..., description="API key for LLM service", alias="API_KEY")
    api_base: str = Field(default="https://openrouter.ai/api/v1", description="API base URL", alias="API_BASE")
    model: str = Field(default="openai/gpt-oss-20b:free", description="Text model name", alias="MODEL")
    vision_model: str = Field(default="gpt-4o", description="Vision model name", alias="VISION_MODEL")
    enable_reasoning: bool = Field(default=True, description="Enable reasoning for compatible models", alias="ENABLE_REASONING")


class VoiceConfig(BaseSettings):
    """Voice service configuration"""
    model_config = SettingsConfigDict(
        env_file=".env",
        env_prefix="VOICE_",
        case_sensitive=False,
        extra="ignore"
    )

    enabled: bool = Field(default=True, description="Enable voice features", alias="ENABLED")
    rate: int = Field(default=230, description="Speech rate", alias="RATE")
    volume: float = Field(default=1.0, description="Speech volume", alias="VOLUME")
    pitch: float = Field(default=1.5, description="Speech pitch", alias="PITCH")
    energy_threshold: int = Field(default=4000, description="Microphone energy threshold", alias="ENERGY_THRESHOLD")
    dynamic_energy_threshold: bool = Field(default=True, description="Enable dynamic energy threshold", alias="DYNAMIC_ENERGY_THRESHOLD")


class SystemConfig(BaseSettings):
    """System configuration settings"""
    model_config = SettingsConfigDict(
        env_file=".env",
        env_prefix="SYSTEM_",
        case_sensitive=False,
        extra="ignore"
    )

    os_type: str = Field(default_factory=lambda: os.name, description="Operating system", alias="OS_TYPE")
    pyautogui_failsafe: bool = Field(default=True, description="Enable PyAutoGUI failsafe", alias="PYAUTOGUI_FAILSAFE")
    pyautogui_pause: float = Field(default=0.5, description="PyAutoGUI pause between actions", alias="PYAUTOGUI_PAUSE")


class APIConfig(BaseSettings):
    """API server configuration"""
    model_config = SettingsConfigDict(
        env_file=".env",
        env_prefix="API_",
        case_sensitive=False,
        extra="ignore"
    )

    host: str = Field(default="0.0.0.0", description="API server host", alias="HOST")
    port: int = Field(default=5000, description="API server port", alias="PORT")
    debug: bool = Field(default=False, description="Enable debug mode", alias="DEBUG")
    cors_origins: list = Field(default=["*"], description="CORS allowed origins", alias="CORS_ORIGINS")


class DatabaseConfig(BaseSettings):
    """Database configuration"""
    model_config = SettingsConfigDict(
        env_file=".env",
        env_prefix="DB_",
        case_sensitive=False,
        extra="ignore"
    )

    url: str = Field(default="sqlite:///jarvis.db", description="Database connection URL", alias="URL")


class SecurityConfig(BaseSettings):
    """Security configuration"""
    model_config = SettingsConfigDict(
        env_file=".env",
        env_prefix="SECURITY_",
        case_sensitive=False,
        extra="ignore"
    )

    jwt_secret: str = Field(..., description="JWT secret key", alias="JWT_SECRET")
    jwt_algorithm: str = Field(default="HS256", description="JWT algorithm", alias="JWT_ALGORITHM")
    jwt_expiry_hours: int = Field(default=24, description="JWT expiry in hours", alias="JWT_EXPIRY_HOURS")


class LoggingConfig(BaseSettings):
    """Logging configuration"""
    model_config = SettingsConfigDict(
        env_file=".env",
        env_prefix="LOG_",
        case_sensitive=False,
        extra="ignore"
    )

    level: str = Field(default="INFO", description="Log level", alias="LEVEL")
    format: str = Field(default="json", description="Log format (json or text)", alias="FORMAT")
    file_path: Optional[str] = Field(default=None, description="Log file path", alias="FILE_PATH")


class Config:
    """Main configuration class"""

    def __init__(self, env_file: Optional[str] = None):
        self.env_file = env_file or ".env"

        # Load all configuration modules
        self.llm = LLMConfig()
        self.voice = VoiceConfig()
        self.system = SystemConfig()
        self.api = APIConfig()
        self.database = DatabaseConfig()
        self.security = SecurityConfig()
        self.logging = LoggingConfig()

        # Load application settings
        self._load_app_settings()

    def _load_app_settings(self):
        """Load application-specific settings"""
        self.search_locations = self._get_search_locations()
        self.installed_apps_cache_file = "installed_apps_cache.json"

    def _get_search_locations(self) -> list:
        """Get common file search locations based on OS"""
        locations = []
        if self.system.os_type == "Windows":
            user_profile = os.environ.get('USERPROFILE', '')
            locations = [
                user_profile,
                os.path.join(user_profile, 'Desktop'),
                os.path.join(user_profile, 'Documents'),
                os.path.join(user_profile, 'Downloads'),
                os.path.join(user_profile, 'Pictures'),
                os.path.join(user_profile, 'Videos'),
                os.path.join(user_profile, 'Music'),
                os.path.join(user_profile, 'OneDrive'),
            ]
        elif self.system.os_type == "Darwin":
            home = os.path.expanduser('~')
            locations = [
                home,
                os.path.join(home, 'Desktop'),
                os.path.join(home, 'Documents'),
                os.path.join(home, 'Downloads'),
                os.path.join(home, 'Pictures'),
                '/Applications',
            ]
        else:
            home = os.path.expanduser('~')
            locations = [
                home,
                os.path.join(home, 'Desktop'),
                os.path.join(home, 'Documents'),
                os.path.join(home, 'Downloads'),
                os.path.join(home, 'Pictures'),
            ]

        return [loc for loc in locations if os.path.exists(loc)]

    def get_dict(self) -> Dict[str, Any]:
        """Get all configuration as dictionary"""
        return {
            "llm": self.llm.dict(),
            "voice": self.voice.dict(),
            "system": self.system.dict(),
            "api": self.api.dict(),
            "database": self.database.dict(),
            "security": self.security.dict(),
            "logging": self.logging.dict(),
            "search_locations": self.search_locations,
        }

    def reload(self):
        """Reload configuration from environment"""
        self.llm = LLMConfig()
        self.voice = VoiceConfig()
        self.system = SystemConfig()
        self.api = APIConfig()
        self.database = DatabaseConfig()
        self.security = SecurityConfig()
        self.logging = LoggingConfig()
        self._load_app_settings()


# Global configuration instance
config = Config()