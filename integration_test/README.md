````markdown
# Integration Test for ats-linter

This integration test builds a Docker image that:
- Installs ats-linter from the local source  
- Provides a flexible container to test against any external test directory
- Can be used with the included sample test repo or your own test files

## Quick Start

Run the automated test script:

```sh
./integration_test/run_test.sh
```

This will build the Docker image and run both direct CLI and pre-commit integration tests.

## Manual Usage

### Option 1: Test with included sample test repo

From the project root:

```sh
# Build the Docker image
docker build -f integration_test/Dockerfile -t ats-linter-integration .

# Run against the included test repo
docker run --rm -v "$(pwd)/integration_test/test_repo:/test_repo" ats-linter-integration
```

### Option 2: Test with your own test directory

```sh
# Build the Docker image  
docker build -f integration_test/Dockerfile -t ats-linter-integration .

# Run against your own test directory
docker run --rm -v "/path/to/your/tests:/test_repo" ats-linter-integration
```

### Option 3: Test with pre-commit integration

```sh
# Run pre-commit integration test with the sample repo (simplified!)
docker run --rm -v "$(pwd)/integration_test/test_repo:/test_repo" ats-linter-integration test-precommit

# Or with your own test directory
docker run --rm -v "/path/to/your/tests:/test_repo" ats-linter-integration test-precommit
```

The container will run ats-linter against the mounted test directory and show the results with colorized output.

## Benefits of This Approach

- **Flexible**: Test against any test directory without rebuilding the container
- **Realistic**: Simulates real-world usage where the linter runs against external codebases
- **Reusable**: Same container can test multiple different test repositories
- **CI-friendly**: Easy to integrate into CI/CD pipelines with volume mounts

````
