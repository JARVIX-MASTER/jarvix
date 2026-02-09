# Features Guide

Detailed documentation for all JARVIX features.

## Voice Control

### Wake Word Detection

JARVIX uses **Vosk** for offline wake word detection.

**Default Wake Word:** "Hey Pikachu"

**How It Works:**
```
Microphone → Vosk Engine → Wake Word Match → Listen for Command → Process
```

**Modes:**
- **Hybrid (default):** Wake word offline, commands use Google API
- **Fully Offline:** Set `OFFLINE_MODE=true` for 100% local processing

---

## Remote Control (Telegram)

Control your PC from anywhere using Telegram.

### Setup
1. Create bot via @BotFather
2. Add token to `.env`
3. Add your username to `ALLOWED_TELEGRAM_USERNAME`

### Features
- Quick-access keyboard buttons
- Natural language processing
- Media delivery (screenshots, audio, video)
- Real-time notifications

### Security
- Username whitelist (only you can control)
- Token-based authentication
- No public API exposure

---

## Activity Monitoring

Real-time tracking of PC activity.

### What's Tracked
| Data | Source | Refresh |
|------|--------|---------|
| Active window | Windows API | Real-time |
| Running apps | Process list | On-demand |
| Browser tabs | Extension | Real-time |
| Recent apps | Memory | Session |

### Browser Integration

**Chrome Extension:**
- Install from `browser_extension/`
- Tracks active tabs
- Enables tab control

**Firefox Extension:**
- Install from `firefox_extension/`
- Native messaging support
- Tab screenshots

---

## File Intelligence

Smart file tracking and search.

### File Tracker

Automatically logs file access:

```json
{
  "path": "C:/Users/Me/Documents/report.pdf",
  "timestamp": "2025-02-09T10:30:00",
  "app": "Adobe Reader",
  "action": "open"
}
```

**Specifications:**
- 30-day retention
- 40+ file types supported
- Minimal performance impact

### Smart File Search

Natural language queries:

```
"Find that PDF I opened yesterday"
→ Searches: type=PDF, time=yesterday

"Get the Excel file from this morning"  
→ Searches: type=Excel, time=today AM

"That document I was working on"
→ Searches: recent docs, by access time
```

---

## Clipboard History

Never lose copied text again.

### Features
- Stores last 100 entries
- Timestamped entries
- Persistent storage (survives restart)
- Quick retrieval via Telegram

### Data Format
```json
{
  "text": "Copied content here",
  "timestamp": "2025-02-09T10:30:00"
}
```

### Commands
```
/copied_texts       # Show last 20 items
"clipboard history" # Voice/text command
"what did i copy"   # Natural language
```

---

## Focus Mode

Distraction-free productivity.

### How It Works
When enabled, JARVIX blocks:
- Blacklisted applications
- Blacklisted websites
- Notification windows

### Managing Blacklist

```
/blacklist                    # View current list
/blacklist add spotify        # Block Spotify
/blacklist add discord steam  # Block multiple
/blacklist remove spotify     # Unblock
```

### Default Blacklist
Common distractions pre-configured:
- Social media apps
- Gaming platforms
- Entertainment sites

---

## Gmail Automation

Email processing and organization.

### Setup
1. Enable 2FA on Gmail
2. Generate App Password
3. Add to `.env`:
```env
GMAIL_ADDRESS=you@gmail.com
GMAIL_APP_PASSWORD=xxxx xxxx xxxx xxxx
```

### Email Categories

| Category | Detection Method |
|----------|------------------|
| **Promotional** | Unsubscribe links, marketing keywords |
| **Interview** | HR keywords, recruiter patterns |
| **Upcoming** | Interview + future dates |
| **General** | Everything else |

### Commands

```
/emails      → Summary of all categories
/upcoming    → Interview-related emails
/unsubscribe → Promotional with unsubscribe buttons
```

### Smart Detection

**Strong signals (instant match):**
- "Interview scheduled"
- "Technical interview"
- "Phone screen"

**Weak signals (need multiple):**
- "interview"
- "recruiter"
- "position"

**Exclusions (prevent false positives):**
- "Job alerts"
- "New jobs matching"
- "Apply now"

---

## System Monitoring

Real-time PC health tracking.

### Metrics Available

| Metric | Command | Data |
|--------|---------|------|
| Battery | `/batterypercentage` | Level, charging status, time remaining |
| CPU | `/systemhealth` | Usage %, temperature |
| RAM | `/systemhealth` | Used/Total, percentage |
| Disk | `/storage` | Per-drive usage |
| Network | `/location` | IP, connection type |

### Health Check Output
```
🖥️ SYSTEM HEALTH

CPU: 23% | Temp: 45°C
RAM: 8.2GB / 16GB (51%)
Disk: 234GB free / 500GB
Network: Connected (Ethernet)
```

---

## Media Capture

Remote media access.

### Screenshot
- Full screen capture
- PNG format
- Instant Telegram delivery

### Camera
- Live webcam stream
- Start/stop control
- Privacy indicator

### Audio Recording
- 10-second clips
- System + microphone
- Voice message format

---

## Location Tracking

IP-based geolocation.

### How It Works
```
Public IP → Geolocation API → City, Country, Coordinates
```

### Output
```
📍 LOCATION

City: San Francisco
Country: United States
Coordinates: 37.7749, -122.4194
ISP: Comcast
```

### Use Cases
- Lost device tracking
- Remote work verification
- Network diagnostics

---

## Browser Control

Advanced tab management.

### Requirements
- Browser extension installed
- Native host registered

### Capabilities

| Action | Command | Example |
|--------|---------|---------|
| Close tab | "close" | "Close the YouTube tab" |
| Mute tab | "mute" | "Mute Spotify" |
| Play/Pause | "play/pause" | "Pause the video" |
| Screenshot | "screenshot" | "Screenshot this page" |

### Smart Matching
JARVIX uses context to find the right tab:
- Title matching
- URL matching
- Recent focus priority

---

**Next:** [Configuration](CONFIGURATION.md)
