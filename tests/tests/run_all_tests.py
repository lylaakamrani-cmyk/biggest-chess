# © 2025 AmirAli Kamrani. All rights reserved.

# tests/run_all_tests.py
import unittest
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def run_all_tests():
    """Run all test cases"""
    # Import test modules
    from tests.test_board import TestBoard
    from tests.test_game import TestGame
    from tests.test_ai import TestAI
    from tests.test_database import TestDatabase
    
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add test cases
    suite.addTests(loader.loadTestsFromTestCase(TestBoard))
    suite.addTests(loader.loadTestsFromTestCase(TestGame))
    suite.addTests(loader.loadTestsFromTestCase(TestAI))
    suite.addTests(loader.loadTestsFromTestCase(TestDatabase))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Print summary
    print("\n" + "=" * 50)
    print("TEST SUMMARY")
    print("=" * 50)
    print(f"Ran {result.testsRun} tests")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    
    if result.wasSuccessful():
        print("✅ ALL TESTS PASSED!")
    else:
        print("❌ SOME TESTS FAILED!")
        for failure in result.failures:
            print(f"\n{failure[0]}: {failure[1]}")
            
    return result.wasSuccessful()

if __name__ == '__main__':
    success = run_all_tests()
    sys.exit(0 if success else 1)