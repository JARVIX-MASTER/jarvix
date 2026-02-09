# System Architecture

A deep dive into how JARVIX works under the hood.

## High-Level Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                         USER INTERFACES                         │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────────┐  │
│  │    Voice    │  │  Telegram   │  │    Browser Extension    │  │
│  │  "Hey Pikachu" │  │    Bot      │  │    (Tab Monitoring)     │  │
│  └──────┬──────┘  └──────┬──────┘  └───────────┬─────────────┘  │
└─────────┼────────────────┼─────────────────────┼────────────────┘
          │                │                     │
          ▼                ▼                     ▼
┌─────────────────────────────────────────────────────────────────┐
│                         CORE ENGINE                              │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────────┐  │
│  │   Brain     │  │   Memory    │  │      Wake Word          │  │
│  │  (Ollama)   │  │  (Context)  │  │       (Vosk)            │  │
│  └──────┬──────┘  └─────────────┘  └─────────────────────────┘  │
└─────────┼───────────────────────────────────────────────────────┘
          │
          ▼
┌─────────────────────────────────────────────────────────────────┐
│                      AGENT LAYER                                 │
│  ┌─────────────────────────┐  ┌─────────────────────────────┐   │
│  │     System Agent        │  │     Feature Modules         │   │
│  │  (Command Execution)    │  │  • Activity Monitor         │   │
│  │  • Power Control        │  │  • Clipboard Manager        │   │
│  │  • App Launcher         │  │  • Focus Mode               │   │
│  │  • File Operations      │  │  • Gmail Automation         │   │
│  │  • Media Capture        │  │  • File Tracker             │   │
│  └─────────────────────────┘  └─────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
          │
          ▼
┌─────────────────────────────────────────────────────────────────┐
│                     OPERATING SYSTEM                             │
│         Windows APIs • File System • Hardware Access             │
└─────────────────────────────────────────────────────────────────┘
```

## Directory Structure

```
src/jarvix/
├── main.py              # Application entry point
├── core/                # Core intelligence modules
│   ├── brain.py         # AI inference engine (Ollama)
│   ├── voice.py         # Voice input/output
│   ├── wake_word.py     # Offline wake word detection
│   ├── memory.py        # Context and preference storage
│   └── browser_host.py  # Native messaging for browser
│
├── agents/              # Autonomous agent modules
│   ├── system.py        # System command executor
│   └── telegram.py      # Telegram bot handler
│
├── features/            # Feature implementations
│   ├── activity.py      # App & browser monitoring
│   ├── clipboard.py     # Clipboard history tracker
│   ├── focus_mode.py    # Do-not-disturb mode
│   ├── gmail.py         # Email automation
│   └── files/           # File system utilities
│       ├── finder.py    # Smart file search
│       └── tracker.py   # File activity logger
│
└── utils/               # Shared utilities
```

## Core Components

### 1. Brain (`core/brain.py`)

The AI decision-making engine that interprets natural language.

**Key Features:**
- Uses Ollama with Qwen 2.5 Coder model
- Converts natural language → JSON commands
- Context-aware command parsing
- Fallback handling for ambiguous inputs

**Flow:**
```
User Input → Prompt Construction → Ollama Inference → JSON Command → Execution
```

**Example:**
```
Input:  "Open Chrome and go to YouTube"
Output: {"action": "open_url", "url": "https://youtube.com", "browser": "chrome"}
```

### 2. Memory (`core/memory.py`)

Maintains context and user preferences.

**Stores:**
- User preferences (name, favorite browser)
- Recent actions for context resolution
- Last opened files and apps
- Session state

**Context Resolution:**
```
User: "Close it"
Memory: Last focused = YouTube tab
Result: {"action": "browser_control", "command": "close", "query": "YouTube"}
```

### 3. Voice (`core/voice.py`)

Handles speech-to-text and text-to-speech.

**Technologies:**
- **Wake Word:** Vosk (offline, local)
- **Speech Recognition:** Google Speech API or Vosk
- **TTS:** Windows SAPI (pyttsx3)

### 4. System Agent (`agents/system.py`)

Executes commands on the operating system.

**Capabilities:**
| Category | Functions |
|----------|-----------|
| Power | Sleep, shutdown, restart |
| Apps | Launch, close applications |
| Files | Browse, search, open |
| Media | Screenshot, camera, audio |
| System | Battery, health, storage |

### 5. Telegram Agent (`agents/telegram.py`)

Bidirectional communication with user via Telegram.

**Features:**
- Command shortcuts (keyboard buttons)
- Natural language processing
- Media file delivery (screenshots, audio)
- Real-time notifications

## Feature Modules

### Activity Monitor (`features/activity.py`)

Tracks running applications and browser tabs.

**Data Collected:**
- Active window titles
- Running processes
- Browser tabs (via extension)
- Recent app switches

### Clipboard Manager (`features/clipboard.py`)

Maintains history of copied text.

**Specifications:**
- Stores last 100 entries
- Timestamps each entry
- JSON persistence
- Quick retrieval

### Focus Mode (`features/focus_mode.py`)

Productivity-focused distraction blocking.

**Capabilities:**
- App blocking (games, social media)
- Website blocking
- Notification suppression
- Customizable blacklist

### Gmail Automation (`features/gmail.py`)

Email processing and categorization.

**Features:**
- IMAP connection (App Password)
- Email categorization:
  - Promotional
  - Interview-related
  - Upcoming meetings
  - General
- Unsubscribe link extraction

### File Tracker (`features/files/`)

Intelligent file monitoring and search.

**Finder:**
- Natural language queries
- Time-based filtering
- File type detection
- Context-aware suggestions

**Tracker:**
- 30-day activity log
- Application associations
- Access frequency tracking

## Data Flow

### 1. Voice Command Flow
```
Microphone → Wake Word Detection → Speech Recognition 
           → Brain (AI) → System Agent → Execute → Response → TTS
```

### 2. Telegram Command Flow
```
Telegram Message → Bot Handler → Pattern Matching
                 → Brain (if needed) → System Agent
                 → Execute → Format Response → Send to Telegram
```

### 3. Background Monitoring
```
Clipboard Changes → Clipboard Monitor → Store in History
File Access       → File Tracker     → Log Activity
App Switches      → Activity Monitor → Update Context
```

## Security Model

```
┌────────────────────────────────────────┐
│           SECURITY LAYERS              │
├────────────────────────────────────────┤
│  1. Username Whitelist (Telegram)      │
│  2. Local-only AI Processing           │
│  3. No Cloud API Calls                 │
│  4. SSL for IMAP (Gmail)               │
│  5. App Passwords (no OAuth tokens)    │
└────────────────────────────────────────┘
```

## Extension Points

JARVIX is designed for extensibility:

### Adding New Commands

1. Add keyword patterns to `brain.py`
2. Add action handler to `system.py`
3. Add Telegram handler to `telegram.py`

### Adding New Features

1. Create module in `features/`
2. Initialize in `main.py`
3. Connect to system agent

---

**Next:** [Commands Reference](COMMANDS.md)
