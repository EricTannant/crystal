"""
Crystal Personal Assistant AI - Logging Utilities

Implements structured logging as specified in PROJECT_OVERVIEW.md core components.
"""

import logging
import sys
from pathlib import Path
from typing import Optional
import structlog

from config.settings import settings

def setup_logging() -> None:
    """
    Setup structured logging for Crystal AI system.
    
    Configures both standard Python logging and structured logging
    based on settings in PROJECT_OVERVIEW.md.
    """
    
    # Create logs directory if it doesn't exist
    if settings.log_file:
        log_path = Path(settings.log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Configure standard logging
    logging.basicConfig(
        level=getattr(logging, settings.log_level.upper()),
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler(settings.log_file) if settings.log_file else logging.NullHandler()
        ]
    )
    
    # Configure structured logging if enabled
    if settings.structured_logging:
        structlog.configure(
            processors=[
                structlog.stdlib.filter_by_level,
                structlog.stdlib.add_logger_name,
                structlog.stdlib.add_log_level,
                structlog.stdlib.PositionalArgumentsFormatter(),
                structlog.processors.TimeStamper(fmt="iso"),
                structlog.processors.StackInfoRenderer(),
                structlog.processors.format_exc_info,
                structlog.processors.UnicodeDecoder(),
                structlog.processors.JSONRenderer()
            ],
            context_class=dict,
            logger_factory=structlog.stdlib.LoggerFactory(),
            wrapper_class=structlog.stdlib.BoundLogger,
            cache_logger_on_first_use=True,
        )

def get_logger(name: str) -> structlog.BoundLogger:
    """Get a structured logger instance."""
    return structlog.get_logger(name)

class CrystalLogger:
    """
    Crystal-specific logger with assistant context.
    
    Provides logging methods specific to Crystal AI operations
    with automatic context injection.
    """
    
    def __init__(self, component: str):
        self.logger = get_logger(component)
        self.component = component
    
    def assistant_action(self, assistant: str, action: str, **kwargs):
        """Log an assistant action."""
        self.logger.info(
            "assistant_action",
            assistant=assistant,
            action=action,
            component=self.component,
            **kwargs
        )
    
    def system_event(self, event: str, **kwargs):
        """Log a system event."""
        self.logger.info(
            "system_event",
            event=event,
            component=self.component,
            **kwargs
        )
    
    def error(self, message: str, **kwargs):
        """Log an error with context."""
        self.logger.error(
            message,
            component=self.component,
            **kwargs
        )
    
    def warning(self, message: str, **kwargs):
        """Log a warning with context."""
        self.logger.warning(
            message,
            component=self.component,
            **kwargs
        )
    
    def info(self, message: str, **kwargs):
        """Log an info message with context."""
        self.logger.info(
            message,
            component=self.component,
            **kwargs
        )
    
    def debug(self, message: str, **kwargs):
        """Log a debug message with context."""
        self.logger.debug(
            message,
            component=self.component,
            **kwargs
        )
