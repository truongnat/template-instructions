# Installation Guide

This guide provides detailed installation instructions for the Agentic SDLC Kit across different environments and platforms.

## 📋 System Requirements

### Minimum Requirements
- **Python**: 3.9 or higher
- **RAM**: 4GB minimum, 8GB recommended
- **Disk Space**: 2GB for installation, 5GB recommended for operation
- **OS**: Linux, macOS, or Windows 10+

### Recommended Requirements
- **Python**: 3.10 or 3.11
- **RAM**: 16GB for optimal performance
- **Disk Space**: 10GB+ for knowledge base and cache
- **OS**: Linux (Ubuntu 20.04+) or macOS (12+)

### Dependencies
- Git
- pip (Python package manager)
- Virtual environment tool (venv, virtualenv, or conda)
- Docker (optional, for containerized deployment)

## 🚀 Installation Methods

### Method 1: pip Installation (Recommended)

This is the simplest and recommended method for most users.

#### Step 1: Create a Virtual Environment

**Linux/macOS:**
```bash
python3 -m venv .venv
source .venv/bin/activate
```

**Windows:**
```cmd
python -m venv .venv
.venv\Scripts\activate
```

#### Step 2: Install the Package

```bash
# Install latest stable version
pip install agentic-sdlc

# Or install specific version
pip install agentic-sdlc==2.5.0

# Verify installation
asdlc --version
```

#### Step 3: Verify Installation

```bash
# Check that the CLI is available
asdlc --help

# Verify Python package
python -c "import agentic_sdlc; print(agentic_sdlc.__version__)"
```

### Method 2: Docker Installation

Docker provides a consistent environment across all platforms.

#### Step 1: Install Docker

