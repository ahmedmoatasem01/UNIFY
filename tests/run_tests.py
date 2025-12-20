"""
Test Runner Script
Runs all unit and integration tests and generates a pass/fail summary report
"""
import unittest
import sys
import os
from datetime import datetime
import io
from contextlib import redirect_stdout, redirect_stderr

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'src'))


def run_tests():
    """Run all tests and generate a report"""
    # Discover all test files
    test_dir = os.path.dirname(os.path.abspath(__file__))
    loader = unittest.TestLoader()
    suite = loader.discover(test_dir, pattern='test_*.py')
    
    # Run tests and capture output
    stream = io.StringIO()
    runner = unittest.TextTestRunner(stream=stream, verbosity=2)
    result = runner.run(suite)
    
    # Generate report
    report_lines = []
    report_lines.append("=" * 80)
    report_lines.append("TEST REPORT - UNIFY PROJECT")
    report_lines.append("=" * 80)
    report_lines.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    report_lines.append("")
    
    # Test Summary
    report_lines.append("TEST SUMMARY")
    report_lines.append("-" * 80)
    total_tests = result.testsRun
    failures = len(result.failures)
    errors = len(result.errors)
    skipped = len(result.skipped)
    passed = total_tests - failures - errors - skipped
    
    report_lines.append(f"Total Tests: {total_tests}")
    report_lines.append(f"Passed: {passed} [PASS]")
    report_lines.append(f"Failed: {failures} [FAIL]")
    report_lines.append(f"Errors: {errors} [ERROR]")
    report_lines.append(f"Skipped: {skipped} [SKIP]")
    report_lines.append("")
    
    # Pass/Fail Status
    report_lines.append("OVERALL STATUS")
    report_lines.append("-" * 80)
    if failures == 0 and errors == 0:
        report_lines.append("STATUS: PASS")
        report_lines.append("All tests passed successfully!")
    else:
        report_lines.append("STATUS: FAIL")
        report_lines.append(f"Tests failed: {failures} failures, {errors} errors")
    report_lines.append("")
    
    # Test Details
    report_lines.append("TEST DETAILS")
    report_lines.append("-" * 80)
    
    # Add failures
    if result.failures:
        report_lines.append("FAILURES:")
        for test, traceback in result.failures:
            report_lines.append(f"  [FAIL] {test}")
            # Add first few lines of traceback
            tb_lines = traceback.split('\n')[:3]
            for line in tb_lines:
                if line.strip():
                    report_lines.append(f"    {line.strip()}")
        report_lines.append("")
    
    # Add errors
    if result.errors:
        report_lines.append("ERRORS:")
        for test, traceback in result.errors:
            report_lines.append(f"  [ERROR] {test}")
            # Add first few lines of traceback
            tb_lines = traceback.split('\n')[:3]
            for line in tb_lines:
                if line.strip():
                    report_lines.append(f"    {line.strip()}")
        report_lines.append("")
    
    # List passed tests
    if passed > 0:
        report_lines.append("PASSED TESTS:")
        # Extract test names from successful tests
        all_tests = []
        try:
            for test_group in suite:
                if test_group:
                    for test_case in test_group:
                        if test_case:
                            for test in test_case:
                                test_str = str(test)
                                # Check if this test didn't fail or error
                                if not any(test_str in str(f[0]) for f in result.failures) and \
                                   not any(test_str in str(e[0]) for e in result.errors):
                                    all_tests.append(test_str)
        except (TypeError, AttributeError):
            # If we can't iterate through tests, just show the count
            pass
        
        if all_tests:
            for test in all_tests[:20]:  # Limit to first 20 for readability
                report_lines.append(f"  [PASS] {test}")
            if len(all_tests) > 20:
                report_lines.append(f"  ... and {len(all_tests) - 20} more")
        else:
            report_lines.append(f"  [PASS] {passed} test(s) passed")
        report_lines.append("")
    
    report_lines.append("=" * 80)
    report_lines.append("END OF REPORT")
    report_lines.append("=" * 80)
    
    # Print report
    report = '\n'.join(report_lines)
    print(report)
    
    # Save report to file
    report_file = os.path.join(test_dir, 'test_report.txt')
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write(report)
    
    print(f"\nDetailed test output saved to: {report_file}")
    print(f"\nFull test output:\n{stream.getvalue()}")
    
    # Return exit code: 0 if all passed, 1 if any failed
    return 0 if (failures == 0 and errors == 0) else 1


if __name__ == '__main__':
    exit_code = run_tests()
    sys.exit(exit_code)

