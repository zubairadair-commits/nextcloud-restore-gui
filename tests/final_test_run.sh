#!/bin/bash
echo "╔════════════════════════════════════════════════════════════════╗"
echo "║  FINAL COMPREHENSIVE TEST - Status Color & Mouse Scrolling    ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""

total_tests=0
passed_tests=0

# Test 1: Status color and scrolling
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "TEST 1: Status Text Color and Scrolling Implementation"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
if python3 test_status_color_scrolling.py > /tmp/test1.log 2>&1; then
    echo "✅ PASSED - test_status_color_scrolling.py (14/14 checks)"
    passed_tests=$((passed_tests + 1))
else
    echo "❌ FAILED - test_status_color_scrolling.py"
    cat /tmp/test1.log
fi
total_tests=$((total_tests + 1))
echo ""

# Test 2: Main app scrolling
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "TEST 2: Main Application Implementation"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
if python3 test_main_app_scrolling.py > /tmp/test2.log 2>&1; then
    echo "✅ PASSED - test_main_app_scrolling.py (13/13 checks)"
    passed_tests=$((passed_tests + 1))
else
    echo "❌ FAILED - test_main_app_scrolling.py"
    cat /tmp/test2.log
fi
total_tests=$((total_tests + 1))
echo ""

# Test 3: Backward compatibility
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "TEST 3: Backward Compatibility"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
if python3 test_test_run_button.py > /tmp/test3.log 2>&1; then
    echo "✅ PASSED - test_test_run_button.py (7/7 tests)"
    passed_tests=$((passed_tests + 1))
else
    echo "❌ FAILED - test_test_run_button.py"
    cat /tmp/test3.log
fi
total_tests=$((total_tests + 1))
echo ""

# Test 4: Syntax validation
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "TEST 4: Python Syntax Validation"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
if python3 -m py_compile ../src/nextcloud_restore_and_backup-v9.py 2>/dev/null; then
    echo "✅ PASSED - Python syntax validation"
    passed_tests=$((passed_tests + 1))
else
    echo "❌ FAILED - Syntax errors found"
fi
total_tests=$((total_tests + 1))
echo ""

# Summary
echo "╔════════════════════════════════════════════════════════════════╗"
echo "║                       TEST SUMMARY                             ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""
echo "Total Tests:  $total_tests"
echo "Passed:       $passed_tests"
echo "Failed:       $((total_tests - passed_tests))"
echo ""

if [ $passed_tests -eq $total_tests ]; then
    echo "╔════════════════════════════════════════════════════════════════╗"
    echo "║         ✅ ALL TESTS PASSED - READY FOR PRODUCTION ✅          ║"
    echo "╚════════════════════════════════════════════════════════════════╝"
    exit 0
else
    echo "╔════════════════════════════════════════════════════════════════╗"
    echo "║              ❌ SOME TESTS FAILED - REVIEW NEEDED ❌            ║"
    echo "╚════════════════════════════════════════════════════════════════╝"
    exit 1
fi
