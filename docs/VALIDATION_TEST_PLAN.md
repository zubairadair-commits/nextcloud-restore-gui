# Validation Test Plan - Page Alignment Fix

## Overview
This document outlines the testing procedures to validate that the page alignment fix works correctly across all wizard pages and window sizes.

## Test Environment Setup

### Prerequisites
- Python 3.x installed
- Tkinter library available (python3-tk on Linux)
- Test backup files (encrypted and unencrypted)
- Docker installed (for full restore testing)

### Running the Application
```bash
python3 nextcloud_restore_and_backup-v9.py
```

## Test Cases

### Test 1: Visual Centering - Page 1
**Objective**: Verify all elements on Page 1 are properly centered

**Steps**:
1. Launch the application
2. Click "Start Restore"
3. Navigate to Page 1 of wizard

**Expected Results**:
- [ ] "Step 1: Select Backup Archive" header is centered
- [ ] Backup file entry field is centered
- [ ] Browse button is centered
- [ ] "Step 2: Decryption Password" header is centered
- [ ] Password entry field is centered
- [ ] Entry fields have consistent, appropriate width
- [ ] No elements appear left-aligned

**Screenshot**: Take a screenshot of Page 1 for documentation

---

### Test 2: Visual Centering - Page 2
**Objective**: Verify all elements on Page 2 are properly centered

**Steps**:
1. From Page 1, click "Next →" to navigate to Page 2

**Expected Results**:
- [ ] "Step 3: Database Configuration" header is centered
- [ ] Info box about auto-detection is centered
- [ ] Database credential form (labels + entry fields) is centered as a unit
- [ ] Database Name, User, and Password fields are aligned
- [ ] Hint text appears to the right of entry fields
- [ ] "Step 4: Nextcloud Admin Credentials" header is centered
- [ ] Admin credential form is centered as a unit
- [ ] No elements appear left-aligned

**Screenshot**: Take a screenshot of Page 2 for documentation

---

### Test 3: Visual Centering - Page 3
**Objective**: Verify all elements on Page 3 are properly centered

**Steps**:
1. From Page 2, click "Next →" to navigate to Page 3

**Expected Results**:
- [ ] "Step 5: Container Configuration" header is centered
- [ ] Container configuration form is centered as a unit
- [ ] Container Name and Port fields are aligned
- [ ] Checkbox "Use existing Nextcloud container" is centered
- [ ] Info box about restore process is centered
- [ ] All info bullet points are centered
- [ ] No elements appear left-aligned

**Screenshot**: Take a screenshot of Page 3 for documentation

---

### Test 4: Responsive Layout - Minimum Window Size
**Objective**: Verify centering is maintained at minimum window size

**Steps**:
1. Resize window to minimum practical size (approximately 700x600)
2. Navigate through all 3 wizard pages
3. Observe element positioning

**Expected Results**:
- [ ] All elements remain centered at minimum size
- [ ] No horizontal scrollbar appears
- [ ] Forms remain readable and usable
- [ ] Vertical scrollbar appears if content exceeds viewport

**Screenshot**: Take screenshots at minimum size for each page

---

### Test 5: Responsive Layout - Maximum Window Size
**Objective**: Verify centering is maintained at maximum window size

**Steps**:
1. Maximize or resize window to large size (e.g., 1920x1080)
2. Navigate through all 3 wizard pages
3. Observe element positioning

**Expected Results**:
- [ ] All elements remain centered at maximum size
- [ ] Forms don't stretch unnaturally wide
- [ ] Content appears as a cohesive, centered block
- [ ] Appropriate whitespace on left and right sides

**Screenshot**: Take screenshots at maximum size for each page

---

### Test 6: SQLite Database Detection
**Objective**: Verify UI updates correctly when SQLite is detected

**Steps**:
1. Navigate to Page 2
2. Use a backup with SQLite database
3. Observe database credential section

**Expected Results**:
- [ ] Database credential form is hidden
- [ ] SQLite message box is displayed
- [ ] Message box is centered
- [ ] Text within message box is centered
- [ ] Navigation still works correctly

**Screenshot**: Take a screenshot of Page 2 with SQLite detection

---

### Test 7: PostgreSQL/MySQL Database Detection
**Objective**: Verify UI updates correctly when PostgreSQL/MySQL is detected

**Steps**:
1. Navigate to Page 2
2. Use a backup with PostgreSQL or MySQL database
3. Observe database credential section

**Expected Results**:
- [ ] Database credential form is visible
- [ ] Form is centered
- [ ] Warning labels are centered
- [ ] All fields are editable
- [ ] Fields are pre-populated from detected config
- [ ] Navigation still works correctly

