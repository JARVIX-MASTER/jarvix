"""
JARVIX Action Executor - Executes browser actions via Playwright.
Handles individual step execution with verification.
"""

from typing import Dict, Any, Optional
from dataclasses import dataclass, field
from pathlib import Path
import os
import time


@dataclass
class ActionResult:
    """Result of executing an action."""
    success: bool = False
    action: str = ""
    error: str = ""
    data: Dict[str, Any] = field(default_factory=dict)
    screenshot_path: str = ""
    duration_ms: float = 0


class ActionExecutor:
    """Executes browser actions with Playwright."""
    
    def __init__(self):
        self._web_automation = None
        self.screenshot_dir = Path(os.environ.get('TEMP', '.')) / 'jarvix_agent'
        self.screenshot_dir.mkdir(exist_ok=True)
    
    @property
    def web_automation(self):
        """Lazy load web automation module."""
        if self._web_automation is None:
            from jarvix.features.web_automation import web_automation
            self._web_automation = web_automation
        return self._web_automation
    
    def execute(self, action: str, params: Dict[str, Any]) -> ActionResult:
        """
        Execute a single browser action.
        
        Args:
            action: Action type (navigate, click, type, etc.)
            params: Action parameters
            
        Returns:
            ActionResult with success status and any extracted data
        """
        start_time = time.time()
        result = ActionResult(action=action)
        
        try:
            # Ensure browser is started
            if not self.web_automation.is_running:
                self.web_automation.ensure_browser()
                time.sleep(1)
            
            # Execute based on action type
            if action == "navigate":
                result = self._navigate(params)
            elif action == "click":
                result = self._click(params)
            elif action == "type":
                result = self._type(params)
            elif action == "press_key":
                result = self._press_key(params)
            elif action == "scroll":
                result = self._scroll(params)
            elif action == "wait_for":
                result = self._wait_for(params)
            elif action == "wait":
                result = self._wait(params)
            elif action == "extract":
                result = self._extract(params)
            elif action == "screenshot":
                result = self._screenshot(params)
            elif action == "read_dom":
                result = self._read_dom(params)
            else:
                result.error = f"Unknown action: {action}"
            
        except Exception as e:
            result.error = str(e)
        
        result.duration_ms = (time.time() - start_time) * 1000
        result.action = action
        return result
    
    def _navigate(self, params: Dict) -> ActionResult:
        """Navigate to URL."""
        url = params.get("url", "")
        if not url:
            return ActionResult(error="No URL provided")
        
        # Ensure URL has protocol
        if not url.startswith("http"):
            url = "https://" + url
        
        try:
            self.web_automation.page.goto(url, wait_until="domcontentloaded", timeout=30000)
            return ActionResult(
                success=True,
                data={"url": self.web_automation.page.url}
            )
        except Exception as e:
            error_str = str(e).lower()
            # Detect if browser was closed externally
            if "closed" in error_str or "target page" in error_str or "context" in error_str:
                # Try to restart browser
                try:
                    print("🔄 Browser was closed, restarting...")
                    self.web_automation.stop_browser()
                    self.web_automation.start_browser()
                    time.sleep(1)
                    self.web_automation.page.goto(url, wait_until="domcontentloaded", timeout=30000)
                    return ActionResult(
                        success=True,
                        data={"url": self.web_automation.page.url}
                    )
                except Exception as restart_error:
                    return ActionResult(error=f"Browser restart failed: {restart_error}")
            return ActionResult(error=f"Navigation failed: {e}")
    
    def _click(self, params: Dict) -> ActionResult:
        """Click an element."""
        selector = params.get("selector", "")
        text = params.get("text", "")
        
        try:
            if text:
                # Click by visible text
                locator = self.web_automation.page.get_by_text(text, exact=False).first
            else:
                # Click by selector
                locator = self.web_automation.page.locator(selector).first
            
            locator.click(timeout=10000)
            return ActionResult(success=True)
        except Exception as e:
            return ActionResult(error=f"Click failed: {e}")
    
    def _type(self, params: Dict) -> ActionResult:
        """Type text into an input."""
        selector = params.get("selector", "")
        text = params.get("text", "")
        
        if not text:
            return ActionResult(error="No text to type")
        
        try:
            locator = self.web_automation.page.locator(selector).first
            locator.click(timeout=5000)
            locator.fill("")  # Clear first
            locator.fill(text)
            return ActionResult(success=True, data={"typed": text})
        except Exception as e:
            return ActionResult(error=f"Type failed: {e}")
    
    def _press_key(self, params: Dict) -> ActionResult:
        """Press a keyboard key."""
        key = params.get("key", "Enter")
        
        try:
            self.web_automation.page.keyboard.press(key)
            return ActionResult(success=True, data={"key": key})
        except Exception as e:
            return ActionResult(error=f"Key press failed: {e}")
    
    def _scroll(self, params: Dict) -> ActionResult:
        """Scroll the page."""
        direction = params.get("direction", "down")
        amount = params.get("amount", 500)
        
        try:
            if direction == "down":
                self.web_automation.page.mouse.wheel(0, amount)
            else:
                self.web_automation.page.mouse.wheel(0, -amount)
            return ActionResult(success=True)
        except Exception as e:
            return ActionResult(error=f"Scroll failed: {e}")
    
    def _wait_for(self, params: Dict) -> ActionResult:
        """Wait for an element to appear."""
        selector = params.get("selector", "")
        timeout = params.get("timeout", 10000)
        
        try:
            self.web_automation.page.wait_for_selector(selector, timeout=timeout)
            return ActionResult(success=True)
        except Exception as e:
            return ActionResult(error=f"Wait timed out: {e}")
    
    def _wait(self, params: Dict) -> ActionResult:
        """Wait for specified milliseconds."""
        ms = params.get("ms", 1000)
        time.sleep(ms / 1000)
        return ActionResult(success=True, data={"waited_ms": ms})
    
    def _extract(self, params: Dict) -> ActionResult:
        """Extract data from an element."""
        selector = params.get("selector", "")
        attribute = params.get("attribute", "text")
        save_as = params.get("save_as", "extracted")
        
        try:
            locator = self.web_automation.page.locator(selector).first
            
            if attribute == "text":
                value = locator.inner_text()
            elif attribute == "href":
                value = locator.get_attribute("href")
            elif attribute == "src":
                value = locator.get_attribute("src")
            else:
                value = locator.get_attribute(attribute)
            
            return ActionResult(
                success=True,
                data={save_as: value, "raw_value": value}
            )
        except Exception as e:
            return ActionResult(error=f"Extract failed: {e}")
    
    def _screenshot(self, params: Dict) -> ActionResult:
        """Take a screenshot."""
        name = params.get("name", "screenshot")
        filename = f"{name}_{int(time.time())}.png"
        filepath = self.screenshot_dir / filename
        
        try:
            self.web_automation.page.screenshot(path=str(filepath))
            return ActionResult(
                success=True,
                screenshot_path=str(filepath),
                data={"path": str(filepath)}
            )
        except Exception as e:
            return ActionResult(error=f"Screenshot failed: {e}")
    
    def _read_dom(self, params: Dict) -> ActionResult:
        """Read DOM content."""
        selector = params.get("selector", "body")
        
        try:
            content = self.web_automation.page.locator(selector).first.inner_text()
            return ActionResult(
                success=True,
                data={"content": content[:2000]}  # Limit length
            )
        except Exception as e:
            return ActionResult(error=f"Read DOM failed: {e}")
    
    def get_current_url(self) -> str:
        """Get current page URL."""
        try:
            return self.web_automation.page.url
        except:
            return ""
    
    def is_browser_open(self) -> bool:
        """Check if browser is running."""
        return self.web_automation.is_running


# Singleton instance
action_executor = ActionExecutor()
