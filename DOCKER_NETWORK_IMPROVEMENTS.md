# Docker Network Configuration Improvements

## Overview
This update ensures that Docker containers are always started or connected to the correct network (bridge network by default), preventing restore failures due to network configuration issues.

## Problem Statement
Previously, containers could fail during restore with the error "not attached to default bridge network". This happened because:
1. New containers were started without explicitly specifying the network
2. Existing containers were not checked for proper network connectivity
3. No clear error messages guided users when network issues occurred

## Solution Implemented

### 1. Added Network Helper Functions
Two new utility functions were added to check and manage container networks:

#### `check_container_network(container_name, network_name="bridge")`
- Checks if a container is connected to a specific network
- Uses Docker inspect to query the container's network settings
- Returns True if connected, False otherwise
- Includes error handling for edge cases

#### `attach_container_to_network(container_name, network_name="bridge")`
- Attaches a container to a specified network
- First checks if already connected (to avoid redundant operations)
- Uses `docker network connect` command
- Provides detailed logging of success/failure
- Returns True on success, False on failure

### 2. Updated Container Creation Functions

#### `ensure_nextcloud_container()` Updates
**For New Containers:**
- Added `--network bridge` parameter to both docker run commands
- First attempt: `docker run -d --name {name} --network bridge --link {db}:db -p {port}:80 {image}`
- Fallback (if linking fails): `docker run -d --name {name} --network bridge -p {port}:80 {image}`
- Enhanced error messages that specifically mention "not attached to default bridge network"

**For Existing Containers:**
- Added automatic network connectivity check
- If not connected to bridge network, automatically attempts to attach
- Shows progress updates: "Attaching {container} to bridge network..."
- Provides detailed error message with manual fix instructions if attachment fails
- Error message includes exact Docker command user can run manually

#### `ensure_db_container()` Updates
**For New Containers:**
- Added `--network bridge` parameter: `docker run -d --name {name} --network bridge -e POSTGRES_DB=...`
- Enhanced error messages mentioning network issues

**For Existing Containers:**
- Added automatic network connectivity check
- Automatically attaches to bridge network if not connected
- Same error handling and user guidance as Nextcloud container

#### `launch_nextcloud_instance()` Updates
- Added `--network bridge` parameter for standalone Nextcloud launches
- Enhanced error message with network troubleshooting tips

### 3. Enhanced Error Messages
All error messages now include:
- Clear description of the problem
- Common causes (container/port already in use, network issues)
- Specific mention of "not attached to default bridge network" issue
- Manual fix instructions with exact Docker commands
- Guidance to check Docker status

Example error message:
```
Failed to attach container 'nextcloud-app' to bridge network.

This is required for the restore process to work correctly.
Please ensure the container is running and you have permission to modify it.

You can manually attach it using:
  docker network connect bridge nextcloud-app

Or restart the container with proper network settings.
```

## Technical Details

### Network Detection
The `check_container_network` function uses Docker inspect with a Go template format string:
```bash
docker inspect {container} --format '{{range $net, $config := .NetworkSettings.Networks}}{{$net}} {{end}}'
```
This returns a space-separated list of network names the container is connected to.

### Network Attachment
The `attach_container_to_network` function uses:
```bash
docker network connect bridge {container}
```
This command is safe to run and adds the container to the bridge network without disrupting existing connections.

### Progress Updates
The restore process now shows additional progress steps:
- 32%: "Attaching {container} to bridge network..." (for existing Nextcloud containers)
- 33%: "Container {container} attached to bridge network"
- 42%: "Attaching {db} to bridge network..." (for existing DB containers)
- 43%: "Database container {db} attached to bridge network"

## Benefits

1. **Reliability**: Containers always have proper network configuration
2. **Automatic Recovery**: Existing containers are automatically fixed if misconfigured
3. **User Guidance**: Clear error messages help users resolve issues independently
4. **Prevention**: Explicitly setting network prevents accidental misconfiguration
5. **Backward Compatible**: Changes don't affect existing functionality for properly configured systems

## Testing

### Manual Testing Scenarios
1. ✅ Start new containers with network specification
2. ✅ Detect existing container network status
3. ✅ Attach existing container to network
4. ✅ Handle network attachment failures gracefully
5. ✅ Display clear error messages
6. ✅ Verify Python syntax

### Test Results
- All network helper functions tested successfully
- Docker network detection working correctly
- Container attachment working as expected
- Error handling verified
- Syntax validation passed

## Code Changes Summary

### Files Modified
- `nextcloud_restore_and_backup-v9.py`

### Lines Added/Modified
- Added 2 new helper functions (~40 lines)
- Updated `ensure_nextcloud_container()` (~30 lines modified/added)
- Updated `ensure_db_container()` (~30 lines modified/added)
- Updated `launch_nextcloud_instance()` (~10 lines modified)
- Enhanced error messages throughout

### Total Impact
- ~110 lines of code added/modified
- 4 functions updated
- 2 new utility functions added
- 0 breaking changes

## Usage

Users will now experience:
1. Automatic network configuration when starting new containers
2. Automatic network fixing for existing containers
3. Clear error messages if network issues can't be automatically resolved
4. Specific guidance on how to manually fix network issues

No changes are required to user workflows or configuration files.

## Future Enhancements

Potential future improvements:
1. Support for custom network names (not just "bridge")
2. Add network selection in GUI
3. Validate network exists before attempting to use it
4. Support for multiple networks simultaneously
5. Network isolation options for security

## References

- Docker network documentation: https://docs.docker.com/network/
- Docker bridge network: https://docs.docker.com/network/bridge/
- Issue reference: "not attached to default bridge network" restore failure
