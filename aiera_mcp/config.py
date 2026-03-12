#!/usr/bin/env python3

"""Configuration module for Aiera MCP using Pydantic BaseSettings."""

from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional


class AieraSettings(BaseSettings):
    """Configuration settings for Aiera MCP.

    All settings can be configured via environment variables.
    Environment variables are automatically loaded and override defaults.

    Example:
        export AIERA_BASE_URL="https://custom.aiera.com/api"
        export AIERA_API_KEY="your-api-key"
        export DEFAULT_PAGE_SIZE=100
    """

    # API Configuration
    aiera_base_url: str = "https://premium.aiera.com/api"
    aiera_api_key: Optional[str] = None

    # Pagination Configuration
    default_page_size: int = 50
    default_max_page_size: int = 100

    # HTTP Client Configuration
    http_timeout: float = 30.0
    http_max_keepalive_connections: int = 10
    http_max_connections: int = 20
    http_keepalive_expiry: float = 30.0

    # Logging Configuration
    log_level: str = "INFO"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )


# Global settings instance
_settings: Optional[AieraSettings] = None


def get_settings() -> AieraSettings:
    """Get or create the global settings instance.

    Returns:
        AieraSettings: The global settings instance

    Example:
        from aiera_mcp.config import get_settings

        settings = get_settings()
        print(settings.aiera_base_url)
    """
    global _settings
    if _settings is None:
        _settings = AieraSettings()
    return _settings


def reload_settings() -> AieraSettings:
    """Reload settings from environment (useful for testing).

    Returns:
        AieraSettings: The reloaded settings instance
    """
    global _settings
    _settings = AieraSettings()
    return _settings


# Convenience constants for backward compatibility
# These are initialized lazily to avoid circular imports
def _get_constant(attr: str):
    """Lazy getter for backward compatibility constants."""
    settings = get_settings()
    return getattr(settings, attr)


# These are kept for backward compatibility but now pull from settings
AIERA_BASE_URL = property(lambda self: _get_constant("aiera_base_url"))
DEFAULT_PAGE_SIZE = property(lambda self: _get_constant("default_page_size"))
DEFAULT_MAX_PAGE_SIZE = property(lambda self: _get_constant("default_max_page_size"))


__all__ = [
    "AieraSettings",
    "get_settings",
    "reload_settings",
]
