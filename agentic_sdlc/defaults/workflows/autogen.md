---
description: Process - Multi-Agent Task Execution with AutoGen
---

# AutoGen Workflow

> **Skill Definition:** Multi-agent orchestration using Microsoft AutoGen framework

// turbo-all

## Overview
Use AutoGen for complex tasks requiring autonomous multi-agent collaboration:
- Debugging sessions
- Code generation with testing
- Research and synthesis

## Usage

### Single Agent
```bash
agentic-sdlc autogen --task "Write a Python function to parse JSON" --team dev
```

### Multi-Agent Team
```bash
agentic-sdlc autogen --task "Write and test a sorting algorithm" --team dev,tester
```

### With Custom Model
```bash
agentic-sdlc autogen --task "Debug login issue" --team dev --model gpt-4o
```

## Available Roles
| Role | Description |
|------|-------------|
| `dev` | Developer - code implementation |
| `tester` | Quality Assurance - testing and verification |
| `orchestrator` | Coordinator - task breakdown and delegation |

## Options
| Flag | Description | Default |
|------|-------------|---------|
| `--task, -t` | Task description (required) | - |
| `--team` | Comma-separated roles | `dev` |
| `--model, -m` | LLM model | `gemini-2.0-flash` |
| `--max-turns` | Max conversation turns | `10` |

## Examples

### Debug a Bug
```bash
agentic-sdlc autogen -t "Find why login returns 401" --team dev,tester
```

### Generate Feature
```bash
agentic-sdlc autogen -t "Create REST API for user profiles" --team dev
```

## Requirements
- `GOOGLE_GENAI_API_KEY` or `OPENAI_API_KEY` in `.env`
- AutoGen packages installed: `pip install -r tools/requirements.txt`

#autogen #multi-agent #automation
