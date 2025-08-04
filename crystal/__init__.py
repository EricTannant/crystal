"""
Crystal Personal Assistant AI - Package Initialization

This package implements the Crystal personal assistant system as outlined in PROJECT_OVERVIEW.md.
"""

__version__ = "0.1.0"
__author__ = "Crystal Development Team"
__description__ = "A suite of personal AI assistants with gemstone-themed names"

# Import main components for easy access
from crystal.core.orchestrator import CrystalOrchestrator
from crystal.assistants.ruby import RubyAssistant

__all__ = [
    "CrystalOrchestrator",
    "RubyAssistant",
]
