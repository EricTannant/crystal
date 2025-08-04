"""
Crystal API Routes - FastAPI Endpoints

Implements REST API endpoints as outlined in PROJECT_OVERVIEW.md:
- Assistant communication endpoints
- System management endpoints
- File operation endpoints
- Task scheduling endpoints
"""

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Dict, Any, Optional, List
from datetime import datetime

from crystal.core.orchestrator import CrystalOrchestrator

# API Router
api_router = APIRouter()

# Pydantic models for request/response
class MessageRequest(BaseModel):
    message: str
    assistant: str = "ruby"
    context: Optional[Dict[str, Any]] = None

class MessageResponse(BaseModel):
    message: str
    assistant: str
    timestamp: str
    actions_taken: List[str] = []
    metadata: Dict[str, Any] = {}
    error: bool = False

class TaskRequest(BaseModel):
    task_type: str
    parameters: Dict[str, Any] = {}
    assistant: str = "ruby"

# Dependency to get orchestrator
async def get_orchestrator() -> CrystalOrchestrator:
    """Dependency to get the Crystal orchestrator."""
    # This will be injected by the main app
    from crystal.main import app
    return app.state.orchestrator

@api_router.post("/chat", response_model=MessageResponse)
async def chat_with_assistant(
    request: MessageRequest,
    orchestrator: CrystalOrchestrator = Depends(get_orchestrator)
):
    """Send a message to an assistant and get a response."""
    try:
        response = await orchestrator.process_message(
            assistant_name=request.assistant,
            message=request.message,
            context=request.context
        )
        
        return MessageResponse(**response)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/assistants")
async def list_assistants(orchestrator: CrystalOrchestrator = Depends(get_orchestrator)):
    """Get list of available assistants and their capabilities."""
    try:
        status = await orchestrator.get_assistant_status()
        return {
            "assistants": status.get("assistants", {}),
            "count": len(status.get("assistants", {}))
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/assistants/{assistant_name}/status")
async def get_assistant_status(
    assistant_name: str,
    orchestrator: CrystalOrchestrator = Depends(get_orchestrator)
):
    """Get status of a specific assistant."""
    try:
        status = await orchestrator.get_assistant_status(assistant_name)
        if "error" in status:
            raise HTTPException(status_code=404, detail=status["error"])
        return status
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@api_router.post("/tasks/execute")
async def execute_task(
    request: TaskRequest,
    orchestrator: CrystalOrchestrator = Depends(get_orchestrator)
):
    """Execute a specific task through an assistant."""
    try:
        # Convert task execution to a message
        message = f"Execute task: {request.task_type} with parameters: {request.parameters}"
        
        response = await orchestrator.process_message(
            assistant_name=request.assistant,
            message=message,
            context={"task_execution": True, "task_type": request.task_type}
        )
        
        return response
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/system/health")
async def system_health():
    """System health check endpoint."""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "service": "Crystal Personal Assistant AI"
    }

@api_router.get("/system/info")
async def system_info(orchestrator: CrystalOrchestrator = Depends(get_orchestrator)):
    """Get system information."""
    try:
        status = await orchestrator.get_assistant_status()
        return {
            "app_name": "Crystal Personal Assistant AI",
            "version": "0.1.0",
            "orchestrator": status.get("orchestrator", {}),
            "assistants_count": len(status.get("assistants", {})),
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
