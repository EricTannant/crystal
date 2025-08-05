"""
Crystal Personal Assistant AI - Main Application Entry Point

This module implements the FastAPI web server as outlined in PROJECT_OVERVIEW.md:
- Local PC application with web interface
- WebSocket support for real-time chat
- Authentication system
- Auto-generated API documentation
"""

import asyncio
import uvicorn
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging

from config.settings import settings
from crystal.core.orchestrator import CrystalOrchestrator
from crystal.api.routes import api_router
from crystal.api.websocket import WebSocketManager
from crystal.utils.logging import setup_logging

# Setup logging
setup_logging()
logger = logging.getLogger(__name__)

# WebSocket manager for real-time communication
websocket_manager = WebSocketManager()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager - startup and shutdown events."""
    logger.info("Crystal Personal Assistant AI starting up...")
    
    # Initialize the orchestrator
    orchestrator = CrystalOrchestrator()
    await orchestrator.initialize()
    app.state.orchestrator = orchestrator
    
    logger.info(f"Web interface available at http://{settings.host}:{settings.port}")
    logger.info(f"API documentation at http://{settings.host}:{settings.port}/docs")
    logger.info("Ruby assistant ready for tasks!")
    
    yield
    
    # Cleanup
    logger.info("🔮 Crystal shutting down...")
    await orchestrator.shutdown()

# Create FastAPI application
app = FastAPI(
    title=settings.app_name,
    version=settings.version,
    description="A suite of personal AI assistants with gemstone-themed names",
    docs_url="/docs" if settings.api_docs_enabled else None,
    lifespan=lifespan
)

# CORS middleware for web interface
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", f"http://{settings.host}:{settings.port}"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(api_router, prefix="/api/v1")

# WebSocket endpoint for real-time chat with Ruby
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time chat with assistants."""
    await websocket_manager.connect(websocket)
    try:
        while True:
            # Receive message from client
            data = await websocket.receive_json()
            
            # Get the orchestrator
            orchestrator = app.state.orchestrator
            
            # Process message through appropriate assistant
            assistant_name = data.get("assistant", "ruby")
            message = data.get("message", "")
            
            if message:
                response = await orchestrator.process_message(assistant_name, message)
                await websocket_manager.send_personal_message(response, websocket)
                
    except WebSocketDisconnect:
        websocket_manager.disconnect(websocket)

# Serve static files for web interface
app.mount("/static", StaticFiles(directory="crystal/web/static"), name="static")

# Basic web interface
@app.get("/", response_class=HTMLResponse)
async def get_web_interface():
    """Serve the main web interface."""
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Crystal - Personal Assistant AI</title>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <style>
            body { font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5; }
            .container { max-width: 800px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
            h1 { color: #dc143c; text-align: center; }
            .assistant-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; margin-top: 30px; }
            .assistant-card { background: #f8f9fa; padding: 20px; border-radius: 8px; text-align: center; border-left: 4px solid #dc143c; }
            .chat-container { margin-top: 30px; border: 1px solid #ddd; border-radius: 8px; height: 400px; display: flex; flex-direction: column; }
            .chat-messages { flex: 1; padding: 20px; overflow-y: auto; background: #fafafa; }
            .chat-input { display: flex; border-top: 1px solid #ddd; }
            .chat-input input { flex: 1; padding: 15px; border: none; font-size: 16px; }
            .chat-input button { padding: 15px 25px; background: #dc143c; color: white; border: none; cursor: pointer; }
            .message { margin: 10px 0; padding: 10px; border-radius: 5px; }
            .user-message { background: #e3f2fd; margin-left: 50px; }
            .assistant-message { background: #f3e5f5; margin-right: 50px; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🔮 Crystal Personal Assistant AI</h1>
            <p style="text-align: center; color: #666;">Your Ruby AI assistant for all your personal tasks</p>
            
            <div class="assistant-grid">
                <div class="assistant-card">
                    <h3>💎 Ruby</h3>
                    <p>Main assistant for scheduling, files, system tasks, and general assistance</p>
                </div>
            </div>
            
            <div class="chat-container">
                <div class="chat-messages" id="messages">
                    <div class="message assistant-message">
                        <strong>Ruby:</strong> Hello! I'm Ruby, your personal assistant. How can I help you today?
                    </div>
                </div>
                <div class="chat-input">
                    <input type="text" id="messageInput" placeholder="Type your message to Ruby..." onkeypress="handleKeyPress(event)">
                    <button onclick="sendMessage()">Send</button>
                </div>
            </div>
            
            <div style="margin-top: 20px; text-align: center; color: #666;">
                <p>📚 <a href="/docs">API Documentation</a> | 🔧 <a href="/health">System Status</a></p>
            </div>
        </div>
        
        <script>
            const ws = new WebSocket(`ws://${window.location.host}/ws`);
            const messages = document.getElementById('messages');
            const messageInput = document.getElementById('messageInput');
            
            ws.onmessage = function(event) {
                const response = JSON.parse(event.data);
                addMessage('Ruby', response.message, 'assistant-message');
            };
            
            function addMessage(sender, message, className) {
                const messageDiv = document.createElement('div');
                messageDiv.className = `message ${className}`;
                messageDiv.innerHTML = `<strong>${sender}:</strong> ${message}`;
                messages.appendChild(messageDiv);
                messages.scrollTop = messages.scrollHeight;
            }
            
            function sendMessage() {
                const message = messageInput.value.trim();
                if (message) {
                    addMessage('You', message, 'user-message');
                    ws.send(JSON.stringify({assistant: 'ruby', message: message}));
                    messageInput.value = '';
                }
            }
            
            function handleKeyPress(event) {
                if (event.key === 'Enter') {
                    sendMessage();
                }
            }
        </script>
    </body>
    </html>
    """

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint for monitoring."""
    return {
        "status": "healthy",
        "app": settings.app_name,
        "version": settings.version,
        "assistants": ["ruby"]
    }

def main():
    """Main entry point for the application."""
    logger.info(f"Starting {settings.app_name} v{settings.version}")
    
    uvicorn.run(
        "crystal.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.reload_on_change,
        log_level=settings.log_level.lower()
    )

if __name__ == "__main__":
    main()
