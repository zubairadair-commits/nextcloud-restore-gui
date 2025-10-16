# Tailscale Detection Flow

## Detection Process Flowchart

```
┌─────────────────────────────────────────────────────────┐
│  App needs to check if Tailscale is installed          │
└─────────────────────┬───────────────────────────────────┘
                      │
                      ▼
          ┌───────────────────────┐
          │  Is Windows?          │
          └───────────┬───────────┘
                      │
        ┌─────────────┴─────────────┐
        │                           │
        ▼ No                        ▼ Yes
┌───────────────┐       ┌─────────────────────────────┐
│ Use 'which'   │       │  Call find_tailscale_exe()  │
│  tailscale    │       └──────────┬──────────────────┘
└───────────────┘                  │
                                   ▼
                      ┌────────────────────────────┐
                      │  METHOD 1: Check PATH      │
                      │  Run: where tailscale      │
                      └──────────┬─────────────────┘
                                 │
                                 ├─ Found? ──────────────┐
                                 │                       │
                                 ▼ Not found            ▼ Yes
                    ┌────────────────────────────┐      │
                    │  METHOD 2: Common Dirs     │      │
                    │  Check:                    │      │
                    │  • Program Files\Tailscale │      │
                    │  • Program Files (x86)     │      │
                    │  • LocalAppData\Tailscale  │      │
                    └──────────┬─────────────────┘      │
                               │                        │
                               ├─ Found? ──────────┐    │
                               │                   │    │
                               ▼ Not found        ▼    │
                  ┌────────────────────────────┐   │    │
                  │  METHOD 3: Registry        │   │    │
                  │  Query:                    │   │    │
                  │  • HKLM\SOFTWARE\...       │   │    │
                  │  • HKCU\SOFTWARE\...       │   │    │
                  └──────────┬─────────────────┘   │    │
                             │                     │    │
                             ├─ Found? ────────┐   │    │
                             │                 │   │    │
                             ▼ Not found      ▼   ▼    ▼
                  ┌──────────────────┐   ┌──────────────────┐
                  │  Return None     │   │  Return Full     │
                  │  (Not Installed) │   │  Path to exe     │
                  └──────────────────┘   └──────────────────┘
                             │                     │
                             └──────────┬──────────┘
                                        │
                                        ▼
                           ┌────────────────────────┐
                           │  Update UI Status      │
                           │                        │
                           │  ✓ Installed           │
                           │    or                  │
                           │  ✗ Not Installed       │
                           └────────────────────────┘
```

## Code Usage Flow

```
User Opens Remote Access Setup
            │
            ▼
    show_tailscale_wizard()
            │
            ├─→ _check_tailscale_installed()
            │            │
            │            └─→ find_tailscale_exe() (Windows)
            │                      │
            │                      └─→ Returns: path or None
            │
            ├─→ _check_tailscale_running()
            │            │
            │            └─→ Uses full path if available
            │                      │
            │                      └─→ subprocess.run([path, 'status'])
            │
            └─→ _display_tailscale_info()
                         │
                         └─→ _get_tailscale_info()
                                    │
                                    └─→ subprocess.run([path, 'status', '--json'])
```

## Example Detection Scenarios

### Scenario A: Standard Installation (PATH Available)
```
Windows 10 User installs Tailscale via MSI installer
→ Tailscale adds itself to PATH
→ Method 1: where tailscale
   Result: C:\Program Files\Tailscale\tailscale.exe
→ Detection: ✓ INSTALLED
→ Status Check: Uses full path
```

### Scenario B: Custom Installation (Not in PATH)
```
User installs Tailscale to custom directory
→ PATH environment variable not updated
→ Method 1: where tailscale
   Result: Not found (exit code 1)
→ Method 2: Check C:\Program Files\Tailscale\tailscale.exe
   Result: File exists ✓
→ Detection: ✓ INSTALLED
→ Status Check: Uses full path
```

### Scenario C: Portable/Custom Location with Registry
```
User runs Tailscale from D:\Apps\Tailscale
→ PATH not updated, not in standard locations
→ Method 1: where tailscale
   Result: Not found
→ Method 2: Standard directories
   Result: Not found
→ Method 3: Check registry HKLM\SOFTWARE\Tailscale IPN
   Result: InstallDir = D:\Apps\Tailscale
→ Detection: ✓ INSTALLED
→ Status Check: Uses full path
```

### Scenario D: Not Installed
```
User has not installed Tailscale
→ Method 1: where tailscale
   Result: Not found
→ Method 2: Standard directories
   Result: Not found
→ Method 3: Registry
   Result: Not found
→ Detection: ✗ NOT INSTALLED
→ UI: Shows installation instructions
```

## Health Check Integration

The `check_service_health()` function also uses enhanced detection:

```python
def check_service_health():
    # ...
    
    # Check Tailscale
    if platform.system() == "Windows":
        tailscale_path = find_tailscale_exe()
        
        if tailscale_path:
            # Found - check if running
            result = subprocess.run([tailscale_path, 'status'], ...)
            
            if result.returncode == 0:
                status = 'healthy'
            else:
                status = 'warning'
        else:
            # Not found
            status = 'not installed'
```

## Benefits of Multi-Method Detection

1. **Reliability**: Multiple fallback methods ensure detection works
2. **Flexibility**: Handles various installation scenarios
3. **Performance**: Fast PATH check tried first
4. **Compatibility**: Works with MSI, portable, and custom installs
5. **Maintainability**: Clear, logical flow with proper error handling

## Error Handling

Each detection method has proper exception handling:

- **PATH Check**: Catches subprocess errors and timeouts
- **File System**: Uses `os.path.isfile()` to verify existence
- **Registry**: Handles `WindowsError`, `FileNotFoundError`, and `ImportError`
- **Overall**: Returns `None` if all methods fail (graceful degradation)

## Future Enhancements

Possible future improvements:

1. Cache detection results for performance
2. Add support for detecting Tailscale service status
3. Detect Tailscale version information
4. Add support for other VPN solutions

## Testing

The detection logic is tested through:

1. **Structure Tests**: Verify function exists and has correct elements
2. **Simulation Tests**: Test detection logic order and error handling
3. **Integration Tests**: Verify all functions use enhanced detection
4. **Syntax Tests**: Ensure valid Python code

All tests pass successfully.
