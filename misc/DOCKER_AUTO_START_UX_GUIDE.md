# Docker Auto-Start - User Experience Guide

## Before: Dialog-Based Flow

When Docker was not running, users would see a popup dialog:

```
┌──────────────────────────────────────────────────────┐
│  ⚠ Docker Not Running                           [X]  │
├──────────────────────────────────────────────────────┤
│                                                      │
│  Docker is not currently running on your system.     │
│  This utility requires Docker to manage Nextcloud    │
│  containers.                                         │
│                                                      │
│  ┌────────────────────────────────────────────────┐ │
│  │  Start Docker Desktop:                         │ │
│  │  1. Open Docker Desktop from the Start menu    │ │
│  │  2. Wait for Docker to fully start             │ │
│  │  3. Try again once Docker is running           │ │
│  └────────────────────────────────────────────────┘ │
│                                                      │
│  ┌──────────────────┐  ┌───────┐  ┌───────┐        │
│  │ Start Docker     │  │ Retry │  │Cancel │        │
│  │    Desktop       │  └───────┘  └───────┘        │
│  └──────────────────┘                               │
│                                                      │
└──────────────────────────────────────────────────────┘
```

**Problems:**
- Blocks the entire UI
- Requires manual user intervention
- Multiple clicks needed
- Interrupts workflow

## After: Silent Auto-Start Flow

When Docker is not running, the app now:

1. **Detects** Docker is not running (silently)
2. **Attempts** to start Docker Desktop automatically (no dialog)
3. **Waits** up to 30 seconds for Docker to start (background)
4. **Shows** status in the main UI

### Main Application Window

```
┌────────────────────────────────────────────────────────────┐
│  Nextcloud Backup & Restore                    ☀️ 🔔 ☰    │
├────────────────────────────────────────────────────────────┤
│                                                            │
│  Status: Docker Desktop is starting...                     │
│          (shown in red/error color if fails)               │
│                                                            │
│  ┌──────────────────────────────────────────────────────┐ │
│  │                                                      │ │
│  │                  [Main Content]                      │ │
│  │                                                      │ │
│  │            User can continue to interact             │ │
│  │                                                      │ │
│  └──────────────────────────────────────────────────────┘ │
│                                                            │
└────────────────────────────────────────────────────────────┘
```

### Success Scenario (Docker Starts)

```
Timeline:
  0s:  User clicks "Restore from backup" or "Start new instance"
  0s:  App detects Docker is not running
  0s:  App issues Docker Desktop start command
  0s:  Returns to main screen (no blocking dialog)
  3-15s: Docker Desktop starts in background
  →  App proceeds automatically to next step
```

### Timeout Scenario (Docker Doesn't Start)

```
Timeline:
  0s:  User clicks "Restore from backup" or "Start new instance"
  0s:  App detects Docker is not running
  0s:  App issues Docker Desktop start command
  0-30s: Waits for Docker to become available
  30s: Timeout - Shows error in status label:

  Status: "Docker Desktop is starting but not ready yet.
          Please wait a moment and try again."
          (shown in red/error color)

  → User returns to main menu, can try again
```

### Linux/No Docker Desktop Scenario

```
Timeline:
  0s:  User clicks "Restore from backup" or "Start new instance"
  0s:  App detects Docker is not running
  0s:  No Docker Desktop found (Linux system)
  0s:  Shows error in status label:

  Status: "Could not start Docker automatically.
          Please start Docker Desktop manually."
          (shown in red/error color)

  → User returns to main menu
```

## Benefits

### 1. Non-Intrusive
- No blocking dialogs
- Status shown in existing UI element
- User can still interact with the app

### 2. Automatic
- No manual clicking required
- Silent operation in the background
- Only shows messages on failure

### 3. Fast
- Immediate feedback
- No delay from user interaction
- Automatic progression when successful

### 4. Platform-Aware
- Windows: Starts Docker Desktop automatically
- macOS: Starts Docker Desktop automatically
- Linux: Shows helpful message (no Docker Desktop)

## Error Messages

All error messages are shown in the status label with theme-aware error colors:

**Light Theme:**
- Error text: `#d32f2f` (red)

**Dark Theme:**
- Error text: `#ef5350` (light red)

## Logging

All Docker startup activity is logged:

```
[INFO] Docker is not running, attempting to start Docker Desktop automatically...
[INFO] Docker Desktop start command issued, waiting for Docker to become available...
[DEBUG] Waiting for Docker to start... (3s/30s)
[DEBUG] Waiting for Docker to start... (6s/30s)
[INFO] Docker started successfully after 9 seconds
```

Or on failure:

```
[INFO] Docker is not running, attempting to start Docker Desktop automatically...
[ERROR] Could not start Docker automatically. Please start Docker Desktop manually.
```

## Code Impact

### Minimal Changes
- Modified 1 method: `check_docker_running()`
- Enhanced 1 function: `start_docker_desktop()` (better logging)
- No changes to Docker detection logic
- No changes to workflows (restore/new instance)

### Backward Compatible
- Old `prompt_start_docker()` function remains (not called)
- All existing tests pass
- No breaking changes
