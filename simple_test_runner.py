#!/usr/bin/env python3
"""
Simple test runner for cdlreq that doesn't depend on pytest
"""

import sys
import traceback
from pathlib import Path

# Add current directory to path
sys.path.insert(0, str(Path(__file__).parent))

def run_test_method(test_class, method_name):
    """Run a single test method"""
    try:
        instance = test_class()
        method = getattr(instance, method_name)
        method()
        print(f"✅ {test_class.__name__}.{method_name}")
        return True
    except Exception as e:
        print(f"❌ {test_class.__name__}.{method_name}: {e}")
        if "--verbose" in sys.argv:
            traceback.print_exc()
        return False

def run_test_class(test_class):
    """Run all test methods in a class"""
    methods = [name for name in dir(test_class) if name.startswith('test_')]
    passed = 0
    total = len(methods)
    
    print(f"\nRunning {test_class.__name__} ({total} tests):")
    print("-" * 50)
    
    for method_name in methods:
        if run_test_method(test_class, method_name):
            passed += 1
    
    print(f"Result: {passed}/{total} passed")
    return passed, total

def main():
    """Main test runner"""
    total_passed = 0
    total_tests = 0
    
    print("=" * 60)
    print("Running cdlreq tests (simple runner)")
    print("=" * 60)
    
    # Import test classes
    try:
        from tests.core.test_models import TestRequirement, TestSpecification
        from tests.core.test_parser import TestRequirementParser, TestSpecificationParser
        from tests.core.test_validator import TestValidationResult, TestCrossReferenceValidator
        from tests.test_simple_integration import TestSimpleIntegration
        
        # Run core tests
        test_classes = [
            TestRequirement,
            TestSpecification, 
            TestRequirementParser,
            TestSpecificationParser,
            TestValidationResult,
            TestCrossReferenceValidator,
            TestSimpleIntegration,
        ]
        
        for test_class in test_classes:
            passed, total = run_test_class(test_class)
            total_passed += passed
            total_tests += total
            
    except ImportError as e:
        print(f"Could not import tests: {e}")
        return 1
    
    print("\n" + "=" * 60)
    print(f"FINAL RESULT: {total_passed}/{total_tests} tests passed")
    print("=" * 60)
    
    if total_passed == total_tests:
        print("🎉 All tests passed!")
        return 0
    else:
        print(f"💥 {total_tests - total_passed} tests failed!")
        return 1

if __name__ == "__main__":
    sys.exit(main())