# Docker Error Handling - UI/UX Guide

## Overview
This guide provides a visual walkthrough of the enhanced Docker error handling user interface, demonstrating how errors are presented to users and what actions they can take.

## UI Components

### 1. Primary Error Dialog

When a Docker container creation fails, users see a modal dialog with the following sections:

```
┌──────────────────────────────────────────────────────────────────┐
│  ❌ Docker Container Failed                                      │  ← Red header bar
├──────────────────────────────────────────────────────────────────┤
│                                                                   │
│  Error Type: Port Conflict                          ← Bold label │
│                                                                   │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │ Container: nextcloud-app  |  Port: 8080                 │    │  ← Info box
│  └─────────────────────────────────────────────────────────┘    │
│                                                                   │
│  Port 8080 is already in use by another application              │  ← Error message
│  or container.                                                    │     (red text)
│                                                                   │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │ 💡 Suggested Action:                                     │    │  ← Action box
│  │                                                           │    │     (green background)
│  │ Try one of these alternative ports: 8081, 8082, 8090     │    │
│  │                                                           │    │
│  │ Or stop the application/container using the port:        │    │
│  │   docker ps (to see running containers)                  │    │
│  │   docker stop <container-name> (to stop container)       │    │
│  └─────────────────────────────────────────────────────────┘    │
│                                                                   │
│  🔌 Try alternative port: 8081                    ← Gold highlight│
│                                                                   │
│  📁 Error logged to:                                             │  ← Gray hint text
│  ~/Documents/NextcloudLogs/nextcloud_docker_errors.log          │
│                                                                   │
│  ┌─────────────────────┐  ┌──────────┐                          │
│  │ 📋 Show Docker      │  │  Close   │            ← Action buttons│
│  │ Error Details       │  │          │                          │
│  └─────────────────────┘  └──────────┘                          │
│                                                                   │
└──────────────────────────────────────────────────────────────────┘
```

**Key Features:**
- **Visual Hierarchy**: Red header immediately indicates error severity
- **Structured Information**: Error type, container info, and message clearly separated
- **Actionable Guidance**: Green suggestion box with specific steps
- **Port Suggestion**: Highlighted alternative port for quick resolution
- **Log Location**: Users know where to find detailed logs
- **Next Steps**: Clear buttons for viewing details or closing

### 2. Detailed Error Dialog

When users click "Show Docker Error Details", they see a comprehensive view:

```
┌──────────────────────────────────────────────────────────────────────────────────┐
│  🐳 Docker Error: Port Conflict                                                  │  ← Dark header
├──────────────────────────────────────────────────────────────────────────────────┤
│  ┌────────────────────────────────────────────────────────────────────────────┐ │
│  │ ▼ Scrollable Content                                                       │ │
│  │                                                                             │ │
│  │  ┌──────────────────────────────────────────────────────────────────────┐ │ │
│  │  │ ❌ Error Description                                                  │ │ │  ← Blue info box
│  │  │                                                                        │ │ │
│  │  │ Port 8080 is already in use by another application or container.     │ │ │
│  │  └──────────────────────────────────────────────────────────────────────┘ │ │
│  │                                                                             │ │
│  │  ┌──────────────────────────────────────────────────────────────────────┐ │ │
│  │  │ 💡 Suggested Action                                                   │ │ │  ← Green action box
│  │  │                                                                        │ │ │
│  │  │ Try one of these alternative ports: 8081, 8082, 8090                 │ │ │
│  │  │                                                                        │ │ │
│  │  │ Or stop the application/container using the port:                    │ │ │
│  │  │   docker ps (to see running containers)                              │ │ │
│  │  │   docker stop <container-name> (to stop conflicting container)       │ │ │
│  │  └──────────────────────────────────────────────────────────────────────┘ │ │
│  │                                                                             │ │
│  │  ┌──────────────────────────────────────────────────────────────────────┐ │ │
│  │  │ 🔌 Alternative Port Suggestion                                        │ │ │  ← Yellow warning box
│  │  │                                                                        │ │ │
│  │  │ Try using port 8081 instead.                                         │ │ │
│  │  └──────────────────────────────────────────────────────────────────────┘ │ │
│  │                                                                             │ │
│  │  📋 Raw Docker Error Output                                                │ │
│  │                                                                             │ │
│  │  ┌──────────────────────────────────────────────────────────────────────┐ │ │
│  │  │ docker: Error response from daemon: driver failed programming     ▲ │ │ │  ← Monospace text
│  │  │ external connectivity on endpoint nextcloud-app: Bind for          │ │ │     box with scrollbar
│  │  │ 0.0.0.0:8080 failed: port is already allocated.                    │ │ │
│  │  │ ERRO[0000] error waiting for container: context canceled           ▼ │ │ │
│  │  └──────────────────────────────────────────────────────────────────────┘ │ │
│  │                                                                             │ │
│  │  📁 Docker errors are logged to:                                           │ │
│  │  ~/Documents/NextcloudLogs/nextcloud_docker_errors.log                    │ │
│  └────────────────────────────────────────────────────────────────────────────┘ │
│                                                                                  │
│  ┌──────────────────────────┐                              ┌────────┐          │
│  │ 📂 Open Docker Error Log │                              │ Close  │          │
│  └──────────────────────────┘                              └────────┘          │
└──────────────────────────────────────────────────────────────────────────────────┘
```

**Key Features:**
- **Complete Context**: All error information in one place
- **Scrollable Content**: Handles long error messages gracefully
- **Color-Coded Sections**: Blue for description, green for actions, yellow for warnings
- **Raw Output**: Full Docker stderr for advanced troubleshooting
- **Quick Access**: Button to open log file location directly

