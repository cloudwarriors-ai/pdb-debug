#!/usr/bin/env python3
"""Sample Python script for debugging demonstration."""

def fibonacci(n):
    """Calculate fibonacci number."""
    if n <= 0:
        return 0
    elif n == 1:
        return 1
    else:
        return fibonacci(n-1) + fibonacci(n-2)


def main():
    """Main function for demonstration."""
    print("Starting fibonacci calculation...")
    
    # Test variables for inspection
    numbers = [1, 2, 3, 4, 5]
    result_dict = {}
    
    for i in numbers:
        result = fibonacci(i)
        result_dict[i] = result
        print(f"fibonacci({i}) = {result}")
    
    print("Calculation complete!")
    print(f"Results: {result_dict}")
    
    # Some more operations for stepping through
    total = sum(result_dict.values())
    average = total / len(result_dict)
    
    print(f"Total: {total}")
    print(f"Average: {average}")


if __name__ == "__main__":
    main()