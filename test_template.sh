#!/bin/bash

# Test script for apply_template.sh
# This script runs the template application with a predefined app name

# Set the test app name
TEST_APP_NAME="test_flutter_app_$(date +%Y%m%d_%H%M%S)"

echo "Running template test with app name: $TEST_APP_NAME"
echo "----------------------------------------"

# Run the template script with the test app name
echo "$TEST_APP_NAME" | bash scripts/apply_template.sh

# Check if the script completed successfully
if [ $? -eq 0 ]; then
    echo "✅ Template test completed successfully"
    echo "Test app created at: $(dirname "$(pwd)")/$TEST_APP_NAME"
else
    echo "❌ Template test failed"
    exit 1
fi 