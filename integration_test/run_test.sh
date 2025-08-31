#!/bin/bash

# Integration test runner for ats-linter
# This script provides easy ways to test the ats-linter Docker container

set -e

# Build the Docker image
echo "Building ats-linter integration test image..."
docker build -f integration_test/Dockerfile -t ats-linter-integration .

echo ""
echo "=== Testing with sample integration test repo ==="
docker run --rm -v $(pwd)/integration_test/test_repo:/test_repo ats-linter-integration

echo ""
echo "=== Testing pre-commit integration ==="
docker run --rm -v $(pwd)/integration_test/test_repo:/test_repo ats-linter-integration test-precommit

echo ""
echo "=== Integration test completed successfully! ==="
