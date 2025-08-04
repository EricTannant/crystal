"""
Crystal Personal Assistant AI - Core Orchestrator

Main orchestration engine as specified in PROJECT_OVERVIEW.md core components.
Manages Ruby assistant and coordinates system activities.
"""

import asyncio
from typing import Dict, Optional, Any
import logging
from datetime import datetime

from crystal.utils.logging import CrystalLogger
from crystal.assistants.ruby import RubyAssistant
from crystal.services.ai_service import AIService
from crystal.services.task_scheduler import TaskScheduler
from crystal.services.file_service import FileService
from config.settings import settings, AssistantConfig

class CrystalOrchestrator:
    """
    Main orchestration engine for Crystal Personal Assistant AI.
    
    Coordinates all gemstone assistants and manages system resources
    as outlined in the project overview.
    """
    
    def __init__(self):
        self.logger = CrystalLogger("orchestrator")
        self.assistants: Dict[str, Any] = {}
        self.ai_service: Optional[AIService] = None
        self.task_scheduler: Optional[TaskScheduler] = None
        self.file_service: Optional[FileService] = None
        self.is_initialized = False
    
    async def initialize(self) -> None:
        """Initialize the Crystal orchestrator and all services."""
        if self.is_initialized:
            return
        
        self.logger.system_event("orchestrator_startup")
        
        try:
            # Initialize core services
            self.ai_service = AIService()
            await self.ai_service.initialize()
            
            self.task_scheduler = TaskScheduler()
            await self.task_scheduler.start()
            
            self.file_service = FileService()
            
            # Initialize assistants based on PROJECT_OVERVIEW.md specifications
            await self._initialize_assistants()
            
            self.is_initialized = True
            self.logger.system_event("orchestrator_ready", assistants=list(self.assistants.keys()))
            
        except Exception as e:
            self.logger.error("orchestrator_initialization_failed", error=str(e))
            raise
    
    async def _initialize_assistants(self) -> None:
        """Initialize Ruby assistant."""
        
        # Ruby - Main general-purpose assistant
        self.assistants["ruby"] = RubyAssistant(
            ai_service=self.ai_service,
            task_scheduler=self.task_scheduler,
            file_service=self.file_service
        )
        await self.assistants["ruby"].initialize()
        
        self.logger.info("assistants_initialized", count=len(self.assistants))
    
    async def process_message(self, assistant_name: str, message: str, context: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Process a message through the specified assistant.
        
        Args:
            assistant_name: Name of the assistant to use (ruby for now)
            message: User message to process
            context: Optional context for the conversation
            
        Returns:
            Response dictionary with assistant's reply and metadata
        """
        if not self.is_initialized:
            await self.initialize()
        
        assistant_name = assistant_name.lower()
        
        if assistant_name not in self.assistants:
            return {
                "message": f"Assistant '{assistant_name}' not found. Available: {', '.join(self.assistants.keys())}",
                "assistant": "system",
                "error": True
            }
        
        assistant = self.assistants[assistant_name]
        
        self.logger.assistant_action(
            assistant=assistant_name,
            action="process_message",
            message_length=len(message)
        )
        
        try:
            response = await assistant.process_message(message, context or {})
            
            self.logger.assistant_action(
                assistant=assistant_name,
                action="message_processed",
                response_length=len(response.get("message", ""))
            )
            
            return {
                "message": response.get("message", ""),
                "assistant": assistant_name,
                "timestamp": datetime.utcnow().isoformat(),
                "actions_taken": response.get("actions", []),
                "metadata": response.get("metadata", {})
            }
            
        except Exception as e:
            self.logger.error(
                "message_processing_failed",
                assistant=assistant_name,
                error=str(e)
            )
            
            return {
                "message": f"Sorry, I encountered an error: {str(e)}",
                "assistant": assistant_name,
                "error": True,
                "timestamp": datetime.utcnow().isoformat()
            }
    
    async def get_assistant_status(self, assistant_name: Optional[str] = None) -> Dict[str, Any]:
        """Get status of assistants."""
        if assistant_name:
            if assistant_name in self.assistants:
                return await self.assistants[assistant_name].get_status()
            else:
                return {"error": f"Assistant '{assistant_name}' not found"}
        
        # Return status of all assistants
        status = {}
        for name, assistant in self.assistants.items():
            status[name] = await assistant.get_status()
        
        return {
            "orchestrator": {
                "initialized": self.is_initialized,
                "assistants_count": len(self.assistants)
            },
            "assistants": status
        }
    
    async def shutdown(self) -> None:
        """Shutdown the orchestrator and all services."""
        self.logger.system_event("orchestrator_shutdown")
        
        # Shutdown assistants
        for name, assistant in self.assistants.items():
            try:
                await assistant.shutdown()
                self.logger.info("assistant_shutdown", assistant=name)
            except Exception as e:
                self.logger.error("assistant_shutdown_failed", assistant=name, error=str(e))
        
        # Shutdown services
        if self.task_scheduler:
            await self.task_scheduler.shutdown()
        
        if self.ai_service:
            await self.ai_service.shutdown()
        
        self.is_initialized = False
        self.logger.system_event("orchestrator_shutdown_complete")
