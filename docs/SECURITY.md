# Security & Privacy

How JARVIX protects your data and privacy.

## Privacy-First Design

JARVIX was built with one core principle: **Your data never leaves your machine.**

```
┌────────────────────────────────────────────────┐
│                YOUR PC                          │
│  ┌──────────────────────────────────────────┐  │
│  │  JARVIX + Ollama + All Processing        │  │
│  │  ═══════════════════════════════════     │  │
│  │  Voice → Local Vosk                      │  │
│  │  AI    → Local Ollama                    │  │
│  │  Data  → Local JSON files                │  │
│  └──────────────────────────────────────────┘  │
│                     ↕                          │
│            Telegram (optional)                  │
└────────────────────────────────────────────────┘
```

---

## What Stays Local

| Data | Storage | Never Leaves PC |
|------|---------|-----------------|
| Voice commands | Processed → discarded | ✅ |
| AI responses | In-memory only | ✅ |
| Clipboard history | `clipboard_history.json` | ✅ |
| File activity | `file_activity_log.json` | ✅ |
| User preferences | `memory.json` | ✅ |
| Screenshots | Sent via Telegram only | ⚠️ |
| Audio recordings | Sent via Telegram only | ⚠️ |

**Note:** Screenshots and audio are only sent if you explicitly request them via Telegram.

---

## External Connections

### Required
| Service | Purpose | Data Sent |
|---------|---------|-----------|
| Telegram API | Remote control | Commands, media |

### Optional (can be disabled)
| Service | Purpose | Disable Method |
|---------|---------|----------------|
| Google Speech | Voice accuracy | `OFFLINE_MODE=true` |
| IP Geolocation | Location feature | Don't use `/location` |
| Gmail IMAP | Email features | Remove Gmail config |

---

## Offline Mode

For maximum privacy, enable offline mode:

```env
OFFLINE_MODE=true
```

**This ensures:**
- ✅ No Google API calls
- ✅ Voice uses Vosk (local)
- ✅ Only Telegram connection remains

---

## Access Control

### Telegram Authentication

Only your username can control the bot:

```env
ALLOWED_TELEGRAM_USERNAME=your_exact_username
```

**Security behavior:**
- Messages from other users are ignored
- No response is sent to unauthorized users
- All attempts are logged

### No Public Endpoints

JARVIX does not expose:
- Web servers
- API endpoints
- Network listeners
- Remote desktop access

---

## Data Storage

### Local Files

```
📁 Project Root
├── clipboard_history.json     # Last 100 copied texts
├── file_activity_log.json     # 30-day file access log
├── blacklist.json             # Focus mode settings
└── .env                       # Your credentials (never commit!)
```

### Data Retention

| Data | Retention | Auto-cleanup |
|------|-----------|--------------|
| Clipboard | Last 100 items | ✅ FIFO |
| File log | 30 days | ✅ Daily |
| Memory | Session | ✅ On restart |

---

## Credential Security

### .env File

**Never commit `.env` to git!**

`.gitignore` includes:
```
.env
*.env
```

### Gmail App Password

- Uses app-specific password, not main password
- Limited to mail access only
- Can be revoked anytime
- No OAuth tokens stored

---

## Threat Model

### What JARVIX Protects Against

| Threat | Protection |
|--------|------------|
| Cloud data collection | All processing local |
| API cost exploitation | No paid APIs used |
| Account compromise | Single-user whitelist |
| Data interception | SSL for all connections |

### What You Should Consider

| Risk | Mitigation |
|------|------------|
| Physical access | Lock your PC |
| Telegram account theft | Enable 2FA on Telegram |
| .env file exposure | Keep file permissions secure |
| Malware | Keep Windows updated |

---

## Best Practices

### For Personal Use

1. ✅ Use unique Telegram bot (don't share)
2. ✅ Enable Telegram 2FA
3. ✅ Keep `.env` permissions restricted
4. ✅ Use `OFFLINE_MODE=true` if maximum privacy needed

### For Development

1. ✅ Never commit credentials
2. ✅ Use `.env.example` for templates
3. ✅ Audit dependencies regularly
4. ✅ Review logs for suspicious activity

---

## Audit

JARVIX is open source. You can audit:

- All source code in `src/`
- All dependencies in `pyproject.toml`
- All network calls (grep for `requests`, `http`, `socket`)

**Zero telemetry. Zero analytics. Zero tracking.**

---

## Reporting Security Issues

Found a vulnerability? Please report responsibly:

1. Do not create public issues
2. Email security concerns directly
3. Allow time for patching

---

**Next:** [API Reference](API.md)