## Error Scenarios and UI Flow

### Scenario 1: Port Conflict

**User Action**: Starts restore with port 8080
**Docker Error**: Port already in use
**UI Response**:
1. Shows primary error dialog with "Port Conflict" type
2. Displays message: "Port 8080 is already in use"
3. Highlights alternative port: 8081
4. Provides commands to check/stop conflicting containers
5. User can click "Show Docker Error Details" for full output
6. User can choose to retry with suggested port

### Scenario 2: Image Not Found

**User Action**: Restore process attempts to pull Nextcloud image
**Docker Error**: Image not found or network issue
**UI Response**:
1. Shows error dialog with "Image Not Found" type
2. Suggests checking internet connection
3. Provides manual pull command
4. Offers to retry after fixing issue

### Scenario 3: Container Name Conflict

**User Action**: Tries to create container with existing name
**Docker Error**: Container name already in use
**UI Response**:
1. Shows error with conflicting container name
2. Provides `docker rm` command to remove existing container
3. Suggests choosing different name in wizard
4. Shows which container ID is using the name

### Scenario 4: Docker Not Running

**User Action**: Attempts restore without Docker running
**Docker Error**: Cannot connect to Docker daemon
**UI Response**:
1. Clear message: "Docker daemon is not running"
2. Platform-specific instructions:
   - Windows/Mac: "Open Docker Desktop"
   - Linux: "sudo systemctl start docker"
3. Instructs to retry after starting Docker

### Scenario 5: Permission Denied

**User Action**: Runs restore without proper Docker permissions
**Docker Error**: Permission denied on Docker socket
**UI Response**:
1. Identifies permission issue
2. Platform-specific solutions:
   - Windows: "Run as Administrator"
   - Linux: "Add user to docker group"
3. Provides exact commands needed

## Color Scheme

### Primary Error Dialog
- **Header**: Red (#d32f2f) - Error severity
- **Info Box**: Theme info background - Container details
- **Action Box**: Light green (#e8f5e9) - Suggested actions
- **Alternative Port**: Gold/Amber (#f7b32b) - Important suggestion
- **Log Location**: Gray hint text - Reference information

### Detailed Error Dialog
- **Header**: Dark theme header - Professional appearance
- **Error Description**: Blue info box - Clear identification
- **Suggested Action**: Green box - Positive guidance
- **Alternative Port**: Yellow warning box - Attention grabber
- **Raw Output**: Monospace dark text box - Technical details

## Accessibility Features

1. **Clear Labels**: All sections have descriptive emoji + text labels
2. **High Contrast**: Red errors, green actions, yellow warnings
3. **Readable Text**: Minimum 10pt font, wrapping enabled
4. **Keyboard Navigation**: All dialogs support Tab/Enter/Esc
5. **Screen Reader Friendly**: Semantic structure with clear headings

## User Journey Improvements

### Before Enhancement
1. "Failed to start Nextcloud container" → User confused
2. Brief error shown → No context
3. User googles error → Time-consuming
4. Trial and error → Frustrating

### After Enhancement
1. "Port Conflict" → User understands issue immediately
2. "Try port 8081" → Clear action
3. User updates port → Quick resolution
4. Success! → Positive experience

## Log File Integration

### Docker Error Log Location
```
~/Documents/NextcloudLogs/nextcloud_docker_errors.log
```

### Log Format
```
================================================================================
[2024-10-19 18:45:32] Docker Error: port_conflict
================================================================================
Container: nextcloud-app
Port: 8080
Error Message:
docker: Error response from daemon: driver failed programming external 
connectivity on endpoint nextcloud-app: Bind for 0.0.0.0:8080 failed: 
port is already allocated.

Additional Information:
Full traceback:
Traceback (most recent call last):
  ...
================================================================================
```

**Benefits**:
- Structured format for easy parsing
- Timestamp for tracking issues over time
- Context included (container, port, etc.)
- Full traceback for debugging
- Separate file from main logs

## Best Practices Demonstrated

1. **Progressive Disclosure**: 
   - Primary dialog shows key info
   - Details dialog for deep dive

2. **Actionable Errors**:
   - Always provide next steps
   - Include specific commands
   - Suggest alternatives

3. **Context Preservation**:
   - Log all errors
   - Keep full stderr
   - Record timestamps

4. **User Guidance**:
   - Explain what happened
   - Show why it matters
   - Tell how to fix

5. **Professional Appearance**:
   - Consistent color scheme
   - Clear visual hierarchy
   - Polished dialogs

## Testing the UI

### Manual Testing Steps

1. **Port Conflict Test**:
   ```bash
   # Start a container on port 8080
   docker run -d -p 8080:80 nginx
   # Try restore with port 8080
   # Should see port conflict dialog with alternative ports
   ```

2. **Container Name Test**:
   ```bash
   # Create a container with the target name
   docker run -d --name nextcloud-app nginx
   # Try restore with same name
   # Should see name conflict dialog
   ```

3. **Docker Not Running Test**:
   ```bash
   # Stop Docker
   # Try restore
   # Should see daemon not running dialog
   ```

### Visual Demo
Run the included demo script:
```bash
python3 tests/demo_docker_error_handling.py
```

This shows all error scenarios with actual UI dialogs.

## Conclusion

The enhanced Docker error handling provides:
- **Clear Communication**: Users understand what went wrong
- **Actionable Guidance**: Specific steps to resolve issues
- **Professional UX**: Polished, informative dialogs
- **Efficient Troubleshooting**: Dedicated logs and detailed views
- **Beginner Friendly**: No Docker expertise required

This implementation transforms Docker errors from obstacles into solvable problems with clear paths to resolution.
