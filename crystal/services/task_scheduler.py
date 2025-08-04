"""
Task Scheduler Service - APScheduler Integration

Implements task scheduling system as outlined in PROJECT_OVERVIEW.md core components.
Handles background tasks, system monitoring, and automated maintenance scripts.
"""

import asyncio
from typing import Dict, Any, List, Optional, Callable
from datetime import datetime, timedelta
import logging

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger
from apscheduler.triggers.date import DateTrigger

from crystal.utils.logging import CrystalLogger
from config.settings import settings

class TaskScheduler:
    """
    Task scheduling service using APScheduler.
    
    Supports the system job management capabilities outlined in PROJECT_OVERVIEW.md:
    - Background task execution
    - System monitoring schedules
    - Automated maintenance scripts
    - Ruby assistant task coordination
    """
    
    def __init__(self):
        self.logger = CrystalLogger("task_scheduler")
        self.scheduler = AsyncIOScheduler(timezone=settings.scheduler_timezone)
        self.is_running = False
        self.active_tasks: Dict[str, Any] = {}
    
    async def start(self) -> None:
        """Start the task scheduler."""
        if self.is_running:
            return
        
        self.scheduler.start()
        self.is_running = True
        
        # Schedule default system tasks
        await self._schedule_default_tasks()
        
        self.logger.system_event("task_scheduler_started")
    
    async def _schedule_default_tasks(self) -> None:
        """Schedule default system monitoring and maintenance tasks."""
        
        # System health check every 5 minutes
        await self.schedule_interval_task(
            task_id="system_health_check",
            func=self._system_health_check,
            minutes=5,
            description="System health monitoring"
        )
        
        # File organization check every hour (if enabled)
        if settings.auto_organize_downloads:
            await self.schedule_interval_task(
                task_id="auto_organize_downloads",
                func=self._auto_organize_downloads,
                hours=1,
                description="Automatic downloads organization"
            )
    
    async def schedule_cron_task(
        self,
        task_id: str,
        func: Callable,
        cron_expression: str,
        args: Optional[List] = None,
        kwargs: Optional[Dict] = None,
        description: str = ""
    ) -> bool:
        """
        Schedule a task using cron expression.
        
        Args:
            task_id: Unique identifier for the task
            func: Function to execute
            cron_expression: Cron expression (e.g., "0 9 * * *" for daily at 9 AM)
            args: Function arguments
            kwargs: Function keyword arguments
            description: Human-readable task description
            
        Returns:
            True if scheduled successfully
        """
        try:
            # Parse cron expression
            trigger = CronTrigger.from_crontab(cron_expression)
            
            self.scheduler.add_job(
                func=func,
                trigger=trigger,
                id=task_id,
                args=args or [],
                kwargs=kwargs or {},
                replace_existing=True,
                max_instances=1
            )
            
            self.active_tasks[task_id] = {
                "type": "cron",
                "expression": cron_expression,
                "description": description,
                "created": datetime.utcnow().isoformat()
            }
            
            self.logger.assistant_action(
                assistant="task_scheduler",
                action="cron_task_scheduled",
                task_id=task_id,
                cron_expression=cron_expression
            )
            
            return True
            
        except Exception as e:
            self.logger.error("cron_task_scheduling_failed", task_id=task_id, error=str(e))
            return False
    
    async def schedule_interval_task(
        self,
        task_id: str,
        func: Callable,
        description: str = "",
        **interval_kwargs
    ) -> bool:
        """
        Schedule a task to run at regular intervals.
        
        Args:
            task_id: Unique identifier for the task
            func: Function to execute
            description: Human-readable task description
            **interval_kwargs: Interval parameters (seconds, minutes, hours, days, weeks)
            
        Returns:
            True if scheduled successfully
        """
        try:
            trigger = IntervalTrigger(**interval_kwargs)
            
            self.scheduler.add_job(
                func=func,
                trigger=trigger,
                id=task_id,
                replace_existing=True,
                max_instances=1
            )
            
            self.active_tasks[task_id] = {
                "type": "interval",
                "interval": interval_kwargs,
                "description": description,
                "created": datetime.utcnow().isoformat()
            }
            
            self.logger.assistant_action(
                assistant="task_scheduler",
                action="interval_task_scheduled",
                task_id=task_id,
                interval=interval_kwargs
            )
            
            return True
            
        except Exception as e:
            self.logger.error("interval_task_scheduling_failed", task_id=task_id, error=str(e))
            return False
    
    async def schedule_one_time_task(
        self,
        task_id: str,
        func: Callable,
        run_date: datetime,
        args: Optional[List] = None,
        kwargs: Optional[Dict] = None,
        description: str = ""
    ) -> bool:
        """
        Schedule a one-time task.
        
        Args:
            task_id: Unique identifier for the task
            func: Function to execute
            run_date: When to run the task
            args: Function arguments
            kwargs: Function keyword arguments
            description: Human-readable task description
            
        Returns:
            True if scheduled successfully
        """
        try:
            trigger = DateTrigger(run_date=run_date)
            
            self.scheduler.add_job(
                func=func,
                trigger=trigger,
                id=task_id,
                args=args or [],
                kwargs=kwargs or {},
                replace_existing=True
            )
            
            self.active_tasks[task_id] = {
                "type": "one_time",
                "run_date": run_date.isoformat(),
                "description": description,
                "created": datetime.utcnow().isoformat()
            }
            
            self.logger.assistant_action(
                assistant="task_scheduler",
                action="one_time_task_scheduled",
                task_id=task_id,
                run_date=run_date.isoformat()
            )
            
            return True
            
        except Exception as e:
            self.logger.error("one_time_task_scheduling_failed", task_id=task_id, error=str(e))
            return False
    
    async def cancel_task(self, task_id: str) -> bool:
        """Cancel a scheduled task."""
        try:
            self.scheduler.remove_job(task_id)
            if task_id in self.active_tasks:
                del self.active_tasks[task_id]
            
            self.logger.assistant_action(
                assistant="task_scheduler",
                action="task_cancelled",
                task_id=task_id
            )
            
            return True
            
        except Exception as e:
            self.logger.error("task_cancellation_failed", task_id=task_id, error=str(e))
            return False
    
    async def get_scheduled_tasks(self) -> Dict[str, Any]:
        """Get list of all scheduled tasks."""
        return {
            "active_tasks": self.active_tasks,
            "scheduler_running": self.is_running,
            "jobs_count": len(self.scheduler.get_jobs())
        }
    
    async def _system_health_check(self) -> None:
        """Default system health check task."""
        self.logger.system_event("system_health_check_executed")
        # TODO: Implement actual system health checks
        # - CPU usage
        # - Memory usage  
        # - Disk space
        # - Process monitoring
    
    async def _auto_organize_downloads(self) -> None:
        """Default auto-organize downloads task."""
        self.logger.system_event("auto_organize_downloads_executed")
        # TODO: Implement actual file organization
        # This would integrate with FileService
    
    async def shutdown(self) -> None:
        """Shutdown the task scheduler."""
        if self.is_running:
            self.scheduler.shutdown(wait=True)
            self.is_running = False
            self.logger.system_event("task_scheduler_shutdown")
