"""
JARVIX Keyword Matcher - Tier 1 of Command Processing
Fast pattern matching with synonyms for instant command resolution.
"""

import re
from typing import Dict, List, Optional, Any, Tuple


# ==================== SYNONYM DICTIONARY ====================
# Maps common variations to standard terms

SYNONYMS = {
    # System actions
    "screenshot": ["snap", "capture screen", "screen capture", "screen shot", "take screenshot", "grab screen"],
    "battery": ["power level", "charge", "battery level", "battery status", "how much battery", "battery percentage"],
    "shutdown": ["turn off", "power off", "shut down", "switch off", "turn off pc", "turn off computer"],
    "restart": ["reboot", "restart pc", "restart computer", "reboot pc"],
    "sleep": ["hibernate", "sleep mode", "put to sleep", "sleep pc"],
    
    # Camera
    "camera": ["webcam", "cam", "video", "camera on", "camera off"],
    
    # Email
    "email": ["mail", "inbox", "gmail", "emails", "check mail", "check email", "my mail", "my emails"],
    "upcoming": ["interviews", "upcoming interviews", "scheduled interviews", "interview schedule"],
    "unsubscribe": ["promotional", "spam", "promotions", "marketing emails"],
    
    # Payments & Subscriptions
    "payments": ["payment reminders", "bills due", "upcoming payments", "my bills", "pending payments", "emi due"],
    "subscriptions": ["subscription alerts", "renewal alerts", "subscriptions expiring", "my subscriptions", "renewal reminders"],
    
    # Web
    "search": ["google", "look up", "look for", "find online", "search for", "search the web", "web search"],
    "browse": ["open website", "go to", "visit", "navigate to", "open url", "open site"],
    "cart": ["add to cart", "buy", "purchase", "order", "add to amazon", "amazon cart"],
    
    # Files
    "find file": ["locate file", "where is", "find my", "search file", "look for file"],
    "storage": ["disk space", "drive space", "how much space", "storage space", "disk usage"],
    "recycle bin": ["trash", "clear bin", "empty bin", "clear trash", "empty trash"],
    
    # Monitoring
    "activities": ["what's open", "active apps", "open apps", "running apps", "activity"],
    "clipboard": ["copied texts", "copy history", "clipboard history", "what i copied"],
    "location": ["where am i", "my location", "gps", "locate me"],
    
    # Media
    "record": ["record audio", "voice recording", "record voice", "audio recording"],
    
    # Profile
    "profile": ["my profile", "my details", "my info", "user profile"],
    
    # Focus
    "focus": ["focus mode", "do not disturb", "dnd", "block apps"],
}


# ==================== COMMAND PATTERNS ====================
# Each pattern defines triggers and how to extract entities

