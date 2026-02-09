"""
JARVIX Browser Agent - Autonomous browser automation orchestrator.
Plans goals, executes steps sequentially, handles errors and replanning.
"""

from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field
from pathlib import Path
import os
import time


@dataclass
class AgentResult:
    """Final result of agent execution."""
    success: bool = False
    goal: str = ""
    message: str = ""
    extracted_data: Dict[str, Any] = field(default_factory=dict)
    screenshots: List[str] = field(default_factory=list)
    steps_completed: int = 0
    steps_total: int = 0
    duration: str = ""
    errors: List[str] = field(default_factory=list)
    final_url: str = ""


class BrowserAgent:
    """
    Autonomous browser agent that:
    1. Decomposes goals into action plans
    2. Executes steps sequentially
    3. Verifies each step
    4. Handles errors with retry/replan
    5. Returns results with evidence
    """
    
    def __init__(self):
        self._planner = None
        self._executor = None
        self._state_manager = None
        self.max_retries = 3
    
    @property
    def planner(self):
        """Lazy load goal planner."""
        if self._planner is None:
            from jarvix.core.goal_planner import goal_planner
            self._planner = goal_planner
        return self._planner
    
    @property
    def executor(self):
        """Lazy load action executor."""
        if self._executor is None:
            from jarvix.core.action_executor import action_executor
            self._executor = action_executor
        return self._executor
    
    @property
    def state(self):
        """Lazy load state manager."""
        if self._state_manager is None:
            from jarvix.core.state_manager import state_manager
            self._state_manager = state_manager
        return self._state_manager
    
    def execute(self, goal: str, progress_callback=None) -> AgentResult:
        """
        Execute a goal autonomously.
        
        Args:
            goal: Natural language goal
            progress_callback: Optional callback(step, total, message) for progress updates
            
        Returns:
            AgentResult with execution outcome
        """
        print(f"\n🤖 Browser Agent: Processing goal: '{goal}'")
        
        # Initialize state
        state = self.state.new_execution(goal)
        
        # Step 1: Plan
        if progress_callback:
            progress_callback(0, 0, "🧠 Planning actions...")
        
        print("📝 Step 1: Creating action plan...")
        plan = self.planner.plan(goal)
        
        if not plan.steps:
            return AgentResult(
                success=False,
                goal=goal,
                message="Failed to create action plan",
                errors=["No steps generated for this goal"]
            )
        
        print(f"✅ Plan created with {len(plan.steps)} steps")
        for i, step in enumerate(plan.steps):
            print(f"   {i+1}. {step.action}: {step.description or step.params}")
        
        # Set plan in state
        state.set_plan([{
            "action": s.action,
            "params": s.params
        } for s in plan.steps])
        
        # Step 2: Execute each step
        print("\n🚀 Step 2: Executing plan...")
        
        for i, step in enumerate(plan.steps):
            step_num = i + 1
            print(f"\n   [{step_num}/{len(plan.steps)}] {step.action}: {step.description}")
            
            if progress_callback:
                progress_callback(step_num, len(plan.steps), f"⚡ {step.action}: {step.description or ''}")
            
            # Execute with retry logic
            success = self._execute_step_with_retry(i, step)
            
            if not success:
                # Check if we should abort or continue
                if self._is_critical_step(step.action):
                    print(f"   ❌ Critical step failed, aborting")
                    state.finish(False)
                    break
                else:
                    print(f"   ⚠️ Non-critical step failed, continuing")
                    state.skip_step(i, "Failed after retries")
        
        # Step 3: Finalize
        print("\n📊 Step 3: Finalizing...")
        
        # Get final state
        summary = state.get_summary()
        progress = state.get_progress()
        
        # Determine overall success
        success = progress['failed'] == 0 or progress['completed'] >= progress['total'] * 0.8
        state.finish(success)
        
        result = AgentResult(
            success=success,
            goal=goal,
            message=self._get_result_message(state),
            extracted_data=state.extracted_data,
            screenshots=state.screenshots,
            steps_completed=progress['completed'],
            steps_total=progress['total'],
            duration=state._get_duration(),
            errors=state.errors,
            final_url=self.executor.get_current_url()
        )
        
        self._print_summary(result)
        return result
    
    def _execute_step_with_retry(self, index: int, step) -> bool:
        """Execute a step with retry logic."""
        state = self.state.get_state()
        
        for attempt in range(self.max_retries + 1):
            if attempt > 0:
                print(f"      🔄 Retry {attempt}/{self.max_retries}...")
                state.retry_step(index)
                time.sleep(1)  # Wait before retry
            
            state.start_step(index)
            
            # Execute the action
            result = self.executor.execute(step.action, step.params)
            
            if result.success:
                print(f"      ✅ Success ({result.duration_ms:.0f}ms)")
                state.complete_step(
                    index=index,
                    success=True,
                    data=result.data,
                    screenshot=result.screenshot_path,
                    duration_ms=result.duration_ms
                )
                
                # Update URL if changed
                current_url = self.executor.get_current_url()
                if current_url:
                    state.update_url(current_url)
                
                return True
            else:
                print(f"      ❌ Failed: {result.error}")
                
                if attempt == self.max_retries:
                    state.complete_step(
                        index=index,
                        success=False,
                        error=result.error,
                        duration_ms=result.duration_ms
                    )
        
        return False
    
    def _is_critical_step(self, action: str) -> bool:
        """Determine if a step failure should abort execution."""
        critical_actions = ["navigate"]  # Only navigation is critical
        return action in critical_actions
    
    def _get_result_message(self, state) -> str:
        """Generate result message."""
        summary = state.get_summary()
        
        if state.status == "success":
            msg = f"✅ Goal completed: {state.goal}"
            if state.extracted_data:
                data_str = ", ".join(f"{k}={v}" for k, v in state.extracted_data.items())
                msg += f"\n📊 Data: {data_str}"
        else:
            msg = f"⚠️ Goal partially completed: {state.goal}"
            if state.errors:
                msg += f"\n❌ Issues: {state.errors[-1]}"
        
        return msg
    
    def _print_summary(self, result: AgentResult):
        """Print execution summary."""
        print("\n" + "="*50)
        print("🏁 EXECUTION SUMMARY")
        print("="*50)
        print(f"Goal: {result.goal}")
        print(f"Status: {'✅ Success' if result.success else '❌ Failed'}")
        print(f"Steps: {result.steps_completed}/{result.steps_total} completed")
        print(f"Duration: {result.duration}")
        
        if result.extracted_data:
            print(f"Data: {result.extracted_data}")
        
        if result.screenshots:
            print(f"Screenshots: {len(result.screenshots)} captured")
            print(f"  Last: {result.screenshots[-1]}")
        
        if result.errors:
            print(f"Errors: {result.errors[-1]}")
        
        print("="*50)


