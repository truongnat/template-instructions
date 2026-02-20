# Project Context (for AI Agents)

This project uses the **Agentic SDLC** framework for AI-assisted development.

> [!TIP]
> Run `asdlc run "your task"` to process requests through the full pipeline.

## Package Structure

- `agentic_sdlc.bridge` — `AgentBridge`: main entry point, E2E pipeline
- `agentic_sdlc.core` — `Config`, `DomainRegistry`, `LLMRouter`, `ArtifactManager`
- `agentic_sdlc.swarm` — `SwarmOrchestrator`, `DeveloperAgent`, `ReviewerAgent`
- `agentic_sdlc.knowledge` — `KnowledgeBase`, `ResearchAgent` (RAG with ChromaDB)
- `agentic_sdlc.prompts` — `PromptLab`, `PromptGenerator`, `ContextOptimizer`
- `agentic_sdlc.intelligence` — `Reasoner`, `SelfImprovementEngine`
- `agentic_sdlc.skills` — `SkillRegistry`, `SkillGenerator`, `SkillLoader`
- `agentic_sdlc.sdlc` — `Board`, `Task`, `Sprint`, `SDLCTracker`

## How the Pipeline Works

```
User Request → Domain Detection → RAG Research → Prompt Optimization → Swarm Execution → Self-Learning
```

## CLI

```bash
asdlc init           # Initialize project with AI agent config
asdlc run "task"     # Process a task through the pipeline
asdlc status         # Show SDLC board
asdlc task next      # Get next available task
asdlc skill list     # List available skills
```

## Configuration

Edit `.agentic_sdlc/config.yaml`:

```yaml
project_name: "my-project"
log_level: "INFO"
default_agent: "antigravity"
```
