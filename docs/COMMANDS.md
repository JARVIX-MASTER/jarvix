# Commands Reference

Complete reference for all JARVIX commands.

## Telegram Commands

### System Control

| Command | Description | Example |
|---------|-------------|---------|
| `/sleep` | Put PC to sleep | `/sleep` |
| `/shutdown` | Shut down PC | `/shutdown` |
| `/restart` | Restart PC | `/restart` |
| `🚨 PANIC` | Emergency lock | Tap button |

### Monitoring

| Command | Description | Output |
|---------|-------------|--------|
| `/batterypercentage` | Check battery | Percentage + charging status |
| `/systemhealth` | CPU, RAM, disk usage | Detailed metrics |
| `/storage` | Disk space per drive | All drives with usage |
| `/activities` | Running apps & tabs | Active windows list |
| `/location` | IP-based geolocation | City, country, map link |

### Media Capture

| Command | Description | Output |
|---------|-------------|--------|
| `/screenshot` | Capture screen | PNG image |
| `/camera_on` | Start webcam stream | Live updates |
| `/camera_off` | Stop webcam | Confirmation |
| `/recordaudio` | Record 10s audio | Voice message |

### Productivity

| Command | Description | Options |
|---------|-------------|---------|
| `/copied_texts` | Clipboard history | Last 20 items |
| `/clear_bin` | Empty recycle bin | Confirmation |
| `/focus_mode_on` | Enable focus mode | Blocks distractions |
| `/focus_mode_off` | Disable focus mode | Resumes normal |
| `/blacklist` | Manage blocked items | See below |

### Focus Mode Blacklist

```
/blacklist                     # Show current blacklist
/blacklist add spotify steam   # Block apps
/blacklist remove spotify      # Unblock app
```

### Gmail Automation

| Command | Description | Output |
|---------|-------------|--------|
| `/emails` | Email summary | Categories + counts |
| `/upcoming` | Interview emails | Scheduled interviews |
| `/unsubscribe` | Promotional emails | With unsubscribe buttons |

---

## Natural Language Commands

JARVIX understands natural language. Here are examples by category:

### App Control

```
"Open Chrome"
"Launch Spotify"
"Close Notepad"
"Open VS Code"
```

### Web Navigation

```
"Open YouTube in Chrome"
"Go to google.com"
"Open Netflix in Firefox"
```

### System

```
"What's my battery level?"
"How's my system doing?"
"Check storage"
"Clear the recycle bin"
```

### Files

```
"Find that PDF I opened yesterday"
"Show me files in Downloads"
"Get that Excel file from this morning"
"That document I was working on"
```

### Browser Control

```
"Close the YouTube tab"
"Mute Spotify"
"Play the video"
"Pause the music"
"Screenshot this tab"
```

### Email

```
"Check my emails"
"Do I have any interviews?"
"Show promotional emails"
"Any upcoming meetings?"
```

### Clipboard

```
"What did I copy?"
"Show clipboard history"
"My copied texts"
```

---

## Voice Commands

Voice commands work the same as text but require the wake word:

```
"Hey Pikachu, take a screenshot"
"Hey Pikachu, what's my battery?"
"Hey Pikachu, open Chrome"
"Hey Pikachu, show me what I'm doing"
```

### Wake Word

Default wake word: **"Hey Pikachu"**

---

## Command Patterns

The AI understands variations of each command:

### Battery
```
"battery" | "battery level" | "power status" | "charge level"
```

### Screenshot
```
"screenshot" | "capture screen" | "ss" | "screen capture"
```

### System Health
```
"system health" | "cpu" | "ram" | "how's my pc" | "pc status"
```

### Activities
```
"activities" | "what's open" | "running apps" | "active windows"
```

### Files
```
"find that" | "get that" | "send that" | "that file" | "that pdf"
```

---

## Telegram Keyboard

Quick access buttons are organized in rows:

```
Row 1: /screenshot | /camera_on | /camera_off
Row 2: 🚨 PANIC
Row 3: /sleep | /restart | /shutdown
Row 4: /batterypercentage | /systemhealth
Row 5: /location | /recordaudio
Row 6: /clear_bin | /storage
Row 7: /activities | /copied_texts
Row 8: /focus_mode_on | /blacklist
Row 9: /emails | /upcoming
Row 10: /unsubscribe
```

---

## Command Response Format

### Success Response
```
✅ [Action completed]
[Relevant data or confirmation]
```

### Error Response
```
❌ [Error description]
[Suggested fix if applicable]
```

### Progress Indicator
```
⚡ Thinking...
📧 Fetching emails...
📅 Checking for interviews...
```

---

**Next:** [Features Guide](FEATURES.md)