**Screenshot**: Take a screenshot of Page 2 with PostgreSQL/MySQL detection

---

### Test 8: Navigation Between Pages
**Objective**: Verify centering is maintained during navigation

**Steps**:
1. Navigate forward through all pages (1 → 2 → 3)
2. Navigate backward through all pages (3 → 2 → 1)
3. Observe element positioning after each navigation

**Expected Results**:
- [ ] Elements remain centered after each navigation
- [ ] No layout shifts or jumps occur
- [ ] Previously entered data is preserved
- [ ] Scrollbar position resets appropriately

---

### Test 9: Background Threading - Encrypted Backup
**Objective**: Verify background decryption still works correctly

**Steps**:
1. Select an encrypted backup (.gpg file) on Page 1
2. Enter decryption password
3. Click "Next →"
4. Observe progress/status messages

**Expected Results**:
- [ ] Decryption happens in background thread
- [ ] UI remains responsive during decryption
- [ ] Progress messages are displayed
- [ ] Database detection completes successfully
- [ ] Page 2 is displayed with detected data
- [ ] No freezing or blocking of UI

---

### Test 10: Full Restore Process
**Objective**: Verify complete restore functionality is preserved

**Steps**:
1. Complete all 3 wizard pages with valid data
2. Click "Start Restore" on Page 3
3. Monitor restore progress
4. Verify Nextcloud starts successfully

**Expected Results**:
- [ ] Restore process initiates correctly
- [ ] Progress bar and messages appear
- [ ] All restore steps complete successfully
- [ ] No errors related to UI layout
- [ ] Nextcloud container starts
- [ ] Final success screen appears

---

## Regression Testing

### Functionality Checklist
Verify the following existing features still work:
- [ ] Backup creation with encryption
- [ ] Backup creation without encryption
- [ ] Browse button for backup file selection
- [ ] Password entry for encrypted backups
- [ ] Database type auto-detection
- [ ] Config.php parsing from backup
- [ ] Form field validation
- [ ] Data persistence between pages
- [ ] "Return to Main Menu" button
- [ ] Progress tracking during restore
- [ ] Error handling and display

### No Regressions
- [ ] No new errors or warnings in console
- [ ] No Python exceptions during navigation
- [ ] No tkinter geometry manager conflicts
- [ ] All existing documentation remains valid

---

## Performance Testing

### Memory and CPU
- [ ] No memory leaks during navigation
- [ ] CPU usage normal during UI updates
- [ ] Background threads work efficiently

### Responsiveness
- [ ] UI remains responsive during:
  - File decryption
  - Database detection
  - Config parsing
  - Page navigation
  - Window resizing

---

## Documentation Updates

After testing, update the following if needed:
- [ ] README with new screenshots
- [ ] User guide with current UI layout
- [ ] Troubleshooting guide
- [ ] Known issues (if any new ones discovered)

---

## Sign-Off Criteria

The fix is considered validated when:
1. ✅ All visual centering tests pass (Tests 1-7)
2. ✅ Navigation and responsive layout tests pass (Tests 8, 4-5)
3. ✅ Background threading and functionality tests pass (Tests 9-10)
4. ✅ No regressions found in existing features
5. ✅ Screenshots documented showing before/after
6. ✅ Performance is acceptable

---

## Test Results Template

```markdown
### Test Execution Date: [DATE]
### Tester: [NAME]
### Environment: [OS, Python Version, Tkinter Version]

| Test # | Test Name | Status | Notes |
|--------|-----------|--------|-------|
| 1 | Visual Centering - Page 1 | ⬜ | |
| 2 | Visual Centering - Page 2 | ⬜ | |
| 3 | Visual Centering - Page 3 | ⬜ | |
| 4 | Responsive - Minimum Size | ⬜ | |
| 5 | Responsive - Maximum Size | ⬜ | |
| 6 | SQLite Detection | ⬜ | |
| 7 | PostgreSQL/MySQL Detection | ⬜ | |
| 8 | Navigation Between Pages | ⬜ | |
| 9 | Background Threading | ⬜ | |
| 10 | Full Restore Process | ⬜ | |

**Overall Result**: [PASS / FAIL / NEEDS REVIEW]
**Issues Found**: [List any issues]
**Screenshots**: [Link to screenshots folder]
```

---

## Automated Testing (Future Enhancement)

While manual testing is required for visual validation, consider adding:
- Unit tests for layout parameter validation
- Integration tests for wizard navigation
- Automated screenshot comparison tools
- UI accessibility testing
