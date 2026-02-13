# Use an official Python runtime as a parent image
FROM python:3.11-slim

# Set the working directory in the container
WORKDIR /app

# Install system dependencies
# git is often needed for installing dependencies from git
# curl/wget for healthchecks
RUN apt-get update && apt-get install -y \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy the project files into the container
COPY . .

# Install the application and dependencies
# We install in editable mode (-e) so changes in the volume mount (if dev) are reflected
# But for a stable build, we just install .
RUN pip install --no-cache-dir .

# Expose ports
# Streamlit default port
EXPOSE 8501

# Define environment variables
ENV PYTHONUNBUFFERED=1
ENV MEMGRAPH_URI=bolt://memgraph:7687
ENV MEMGRAPH_USERNAME=memgraph
ENV MEMGRAPH_PASSWORD=memgraph

# Default command
# This keeps the container running so we can exec into it, or runs the dashboard if preferred
# "run all" might imply running the main entry point or dashboard.
# Let's default to a shell-ready state or the dashboard if that's the main UI.
# Given "CLI" focus, maybe just keep it alive?
# But typically docker containers run a service.
# Let's run the streamlit dashboard as default if it exists, otherwise bash.
# The project has `python asdlc.py dashboard` command.
CMD ["agentic-sdlc", "brain", "status"]
