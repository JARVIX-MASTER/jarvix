# Configuration Guide

All environment variables and configuration options.

## Environment File

Create a `.env` file in the project root:

```env
# ===== REQUIRED =====
TELEGRAM_TOKEN=your_bot_token_here
ALLOWED_TELEGRAM_USERNAME=your_username

# ===== AI MODEL =====
MODEL_NAME=qwen2.5-coder:7b

# ===== PRIVACY =====
OFFLINE_MODE=false

# ===== LOGGING =====
LOG_LEVEL=INFO

# ===== GMAIL (Optional) =====
GMAIL_ADDRESS=your_email@gmail.com
GMAIL_APP_PASSWORD=your_app_password
```

---

## Configuration Options

### Telegram Settings

| Variable | Required | Description | Default |
|----------|----------|-------------|---------|
| `TELEGRAM_TOKEN` | ✅ | Bot token from @BotFather | - |
| `ALLOWED_TELEGRAM_USERNAME` | ✅ | Your Telegram username | - |

**Getting Bot Token:**
1. Open Telegram, search @BotFather
2. Send `/newbot`
3. Follow prompts
4. Copy token

### AI Model

| Variable | Required | Description | Default |
|----------|----------|-------------|---------|
| `MODEL_NAME` | ❌ | Ollama model name | `qwen2.5-coder:7b` |

**Alternative Models:**
```env
MODEL_NAME=llama3.2:3b      # Faster, less accurate
MODEL_NAME=qwen2.5:14b      # Slower, more accurate
MODEL_NAME=codellama:7b     # Code-focused
```

### Privacy Mode

| Variable | Required | Description | Default |
|----------|----------|-------------|---------|
| `OFFLINE_MODE` | ❌ | 100% local processing | `false` |

**When `OFFLINE_MODE=true`:**
- Voice recognition uses Vosk (local)
- No external API calls
- Slightly lower accuracy
- Maximum privacy

### Logging

| Variable | Required | Description | Default |
|----------|----------|-------------|---------|
| `LOG_LEVEL` | ❌ | Logging verbosity | `INFO` |

**Options:**
- `DEBUG` - Detailed debugging
- `INFO` - Standard operation
- `WARNING` - Warnings only
- `ERROR` - Errors only

### Gmail

| Variable | Required | Description |
|----------|----------|-------------|
| `GMAIL_ADDRESS` | ❌ | Your Gmail address |
| `GMAIL_APP_PASSWORD` | ❌ | App-specific password |

**Getting App Password:**
1. Enable 2FA on Google Account
2. Go to Security → App passwords
3. Generate new password for "Mail"
4. Copy 16-character password

---

## Configuration Files

### blacklist.json

Focus mode blocked items:

```json
{
  "apps": ["spotify", "discord", "steam"],
  "sites": ["youtube.com", "twitter.com"]
}
```

### clipboard_history.json

Stored clipboard data (auto-managed):

```json
[
  {
    "text": "copied text",
    "timestamp": "2025-02-09T10:30:00"
  }
]
```

### file_activity_log.json

File access history (auto-managed).

---

## Model Configuration

### Changing Models

```bash
# List available models
ollama list

# Pull new model
ollama pull llama3.2:3b

# Update .env
MODEL_NAME=llama3.2:3b
```

### Model Comparison

| Model | Size | RAM | Speed | Accuracy |
|-------|------|-----|-------|----------|
| `qwen2.5-coder:7b` | 4.7GB | 6GB | Medium | High |
| `llama3.2:3b` | 2GB | 4GB | Fast | Medium |
| `qwen2.5:14b` | 8GB | 12GB | Slow | Highest |

---

## Browser Extension Config

### Chrome Extension ID

After loading extension, find ID at:
```
chrome://extensions → JARVIX Tab Controller → ID
```

### Native Host Registration

```bash
python src/jarvix/scripts/register_native_host.py
```

This creates registry entries for native messaging.

---

## Startup Configuration

### Auto-Start

The installer configures Windows startup. Manual method:

1. `Win + R` → `shell:startup`
2. Create shortcut to `run_silent.vbs`

### Service Mode

For server deployment:
```bash
# Create scheduled task
schtasks /create /tn "JARVIX" /tr "wscript.exe path\to\run_silent.vbs" /sc onlogon
```

---

## Performance Tuning

### Low Memory Mode

For systems with <8GB RAM:

```env
MODEL_NAME=llama3.2:3b  # Smaller model
```

### High Performance Mode

For systems with 16GB+ RAM:

```env
MODEL_NAME=qwen2.5:14b  # Larger model
```

---

## Security Settings

### Restrict Access

Only specified user can control:
```env
ALLOWED_TELEGRAM_USERNAME=your_exact_username
```

### Disable Features

Comment out in `.env`:
```env
# GMAIL_ADDRESS=...   # Disables Gmail
```

---

**Next:** [Security Guide](SECURITY.md)
