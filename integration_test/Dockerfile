# Integration test Dockerfile for ats-linter pre-commit hook

FROM python:3.12-slim
RUN apt-get update && apt-get install -y git && rm -rf /var/lib/apt/lists/*

# Configure git to trust mounted directories
RUN git config --global --add safe.directory /test_repo

WORKDIR /repo

# Install pre-commit
RUN pip install pre-commit colorama

# Copy the entire project root and install from there
COPY . /ats-linter-src
WORKDIR /ats-linter-src
ENV SETUPTOOLS_SCM_PRETEND_VERSION_FOR_ATS_LINTER=0.0.0
RUN pip install .[dev]

# Create helper script for pre-commit testing
RUN echo '#!/bin/bash\ncd /test_repo\ngit init\ngit add .\npre-commit run --all-files --hook-stage manual --config .pre-commit-config.yaml' > /usr/local/bin/test-precommit \
    && chmod +x /usr/local/bin/test-precommit

# Set up working directory for external test repos
WORKDIR /test_repo

# Default command: run ats-linter on mounted test directory
CMD ["ats-linter", "/test_repo", "--debug"]
