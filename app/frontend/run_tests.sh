#!/bin/bash

# Test runner script for frontend tests
echo "Running frontend connection tests..."

# Run the tests
python -m pytest test_front.py -v --tb=short

echo "Frontend tests completed!"
