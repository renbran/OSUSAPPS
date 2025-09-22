#!/usr/bin/env python3
"""
Test script for quantity_percentage module
This script demonstrates the percentage conversion functionality
"""

# This would be run inside the Odoo environment
def test_percentage_conversion():
    """Test the percentage conversion logic"""
    
    # Test cases for the conversion logic
    test_cases = [
        {"input": 5, "expected_storage": 0.05, "expected_display": 5},
        {"input": 10, "expected_storage": 0.10, "expected_display": 10},
        {"input": 0.5, "expected_storage": 0.005, "expected_display": 0.5},
        {"input": 15.75, "expected_storage": 0.1575, "expected_display": 15.75},
        {"input": 100, "expected_storage": 1.0, "expected_display": 100},
    ]
    
    print("Testing Percentage Conversion Logic")
    print("=" * 50)
    
    for i, case in enumerate(test_cases, 1):
        user_input = case["input"]
        expected_storage = case["expected_storage"]
        expected_display = case["expected_display"]
        
        # Simulate the conversion logic from our module
        # User input -> Storage (divide by 100)
        actual_storage = user_input / 100
        
        # Storage -> Display (multiply by 100)
        actual_display = actual_storage * 100
        
        print(f"Test {i}:")
        print(f"  User Input: {user_input}")
        print(f"  Expected Storage: {expected_storage}")
        print(f"  Actual Storage: {actual_storage}")
        print(f"  Expected Display: {expected_display}%")
        print(f"  Actual Display: {actual_display}%")
        print(f"  Storage Match: {'✓' if abs(actual_storage - expected_storage) < 0.0001 else '✗'}")
        print(f"  Display Match: {'✓' if abs(actual_display - expected_display) < 0.0001 else '✗'}")
        print()

if __name__ == "__main__":
    test_percentage_conversion()