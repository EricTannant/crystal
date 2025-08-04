"""
Ruby Assistant - Main General-Purpose Assistant

Ruby is the primary assistant as defined in PROJECT_OVERVIEW.md.
All functionality and behavior is defined in the instructions file
using the new unified Crystal assistant framework.
"""

from crystal.core.crystal_assistant import CrystalAssistant
from config.settings import AssistantConfig

class RubyAssistant(CrystalAssistant):
    """
    Ruby - Main general-purpose assistant using the unified Crystal framework.
    
    All behavior is defined by ruby_instructions.md file and loaded
    through the unified Crystal assistant infrastructure.
    """
    
    def __init__(self, ai_service, task_scheduler, file_service):
        super().__init__(
            assistant_name="Ruby",
            config=AssistantConfig.RUBY,
            ai_service=ai_service,
            task_scheduler=task_scheduler,
            file_service=file_service
        )