Follow the official Docker installation guide for your platform:
- [Docker for Linux](https://docs.docker.com/engine/install/)
- [Docker Desktop for Mac](https://docs.docker.com/desktop/install/mac-install/)
- [Docker Desktop for Windows](https://docs.docker.com/desktop/install/windows-install/)

#### Step 2: Pull the Image

```bash
# Pull the latest image
docker pull truongnat/agentic-sdlc:latest

# Or pull a specific version
docker pull truongnat/agentic-sdlc:2.5.0
```

#### Step 3: Run with Docker Compose

Create a `docker-compose.yml` file:

```yaml
version: '3.8'

services:
  agentic-sdlc:
    image: truongnat/agentic-sdlc:latest
    container_name: agentic-sdlc
    volumes:
      - ./:/workspace
      - ./data:/app/data
      - ./logs:/app/logs
    environment:
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - ANTHROPIC_API_KEY=${ANTHROPIC_API_KEY}
    ports:
      - "8000:8000"
    restart: unless-stopped
```

Start the container:

```bash
docker-compose up -d
```

#### Step 4: Verify Docker Installation

```bash
# Check container status
docker-compose ps

# Run a command in the container
docker-compose exec agentic-sdlc asdlc --version

# View logs
docker-compose logs -f
```

### Method 3: From Source

Install from source for development or to use the latest features.

#### Step 1: Clone the Repository

```bash
git clone https://github.com/truongnat/agentic-sdlc.git
cd agentic-sdlc
```

#### Step 2: Create Virtual Environment

```bash
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

#### Step 3: Install Dependencies

```bash
# Install core dependencies
pip install -r requirements.txt

# Install development dependencies (optional)
pip install -r requirements-dev.txt
```

#### Step 4: Install in Development Mode

```bash
# Install package in editable mode
pip install -e .

# Verify installation
asdlc --version
```

#### Step 5: Run Tests (Optional)

```bash
# Run all tests
pytest tests/

# Run with coverage
pytest tests/ --cov=agentic_sdlc --cov-report=html
```

### Method 4: Using Bun (Alternative)

For projects using Bun as a package manager:

```bash
# Install via Bun
bun install agentic-sdlc

# Verify installation
bunx asdlc --version
```

## 🔧 Post-Installation Setup

### Step 1: Initialize Configuration

```bash
# Create default configuration
asdlc init

# This creates:
# - .agent/ directory
# - docs/ directory
# - agentic.yaml configuration file
```

### Step 2: Configure Environment Variables

Create a `.env` file in your project root:

```bash
# Copy the template
cp .env.template .env
```

Edit `.env` with your settings:

```bash
# LLM Provider Configuration
OPENAI_API_KEY=your_openai_key_here
ANTHROPIC_API_KEY=your_anthropic_key_here

# Or use local LLM (Ollama)
USE_LOCAL_LLM=true
OLLAMA_BASE_URL=http://localhost:11434

# Brain Configuration
BRAIN_ENABLED=true
BRAIN_LEARNING_RATE=0.1

# Logging
LOG_LEVEL=INFO
LOG_FILE=logs/agentic-sdlc.log

# Knowledge Base (Optional)
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=your_password
```

### Step 3: Verify Configuration

```bash
# Validate configuration
asdlc config validate

# Show current configuration
asdlc config show

# Test brain connectivity
asdlc brain status
```

### Step 4: Initialize Brain State

```bash
# Initialize brain for your project
asdlc brain init-state --sprint 1

# Verify brain health
asdlc brain health
```

## 🌐 Platform-Specific Instructions

### Linux (Ubuntu/Debian)

```bash
# Install system dependencies
sudo apt-get update
sudo apt-get install -y python3 python3-pip python3-venv git

# Install SDLC Kit
python3 -m venv .venv
source .venv/bin/activate
pip install agentic-sdlc

# Verify
asdlc --version
```

### macOS

```bash
# Install Homebrew (if not already installed)
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install Python
brew install python@3.11

# Install SDLC Kit
python3 -m venv .venv
source .venv/bin/activate
pip install agentic-sdlc

# Verify
asdlc --version
```

### Windows

**Using PowerShell:**

```powershell
# Install Python from python.org or Microsoft Store

# Create virtual environment
python -m venv .venv
.venv\Scripts\Activate.ps1

# Install SDLC Kit
pip install agentic-sdlc

# Verify
asdlc --version
```

**Using WSL2 (Recommended):**

```bash
# Install WSL2 and Ubuntu
wsl --install

# Follow Linux instructions above
```

## 🔌 Optional Components

### Neo4j Knowledge Base

For advanced knowledge graph features:

**Using Docker:**
```bash
docker run -d \
  --name neo4j \
  -p 7474:7474 -p 7687:7687 \
  -e NEO4J_AUTH=neo4j/your_password \
  neo4j:latest
```

**Using apt (Linux):**
```bash
wget -O - https://debian.neo4j.com/neotechnology.gpg.key | sudo apt-key add -
echo 'deb https://debian.neo4j.com stable latest' | sudo tee /etc/apt/sources.list.d/neo4j.list
sudo apt-get update
sudo apt-get install neo4j
```

### Ollama (Local LLM)

For privacy-first local LLM support:

**Linux:**
```bash
curl -fsSL https://ollama.com/install.sh | sh
ollama pull llama2
```

**macOS:**
```bash
brew install ollama
ollama pull llama2
```

**Windows:**
Download from [ollama.com](https://ollama.com/download)

### Redis (Caching)

For improved performance with caching:

**Using Docker:**
```bash
docker run -d --name redis -p 6379:6379 redis:latest
```

**Using apt (Linux):**
```bash
sudo apt-get install redis-server
sudo systemctl start redis
```

## 🧪 Verification Checklist

After installation, verify everything works:

```bash
# 1. Check CLI is available
asdlc --version

# 2. Verify Python package
python -c "import agentic_sdlc; print('OK')"

# 3. Check configuration
asdlc config validate

# 4. Test brain status
asdlc brain status

# 5. List agents
asdlc agent list

# 6. List workflows
asdlc workflow list

# 7. Run health check
asdlc brain health
```

All commands should complete without errors.

## 🔄 Upgrading

### Upgrading pip Installation

```bash
# Upgrade to latest version
pip install --upgrade agentic-sdlc

# Upgrade to specific version
pip install --upgrade agentic-sdlc==2.6.0

# Verify new version
asdlc --version
```

### Upgrading Docker Installation

```bash
# Pull latest image
docker-compose pull

# Restart containers
docker-compose down
docker-compose up -d

# Verify
docker-compose exec agentic-sdlc asdlc --version
```

### Upgrading from Source

```bash
# Pull latest changes
git pull origin main

# Update dependencies
pip install -r requirements.txt

# Reinstall package
pip install -e .

# Verify
asdlc --version
```

## 🗑️ Uninstallation

### Remove pip Installation

```bash
# Uninstall package
pip uninstall agentic-sdlc

# Remove configuration (optional)
rm -rf .agent/ agentic.yaml
```

### Remove Docker Installation

```bash
# Stop and remove containers
docker-compose down -v

# Remove images
docker rmi truongnat/agentic-sdlc:latest

# Remove volumes (optional)
docker volume prune
```

## 🐛 Troubleshooting Installation

### Common Issues

**Issue: Command not found after installation**
```bash
# Solution: Ensure virtual environment is activated
source .venv/bin/activate  # Linux/macOS
.venv\Scripts\activate     # Windows

# Or add to PATH
export PATH="$HOME/.local/bin:$PATH"
```

**Issue: Permission denied errors**
```bash
# Solution: Use --user flag
pip install --user agentic-sdlc

# Or fix permissions
sudo chown -R $USER:$USER ~/.local
```

**Issue: SSL certificate errors**
```bash
# Solution: Upgrade pip and certifi
pip install --upgrade pip certifi

# Or use trusted host
pip install --trusted-host pypi.org --trusted-host files.pythonhosted.org agentic-sdlc
```

**Issue: Dependency conflicts**
```bash
# Solution: Use fresh virtual environment
deactivate
rm -rf .venv
python3 -m venv .venv
source .venv/bin/activate
pip install agentic-sdlc
```

### Getting Help

If you encounter issues:

1. Check the [Troubleshooting Guide](TROUBLESHOOTING.md)
2. Search [GitHub Issues](https://github.com/truongnat/agentic-sdlc/issues)
3. Run diagnostics: `asdlc diagnose`
4. View logs: `asdlc logs --tail 100`

## 📚 Next Steps

After successful installation:

1. **[Getting Started Guide](GETTING_STARTED.md)** - Quick start tutorial
2. **[Configuration Guide](CONFIGURATION.md)** - Configure the kit
3. **[Architecture Overview](ARCHITECTURE.md)** - Understand the system
4. **[Examples](../examples/)** - Try example workflows

---

**Installation complete?** Head to the [Getting Started Guide](GETTING_STARTED.md) →