# Singleton instance
browser_agent = BrowserAgent()


def execute_goal(goal: str, progress_callback=None) -> AgentResult:
    """Public function to execute a goal."""
    result = browser_agent.execute(goal, progress_callback)
    
    # Update browser context after execution
    from jarvix.core.state_manager import update_browser_context
    update_browser_context(
        url=result.final_url,
        goal=goal,
        screenshot=result.screenshots[-1] if result.screenshots else ""
    )
    
    return result


def execute_continuation(action: str, params: Dict[str, Any]) -> AgentResult:
    """
    Execute a single continuation action on the current browser page.
    Used for commands like "click on X" after a goal has been executed.
    """
    from jarvix.core.state_manager import is_browser_active, update_browser_context
    from jarvix.core.action_executor import action_executor
    
    print(f"\n🔗 Continuation: {action} {params}")
    
    # Check if browser is active
    if not is_browser_active():
        return AgentResult(
            success=False,
            message="❌ No active browser session. Use /agent to start one first."
        )
    
    # Map continuation actions to executor actions
    action_map = {
        "browser_click": "click",
        "browser_scroll": "scroll",
        "browser_type": "type",
        "browser_back": "back",
        "browser_refresh": "refresh"
    }
    
    executor_action = action_map.get(action, action)
    
    # Handle click by text
    if action == "browser_click":
        target = params.get("target", "")
        # Click by visible text
        params = {"text": target}
        executor_action = "click"
    
    # Execute the action
    result = action_executor.execute(executor_action, params)
    
    if result.success:
        print(f"   ✅ {action}: Success")
        
        # Update context
        update_browser_context(
            url=action_executor.get_current_url(),
            action=action
        )
        
        # Take screenshot for confirmation
        screenshot_result = action_executor.execute("screenshot", {"name": f"continuation_{action}"})
        
        return AgentResult(
            success=True,
            message=f"✅ {action} executed successfully",
            screenshots=[screenshot_result.screenshot_path] if screenshot_result.success else [],
            final_url=action_executor.get_current_url()
        )
    else:
        print(f"   ❌ {action}: {result.error}")
        return AgentResult(
            success=False,
            message=f"❌ {action} failed: {result.error}",
            errors=[result.error]
        )


def is_continuation_command(action: str) -> bool:
    """Check if an action is a continuation command."""
    continuation_actions = [
        "browser_click", "browser_scroll", "browser_type", 
        "browser_back", "browser_refresh"
    ]
    return action in continuation_actions
