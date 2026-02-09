# Installation Guide

Complete setup instructions for JARVIX Desktop Assistant.

## System Requirements

| Requirement | Minimum | Recommended |
|-------------|---------|-------------|
| **OS** | Windows 10 (64-bit) | Windows 11 |
| **RAM** | 8 GB | 16 GB |
| **Storage** | 10 GB free | 20 GB free |
| **GPU** | Not required | NVIDIA (for faster AI) |
| **Python** | 3.9+ | 3.11 |

## One-Click Installation

The fastest way to get started:

```bash
# Clone the repository
git clone https://github.com/your-repo/jarvix-assistant.git
cd jarvix-assistant

# Run the installer
install.bat
```

**The installer automatically:**
- ✓ Installs Python 3.11 (if missing)
- ✓ Installs Ollama AI runtime
- ✓ Creates virtual environment
- ✓ Downloads AI model (~4.7GB)
- ✓ Configures Windows startup
- ✓ Creates `.env` template

## Manual Installation

For advanced users who prefer manual setup:

### Step 1: Install Prerequisites

```bash
# Install Python 3.11+
winget install Python.Python.3.11

# Install Ollama
winget install Ollama.Ollama
```

### Step 2: Clone & Setup

```bash
git clone https://github.com/your-repo/jarvix-assistant.git
cd jarvix-assistant

# Create virtual environment
python -m venv venv
.\venv\Scripts\activate

# Install dependencies
pip install -e .
```

### Step 3: Download AI Model

```bash
ollama pull qwen2.5-coder:7b
```

### Step 4: Configure Environment

Create a `.env` file in the project root:

```env
# Required
TELEGRAM_TOKEN=your_bot_token_here
ALLOWED_TELEGRAM_USERNAME=your_username

# Optional
MODEL_NAME=qwen2.5-coder:7b
OFFLINE_MODE=false
LOG_LEVEL=INFO

# Gmail (optional)
GMAIL_ADDRESS=your_email@gmail.com
GMAIL_APP_PASSWORD=your_app_password
```

## Getting a Telegram Bot Token

1. Open Telegram and search for `@BotFather`
2. Send `/newbot` command
3. Follow prompts to name your bot
4. Copy the token provided
5. Add token to `.env`

## Launching JARVIX

### Standard Mode (with console)
```bash
start_jarvix.bat
```

### Stealth Mode (background)
```bash
run_silent.vbs
```

### Development Mode
```bash
.\venv\Scripts\activate
python -m jarvix.main
```

## Auto-Start on Windows

The installer configures auto-start automatically. To manually configure:

1. Press `Win + R`, type `shell:startup`
2. Create a shortcut to `run_silent.vbs`

## Verify Installation

After starting JARVIX:

1. Open Telegram
2. Find your bot
3. Send `/systemhealth`
4. You should see CPU, RAM, and disk information

## Browser Extension (Optional)

For advanced browser control:

### Chrome
1. Go to `chrome://extensions`
2. Enable "Developer mode"
3. Click "Load unpacked"
4. Select `browser_extension/` folder

### Firefox
1. Go to `about:debugging`
2. Click "This Firefox"
3. Click "Load Temporary Add-on"
4. Select `firefox_extension/manifest.json`

## Troubleshooting

### Ollama not found
```bash
# Restart terminal after installing Ollama
# Or add to PATH manually
```

### Model download fails
```bash
# Check internet connection
# Try direct download
ollama pull qwen2.5-coder:7b
```

### Bot not responding
- Verify `TELEGRAM_TOKEN` in `.env`
- Ensure `ALLOWED_TELEGRAM_USERNAME` matches your Telegram username
- Check if Ollama is running: `ollama list`

---

**Next:** [Configuration Guide](CONFIGURATION.md)
