"""
JARVIX Command Router - Central routing for three-tier command processing.

Tier 1: Keyword Matcher (~50ms) - Fast pattern matching
Tier 2: Intent Classifier (~200ms) - Lightweight ML classification
Tier 3: Full LLM (~5-10s) - Complex/ambiguous queries
"""

from typing import Dict, Any, Optional, Tuple
import time


class CommandRouter:
    """
    Routes user commands through the three-tier processing system.
    Starts with fastest (Tier 1), falls through to slower tiers only if needed.
    """
    
    def __init__(self):
        self._keyword_matcher = None
        self._intent_classifier = None
        self._brain = None
        self.last_tier_used = 0
        self.last_response_time = 0
    
    @property
    def keyword_matcher(self):
        """Lazy load keyword matcher."""
        if self._keyword_matcher is None:
            from jarvix.core.keyword_matcher import keyword_matcher
            self._keyword_matcher = keyword_matcher
        return self._keyword_matcher
    
    @property
    def brain(self):
        """Lazy load brain (LLM)."""
        if self._brain is None:
            from jarvix.core.brain import process_command
            self._brain = process_command
        return self._brain
    
    def route(self, text: str) -> Tuple[Optional[Dict[str, Any]], int]:
        """
        Route a command through the three-tier system.
        
        Args:
            text: User input text
            
        Returns:
            Tuple of (command_dict, tier_used)
            tier_used: 1, 2, or 3 indicating which tier resolved the command
        """
        if not text or not text.strip():
            return None, 0
        
        start_time = time.time()
        
        # ==================== TIER 1: Keyword Matcher ====================
        # Fast pattern matching, should handle 60-70% of commands
        try:
            result = self.keyword_matcher.match(text)
            if result:
                self.last_tier_used = 1
                self.last_response_time = (time.time() - start_time) * 1000
                print(f"⚡ Tier 1 match: {result.get('action')} ({self.last_response_time:.0f}ms)")
                return result, 1
        except Exception as e:
            print(f"⚠️ Tier 1 error: {e}")
        
        # ==================== TIER 2: Intent Classifier ====================
        # Lightweight classification (placeholder for now)
        # TODO: Implement intent_classifier.py
        # result = self.intent_classifier.classify(text)
        # if result and result.confidence > 0.85:
        #     self.last_tier_used = 2
        #     return result.command, 2
        
        # ==================== TIER 3: Full LLM ====================
        # Only for complex/ambiguous queries
        try:
            result = self.brain(text)
            if result:
                self.last_tier_used = 3
                self.last_response_time = (time.time() - start_time) * 1000
                print(f"🧠 Tier 3 (LLM): {result.get('action') if isinstance(result, dict) else 'text'} ({self.last_response_time:.0f}ms)")
                return result, 3
        except Exception as e:
            print(f"❌ Tier 3 error: {e}")
        
        return None, 0
    
    def get_stats(self) -> Dict[str, Any]:
        """Return routing statistics."""
        return {
            "last_tier_used": self.last_tier_used,
            "last_response_time_ms": self.last_response_time
        }


# Singleton instance
command_router = CommandRouter()


def route_command(text: str) -> Optional[Dict[str, Any]]:
    """
    Public function to route a command.
    Returns the command dict or None.
    """
    result, tier = command_router.route(text)
    return result


def route_command_with_tier(text: str) -> Tuple[Optional[Dict[str, Any]], int]:
    """
    Route command and return which tier was used.
    Useful for debugging and analytics.
    """
    return command_router.route(text)
