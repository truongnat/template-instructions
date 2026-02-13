# Setup Guide for Agentic SDLC Projects

This guide helps you set up and run your project built with the Agentic SDLC framework.

## Prerequisites

### Required
- **Python 3.10+** - The framework requires Python 3.10 or higher
- **pip** - Python package manager

### Optional (depending on features used)
- **Docker** - If using containerized services
- **Git** - For version control
- **Node.js** - If using JavaScript-based tools

## Installation

### 1. Install the Framework

```bash
pip install agentic-sdlc
```

Or with optional dependencies:

```bash
# For CLI support
pip install agentic-sdlc[cli]

# For all features
pip install agentic-sdlc[dev,cli,graph,mcp,tools]
```

### 2. Environment Variables

The `.env` file has been created from the framework's template. Edit it with your settings:

```bash
nano .env  # or use your preferred editor
```

**Required: At least one AI provider API key**

```bash
# Core Settings (Required)
PROJECT_ROOT=.
CURRENT_SPRINT=1

# AI Model API Keys (At least one required for AI features)
OPENAI_API_KEY=your-openai-key-here
# OR
ANTHROPIC_API_KEY=your-anthropic-key-here
# OR use local models
OLLAMA_BASE_URL=http://localhost:11434

# Optional: GitHub Integration
GITHUB_TOKEN=your-github-token
GITHUB_REPO=username/repo-name

# Optional: Knowledge Graph (if using Memgraph)
MEMGRAPH_URI=bolt://localhost:7687
MEMGRAPH_USERNAME=admin
MEMGRAPH_PASSWORD=admin
```

### 3. Configuration

Edit `.agentic_sdlc/config.yaml` for your project:

```yaml
project_root: "."
log_level: "INFO"

models:
  default_provider: "openai"  # or "anthropic", "ollama"
  default_model: "gpt-4"

workflows:
  # Your workflow configurations

plugins:
  # Your plugin configurations
```

## Running Your Project

### Basic Usage

```python
from agentic_sdlc import Config, create_agent

# Load configuration
config = Config()

# Create an agent
agent = create_agent(
    name="developer",
    role="software_developer",
    model_name="gpt-4"
)

# Your code here...
```

### Using CLI

```bash
# Check status
python3 -m agentic_sdlc.cli status

# Create an agent
python3 -m agentic_sdlc.cli agent create --name dev --role developer

# Run a workflow
python3 -m agentic_sdlc.cli run my-workflow
```

## Optional Services

### Local AI Models (Ollama)

If you want to use local models instead of cloud APIs:

```bash
# Install Ollama
curl -fsSL https://ollama.com/install.sh | sh

# Pull a model
ollama pull llama2

# Set in .env
OLLAMA_BASE_URL=http://localhost:11434
```

### Knowledge Graph (Memgraph)

If your project uses graph-based knowledge management:

```bash
# Using Docker
docker run -p 7687:7687 -p 7444:7444 memgraph/memgraph

# Set in .env
MEMGRAPH_URI=bolt://localhost:7687
```

## Troubleshooting

### Import Errors

```bash
# Verify installation
python3 -c "import agentic_sdlc; print(agentic_sdlc.__version__)"

# Reinstall if needed
pip install --upgrade agentic-sdlc
```

### Missing API Keys

If you see API key errors:
1. Check `.env` file exists and has correct keys
2. Verify keys are not expired
3. Consider using local models (Ollama) as alternative

### Configuration Issues

```bash
# Validate configuration
python3 -c "from agentic_sdlc import Config; Config()"
```

## Next Steps

1. ✅ Review `CONTEXT.md` for framework overview
2. ✅ Configure `.env` with your API keys
3. ✅ Edit `.agentic_sdlc/config.yaml` for your needs
4. ✅ Start building with AI agents!

## Resources

- **Documentation**: See `CONTEXT.md`
- **Examples**: Check framework examples
- **Support**: Visit framework repository

---

**Quick Start Checklist:**
- [ ] Python 3.10+ installed
- [ ] Framework installed: `pip install agentic-sdlc`
- [ ] `.env` file configured with API keys
- [ ] `.agentic_sdlc/config.yaml` reviewed
- [ ] Test run: `python3 -m agentic_sdlc.cli status`
