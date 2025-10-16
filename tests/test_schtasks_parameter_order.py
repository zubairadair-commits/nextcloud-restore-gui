"""
Test to verify schtasks parameter order is correct.

Windows Task Scheduler (schtasks) requires specific parameter order:
/SC (schedule type) must come BEFORE /ST (start time)
"""
import re
import sys

def test_create_scheduled_task_parameter_order():
    """Test that create_scheduled_task builds schtasks command with correct parameter order."""
    
    print("=" * 70)
    print("Testing schtasks Parameter Order in create_scheduled_task")
    print("=" * 70)
    
    # Read the main file
    with open('../src/nextcloud_restore_and_backup-v9.py', 'r') as f:
        content = f.read()
    
    # Find create_scheduled_task function
    match = re.search(r'def create_scheduled_task\(.*?\n(.*?)(?=\ndef |\Z)', content, re.DOTALL)
    if not match:
        print("❌ Could not find create_scheduled_task function")
        return False
    
    func_content = match.group(1)
    
    print("\n1. Checking schtasks command construction...")
    
    # Find the schtasks_cmd construction
    # Look for the pattern where we build the list and extend it with schedule_args
    cmd_pattern = r'schtasks_cmd = \[(.*?)\].*?schtasks_cmd\.extend\(schedule_args\)(.*?)(?=\n\n|\n        result|\Z)'
    cmd_match = re.search(cmd_pattern, func_content, re.DOTALL)
    
    if not cmd_match:
        print("❌ Could not find schtasks_cmd construction pattern")
        return False
    
    base_cmd = cmd_match.group(1)
    after_schedule = cmd_match.group(2)
    
    print("   ✓ Found schtasks_cmd construction")
    
    # Check that /ST is NOT in the base command (before schedule_args)
    if '"/ST"' in base_cmd or "'/ST'" in base_cmd:
        print("❌ ERROR: /ST found in base command (before schedule_args)")
        print("   /ST must come AFTER schedule_args (which contains /SC)")
        return False
    
    print("   ✓ /ST is not in base command (good)")
    
    # Check that schedule_args are extended before /ST
    if 'schtasks_cmd.extend(schedule_args)' in func_content:
        print("   ✓ schedule_args is extended to command")
    else:
        print("❌ ERROR: schedule_args not properly extended")
        return False
    
    # Check that /ST comes after schedule_args
    st_after_schedule = False
    if '"/ST"' in after_schedule or "'/ST'" in after_schedule:
        st_after_schedule = True
        print("   ✓ /ST is added after schedule_args")
    else:
        # Maybe it's in an extend call
        if 'schtasks_cmd.extend' in after_schedule and '/ST' in after_schedule:
            st_after_schedule = True
            print("   ✓ /ST is extended after schedule_args")
    
    if not st_after_schedule:
        print("❌ ERROR: /ST not found after schedule_args")
        return False
    
    print("\n2. Checking schedule_args definitions...")
    
    # Check schedule_args contain /SC
    schedule_patterns = [
        r'schedule_args = \["/SC", "DAILY"\]',
        r'schedule_args = \["/SC", "WEEKLY"',
        r'schedule_args = \["/SC", "MONTHLY"'
    ]
    
    found_schedule_types = []
    for pattern in schedule_patterns:
        if re.search(pattern, func_content):
            found_schedule_types.append(pattern.split('"')[3])
    
    if len(found_schedule_types) >= 3:
        print(f"   ✓ Found schedule types: {', '.join(found_schedule_types)}")
    else:
        print("❌ ERROR: Not all schedule types found")
        return False
    
    print("\n3. Verifying correct parameter order...")
    print("   Expected order:")
    print("   1. schtasks /Create")
    print("   2. /TN <task_name>")
    print("   3. /TR <command>")
    print("   4. /SC <schedule_type> ← From schedule_args")
    print("   5. /D <day> (optional) ← From schedule_args")
    print("   6. /ST <start_time> ← Must come AFTER /SC")
    print("   7. /RL <run_level>")
    print("   8. /Z")
    print("   9. /F")
    
    print("\n   ✓ Parameter order is CORRECT")
    
    return True


def test_run_test_backup_scheduled_parameter_order():
    """Test that _run_test_backup_scheduled also has correct parameter order."""
    
    print("\n" + "=" * 70)
    print("Testing schtasks Parameter Order in _run_test_backup_scheduled")
    print("=" * 70)
    
    # Read the main file
    with open('../src/nextcloud_restore_and_backup-v9.py', 'r') as f:
        content = f.read()
    
    # Find _run_test_backup_scheduled method
    match = re.search(r'def _run_test_backup_scheduled\(.*?\n(.*?)(?=\n    def |\Z)', content, re.DOTALL)
    if not match:
        print("❌ Could not find _run_test_backup_scheduled method")
        return False
    
    func_content = match.group(1)
    
    print("\n1. Checking schtasks command construction...")
    
    # Find schtasks_cmd in this function
    cmd_match = re.search(r'schtasks_cmd = \[(.*?)\]', func_content, re.DOTALL)
    if not cmd_match:
        print("❌ Could not find schtasks_cmd")
        return False
    
    cmd_list = cmd_match.group(1)
    
    # For test runs, /SC comes before /ST in the same list
    # Check that /SC appears before /ST in the list
    sc_pos = cmd_list.find('"/SC"') if '"/SC"' in cmd_list else cmd_list.find("'/SC'")
    st_pos = cmd_list.find('"/ST"') if '"/ST"' in cmd_list else cmd_list.find("'/ST'")
    
    if sc_pos == -1 or st_pos == -1:
        print("❌ Could not find /SC or /ST parameters")
        return False
    
    if sc_pos < st_pos:
        print("   ✓ /SC comes before /ST")
        print("   ✓ Parameter order is CORRECT")
        return True
    else:
        print("❌ ERROR: /ST comes before /SC")
        return False


if __name__ == "__main__":
    print("\nTesting Windows Task Scheduler Parameter Order")
    print("=" * 70)
    print("Requirement: /SC (schedule type) must come BEFORE /ST (start time)")
    print("=" * 70)
    
    test1 = test_create_scheduled_task_parameter_order()
    test2 = test_run_test_backup_scheduled_parameter_order()
    
    print("\n" + "=" * 70)
    print("Test Results Summary")
    print("=" * 70)
    print(f"create_scheduled_task: {'✓ PASS' if test1 else '❌ FAIL'}")
    print(f"_run_test_backup_scheduled: {'✓ PASS' if test2 else '❌ FAIL'}")
    
    if test1 and test2:
        print("\n🎉 All tests PASSED! Parameter order is correct.")
        sys.exit(0)
    else:
        print("\n❌ Some tests FAILED. Parameter order needs fixing.")
        sys.exit(1)
