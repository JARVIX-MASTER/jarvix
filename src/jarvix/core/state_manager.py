"""
JARVIX State Manager - Tracks execution progress and agent state.
Maintains history, extracted data, and recovery context.
"""

from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import json


class StepStatus(Enum):
    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"
    RETRYING = "retrying"
    SKIPPED = "skipped"


@dataclass
class StepRecord:
    """Record of a single step execution."""
    step_index: int
    action: str
    params: Dict[str, Any]
    status: StepStatus = StepStatus.PENDING
    error: str = ""
    result_data: Dict[str, Any] = field(default_factory=dict)
    screenshot: str = ""
    retry_count: int = 0
    duration_ms: float = 0
    timestamp: str = ""
    
    def to_dict(self) -> Dict:
        return {
            "step": self.step_index,
            "action": self.action,
            "status": self.status.value,
            "error": self.error,
            "data": self.result_data,
            "screenshot": self.screenshot,
            "retries": self.retry_count,
            "duration_ms": self.duration_ms
        }


@dataclass 
class AgentState:
    """Complete state of the browser agent."""
    
    # Goal information
    goal: str = ""
    total_steps: int = 0
    
    # Execution state
    current_step: int = 0
    status: str = "idle"  # idle, planning, executing, success, failed
    
    # Browser context
    current_url: str = ""
    last_screenshot: str = ""
    
    # Step history
    steps: List[StepRecord] = field(default_factory=list)
    
    # Extracted data (accumulated from extract actions)
    extracted_data: Dict[str, Any] = field(default_factory=dict)
    
    # Screenshots taken
    screenshots: List[str] = field(default_factory=list)
    
    # Error tracking
    errors: List[str] = field(default_factory=list)
    total_retries: int = 0
    
    # Timing
    start_time: str = ""
    end_time: str = ""
    
    def reset(self, goal: str = ""):
        """Reset state for a new execution."""
        self.goal = goal
        self.total_steps = 0
        self.current_step = 0
        self.status = "planning"
        self.current_url = ""
        self.last_screenshot = ""
        self.steps = []
        self.extracted_data = {}
        self.screenshots = []
        self.errors = []
        self.total_retries = 0
        self.start_time = datetime.now().isoformat()
        self.end_time = ""
    
    def set_plan(self, steps: List[Dict]):
        """Set the action plan."""
        self.total_steps = len(steps)
        self.status = "executing"
        for i, step in enumerate(steps):
            self.steps.append(StepRecord(
                step_index=i,
                action=step.get("action", ""),
                params=step.get("params", {})
            ))
    
    def start_step(self, index: int) -> StepRecord:
        """Mark step as running."""
        if 0 <= index < len(self.steps):
            self.steps[index].status = StepStatus.RUNNING
            self.steps[index].timestamp = datetime.now().isoformat()
            self.current_step = index
            return self.steps[index]
        return None
    
    def complete_step(self, index: int, success: bool, 
                     error: str = "", 
                     data: Dict = None,
                     screenshot: str = "",
                     duration_ms: float = 0):
        """Mark step as completed."""
        if 0 <= index < len(self.steps):
            step = self.steps[index]
            step.status = StepStatus.SUCCESS if success else StepStatus.FAILED
            step.error = error
            step.result_data = data or {}
            step.screenshot = screenshot
            step.duration_ms = duration_ms
            
            # Accumulate extracted data
            if data:
                for key, value in data.items():
                    if key not in ["path", "waited_ms", "typed", "key"]:
                        self.extracted_data[key] = value
            
            # Track screenshots
            if screenshot:
                self.screenshots.append(screenshot)
                self.last_screenshot = screenshot
            
            # Track errors
            if error:
                self.errors.append(f"Step {index}: {error}")
    
    def retry_step(self, index: int):
        """Mark step as retrying."""
        if 0 <= index < len(self.steps):
            self.steps[index].status = StepStatus.RETRYING
            self.steps[index].retry_count += 1
            self.total_retries += 1
    
    def skip_step(self, index: int, reason: str = ""):
        """Mark step as skipped."""
        if 0 <= index < len(self.steps):
            self.steps[index].status = StepStatus.SKIPPED
            self.steps[index].error = reason
    
    def finish(self, success: bool):
        """Mark execution as finished."""
        self.status = "success" if success else "failed"
        self.end_time = datetime.now().isoformat()
    
    def update_url(self, url: str):
        """Update current URL."""
        self.current_url = url
    
    def get_progress(self) -> Dict:
        """Get execution progress."""
        completed = sum(1 for s in self.steps if s.status in [StepStatus.SUCCESS, StepStatus.SKIPPED])
        failed = sum(1 for s in self.steps if s.status == StepStatus.FAILED)
        
        return {
            "current": self.current_step + 1,
            "total": self.total_steps,
            "completed": completed,
            "failed": failed,
            "percent": int((completed / self.total_steps * 100)) if self.total_steps > 0 else 0
        }
    
    def get_last_successful_step(self) -> Optional[StepRecord]:
        """Get the last successfully completed step."""
        for step in reversed(self.steps):
            if step.status == StepStatus.SUCCESS:
                return step
        return None
    
    def get_summary(self) -> Dict:
        """Get execution summary."""
        progress = self.get_progress()
        
        return {
            "goal": self.goal,
            "status": self.status,
            "progress": f"{progress['completed']}/{progress['total']} steps",
            "current_url": self.current_url,
            "extracted_data": self.extracted_data,
            "total_retries": self.total_retries,
            "errors": self.errors[-3:] if self.errors else [],  # Last 3 errors
            "last_screenshot": self.last_screenshot,
            "duration": self._get_duration()
        }
    
    def _get_duration(self) -> str:
        """Calculate execution duration."""
        if not self.start_time:
            return "0s"
        
        try:
            start = datetime.fromisoformat(self.start_time)
            end = datetime.fromisoformat(self.end_time) if self.end_time else datetime.now()
            delta = end - start
            seconds = delta.total_seconds()
            
            if seconds < 60:
                return f"{int(seconds)}s"
            else:
                return f"{int(seconds // 60)}m {int(seconds % 60)}s"
        except:
            return "unknown"
    
    def get_step_log(self) -> List[Dict]:
        """Get log of all steps."""
        return [step.to_dict() for step in self.steps]
    
    def to_json(self) -> str:
        """Export state as JSON."""
        return json.dumps(self.get_summary(), indent=2)