COMMAND_PATTERNS = {
    # --- SYSTEM ---
    "take_screenshot": {
        "triggers": ["screenshot", "ss", "snap", "capture screen", "screen capture", "/screenshot"],
        "action": {"action": "take_screenshot"}
    },
    "check_battery": {
        "triggers": ["battery", "charge", "power level", "battery percentage", "/batterypercentage", "/battery"],
        "action": {"action": "check_battery"}
    },
    "check_health": {
        "triggers": ["system health", "cpu usage", "memory usage", "system status", "/systemhealth", "/health"],
        "action": {"action": "check_health"}
    },
    "shutdown_pc": {
        "triggers": ["shutdown", "turn off", "power off", "shut down", "/shutdown"],
        "action": {"action": "shutdown_pc"}
    },
    "restart_pc": {
        "triggers": ["restart", "reboot", "/restart"],
        "action": {"action": "restart_pc"}
    },
    "system_sleep": {
        "triggers": ["sleep", "hibernate", "put to sleep", "/sleep"],
        "action": {"action": "system_sleep"}
    },
    "system_panic": {
        "triggers": ["panic", "emergency", "🚨"],
        "action": {"action": "system_panic"}
    },
    
    # --- CAMERA ---
    "camera_on": {
        "triggers": ["camera on", "turn on camera", "start camera", "webcam on", "/camera_on"],
        "action": {"action": "camera_stream"}
    },
    "camera_off": {
        "triggers": ["camera off", "turn off camera", "stop camera", "webcam off", "/camera_off"],
        "action": {"action": "camera_snap"}
    },
    
    # --- EMAIL ---
    "get_emails": {
        "triggers": ["emails", "email", "inbox", "check mail", "check email", "check my email", "check my emails", "my mail", "my emails", "show emails", "show my emails", "/emails"],
        "action": {"action": "get_emails"}
    },
    "get_upcoming_interviews": {
        "triggers": ["upcoming interviews", "interview schedule", "my interviews", "upcoming", "/upcoming", "/interviews"],
        "action": {"action": "get_upcoming_interviews"}
    },
    "get_promotional": {
        "triggers": ["promotional", "spam", "unsubscribe", "marketing emails", "/unsubscribe", "/promotional"],
        "action": {"action": "get_promotional"}
    },
    "get_payment_reminders": {
        "triggers": ["payment reminders", "upcoming payments", "bills due", "my bills", "pending payments", "emi due", "payment due", "/payments"],
        "action": {"action": "get_payment_reminders"}
    },
    "get_subscription_alerts": {
        "triggers": ["subscription alerts", "renewal alerts", "subscriptions expiring", "my subscriptions", "renewal reminders", "subscription renewal", "/subscriptions"],
        "action": {"action": "get_subscription_alerts"}
    },
    
    # --- WEB AUTOMATION ---
    "web_search": {
        "triggers": ["search", "google", "look up", "find online", "/search"],
        "extract_pattern": r"(?:search\s+(?:for\s+)?|google\s+|look\s+up\s+|find\s+online\s+|/search\s+)(.+)",
        "action_template": {"action": "web_search", "query": "$1"}
    },
    # Multi-site shopping / browser agent goals
    "browser_compare": {
        "triggers": ["compare prices", "compare price", "price comparison"],
        "extract_pattern": r"(compare.+)",
        "action_template": {"action": "browser_agent", "goal": "$1"}
    },
    # Multi-step browser goals (open X and search Y)
    "browser_goal": {
        "triggers": ["open", "go to", "visit", "browse", "/browse"],
        "multi_step_hints": ["and search", "and find", "then search", "then find", "and click", "and select"],
        "extract_pattern": r"((?:open|go\s+to|visit|browse|/browse)\s+.+(?:and|then)\s+.+)",
        "action_template": {"action": "browser_agent", "goal": "$1"}
    },
    "browser_navigate": {
        "triggers": ["browse", "go to", "open", "visit", "navigate to", "/browse"],
        "url_hints": [".com", ".in", ".org", ".net", ".io", "http", "www", "youtube", "amazon", "google", "flipkart", "github"],
        "extract_pattern": r"(?:browse\s+|go\s+to\s+|open\s+|visit\s+|navigate\s+to\s+|/browse\s+)(\S+)",
        "action_template": {"action": "browser_navigate", "url": "$1"}
    },
    "add_to_cart": {
        "triggers": ["add to cart", "add to amazon", "buy from amazon", "order from amazon", "/addcart", "/add_cart"],
        "extract_pattern": r"(?:add\s+to\s+cart\s+|add\s+to\s+amazon\s+(?:cart\s+)?|buy\s+from\s+amazon\s+|order\s+from\s+amazon\s+|/addcart\s+|/add_cart\s+)(.+)",
        "action_template": {"action": "add_to_cart", "product": "$1"}
    },
    "browser_screenshot": {
        "triggers": ["browser screenshot", "show browser", "what's on the page", "/browser_screenshot"],
        "action": {"action": "browser_screenshot"}
    },
    "stop_browser": {
        "triggers": ["stop browser", "close browser", "/stop_browser"],
        "action": {"action": "stop_browser"}
    },
    
    # --- FILES ---
    "check_storage": {
        "triggers": ["storage", "disk space", "drive space", "how much space", "/storage"],
        "action": {"action": "check_storage"}
    },
    "clear_recycle_bin": {
        "triggers": ["clear bin", "empty bin", "clear trash", "empty trash", "clear recycle bin", "/clear_bin"],
        "action": {"action": "clear_recycle_bin"}
    },
    "get_activities": {
        "triggers": ["activities", "what's open", "active apps", "open apps", "running apps", "/activities"],
        "action": {"action": "get_activities"}
    },
    "get_clipboard_history": {
        "triggers": ["clipboard", "copied texts", "copy history", "clipboard history", "/copied_texts"],
        "action": {"action": "get_clipboard_history"}
    },
    
    # --- LOCATION ---
    "get_location": {
        "triggers": ["location", "where am i", "my location", "gps", "/location"],
        "action": {"action": "get_location"}
    },
    
    # --- MEDIA ---
    "record_audio": {
        "triggers": ["record audio", "voice recording", "record voice", "/recordaudio", "/record"],
        "action": {"action": "record_audio", "duration": 10}
    },
    
    # --- PROFILE ---
    "get_profile": {
        "triggers": ["my profile", "show profile", "view profile", "/my_profile", "/profile"],
        "action": {"action": "get_profile"}
    },
    "fill_form_auto": {
        "triggers": ["fill form", "fill this form", "autofill", "auto fill", "/fill_form"],
        "action": {"action": "fill_form_auto"}
    },
    "clear_profile": {
        "triggers": ["clear profile", "delete profile", "/clear_profile"],
        "action": {"action": "clear_profile"}
    },
    
    # --- FOCUS MODE ---
    "focus_mode_on": {
        "triggers": ["focus mode", "focus on", "do not disturb", "dnd", "/focus_mode_on"],
        "action": {"action": "focus_mode", "sub_action": "on"}
    },
    "focus_mode_off": {
        "triggers": ["focus off", "focus mode off", "/focus_mode_off"],
        "action": {"action": "focus_mode", "sub_action": "off"}
    },
    "focus_mode_status": {
        "triggers": ["focus status", "blacklist", "/blacklist"],
        "action": {"action": "focus_mode", "sub_action": "status"}
    },
    
    # --- BROWSER AGENT ---
    # --- CONTINUATION COMMANDS (use with active browser) ---
    "browser_click": {
        "triggers": ["click on", "click", "tap on", "tap", "press on", "press the", "select"],
        "extract_pattern": r"(?:click on|click|tap on|tap|press on|press the|select)\s+(.+)",
        "action_template": {"action": "browser_click", "target": "$1"}
    },
    "browser_scroll": {
        "triggers": ["scroll down", "scroll up", "scroll"],
        "action": {"action": "browser_scroll", "direction": "down"}
    },
    "browser_type": {
        "triggers": ["type", "enter text", "write"],
        "extract_pattern": r"(?:type|enter text|write)\s+(.+)",
        "action_template": {"action": "browser_type", "text": "$1"}
    },
    "browser_back": {
        "triggers": ["go back", "back", "previous page"],
        "action": {"action": "browser_back"}
    },
    "browser_refresh": {
        "triggers": ["refresh", "reload"],
        "action": {"action": "browser_refresh"}
    },
    # Sort / filter continuation commands on shopping sites
    "browser_sort": {
        "triggers": ["sort by"],
        "extract_pattern": r"(?:sort\s+by\s+)(.+)",
        "action_template": {"action": "browser_sort", "sort_by": "$1"}
    },
    "browser_filter_price": {
        "triggers": ["filter by price", "price under", "price below", "under", "below"],
        "extract_pattern": r"(?:filter\s+by\s+price\s+|price\s+under\s+|price\s+below\s+|under\s+|below\s+)(.+)",
        "action_template": {"action": "browser_filter_price", "max_price": "$1"}
    },
}


