#!/usr/bin/env python3
"""
Test suite runner for Smart Shift Planner Backend.

Usage:
    python run_tests.py                    # Run all tests
    python run_tests.py --unit             # Run only unit tests
    python run_tests.py --integration      # Run only integration tests
    python run_tests.py --ml               # Run only ML prediction tests
"""
import subprocess
import sys
from pathlib import Path


def run_command(cmd, description):
    """Run a command and return success status."""
    print(f"\n{'='*70}")
    print(f"🧪 {description}")
    print(f"{'='*70}")
    print(f"Command: {' '.join(cmd)}\n")
    
    result = subprocess.run(cmd, cwd=Path(__file__).parent)
    
    if result.returncode == 0:
        print(f"\n✅ {description} PASSED\n")
        return True
    else:
        print(f"\n❌ {description} FAILED\n")
        return False


def main():
    """Run test suite."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Run Smart Shift Planner tests")
    parser.add_argument(
        "--unit",
        action="store_true",
        help="Run only unit tests"
    )
    parser.add_argument(
        "--integration",
        action="store_true",
        help="Run only integration tests"
    )
    parser.add_argument(
        "--ml",
        action="store_true",
        help="Run only ML prediction tests"
    )
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Verbose output"
    )
    
    args = parser.parse_args()
    
    # Determine which tests to run
    run_all = not (args.unit or args.integration or args.ml)
    run_unit = args.unit or run_all
    run_integration = args.integration or run_all
    run_ml = args.ml or run_all
    
    results = {}
    
    if run_unit:
        cmd = ["python", "-m", "pytest", "tests/unit/test_basic.py"]
        if args.verbose:
            cmd.append("-vv")
        else:
            cmd.append("-v")
        results["unit"] = run_command(cmd, "Unit Tests")
    
    if run_integration:
        cmd = ["python", "-m", "pytest", "tests/integration/test_workers_shifts.py"]
        if args.verbose:
            cmd.append("-vv")
        else:
            cmd.append("-v")
        results["integration"] = run_command(cmd, "Integration Tests (Workers/Shifts)")
    
    if run_ml:
        cmd = ["python", "-m", "pytest", "tests/integration/test_predictions.py"]
        if args.verbose:
            cmd.append("-vv")
        else:
            cmd.append("-v")
        results["ml"] = run_command(cmd, "Integration Tests (ML Predictions)")
    
    # Summary
    print(f"\n{'='*70}")
    print("📊 TEST SUMMARY")
    print(f"{'='*70}")
    
    for test_type, passed in results.items():
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"{test_type.upper():15} {status}")
    
    all_passed = all(results.values())
    
    if all_passed:
        print(f"\n🎉 ALL TESTS PASSED!\n")
        return 0
    else:
        print(f"\n⚠️  SOME TESTS FAILED\n")
        return 1


if __name__ == "__main__":
    sys.exit(main())