class StateManager:
    """Manages agent state across executions."""
    
    def __init__(self):
        self.state = AgentState()
        self.history: List[Dict] = []  # Previous execution summaries
        self.browser_context = BrowserContext()  # Session context for continuations
    
    def new_execution(self, goal: str) -> AgentState:
        """Start a new execution."""
        # Save previous state to history if it has data
        if self.state.goal:
            self.history.append(self.state.get_summary())
            # Keep only last 10 executions
            self.history = self.history[-10:]
        
        self.state.reset(goal)
        return self.state
    
    def get_state(self) -> AgentState:
        """Get current state."""
        return self.state
    
    def get_history(self) -> List[Dict]:
        """Get execution history."""
        return self.history
    
    def get_browser_context(self) -> 'BrowserContext':
        """Get browser session context."""
        return self.browser_context
    
    def update_browser_context(self, url: str = "", goal: str = "", screenshot: str = ""):
        """Update browser context after execution."""
        self.browser_context.update(url=url, goal=goal, screenshot=screenshot)


@dataclass
class BrowserContext:
    """
    Tracks browser session state between commands.
    Enables the agent to remember what happened in previous interactions.
    """
    
    # Browser state
    is_open: bool = False
    current_url: str = ""
    current_domain: str = ""
    
    # Last action context
    last_goal: str = ""
    last_action: str = ""
    last_action_time: Optional[datetime] = None
    
    # Visual context
    last_screenshot: str = ""
    
    # Session data
    extracted_data: Dict[str, Any] = field(default_factory=dict)
    
    # Timeout for context validity (5 minutes)
    CONTEXT_TIMEOUT_SECONDS: int = 300
    
    def update(self, url: str = "", goal: str = "", action: str = "", screenshot: str = "", data: Dict = None):
        """Update context after an action."""
        self.is_open = True
        self.last_action_time = datetime.now()
        
        if url:
            self.current_url = url
            # Extract domain
            try:
                from urllib.parse import urlparse
                parsed = urlparse(url)
                self.current_domain = parsed.netloc.replace("www.", "")
            except:
                pass
        
        if goal:
            self.last_goal = goal
        
        if action:
            self.last_action = action
        
        if screenshot:
            self.last_screenshot = screenshot
        
        if data:
            self.extracted_data.update(data)
    
    def is_active(self) -> bool:
        """Check if browser context is still valid (browser open and recent activity)."""
        if not self.is_open:
            return False
        
        if not self.last_action_time:
            return False
        
        # Check if context is still fresh
        elapsed = (datetime.now() - self.last_action_time).total_seconds()
        return elapsed < self.CONTEXT_TIMEOUT_SECONDS
    
    def mark_closed(self):
        """Mark browser as closed."""
        self.is_open = False
    
    def get_summary(self) -> Dict:
        """Get context summary."""
        return {
            "is_open": self.is_open,
            "is_active": self.is_active(),
            "current_url": self.current_url,
            "current_domain": self.current_domain,
            "last_goal": self.last_goal,
            "last_action": self.last_action
        }
    
    def reset(self):
        """Reset context."""
        self.is_open = False
        self.current_url = ""
        self.current_domain = ""
        self.last_goal = ""
        self.last_action = ""
        self.last_action_time = None
        self.last_screenshot = ""
        self.extracted_data = {}


# Singleton instance
state_manager = StateManager()


# Convenience functions
def get_browser_context() -> BrowserContext:
    """Get the current browser context."""
    return state_manager.get_browser_context()


def is_browser_active() -> bool:
    """Check if browser is currently active."""
    return state_manager.browser_context.is_active()


def update_browser_context(**kwargs):
    """Update browser context."""
    state_manager.browser_context.update(**kwargs)
