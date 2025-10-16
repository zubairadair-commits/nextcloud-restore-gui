# Testing Checklist for Tailscale Feature

## Quick Verification

Run the automated test first:
```bash
python3 test_tailscale_feature.py
```

Expected output: ✓ All tests passed!

## Manual Testing Checklist

### Part 1: UI Changes

#### Header Controls
- [ ] Application starts without errors
- [ ] Header shows centered title
- [ ] Top-right corner has theme icon (☀️ or 🌙)
- [ ] Top-right corner has menu icon (☰)
- [ ] Icons are appropriately sized (not too small, not too large)
- [ ] Icons are clearly visible in both themes

#### Theme Toggle
- [ ] Click theme icon → Theme switches instantly
- [ ] Icon changes: 🌙 → ☀️ or ☀️ → 🌙
- [ ] All UI elements update to new theme
- [ ] Header updates to new theme
- [ ] Button colors update appropriately
- [ ] Text remains readable in both themes

#### Landing Page
- [ ] Landing page shows 4 main buttons
- [ ] Theme toggle button NOT on landing page
- [ ] All buttons visible and properly spaced
- [ ] Schedule status shows (if configured)
- [ ] Landing page looks cleaner than before

### Part 2: Dropdown Menu

#### Menu Access
- [ ] Click ☰ button → Menu appears
- [ ] Menu positioned below ☰ button
- [ ] Menu aligned to the right
- [ ] Menu has title "Advanced Features"
- [ ] Menu has separator line
- [ ] Menu blocks interaction with main window

#### Menu Content
- [ ] Menu shows "🌐 Remote Access (Tailscale)" option
- [ ] Menu has "Close" button at bottom
- [ ] Menu follows current theme colors
- [ ] Hover over option → Background changes
- [ ] Click option → Menu closes, wizard opens
- [ ] Click "Close" → Menu closes, returns to landing

### Part 3: Tailscale Wizard - Initial State

#### Without Tailscale Installed
- [ ] Wizard opens with title "🌐 Remote Access Setup"
- [ ] Subtitle explains Tailscale
- [ ] Info box explains what Tailscale is
- [ ] "Return to Main Menu" button visible
- [ ] Status shows "✗ Not Installed"
- [ ] "📦 Install Tailscale" button visible
- [ ] Note about admin privileges shown

#### Installation Guide
- [ ] Click "Install Tailscale" → Dialog opens
- [ ] Dialog shows installation instructions
- [ ] Instructions match your platform (Windows/Linux/macOS)
- [ ] "Open Download Page" button present
- [ ] "Check Installation" button present
- [ ] "Cancel" button present
- [ ] Click "Open Download Page" → Browser opens Tailscale site
- [ ] Click "Check Installation" → Returns to wizard

### Part 4: Tailscale Wizard - With Tailscale

#### With Tailscale Not Running
- [ ] Status shows "✓ Installed"
- [ ] Status shows "✗ Not Running"
- [ ] "▶️ Start Tailscale" button visible
- [ ] Click "Start Tailscale" → Attempts to start service
- [ ] Appropriate message shown (success or auth needed)

#### With Tailscale Running
- [ ] Status shows "✓ Installed"
- [ ] Status shows "✓ Running"
- [ ] "⚙️ Configure Remote Access" button visible
- [ ] Network info box shows current IP/hostname
- [ ] All info displayed correctly

### Part 5: Configuration Wizard

#### Initial Display
- [ ] Configuration wizard opens
- [ ] Title shows "⚙️ Configure Remote Access"
- [ ] "← Back to Tailscale Setup" link visible
- [ ] Network info box displays:
  - [ ] Tailscale IP (e.g., 100.101.102.103)
  - [ ] MagicDNS name (if available)
- [ ] Explanation text about using these addresses

#### Custom Domain Input
- [ ] "Custom Domains (Optional)" section visible
- [ ] Input field present and editable
- [ ] Placeholder or example text shown
- [ ] Can type custom domain
- [ ] Domain input follows theme

