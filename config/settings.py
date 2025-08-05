"""
Crystal Personal Assistant AI - Configuration Settings

Based on PROJECT_OVERVIEW.md:
- Local PC application with web server
- PostgreSQL database for robust storage
- Hybrid AI approach (local + OpenAI API)
- Security and privacy focused
"""

from typing import Optional, List
from pydantic import Field
from pydantic_settings import BaseSettings
from pathlib import Path
import os

class Settings(BaseSettings):
    """Main application settings following project overview specifications."""
    
    # Application
    app_name: str = "Crystal Personal Assistant AI"
    version: str = "0.1.0"
    debug: bool = False
    
    # Web Server (as per project overview)
    host: str = "localhost"
    port: int = 8000
    reload: bool = False
    
    # Database (PostgreSQL with asyncpg driver for Windows compatibility)
    database_url: str = Field(
        default="postgresql+asyncpg://crystal:crystal@localhost/crystal"
    )
    
    # AI Configuration (Hybrid approach as per overview)
    # OpenAI API
    openai_api_key: Optional[str] = Field(default=None)
    openai_model: str = "gpt-3.5-turbo"
    openai_max_tokens: int = 1000
    
    # Local Models (Ollama)
    ollama_host: str = "http://localhost:11434"
    default_local_model: str = "llama3.1:8b"
    
    # Model selection strategy
    use_local_first: bool = True
    fallback_to_api: bool = True
    
    # Security & Privacy (as outlined in overview)
    secret_key: str = Field(
        default="change-this-in-production"
    )
    access_token_expire_minutes: int = 30
    algorithm: str = "HS256"
    
    # System Access Permissions
    allow_file_operations: bool = True
    allow_system_commands: bool = False  # Conservative default
    allowed_directories: List[str] = Field(
        default_factory=lambda: [
            str(Path.home() / "Documents"),
            str(Path.home() / "Downloads"),
            str(Path.home() / "Desktop")
        ]
    )
    
    # Task Scheduling
    scheduler_timezone: str = "UTC"
    max_concurrent_tasks: int = 5
    
    # Logging
    log_level: str = "INFO"
    log_file: Optional[str] = "logs/crystal.log"
    structured_logging: bool = True
    
    # File Organization (Ruby assistant capabilities)
    auto_organize_downloads: bool = False
    duplicate_check_enabled: bool = True
    backup_before_organize: bool = True
    
    # Integration Settings
    calendar_integration_enabled: bool = False
    google_calendar_credentials_file: Optional[str] = None
    
    # Development
    reload_on_change: bool = False
    api_docs_enabled: bool = True
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False

# Global settings instance
settings = Settings()

# Assistant-specific configurations
class AssistantConfig:
    """Configuration for individual gemstone assistants."""
    
    RUBY = {
        "name": "Ruby",
        "description": "Main general-purpose assistant",
        "preferred_model": "gpt-4o-mini",
        "fallback_model": "llama3.1:8b",
        "instructions_file": "crystal/assistants/instructions/ruby_instructions.md",
        "capabilities": {
            "schedule_management": "Manage calendars, appointments, and reminders",
            "file_organization": "Organize, search, and manage files and folders", 
            "task_automation": "Create and execute automated workflows",
            "system_monitoring": "Monitor system resources and performance",
            "general_assistance": "Provide helpful information and support"
        }
    }

# Export commonly used settings
DATABASE_URL = settings.database_url
SECRET_KEY = settings.secret_key
DEBUG = settings.debug
