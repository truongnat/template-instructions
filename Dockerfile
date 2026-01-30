# Use an official Python runtime as a parent image
FROM python:3.10-slim

# Set the working directory in the container
WORKDIR /app

# Install system dependencies
# git: for cloning repositories and git operations
# curl: for healthchecks
RUN apt-get update && apt-get install -y \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy configuration files
COPY pyproject.toml .
COPY README.md .
COPY LICENSE .

# Install dependencies from pyproject.toml
# We use a dummy setup to cache dependencies
RUN pip install --no-cache-dir .

# Copy the rest of the application code
COPY . .

# Re-install package to include the code mappings
RUN pip install --no-cache-dir -e .

# Define environment variable
ENV PYTHONUNBUFFERED=1
ENV PROJECT_ROOT=/app

# Create a user to avoid running as root (Security Best Practice)
RUN useradd -m agentic
USER agentic

# Run asdlc.py when the container launches
CMD ["python", "asdlc.py", "brain", "health"]