#### Configuration Preview
- [ ] "What will be configured" info box visible
- [ ] Shows Tailscale IP (if available)
- [ ] Shows MagicDNS name (if available)
- [ ] Shows custom domain (if entered)
- [ ] "✓ Apply Configuration to Nextcloud" button visible

### Part 6: Applying Configuration

#### Prerequisites
- [ ] Nextcloud container is running (`docker ps`)
- [ ] Can access Nextcloud config.php

#### Apply Process
- [ ] Enter custom domain (optional)
- [ ] Click "Apply Configuration"
- [ ] Status label shows "Updating Nextcloud configuration..."
- [ ] Success dialog appears with:
  - [ ] List of added domains
  - [ ] Message about accessing Nextcloud
- [ ] Returns to main menu after success

#### Verification
- [ ] Check trusted_domains in config.php:
  ```bash
  docker exec nextcloud-app cat /var/www/html/config/config.php | grep -A 10 trusted_domains
  ```
- [ ] Verify Tailscale IP is listed
- [ ] Verify MagicDNS name is listed (if was available)
- [ ] Verify custom domain is listed (if was entered)
- [ ] Existing domains still present

### Part 7: Error Handling

#### No Nextcloud Container
- [ ] Stop Nextcloud: `docker stop nextcloud-app`
- [ ] Try to apply configuration
- [ ] Error message shows: "No running Nextcloud container found"
- [ ] Returns to wizard (doesn't crash)

#### No Tailscale Info
- [ ] Stop Tailscale (if possible)
- [ ] Open configuration wizard
- [ ] Shows "Could not retrieve Tailscale information"
- [ ] Still allows continuing
- [ ] Doesn't crash

#### Invalid Input
- [ ] Enter invalid domain (e.g., spaces, special chars)
- [ ] Behavior is reasonable (accepts or rejects appropriately)

### Part 8: Theme Consistency

#### Light Theme
- [ ] All wizard pages use light theme colors
- [ ] Info boxes use light blue background
- [ ] Buttons use appropriate light colors
- [ ] Text is black/dark gray
- [ ] All text readable

#### Dark Theme
- [ ] Switch to dark theme
- [ ] Open Tailscale wizard
- [ ] All wizard pages use dark theme colors
- [ ] Info boxes use dark blue background
- [ ] Buttons use appropriate dark colors
- [ ] Text is light gray/white
- [ ] All text readable

### Part 9: Navigation

#### Wizard Navigation
- [ ] From landing → Click ☰ → Remote Access → Wizard opens
- [ ] From wizard → Click "Return to Main Menu" → Returns to landing
- [ ] From wizard → Click "Configure" → Config wizard opens
- [ ] From config → Click "Back to Tailscale Setup" → Returns to main wizard
- [ ] From config → Click "Apply" → Success → Returns to landing
- [ ] All navigation smooth, no crashes

#### State Preservation
- [ ] Enter custom domain in config wizard
- [ ] Click back button
- [ ] Return to config wizard
- [ ] Custom domain still there (or acceptably cleared)

### Part 10: Real-World Usage

#### Complete Setup Flow
- [ ] Start with Tailscale not installed
- [ ] Follow wizard to install Tailscale
- [ ] Authenticate with Tailscale
- [ ] Configure remote access
- [ ] Add custom domain (optional)
- [ ] Apply configuration
- [ ] Verify Nextcloud accessible via Tailscale IP
- [ ] Verify Nextcloud accessible via MagicDNS (if available)
- [ ] Verify Nextcloud accessible via custom domain (if added)

#### Remote Access Test
- [ ] Connect to Tailscale on another device (phone/laptop)
- [ ] Open browser on that device
- [ ] Navigate to `http://<tailscale-ip>:<port>`
  - Example: `http://100.101.102.103:8080`
- [ ] Nextcloud loads successfully
- [ ] Can log in and use Nextcloud
- [ ] No "untrusted domain" errors

## Expected Results

### ✅ Success Criteria

All of the following should be true:
- ✅ Automated tests pass
- ✅ UI changes visible and functional
- ✅ Theme toggle works in header
- ✅ Dropdown menu accessible and functional
- ✅ Tailscale wizard guides through setup
- ✅ Configuration applies successfully
- ✅ Nextcloud accessible via Tailscale
- ✅ Both themes work correctly
- ✅ Navigation works smoothly
- ✅ No crashes or errors

### ⚠️ Known Limitations

These are expected and acceptable:
- Tailscale must be installed manually (wizard guides, but doesn't auto-install)
- Platform differences (Windows/Linux/macOS have different start methods)
- MagicDNS may not be available (depends on Tailscale plan/config)
- Container must be running (wizard checks but doesn't start)
- Some operations require sudo/admin privileges

### ❌ Issues to Report

Report these if encountered:
- Application crashes
- Wizard doesn't open
- Menu doesn't appear
- Theme doesn't switch
- Configuration fails silently
- Trusted domains not updated
- UI elements invisible
- Navigation broken

## Troubleshooting

### Test Fails: "Tailscale installation check"
**Solution**: Install Tailscale from https://tailscale.com/download

### Test Fails: "No running Nextcloud container"
**Solution**: Start Nextcloud: `docker start nextcloud-app`

### Theme Toggle Doesn't Work
**Solution**: 
1. Check console for errors
2. Verify theme button exists: Look for ☀️ or 🌙 in header
3. Try clicking it multiple times

### Menu Doesn't Open
**Solution**:
1. Check console for errors
2. Verify menu button exists: Look for ☰ in header
3. Try resizing window
4. Restart application

### Configuration Fails
**Solution**:
1. Verify Nextcloud is running: `docker ps | grep nextcloud`
2. Check container name: `docker ps --format '{{.Names}}'`
3. Test manual access: `docker exec nextcloud-app cat /var/www/html/config/config.php`
4. Check logs: `docker logs nextcloud-app`

### Can't Access Nextcloud via Tailscale
**Solution**:
1. Verify Tailscale running: `tailscale status`
2. Verify IP correct: `tailscale ip`
3. Check Nextcloud port: Usually 8080 or 80
4. Try: `http://<tailscale-ip>:<port>`
5. Check trusted_domains was updated
6. Restart Nextcloud: `docker restart nextcloud-app`

## Performance Check

### Response Times (Expected)
- Theme toggle: < 0.5s
- Menu open: < 0.3s
- Wizard open: < 1s
- Install check: < 2s
- Status check: < 2s
- Get network info: < 2s
- Apply config: < 5s

### Resource Usage
- Memory: < 100 MB increase
- CPU: Minimal (< 5% during operations)
- Network: Only Tailscale commands (minimal)

## Report Template

If you find issues, report using this template:

```
### Issue Description
[Brief description of the problem]

### Steps to Reproduce
1. 
2. 
3. 

### Expected Behavior
[What should happen]

### Actual Behavior
[What actually happened]

### Environment
- OS: [Windows/Linux/macOS]
- Python version: [output of `python3 --version`]
- Tailscale installed: [Yes/No]
- Tailscale version: [output of `tailscale version`]
- Docker version: [output of `docker --version`]
- Nextcloud running: [Yes/No]

### Screenshots
[If applicable]

### Console Output
[Any error messages from terminal]
```

## Success!

If all tests pass, congratulations! 🎉

You now have:
- ✅ Professional header with controls
- ✅ Theme toggle in convenient location
- ✅ Extensible dropdown menu
- ✅ Full Tailscale setup wizard
- ✅ Secure remote access to Nextcloud

Enjoy your enhanced Nextcloud management tool!

---

**Pro Tip**: Bookmark the Tailscale admin console at https://login.tailscale.com/admin/machines to manage your devices easily.
