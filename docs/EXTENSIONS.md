# Browser Extensions Guide

Complete guide for JARVIX browser extensions.

## Overview

JARVIX includes browser extensions for advanced features:
- Real-time tab monitoring
- Tab control (close, mute, screenshot)
- Media control (play/pause)
- Native messaging integration

---

## Chrome Extension

### Installation

1. Open Chrome and go to `chrome://extensions`
2. Enable **Developer mode** (toggle in top-right)
3. Click **Load unpacked**
4. Select the `browser_extension/` folder

### Files

```
browser_extension/
├── manifest.json     # Extension configuration
├── background.js     # Service worker
├── popup.html        # Extension popup UI
├── popup.js          # Popup logic
└── icons/
    ├── icon16.png
    ├── icon48.png
    └── icon128.png
```

### Features

| Feature | Description |
|---------|-------------|
| Tab Tracking | Reports active tabs to JARVIX |
| Tab Control | Close/mute tabs via commands |
| Media Control | Play/pause media in tabs |
| Screenshot | Capture specific tabs |

---

## Firefox Extension

### Installation

1. Open Firefox and go to `about:debugging`
2. Click **This Firefox** in sidebar
3. Click **Load Temporary Add-on**
4. Select `firefox_extension/manifest.json`

> **Note:** Temporary add-ons are removed when Firefox closes. For permanent installation, sign through Mozilla Add-ons.

### Files

```
firefox_extension/
├── manifest.json     # Extension configuration
├── background.js     # Background script
├── icon16.png
├── icon48.png
└── icon128.png
```

---

## Native Messaging

Native messaging allows the extension to communicate with JARVIX directly.

### Setup

```bash
python src/jarvix/scripts/register_native_host.py
```

This registers the native host with your browser.

### How It Works

```
Browser Extension ←→ Native Host ←→ JARVIX
     (JS)              (Python)      (Agent)
```

### Configuration

Native host config (`core/jarvix_native_host.json`):

```json
{
  "name": "jarvix_native_host",
  "description": "JARVIX Native Messaging Host",
  "path": "path/to/browser_host.py",
  "type": "stdio",
  "allowed_origins": ["chrome-extension://...", "moz-extension://..."]
}
```

---

## Commands

### Tab Management

| Command | Example |
|---------|---------|
| Close tab | "Close the YouTube tab" |
| Mute tab | "Mute Spotify" |
| Tab screenshot | "Screenshot this page" |

### Media Control

| Command | Example |
|---------|---------|
| Play | "Play the video" |
| Pause | "Pause the music" |
| Next | "Next track" |

---

## Tab Matching

JARVIX uses smart matching to find tabs:

### By Title
```
"Close YouTube" → Finds tab with "YouTube" in title
```

### By URL
```
"Mute spotify.com" → Finds tab with spotify.com URL
```

### By Context
```
"Close it" → Closes most recently focused tab
```

### Ranking
When multiple tabs match, JARVIX ranks by:
1. Exact title match
2. Partial title match
3. URL match
4. Recent focus time

---

## Troubleshooting

### Extension Not Loading

**Chrome:**
- Ensure Developer mode is enabled
- Check for manifest errors in Extensions page

**Firefox:**
- Use `about:debugging` → "This Firefox"
- Check Browser Console for errors

### Native Host Not Working

1. Re-run registration:
   ```bash
   python src/jarvix/scripts/register_native_host.py
   ```

2. Verify registry (Windows):
   ```bash
   reg query HKCU\SOFTWARE\Google\Chrome\NativeMessagingHosts
   ```

3. Check host path in JSON config

### Tabs Not Tracking

1. Verify extension is active (icon visible)
2. Refresh browser
3. Restart JARVIX

### Permission Errors

Ensure extension has required permissions:
- `tabs` - Tab access
- `activeTab` - Current tab info
- `nativeMessaging` - Host communication

---

## Development

### Modifying Extensions

1. Edit files in `browser_extension/` or `firefox_extension/`
2. Save changes
3. Reload extension:
   - **Chrome:** Click refresh icon in `chrome://extensions`
   - **Firefox:** Click "Reload" in `about:debugging`

### Adding Features

1. Add message handler in `background.js`
2. Add corresponding handler in `browser_host.py`
3. Connect to JARVIX agent

### Debugging

**Chrome:**
- Open DevTools on extension popup
- Check background page console

**Firefox:**
- Use Browser Console (Ctrl+Shift+J)
- Debug with `about:debugging`

---

## Security

### Permissions Used

| Permission | Purpose |
|------------|---------|
| `tabs` | Read/modify tabs |
| `activeTab` | Current tab operations |
| `nativeMessaging` | Connect to JARVIX |
| `scripting` | Tab screenshots |

### Privacy

- Extensions only communicate with local JARVIX instance
- No data sent to external servers
- Tab info stays on your machine

---

**Back to:** [Documentation Index](README.md)
