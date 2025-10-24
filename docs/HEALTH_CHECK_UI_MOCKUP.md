# Tailscale Health Check - UI Mockup

## Page Location
**Main Menu** → **Remote Access Setup** → **Configure Remote Access**

---

## UI Layout

```
┌─────────────────────────────────────────────────────────────────────┐
│                                                                     │
│  ⚙️ Configure Remote Access                                        │
│                                                                     │
│  [← Back to Remote Access Setup]                                   │
│                                                                     │
│  ┌─────────────────────────────────────────────────────────────┐  │
│  │ 📡 Your Tailscale Network Information                        │  │
│  │                                                               │  │
│  │ Tailscale IP: 100.64.1.2                                     │  │
│  │ MagicDNS Name: myserver.tailnet.ts.net                       │  │
│  │                                                               │  │
│  │ 🌐 Access Nextcloud via:                                     │  │
│  │   Local: http://localhost:8080                               │  │
│  │   Tailscale IP: https://100.64.1.2                           │  │
│  │   Tailscale Hostname: https://myserver.tailnet.ts.net        │  │
│  │                                                               │  │
│  │ Use these addresses to access Nextcloud from any device      │  │
│  │ on your Tailscale network.                                   │  │
│  └─────────────────────────────────────────────────────────────┘  │
│                                                                     │
│  Connection Health Check                                            │
│                                                                     │
│  Test your Tailscale Serve configuration and verify accessibility: │
│                                                                     │
│  ┌─────────────────────────────────────────────────────────────┐  │
│  │              🔍 Run Health Check                              │  │
│  └─────────────────────────────────────────────────────────────┘  │
│                                                                     │
│  [When button clicked, shows:]                                      │
│                                                                     │
│  ┌─────────────────────────────────────────────────────────────┐  │
│  │ ⏳ Running health checks...                                   │  │
│  └─────────────────────────────────────────────────────────────┘  │
│                                                                     │
│  [After checks complete, shows one of these results:]              │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Result Display - Success Scenario

```
┌─────────────────────────────────────────────────────────────────────┐
│  ┌─────────────────────────────────────────────────────────────┐  │
│  │ ✅ All checks passed!                                         │  │
│  │                                                               │  │
│  │ ✓ Tailscale Serve Status                                     │  │
│  │    Tailscale Serve is running and configured for port 8080   │  │
│  │                                                               │  │
│  │ ✓ Nextcloud Port Detection                                   │  │
│  │    Nextcloud detected on port 8080                           │  │
│  │                                                               │  │
│  │ ✓ Tailscale IP Accessibility                                 │  │
│  │    Tailscale IP 100.64.1.2 is accessible via HTTPS           │  │
│  │    🔗 https://100.64.1.2                                     │  │
│  │                                                               │  │
│  │ ✓ MagicDNS Hostname Accessibility                            │  │
│  │    MagicDNS hostname myserver.tailnet.ts.net is accessible   │  │
│  │    🔗 https://myserver.tailnet.ts.net                        │  │
│  │                                                               │  │
│  └─────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Result Display - Partial Failure Scenario

```
┌─────────────────────────────────────────────────────────────────────┐
│  ┌─────────────────────────────────────────────────────────────┐  │
│  │ ⚠️ Some checks failed                                         │  │
│  │                                                               │  │
│  │ ✗ Tailscale Serve Status                                     │  │
│  │    Tailscale Serve is not configured                         │  │
│  │    💡 Suggestion: Enable automatic Tailscale Serve below     │  │
│  │                                                               │  │
│  │ ✓ Nextcloud Port Detection                                   │  │
│  │    Nextcloud detected on port 8080                           │  │
│  │                                                               │  │
│  │ ✗ Tailscale IP Accessibility                                 │  │
│  │    Cannot connect to Tailscale IP                            │  │
│  │    🔗 https://100.64.1.2                                     │  │
│  │    💡 Suggestion: Ensure Tailscale Serve is running and      │  │
│  │       check scheduled task status                            │  │
│  │                                                               │  │
│  │ ✗ MagicDNS Hostname Accessibility                            │  │
│  │    Cannot connect to MagicDNS hostname                       │  │
│  │    🔗 https://myserver.tailnet.ts.net                        │  │
│  │    💡 Suggestion: Ensure Tailscale Serve is running          │  │
│  │                                                               │  │
│  └─────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Result Display - Complete Failure Scenario

```
┌─────────────────────────────────────────────────────────────────────┐
│  ┌─────────────────────────────────────────────────────────────┐  │
│  │ ❌ Multiple checks failed                                     │  │
│  │                                                               │  │
│  │ ✗ Tailscale Serve Status                                     │  │
│  │    Tailscale service is not running                          │  │
│  │    💡 Suggestion: Start Tailscale from the application       │  │
│  │       or system tray                                         │  │
│  │                                                               │  │
│  │ ✓ Nextcloud Port Detection                                   │  │
│  │    Nextcloud detected on port 8080                           │  │
│  │                                                               │  │
│  │ ✗ Tailscale IP Accessibility                                 │  │
│  │    Tailscale IP not available                                │  │
│  │    💡 Suggestion: Check Tailscale connection and ensure      │  │
│  │       you're logged in                                       │  │
│  │                                                               │  │
│  │ ✗ MagicDNS Hostname Accessibility                            │  │
│  │    MagicDNS hostname not available                           │  │
│  │    💡 Suggestion: Enable MagicDNS in Tailscale admin console │  │
│  │                                                               │  │
│  └─────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Color Scheme

### Success State
- ✅ Icon: Green
- ✓ Check marks: Green (#45bf55)
- Background: Info background color

### Warning State
- ⚠️ Icon: Orange
- Message: Orange (#FFA500)
- Background: Info background color

### Error State
- ❌ Icon: Red
- ✗ X marks: Red (error_fg theme color)
- Message: Red
- Background: Info background color

### Interactive Elements
- 🔗 Links: Blue (#3daee9), underlined, clickable
- 💡 Suggestions: Hint foreground color, italic

---

## User Interaction

1. **Click "Run Health Check" button**
   - Button becomes disabled (prevents multiple simultaneous checks)
   - Loading indicator appears: "⏳ Running health checks..."

2. **Health checks execute** (2-10 seconds depending on network)
   - Runs in background thread (UI remains responsive)
   - Checks performed sequentially

3. **Results appear**
   - Loading indicator replaced with results panel
   - Color-coded status header (✅/⚠️/❌)
   - Individual check results with details
   - Clickable URLs open in browser
   - Clear suggestions for any failures

4. **User can click button again** to re-run checks
   - Useful after making configuration changes
   - Previous results are cleared

---

## Key Features

✅ **Non-blocking**: Health checks run in background thread
✅ **Clear visual feedback**: Color-coded results (green/orange/red)
✅ **Actionable suggestions**: Every failure includes a troubleshooting tip
✅ **Clickable links**: URLs open directly in browser for testing
✅ **Self-contained**: All checks run locally, no external dependencies
✅ **Error resilient**: Gracefully handles SSL cert errors (common with Tailscale)
