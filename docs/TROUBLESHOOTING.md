# Troubleshooting

Common issues and solutions.

## Installation Issues

### Python Not Found

**Symptoms:**
```
'python' is not recognized as an internal or external command
```

**Solution:**
```bash
# Install Python
winget install Python.Python.3.11

# Restart terminal
# Or add to PATH manually
```

---

### Ollama Not Starting

**Symptoms:**
```
Error: Could not connect to Ollama
```

**Solution:**
```bash
# Check if Ollama is running
ollama list

# If not, start it
ollama serve

# Or reinstall
winget install Ollama.Ollama
```

---

### Model Download Fails

**Symptoms:**
```
Error pulling model: connection timeout
```

**Solution:**
```bash
# Check internet connection
ping google.com

# Retry with smaller model first
ollama pull llama3.2:3b

# Then try main model
ollama pull qwen2.5-coder:7b
```

---

## Telegram Bot Issues

### Bot Not Responding

**Checklist:**
1. ✓ Is JARVIX running?
2. ✓ Is `TELEGRAM_TOKEN` correct?
3. ✓ Is `ALLOWED_TELEGRAM_USERNAME` your exact username?
4. ✓ Is Ollama running?

**Debug:**
```bash
# Run in visible mode
start_jarvix.bat

# Check console for errors
```

---

### "Unauthorized" Messages

**Cause:** Username mismatch

**Solution:**
```env
# Use your exact Telegram username (without @)
ALLOWED_TELEGRAM_USERNAME=your_username
```

---

### Media Not Sending

**Symptoms:** Screenshots/audio don't arrive

**Solution:**
1. Check file exists in project folder
2. Verify bot has file access
3. Check Telegram file size limits (50MB)

---

## Voice Issues

### Wake Word Not Detected

**Checklist:**
1. ✓ Microphone working?
2. ✓ Vosk model downloaded?
3. ✓ Correct wake word phrase?

**Test Microphone:**
```bash
# Open Sound Settings
# Speak and watch input level
```

---

### Speech Not Recognized

**Symptoms:** "I had a brain glitch" response

**Solution:**
```bash
# Check Ollama is responding
ollama run qwen2.5-coder:7b "Hello"

# Restart JARVIX
stop_jarvix.bat
start_jarvix.bat
```

---

## Gmail Issues

### Connection Failed

**Error:**
```
❌ Gmail login failed: Invalid credentials
```

**Solutions:**

1. **Enable 2FA** on Google Account
2. **Generate App Password:**
   - Go to Google Account → Security
   - 2-Step Verification → App passwords
   - Generate for "Mail"
3. **Update `.env`:**
   ```env
   GMAIL_APP_PASSWORD=xxxx xxxx xxxx xxxx
   ```

---

### IMAP Not Enabled

**Error:**
```
❌ Gmail connection error: IMAP disabled
```

**Solution:**
1. Open Gmail Settings
2. See all settings → Forwarding and POP/IMAP
3. Enable IMAP

---

### No Emails Found

**Possible causes:**
- Credentials incorrect
- Inbox empty
- IMAP folder issue

**Debug:**
```python
# Test in Python
from jarvix.features.gmail import test_connection
test_connection()
```

---

## Performance Issues

### High CPU Usage

**Cause:** Ollama processing

**Solutions:**
1. Use smaller model:
   ```env
   MODEL_NAME=llama3.2:3b
   ```
2. Increase Ollama timeout
3. Close other heavy applications

---

### High Memory Usage

**Cause:** Ollama model loaded in RAM

**Solutions:**
1. Use smaller model (3B vs 7B)
2. Set Ollama to unload after use:
   ```python
   # In brain.py, keep_alive=0 already configured
   ```

---

### Slow Response

**Causes:**
- Model too large
- CPU-only inference
- Background tasks

**Solutions:**
1. Use GPU if available
2. Switch to smaller model
3. Disable file tracking if not needed

---

## Browser Extension Issues

### Extension Not Loaded

**Chrome:**
1. Go to `chrome://extensions`
2. Enable "Developer mode"
3. "Load unpacked" → select `browser_extension/`

**Firefox:**
1. Go to `about:debugging`
2. "This Firefox" → "Load Temporary Add-on"
3. Select `manifest.json`

---

### Tabs Not Tracking

**Solution:**
1. Verify extension is active (icon visible)
2. Check native host registration:
   ```bash
   python src/jarvix/scripts/register_native_host.py
   ```
3. Restart browser

---

## Common Error Messages

### "I had a brain glitch"

**Cause:** AI failed to process command

**Solutions:**
- Rephrase command
- Check Ollama is running
- Restart JARVIX

---

### "Failed to connect"

**Cause:** Network/service unavailable

**Solutions:**
- Check internet connection
- Verify service is running
- Check credentials

---

### "No permission"

**Cause:** Windows security blocking

**Solutions:**
- Run as administrator (for camera/audio)
- Check antivirus isn't blocking
- Add exception for JARVIX

---

## Logs

### Viewing Logs

```bash
# Console output in start_jarvix.bat
# Or check Windows Event Viewer for errors
```

### Enabling Debug Mode

```env
LOG_LEVEL=DEBUG
```

---

## Reset Everything

If all else fails:

```bash
# Stop JARVIX
stop_jarvix.bat

# Delete config files
del .env
del clipboard_history.json
del file_activity_log.json

# Reinstall
pip install -e .

# Reconfigure
copy .env.example .env
# Edit .env with your settings
```

---

## Getting Help

1. Check this guide first
2. Search existing issues
3. Create new issue with:
   - Error message
   - Steps to reproduce
   - System info (Windows version, RAM)
   - Relevant logs

---

**Back to:** [Documentation Index](README.md)