class KeywordMatcher:
    """Fast keyword-based command matching (Tier 1)."""
    
    def __init__(self):
        self.patterns = COMMAND_PATTERNS
        self.synonyms = SYNONYMS
        self._build_trigger_index()
    
    def _build_trigger_index(self):
        """Build inverted index for fast lookup."""
        self.trigger_index = {}
        for cmd_name, config in self.patterns.items():
            for trigger in config.get("triggers", []):
                trigger_lower = trigger.lower()
                if trigger_lower not in self.trigger_index:
                    self.trigger_index[trigger_lower] = []
                self.trigger_index[trigger_lower].append(cmd_name)
    
    def _normalize_text(self, text: str) -> str:
        """Normalize text for matching."""
        return text.lower().strip()
    
    def _expand_synonyms(self, text: str) -> str:
        """Expand synonyms in text to standard terms."""
        text_lower = text.lower()
        for standard, variations in self.synonyms.items():
            for variation in variations:
                v = variation.lower()
                if not v:
                    continue
                # Very short variations (like "ss") should only match whole words
                if len(v) <= 2 and v.isalnum():
                    text_lower = re.sub(rf"\b{re.escape(v)}\b", standard, text_lower)
                else:
                    if v in text_lower:
                        text_lower = text_lower.replace(v, standard)
        return text_lower

    def _trigger_matches(self, text_expanded: str, trigger: str) -> bool:
        """Return True if a trigger matches safely.
        
        Important: avoid short-trigger substring collisions like:
        - trigger "ss" matching "across"
        """
        t = trigger.lower().strip()
        if not t:
            return False

        # Slash commands should match at start
        if t.startswith("/"):
            return text_expanded.startswith(t)

        # Multi-word triggers can be substring matched
        if " " in t:
            return t in text_expanded

        # Very short triggers are matched as whole words only
        if len(t) <= 2 and t.isalnum():
            return re.search(rf"\b{re.escape(t)}\b", text_expanded) is not None

        # Default: substring match or startswith
        return t in text_expanded or text_expanded.startswith(t)
    
    def match(self, text: str) -> Optional[Dict[str, Any]]:
        """
        Try to match text against known patterns.
        Returns action dict if matched, None otherwise.
        """
        if not text:
            return None
        
        text_normalized = self._normalize_text(text)
        text_expanded = self._expand_synonyms(text_normalized)

        # Priority: explicit /browse commands should always go to browser agent,
        # not system-level actions like screenshot.
        if text_normalized.startswith("/browse "):
            goal = text.strip()[len("/browse "):].strip()
            if goal:
                return {"action": "browser_agent", "goal": goal}
        
        # Priority check: Multi-step browser commands (open/browse X and search Y)
        multi_step_hints = ["and search", "and find", "then search", "then find", "and click", "and select", "and add"]
        if any(hint in text_normalized for hint in multi_step_hints):
            config = self.patterns.get("browser_goal", {})
            if config and "extract_pattern" in config:
                result = self._extract_and_build(text, text_normalized, config)
                # If we successfully built a browser_goal command, return it.
                # Otherwise, fall through to normal trigger matching so that
                # commands like "/browse amazon.in and search X" still work.
                if result:
                    return result
        
        # Try exact trigger match first (fastest)
        for trigger, cmd_names in self.trigger_index.items():
            if self._trigger_matches(text_expanded, trigger):
                cmd_name = cmd_names[0]  # Take first match
                config = self.patterns[cmd_name]
                
                # Check if we need to extract entities
                if "extract_pattern" in config:
                    action = self._extract_and_build(text, text_normalized, config)
                    # Only return if we successfully built an action. If extraction
                    # fails (e.g. pattern doesn't match), keep searching so other
                    # commands like browser_navigate can still handle the text.
                    if action:
                        return action
                else:
                    # Simple action, no extraction needed
                    return config.get("action", {}).copy()
        
        # Try URL detection for browse
        if any(hint in text_normalized for hint in [".com", ".in", ".org", ".net", ".io", "http", "www"]):
            url_match = re.search(r'(https?://\S+|www\.\S+|\S+\.(com|in|org|net|io)\S*)', text_normalized)
            if url_match:
                return {"action": "browse_url", "url": url_match.group(1)}
        
        return None
    
    def _extract_and_build(self, original_text: str, normalized_text: str, config: Dict) -> Optional[Dict]:
        """Extract entities from text and build action."""
        pattern = config.get("extract_pattern")
        if not pattern:
            return config.get("action", {}).copy()
        
        # Try matching
        match = re.search(pattern, normalized_text, re.IGNORECASE)
        if match:
            action = config.get("action_template", {}).copy()
            # Replace placeholders with captured groups
            for key, value in action.items():
                if isinstance(value, str) and value.startswith("$"):
                    group_num = int(value[1:])
                    if group_num <= len(match.groups()):
                        action[key] = match.group(group_num).strip()
            return action
        
        # Fallback: extract everything after trigger
        for trigger in config.get("triggers", []):
            if trigger in normalized_text:
                entity = normalized_text.split(trigger, 1)[-1].strip()
                if entity:
                    action = config.get("action_template", {}).copy()
                    for key, value in action.items():
                        if isinstance(value, str) and value.startswith("$"):
                            action[key] = entity
                    return action
        
        return None


# Singleton instance
keyword_matcher = KeywordMatcher()


def match_command(text: str) -> Optional[Dict[str, Any]]:
    """Public function to match text against patterns."""
    return keyword_matcher.match(text)
