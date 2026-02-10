<div align="center">

# JARVIX

### Your Intelligent Desktop Companion

**100% Local • 100% Private • Zero Cloud Dependencies**

[![Python](https://img.shields.io/badge/Python-3.11-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![Windows](https://img.shields.io/badge/Windows-10%2F11-0078D6?style=for-the-badge&logo=windows&logoColor=white)](https://microsoft.com)
[![AI](https://img.shields.io/badge/AI-Ollama-000000?style=for-the-badge&logo=ai&logoColor=white)](https://ollama.com)
[![Privacy](https://img.shields.io/badge/Privacy-100%25%20Local-00C853?style=for-the-badge&logo=shield&logoColor=white)](#)

[Installation](#-quick-start) • [Features](#-features) • [Commands](#-commands) • [Documentation](#-documentation)

</div>

---

## ✨ What is JARVIX?

JARVIX is an **AI-powered desktop assistant** that runs entirely on your local machine. Control your PC with voice commands or remotely via Telegram — all without sending a single byte to the cloud.

```
🎤 "Hey Pikachu, take a screenshot"     →  📸 Screenshot captured
📱 /batterypercentage                    →  🔋 85% charging
💬 "Check my emails"                     →  📧 3 interview, 12 promo, 8 general
```

---

## 🎯 Key Highlights

| Feature | Description |
|---------|-------------|
| 🔒 **100% Private** | Everything runs locally. Your data never leaves your PC. |
| 🎤 **Voice Control** | Say "Hey Pikachu" and command your computer naturally. |
| 📱 **Remote Access** | Control your PC from anywhere using Telegram. |
| 🤖 **Smart AI** | Powered by Qwen 2.5 Coder with context-aware responses. |
| 💰 **Zero Cost** | No APIs, no subscriptions, completely free. |
| 📧 **Email Automation** | Categorize emails, detect interviews, find unsubscribe links. |

---

## 🚀 Quick Start

### One-Click Installation

```bash
git clone https://github.com/JARVIX-MASTER/jarvix
cd jarvix
./install.bat
```

**That's it.** The installer handles Python, Ollama, dependencies, and AI model (~4.7GB).

### Configuration

Create `.env` in project root:

```env
TELEGRAM_TOKEN=your_bot_token
ALLOWED_TELEGRAM_USERNAME=your_username
MODEL_NAME=qwen2.5-coder:7b # Use whatever suits you but this one is the fastest on low-end RAMs    
GMAIL_ADDRESS=your_gmail_address_here
GMAIL_APP_PASSWORD=your_gmail_app_password_here
# You can generate an app password for your Gmail account here: https://myaccount.google.com/apppasswords
```

### Launch

```bash
./start_jarvix.bat        # Visible mode
./run_silent.vbs          # Stealth mode (background)
```

📖 **[Full Installation Guide →](docs/INSTALLATION.md)**

---

## ⚡ Features

### System Control
- Launch/close applications
- Power management (sleep, shutdown, restart)
- File browsing and search
- Window management

### Monitoring
- Real-time CPU, RAM, disk usage
- Battery status and health
- Active apps and browser tabs
- Clipboard history (last 100 items)

### Media Capture
- Screenshot on demand
- Live webcam feed
- Audio recording (10s clips)
- Instant Telegram delivery

### Smart Search
- Natural language file finder
- "Find that PDF from yesterday"
- 30-day file activity log
- Context-aware suggestions

### Email Automation *(New)*
- Gmail IMAP integration
- Auto-categorization (promo, interview, general)
- Interview date detection
- One-click unsubscribe

### Focus Mode
- Block distracting apps
- Website blocking
- Customizable blacklist

📖 **[Full Features Guide →](docs/FEATURES.md)**

---

## 💬 Commands

### Telegram Shortcuts

| Command | Action |
|---------|--------|
| `/screenshot` | Capture screen |
| `/batterypercentage` | Check battery |
| `/systemhealth` | CPU, RAM, disk status |
| `/activities` | Running apps & tabs |
| `/emails` | Email summary |
| `/upcoming` | Interview emails |
| `/unsubscribe` | Promotional emails |
| `/focus_mode_on` | Enable focus mode |

### Voice Commands

```
"Hey Pikachu, open Chrome"
"Hey Pikachu, what's my battery?"
"Hey Pikachu, find that Excel file"
"Hey Pikachu, check my emails"
```

### Natural Language

```
"Open YouTube in Firefox"
"Show me my system health"
"Find that PDF I opened yesterday"
"Do I have any upcoming interviews?"
```

📖 **[Full Commands Reference →](docs/COMMANDS.md)**

---

## 🏗️ Architecture

```
JARVIX
├── Core Engine
│   ├── Brain (Ollama AI)        # Natural language → commands
│   ├── Voice (Vosk + TTS)       # Wake word + speech
│   └── Memory                   # Context & preferences
│
├── Agents
│   ├── System Agent             # Execute commands
│   └── Telegram Agent           # Remote control
│
└── Features
    ├── Activity Monitor         # Apps & tabs tracking
    ├── Clipboard Manager        # Copy history
    ├── Gmail Automation         # Email processing
    ├── Focus Mode               # Distraction blocking
    └── File Intelligence        # Smart search
```

📖 **[Full Architecture →](docs/ARCHITECTURE.md)**

---

## 📚 Documentation

| Guide | Description |
|-------|-------------|
| [Installation](docs/INSTALLATION.md) | Setup and configuration |
| [Architecture](docs/ARCHITECTURE.md) | System design |
| [Commands](docs/COMMANDS.md) | All available commands |
| [Features](docs/FEATURES.md) | Detailed feature docs |
| [Configuration](docs/CONFIGURATION.md) | Environment variables |
| [Security](docs/SECURITY.md) | Privacy information |
| [API Reference](docs/API.md) | Developer documentation |
| [Troubleshooting](docs/TROUBLESHOOTING.md) | Common issues |
| [Contributing](docs/CONTRIBUTING.md) | How to contribute |

---

## 🔒 Privacy & Security

**Your data stays on YOUR machine.**

- ✅ All AI processing runs locally (Ollama)
- ✅ No cloud APIs or external services
- ✅ No telemetry or analytics
- ✅ Open source — audit the code yourself
- ✅ Telegram username whitelist for security

📖 **[Security Details →](docs/SECURITY.md)**

---

## 🛠️ Requirements

| Requirement | Minimum | Recommended |
|-------------|---------|-------------|
| OS | Windows 10 | Windows 11 |
| RAM | 8 GB | 16 GB |
| Storage | 10 GB | 20 GB |
| Python | 3.9+ | 3.11 |

---

## 🤝 Contributing

Contributions are welcome! See [CONTRIBUTING.md](docs/CONTRIBUTING.md) for guidelines.

```bash
# Development setup
git clone https://github.com/JARVIX-MASTER/jarvix
cd jarvix
git checkout -b feature/your-feature
pip install -e .
```

---

## 📄 License

MIT License — Free to use, modify, and distribute.

---

<div align="center">

**Built with ❤️ for privacy-conscious power users**

[⬆ Back to Top](#jarvix)

</div>