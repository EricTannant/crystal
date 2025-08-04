"""
Crystal Assistant Class - Unified Foundation for All Assistants

A complete modular assistant that can be configured entirely through
instruction files and configuration settings. This replaces both
BaseAssistant and GeneralizedAssistant with a single, clean implementation.
"""

from typing import Dict, Any, List, Optional
import asyncio
from datetime import datetime
from pathlib import Path

from crystal.utils.logging import CrystalLogger

class CrystalAssistant:
    """
    Unified Crystal assistant class that can be configured entirely through external files.
    
    This class provides a complete modular framework where:
    - All behavior is defined by instruction files
    - Capabilities are configured through settings
    - Personality and responses are entirely customizable
    - No hardcoded functionality - everything is data-driven
    """
    
    def __init__(self, assistant_name: str, config: Dict[str, Any], ai_service, task_scheduler, file_service):
        self.name = assistant_name
        self.config = config
        self.ai_service = ai_service
        self.task_scheduler = task_scheduler
        self.file_service = file_service
        self.is_active = False
        self.logger = CrystalLogger(f"{assistant_name.lower()}_assistant")
        
        # Instructions and configuration
        self.instructions = ""
        self.capabilities: Dict[str, Any] = {}
        self.personality_traits: Dict[str, Any] = {}
        
        # Base capabilities all assistants have
        self.base_capabilities = {
            "natural_language_processing": True,
            "task_execution": True,
            "status_reporting": True,
            "instruction_reloading": True
        }
        
    async def initialize(self) -> None:
        """Initialize the assistant with all configuration from external files."""
        self.is_active = True
        await self._load_instructions()
        await self._load_capabilities()
        
        self.logger.assistant_action(
            assistant=self.name.lower(),
            action="initialized",
            instructions_loaded=len(self.instructions) > 0,
            capabilities_count=len(self.capabilities)
        )
    
    async def _load_instructions(self) -> None:
        """Load assistant instructions from the configured file."""
        try:
            instructions_file = self.config.get("instructions_file")
            if not instructions_file:
                self.logger.warning("no_instructions_file_configured")
                self.instructions = f"I am {self.name}, your assistant. How can I help you today?"
                return
            
            instructions_path = Path(instructions_file)
            if instructions_path.exists():
                with open(instructions_path, 'r', encoding='utf-8') as f:
                    self.instructions = f.read()
                
                self.logger.info(
                    "instructions_loaded",
                    file_path=str(instructions_path),
                    instruction_length=len(self.instructions)
                )
            else:
                self.logger.warning(
                    "instructions_file_not_found",
                    file_path=str(instructions_path)
                )
                self.instructions = f"I am {self.name}, your assistant. How can I help you today?"
                
        except Exception as e:
            self.logger.error("instructions_loading_failed", error=str(e))
            self.instructions = f"I am {self.name}, your assistant. How can I help you today?"
    
    async def _load_capabilities(self) -> None:
        """Load capabilities from configuration or instruction parsing."""
        try:
            # Load capabilities from config if available
            self.capabilities = self.config.get("capabilities", {})
            
            # Parse personality traits from instructions if they exist
            if "personality" in self.instructions.lower() or "traits" in self.instructions.lower():
                self.personality_traits = self._parse_personality_from_instructions()
            
            self.logger.info(
                "capabilities_loaded",
                capabilities=list(self.capabilities.keys()),
                personality_traits=list(self.personality_traits.keys())
            )
            
        except Exception as e:
            self.logger.error("capabilities_loading_failed", error=str(e))
            self.capabilities = {}
            self.personality_traits = {}
    
    def _parse_personality_from_instructions(self) -> Dict[str, Any]:
        """Parse personality traits from instruction text."""
        traits = {}
        
        lines = self.instructions.split('\n')
        in_personality_section = False
        
        for line in lines:
            line = line.strip()
            if 'personality' in line.lower() or 'traits' in line.lower():
                in_personality_section = True
                continue
            
            if in_personality_section and line.startswith('-'):
                # Parse bullet points as traits
                trait = line[1:].strip()
                if ':' in trait:
                    key, value = trait.split(':', 1)
                    traits[key.strip().lower().replace(' ', '_')] = value.strip()
                else:
                    traits[trait.lower().replace(' ', '_')] = True
                    
            elif in_personality_section and line and not line.startswith('#'):
                # Stop parsing when we hit a new section
                break
        
        return traits
    
    async def process_message(self, message: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process user message using current instructions and configuration.
        
        This method is completely data-driven - all behavior comes from
        the instruction file and configuration, not hardcoded logic.
        """
        self.logger.assistant_action(
            assistant=self.name.lower(),
            action="processing_message",
            message_preview=message[:50]
        )
        
        # Reload instructions to get any updates
        await self._load_instructions()
        
        # Build context-aware prompt
        full_prompt = await self._build_context_prompt(message, context)
        
        try:
            # Generate response using AI service
            ai_response = await self.ai_service.generate_response(
                message=full_prompt,
                model=self.config.get("preferred_model", "llama3.1:8b"),
                context=context
            )
            
            # Post-process response if needed
            processed_response = await self._post_process_response(ai_response, context)
            
            return {
                "message": processed_response,
                "actions": ["message_processed"],
                "metadata": {
                    "assistant": self.name.lower(),
                    "instructions_version": len(self.instructions),
                    "capabilities_used": list(self.capabilities.keys()),
                    "processing_time": datetime.utcnow().isoformat()
                }
            }
            
        except Exception as e:
            self.logger.error("message_processing_failed", error=str(e))
            
            # Fallback response
            return {
                "message": f"I apologize, but I encountered an error processing your request. Please try again or contact support if the problem persists.",
                "actions": ["error_occurred"],
                "metadata": {
                    "assistant": self.name.lower(),
                    "error": str(e),
                    "processing_time": datetime.utcnow().isoformat()
                }
            }
    
    async def _build_context_prompt(self, message: str, context: Dict[str, Any]) -> str:
        """Build a comprehensive prompt with instructions and context."""
        prompt_parts = []
        
        # Add main instructions
        if self.instructions:
            prompt_parts.append(self.instructions)
        
        # Add capability context
        if self.capabilities:
            capabilities_text = "Available capabilities:\n" + "\n".join([
                f"- {cap}: {desc}" for cap, desc in self.capabilities.items()
            ])
            prompt_parts.append(capabilities_text)
        
        # Add personality context
        if self.personality_traits:
            personality_text = "Personality traits to embody:\n" + "\n".join([
                f"- {trait}: {value}" for trait, value in self.personality_traits.items()
            ])
            prompt_parts.append(personality_text)
        
        # Add conversation context if available
        if context.get("conversation_history"):
            prompt_parts.append("Recent conversation context:")
            for entry in context["conversation_history"][-3:]:  # Last 3 exchanges
                prompt_parts.append(f"User: {entry.get('user', '')}")
                prompt_parts.append(f"{self.name}: {entry.get('assistant', '')}")
        
        # Add current message
        prompt_parts.extend([
            "---",
            f"Current user message: {message}",
            f"Please respond as {self.name}, following all instructions and embodying the personality traits above."
        ])
        
        return "\n\n".join(prompt_parts)
    
    async def _post_process_response(self, response: str, context: Dict[str, Any]) -> str:
        """Post-process the AI response if needed."""
        return response.strip()
    
    async def get_status(self) -> Dict[str, Any]:
        """Get comprehensive status of this assistant."""
        return {
            "name": self.name,
            "active": self.is_active,
            "model": self.config.get("preferred_model", "llama3.1:8b"),
            "instructions_loaded": len(self.instructions) > 0,
            "instructions_length": len(self.instructions),
            "capabilities": dict(self.capabilities),
            "personality_traits": dict(self.personality_traits),
            "configuration_file": self.config.get("instructions_file"),
            "description": f"Crystal modular assistant - behavior defined by configuration files"
        }
    
    def get_capabilities(self) -> Dict[str, Any]:
        """Get all capabilities (base + specific)."""
        all_capabilities = self.base_capabilities.copy()
        all_capabilities.update(self.capabilities)
        return all_capabilities
    
    async def execute_task(self, task_type: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a specific task with parameters."""
        self.logger.assistant_action(
            assistant=self.name.lower(),
            action="task_execution_started",
            task_type=task_type
        )
        
        try:
            if task_type == "status_check":
                result = await self.get_status()
            elif task_type == "capability_list":
                result = self.get_capabilities()
            elif task_type == "reload_instructions":
                await self.reload_configuration()
                result = {"reloaded": True, "instructions_length": len(self.instructions)}
            else:
                raise NotImplementedError(f"Task type '{task_type}' not implemented for {self.name}")
            
            self.logger.assistant_action(
                assistant=self.name.lower(),
                action="task_execution_completed",
                task_type=task_type
            )
            
            return {
                "success": True,
                "result": result,
                "task_type": task_type,
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            self.logger.error(
                "task_execution_failed",
                task_type=task_type,
                error=str(e)
            )
            
            return {
                "success": False,
                "error": str(e),
                "task_type": task_type,
                "timestamp": datetime.utcnow().isoformat()
            }
    
    async def reload_configuration(self) -> None:
        """Reload all configuration from files - useful for live updates."""
        await self._load_instructions()
        await self._load_capabilities()
        
        self.logger.assistant_action(
            assistant=self.name.lower(),
            action="configuration_reloaded",
            instructions_length=len(self.instructions),
            capabilities_count=len(self.capabilities)
        )
    
    async def update_capability(self, capability: str, enabled: bool, description: Optional[str] = None) -> None:
        """Dynamically update a capability."""
        if enabled:
            self.capabilities[capability] = description or True
        else:
            self.capabilities.pop(capability, None)
        
        self.logger.assistant_action(
            assistant=self.name.lower(),
            action="capability_updated",
            capability=capability,
            enabled=enabled
        )
    
    async def shutdown(self) -> None:
        """Shutdown the assistant gracefully."""
        self.is_active = False
        self.logger.assistant_action(
            assistant=self.name.lower(),
            action="shutdown_complete"
        )
