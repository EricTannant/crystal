"""
CLI Interface - Command Line Access

Implements CLI interface using Typer as outlined in PROJECT_OVERVIEW.md.
Provides command-line access to all Crystal assistants.
"""

import asyncio
from typing import Optional
import typer
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn

from crystal.core.orchestrator import CrystalOrchestrator
from config.settings import settings

# Initialize Typer app and Rich console
app = typer.Typer(name="crystal", help="Crystal Personal Assistant AI - CLI Interface")
console = Console()

# Global orchestrator instance
orchestrator: Optional[CrystalOrchestrator] = None

async def get_orchestrator() -> CrystalOrchestrator:
    """Get initialized orchestrator instance."""
    global orchestrator
    if not orchestrator:
        orchestrator = CrystalOrchestrator()
        await orchestrator.initialize()
    return orchestrator

@app.command()
def chat(
    message: str = typer.Argument(..., help="Message to send to the assistant"),
    assistant: str = typer.Option("ruby", "--assistant", "-a", help="Assistant to chat with (ruby, emerald, diamond, sapphire)"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Show detailed response information")
):
    """Chat with a Crystal assistant."""
    async def _chat():
        orch = await get_orchestrator()
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
            transient=True,
        ) as progress:
            task = progress.add_task(f"Chatting with {assistant.title()}...", total=None)
            
            response = await orch.process_message(assistant, message)
            
            progress.remove_task(task)
        
        # Display response
        if response.get("error"):
            console.print(f"[red]Error:[/red] {response['message']}")
        else:
            console.print(Panel(
                response["message"],
                title=f"💎 {assistant.title()} Assistant",
                border_style="blue"
            ))
            
            if verbose and response.get("actions_taken"):
                console.print("\n[dim]Actions taken:[/dim]")
                for action in response["actions_taken"]:
                    console.print(f"  • {action}")
    
    asyncio.run(_chat())

@app.command()
def ruby(message: str = typer.Argument(..., help="Message for Ruby assistant")):
    """Quick access to Ruby assistant."""
    chat(message, "ruby")

@app.command()
def emerald(message: str = typer.Argument(..., help="Message for Emerald assistant")):
    """Quick access to Emerald assistant (development/coding)."""
    chat(message, "emerald")

@app.command()
def diamond(message: str = typer.Argument(..., help="Message for Diamond assistant")):
    """Quick access to Diamond assistant (data analysis)."""
    chat(message, "diamond")

@app.command()
def sapphire(message: str = typer.Argument(..., help="Message for Sapphire assistant")):
    """Quick access to Sapphire assistant (communication)."""
    chat(message, "sapphire")

@app.command()
def status():
    """Show status of all assistants and services."""
    async def _status():
        orch = await get_orchestrator()
        status_info = await orch.get_assistant_status()
        
        # Create status table
        table = Table(title="🔮 Crystal Assistant Status")
        table.add_column("Assistant", style="cyan", no_wrap=True)
        table.add_column("Status", style="green")
        table.add_column("Capabilities", style="yellow")
        table.add_column("Model", style="magenta")
        
        for name, info in status_info.get("assistants", {}).items():
            status = "🟢 Active" if info.get("active") else "🔴 Inactive"
            capabilities = ", ".join(info.get("capabilities", {}).keys())
            model = info.get("model", "Unknown")
            
            table.add_row(name.title(), status, capabilities, model)
        
        console.print(table)
        
        # Show orchestrator status
        orch_info = status_info.get("orchestrator", {})
        console.print(f"\n[dim]Orchestrator:[/dim] {'✅ Initialized' if orch_info.get('initialized') else '❌ Not initialized'}")
        console.print(f"[dim]Assistants loaded:[/dim] {orch_info.get('assistants_count', 0)}")
    
    asyncio.run(_status())

@app.command()
def organize(
    directory: str = typer.Argument(..., help="Directory path to organize"),
    create_subdirs: bool = typer.Option(True, "--subdirs/--no-subdirs", help="Create category subdirectories")
):
    """Organize files in a directory using Ruby assistant."""
    async def _organize():
        orch = await get_orchestrator()
        
        console.print(f"🗂️  Organizing directory: {directory}")
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
            transient=True,
        ) as progress:
            task = progress.add_task("Organizing files...", total=None)
            
            # Use Ruby assistant to organize files
            message = f"organize the directory {directory}"
            if create_subdirs:
                message += " and create subdirectories for each file type"
            
            response = await orch.process_message("ruby", message)
            progress.remove_task(task)
        
        if response.get("error"):
            console.print(f"[red]Error:[/red] {response['message']}")
        else:
            console.print(f"[green]✅ Organization complete![/green]")
            console.print(response["message"])
    
    asyncio.run(_organize())

@app.command()
def schedule(
    task_description: str = typer.Argument(..., help="Description of the task to schedule"),
    when: str = typer.Option("now", "--when", "-w", help="When to run the task (e.g., 'daily at 9am', 'every hour', 'tomorrow at 2pm')")
):
    """Schedule a task using Ruby assistant."""
    async def _schedule():
        orch = await get_orchestrator()
        
        message = f"schedule a task: {task_description} to run {when}"
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
            transient=True,
        ) as progress:
            task = progress.add_task("Scheduling task...", total=None)
            
            response = await orch.process_message("ruby", message)
            progress.remove_task(task)
        
        if response.get("error"):
            console.print(f"[red]Error:[/red] {response['message']}")
        else:
            console.print(f"[green]✅ Task scheduled![/green]")
            console.print(response["message"])
    
    asyncio.run(_schedule())

@app.command()
def config():
    """Show current configuration."""
    console.print(Panel("🔮 Crystal Configuration", border_style="blue"))
    
    table = Table()
    table.add_column("Setting", style="cyan")
    table.add_column("Value", style="yellow")
    
    table.add_row("App Name", settings.app_name)
    table.add_row("Version", settings.version)
    table.add_row("Host", settings.host)
    table.add_row("Port", str(settings.port))
    table.add_row("Debug Mode", "Yes" if settings.debug else "No")
    table.add_row("OpenAI API", "Configured" if settings.openai_api_key else "Not configured")
    table.add_row("Ollama Host", settings.ollama_host)
    table.add_row("Default Local Model", settings.default_local_model)
    table.add_row("File Operations", "Enabled" if settings.allow_file_operations else "Disabled")
    
    console.print(table)

@app.command()
def web():
    """Start the web interface."""
    console.print("🌐 Starting Crystal web interface...")
    console.print(f"📍 Web UI will be available at: http://{settings.host}:{settings.port}")
    console.print(f"📚 API docs will be available at: http://{settings.host}:{settings.port}/docs")
    console.print("\n[dim]Press Ctrl+C to stop the server[/dim]")
    
    # Import and run the main application
    from crystal.main import main
    main()

def main():
    """Main CLI entry point."""
    app()

if __name__ == "__main__":
    main()
