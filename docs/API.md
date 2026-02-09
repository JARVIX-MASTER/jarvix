# API Reference

Developer documentation for extending JARVIX.

## Core Modules

### Brain (`core/brain.py`)

The AI inference engine.

```python
from jarvix.core.brain import process_command

# Process natural language command
result = process_command("open chrome")
# Returns: {"action": "open_app", "app_name": "chrome"}
```

**Key Functions:**

| Function | Parameters | Returns |
|----------|------------|---------|
| `process_command(user_input)` | str | dict (JSON command) |

---

### Memory (`core/memory.py`)

Context and preference storage.

```python
from jarvix.core.memory import save_preference, get_preference

# Save user preference
save_preference("browser", "chrome")

# Retrieve preference
browser = get_preference("browser")  # Returns: "chrome"
```

**Key Functions:**

| Function | Parameters | Returns |
|----------|------------|---------|
| `save_preference(key, value)` | str, any | None |
| `get_preference(key)` | str | any |
| `get_context_string()` | None | str |

---

### System Agent (`agents/system.py`)

Command execution engine.

```python
from jarvix.agents.system import execute_command

# Execute a command
result = execute_command({"action": "check_battery"})
# Returns: {"level": 85, "charging": True, ...}
```

**Available Actions:**

| Action | Parameters | Returns |
|--------|------------|---------|
| `take_screenshot` | None | Image path |
| `camera_stream` | None | Image path |
| `check_battery` | None | Battery dict |
| `check_health` | None | System info dict |
| `open_app` | `app_name` | None |
| `close_app` | `app_name` | None |
| `open_url` | `url`, `browser` | None |
| `get_activities` | None | Activities dict |
| `get_clipboard_history` | None | List of entries |
| `get_emails` | None | Categorized emails |
| `get_upcoming_interviews` | None | Interview emails |
| `get_promotional` | None | Promo emails |

---

## Feature Modules

### Activity Monitor (`features/activity.py`)

```python
from jarvix.features.activity import ActivityMonitor

monitor = ActivityMonitor()
activities = monitor.get_current_activities()

# Returns:
{
    "active_window": "Visual Studio Code",
    "running_apps": ["chrome.exe", "spotify.exe"],
    "browser_tabs": [{"title": "YouTube", "url": "..."}]
}
```

---

### Clipboard Manager (`features/clipboard.py`)

```python
from jarvix.features.clipboard import ClipboardMonitor

monitor = ClipboardMonitor()

# Get history
history = monitor.get_clipboard_history()
# Returns: List of {text, timestamp} dicts

# Start monitoring
monitor.start()
```

---

### Focus Mode (`features/focus_mode.py`)

```python
from jarvix.features.focus_mode import FocusMode

fm = FocusMode()

# Enable focus mode
fm.enable()

# Add to blacklist
fm.add_to_blacklist("spotify")

# Check status
status = fm.get_status()
# Returns: {"enabled": True, "blacklist": ["spotify", ...]}
```

---

### Gmail Client (`features/gmail.py`)

```python
from jarvix.features.gmail import GmailClient

client = GmailClient()

# Connect
if client.connect():
    # Get categorized emails
    emails = client.get_all_categorized(limit=30)
    
    # Get upcoming interviews
    interviews = client.get_upcoming_interviews()
    
    # Get promotional emails
    promo = client.get_promotional_emails()
    
    client.disconnect()
```

**Email Categories:**
- `promotional` - Marketing emails
- `interview` - HR/recruiter emails
- `upcoming_interview` - Interviews with future dates
- `general` - Everything else

---

### File Finder (`features/files/finder.py`)

```python
from jarvix.features.files.finder import FileFinder

finder = FileFinder()

# Natural language search
results = finder.find_file("that pdf from yesterday")
# Returns: List of matching files

# Filter by type
pdfs = finder.find_by_type("pdf", time_query="yesterday")
```

---

## Extending JARVIX

### Adding a New Command

**Step 1:** Add to `brain.py`

```python
# In BASE_SYSTEM_PROMPT
"""
22. My Custom Action: {"action": "custom_action", "param": "value"}
    (Triggers: custom, do custom thing, my action)
"""

# In process_command(), add force override
elif any(x in lower for x in ["custom", "my action"]):
    data = {"action": "custom_action"}
```

**Step 2:** Add handler to `system.py`

```python
# In execute_command()
elif action == "custom_action":
    return do_custom_action(cmd_json.get("param"))
```

**Step 3:** Add Telegram handler to `telegram.py`

```python
# In command matching section
elif "/custom" in lower_text or "custom" in lower_text:
    command_json = {"action": "custom_action"}

# In action handlers section
elif action == "custom_action":
    result = execute_command(command_json)
    await update.message.reply_text(f"Custom result: {result}")
```

---

### Adding a New Feature Module

**Step 1:** Create module in `features/`

```python
# features/my_feature.py
class MyFeature:
    def __init__(self):
        # Initialize
        pass
    
    def do_something(self, param):
        # Feature logic
        return {"result": "success"}
```

**Step 2:** Import in `system.py`

```python
from jarvix.features.my_feature import MyFeature

my_feature = MyFeature()
```

**Step 3:** Add action handler

```python
elif action == "my_feature_action":
    return my_feature.do_something(cmd_json.get("param"))
```

---

## JSON Command Format

All commands follow this structure:

```json
{
    "action": "action_name",
    "param1": "value1",
    "param2": "value2"
}
```

**Standard Actions:**
| Action | Description |
|--------|-------------|
| `general_chat` | AI conversation |
| `take_screenshot` | Capture screen |
| `camera_stream` | Webcam access |
| `check_battery` | Battery status |
| `check_health` | System health |
| `open_app` | Launch application |
| `close_app` | Close application |
| `open_url` | Open URL in browser |
| `get_activities` | Running apps/tabs |
| `get_clipboard_history` | Clipboard data |
| `focus_mode` | Focus mode control |
| `get_emails` | Email summary |
| `get_upcoming_interviews` | Interview emails |
| `get_promotional` | Promo emails |
| `find_file` | File search |
| `browser_control` | Tab management |

---

## Event Hooks

### On Startup

```python
# In main.py
def on_startup():
    # Initialize monitors
    clipboard_monitor.start()
    activity_monitor.start()
```

### On Command

```python
# In telegram.py
async def on_command(command_json):
    # Log or process before execution
    log_command(command_json)
```

---

## Testing

```python
# Test brain parsing
from jarvix.core.brain import process_command

assert process_command("take a screenshot")["action"] == "take_screenshot"
assert process_command("open chrome")["action"] == "open_app"
```

---

**Back to:** [Documentation Index](README.md)
