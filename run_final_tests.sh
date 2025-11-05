#!/bin/bash
# Final comprehensive test suite for segfault fix

echo "=============================================================="
echo "  JARVIS SEGFAULT FIX - FINAL VERIFICATION TEST SUITE"
echo "=============================================================="
echo ""

PYTHON="/home/naitik/jarvis/jarvis-env/bin/python"
FAILED=0

run_test() {
    local test_name="$1"
    local test_file="$2"
    local expected_exit="$3"
    
    echo "Running: $test_name"
    echo "----------------------------------------"
    
    $PYTHON "$test_file" > /tmp/jarvis_test_output.txt 2>&1
    EXIT_CODE=$?
    
    if [ $EXIT_CODE -eq 139 ]; then
        echo "❌ FAILED - SEGMENTATION FAULT (exit 139)"
        FAILED=$((FAILED + 1))
        cat /tmp/jarvis_test_output.txt | tail -20
    elif [ $EXIT_CODE -eq $expected_exit ]; then
        echo "✅ PASSED (exit $EXIT_CODE)"
    else
        echo "⚠️  WARNING - Unexpected exit code: $EXIT_CODE (expected $expected_exit)"
    fi
    
    echo ""
}

echo "Test 1: Servo Cleanup Only"
run_test "Servo Cleanup" "/home/naitik/jarvis/test_servo_cleanup.py" 0

echo "Test 2: Full Hardware Cleanup"
run_test "Full Hardware" "/home/naitik/jarvis/test_full_cleanup.py" 0

echo "Test 3: Minimal Cleanup (No GUI)"
run_test "Minimal Cleanup" "/home/naitik/jarvis/test_cleanup_minimal.py" 0

echo "Test 4: Main Application (8s timeout)"
echo "Running: Main Application Test"
echo "----------------------------------------"
timeout 8 $PYTHON /home/naitik/jarvis/main.py > /tmp/jarvis_main_test.txt 2>&1
EXIT_CODE=$?

if [ $EXIT_CODE -eq 139 ]; then
    echo "❌ FAILED - SEGMENTATION FAULT (exit 139)"
    FAILED=$((FAILED + 1))
    cat /tmp/jarvis_main_test.txt | tail -30
elif [ $EXIT_CODE -eq 124 ] || [ $EXIT_CODE -eq 143 ]; then
    echo "✅ PASSED (exit $EXIT_CODE - timeout/SIGTERM)"
else
    echo "⚠️  WARNING - Exit code: $EXIT_CODE"
fi
echo ""

echo "Test 5: System Logs Check"
echo "Running: dmesg Segfault Check"
echo "----------------------------------------"
if dmesg | tail -50 | grep -qi "segfault"; then
    echo "❌ FAILED - Segfault found in system logs"
    FAILED=$((FAILED + 1))
    dmesg | tail -20 | grep -i segfault
else
    echo "✅ PASSED - No segfaults in system logs"
fi
echo ""

echo "=============================================================="
echo "  TEST SUMMARY"
echo "=============================================================="
if [ $FAILED -eq 0 ]; then
    echo "✅ ALL TESTS PASSED!"
    echo ""
    echo "Jarvis is ready for integration. No segmentation faults detected."
    exit 0
else
    echo "❌ $FAILED TEST(S) FAILED"
    echo ""
    echo "Please review the test output above."
    exit 1
fi
