"""Agent Bridge - Main interface between core and CLI/IDE agents.

The AgentBridge is the primary entry point for external agents.
It processes user requests through a full E2E pipeline:
1. Domain Detection → 2. Research → 3. Prompt Optimization →
4. Task Design → 5. Swarm Execution → 6. Self-Learning
"""

from pathlib import Path
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field

from ..core.artifact_manager import ArtifactManager, ArtifactType
from ..core.domain import DomainRegistry
from ..core.llm import LLMConfig, LLMProviderType, LLMRouter, get_router
from ..core.logging import get_logger
from ..intelligence.learning.self_improvement import SelfImprovementEngine
from ..intelligence.reasoning.reasoner import Reasoner
from ..knowledge.knowledge_base import KnowledgeBase
from ..knowledge.research_agent import ResearchAgent
from ..prompts.context_optimizer import ContextItem, ContextOptimizer
from ..prompts.generator import PromptGenerator
from ..prompts.prompt_lab import PromptLab
from ..sdlc.board import TaskStatus
from ..sdlc.tracker import SDLCTracker
from ..skills.generator import SkillGenerator
from ..skills.registry import SkillRegistry
from ..skills.skill import Skill
from ..swarm.orchestrator import SwarmConfig, SwarmOrchestrator

logger = get_logger(__name__)


class AgentResponse(BaseModel):
    """Response from the AgentBridge to the calling agent.

    Contains the generated instructions, context, and metadata
    the agent needs to execute the task.
    """

    success: bool = True
    message: str = ""
    skill_instructions: str = Field(default="", description="SKILL.md content for agent")
    prompt: str = Field(default="", description="Optimized execution prompt")
    board_state: str = Field(default="", description="Current board markdown")
    task_id: Optional[str] = None
    sprint_id: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)


class AgentBridge:
    """Bridge between agentic-sdlc core and external CLI/IDE agents.

    This is the main coordination class. It handles:
    1. Processing user requests into skill lookups
    2. Generating optimized prompts for agent execution
    3. Managing SDLC board state
    4. Submitting and reviewing outputs

    Example:
        >>> bridge = AgentBridge(project_dir=Path("."))
        >>> response = bridge.process_request("Create a todo webapp")
        >>> # Agent reads response.skill_instructions and executes
        >>> result = bridge.submit_output(response.task_id, "output here")
    """

    def __init__(
        self,
        project_dir: Path,
        project_name: Optional[str] = None,
        enable_research: bool = True,
        enable_swarm: bool = True,
        enable_learning: bool = True,
        llm_provider: Optional[str] = None,
        llm_model: Optional[str] = None,
    ) -> None:
        """Initialize the bridge with full pipeline capabilities.

        Args:
            project_dir: Project root directory.
            project_name: Project name (defaults to directory name).
            enable_research: Enable RAG/research pipeline.
            enable_swarm: Enable swarm multi-agent execution.
            enable_learning: Enable self-learning engine.
            llm_provider: Preferred LLM ('gemini', 'openai', 'anthropic', 'ollama').
                          If None, auto-selects best available.
            llm_model: Specific model name to use.
        """
        self._project_dir = project_dir
        self._project_name = project_name or project_dir.name

        # Storage directories
        self._data_dir = project_dir / ".agentic_sdlc"
        self._skills_dir = self._data_dir / "skills"
        self._generated_dir = self._skills_dir / "generated"

        # Core components
        self._registry = SkillRegistry(
            metadata_path=self._data_dir / "skill_metadata.json"
        )
        self._generator = SkillGenerator(output_dir=self._generated_dir)
        self._prompt_gen = PromptGenerator()
        self._context_opt = ContextOptimizer()
        self._tracker = SDLCTracker(
            project_name=self._project_name,
            storage_dir=self._data_dir,
        )

        # Domain Engine
        self._domain_registry = DomainRegistry()
        domain_config = self._data_dir / "domains.yaml"
        if domain_config.exists():
            self._domain_registry.load_from_yaml(domain_config)

        # Reasoner with domain detection
        self._reasoner = Reasoner(domain_registry=self._domain_registry)

        # Knowledge & Research (Phase 2)
        self._knowledge_base = None
        self._researcher = None
        if enable_research:
            try:
                self._knowledge_base = KnowledgeBase(
                    persist_dir=self._data_dir / "knowledge"
                )
                self._researcher = ResearchAgent(
                    knowledge_base=self._knowledge_base
                )
            except Exception as e:
                logger.warning(f"Research components init failed: {e}")

        # LLM Router (supports Gemini, OpenAI, Anthropic, Ollama)
        llm_configs = {}
        if llm_provider and llm_model:
            ptype = LLMProviderType(llm_provider.lower())
            llm_configs[ptype] = LLMConfig(provider=ptype, model=llm_model)
        elif llm_provider:
            ptype = LLMProviderType(llm_provider.lower())
            llm_configs[ptype] = LLMConfig(provider=ptype)

        self._llm_router = get_router(
            preferred=llm_provider,
            configs={k.value: {"model": v.model} for k, v in llm_configs.items()} if llm_configs else None,
        )

        # Prompt Lab (Phase 3) — with LLM-powered evaluation
        self._prompt_lab = PromptLab(
            history_dir=self._data_dir / "prompts" / "history",
            llm=self._llm_router,
        )

        # Self-Improvement (Phase 4)
        self._improvement_engine = None
        if enable_learning:
            self._improvement_engine = SelfImprovementEngine(
                data_dir=self._data_dir / "learning"
            )

        # Swarm Orchestrator (Phase 5) — with LLM for agent reasoning
        self._swarm = None
        if enable_swarm:
            self._swarm = SwarmOrchestrator(llm=self._llm_router)

        # Artifact Manager (Phase 6)
        self._artifacts = ArtifactManager(
            base_dir=self._data_dir / "artifacts"
        )

        # Load built-in skills
        builtin_dir = Path(__file__).parent.parent / "skills" / "builtin"
        self._registry.discover(builtin_dir)

        # Load generated skills
        if self._generated_dir.exists():
            self._registry.discover(self._generated_dir)

        # Load user skills
        user_skills_dir = project_dir / ".agentic_sdlc" / "skills"
        if user_skills_dir.exists():
            self._registry.discover(user_skills_dir)

        logger.info(
            "AgentBridge initialized: %s (%d skills, research=%s, swarm=%s)",
            self._project_name,
            self._registry.count,
            enable_research,
            enable_swarm,
        )

    def process_request(
        self,
        user_input: str,
        context: Optional[Dict[str, Any]] = None,
        agent_type: str = "antigravity",
    ) -> AgentResponse:
        """Process a user request into actionable agent instructions.

        Flow:
        1. Search for matching skills
        2. Generate new skill if none found
        3. Create SDLC sprint + tasks
        4. Generate optimized prompt
        5. Return instructions for agent

        Args:
            user_input: User's natural language request.
            context: Optional project context.
            agent_type: Target agent (antigravity, gemini, cursor, generic).

        Returns:
            AgentResponse with instructions and metadata.
        """
        context = context or {}

        # Step 1: Find matching skills
        skills = self._registry.search(user_input, limit=5)

        # Step 2: Generate skill if no good matches
        if not skills:
            logger.info("No matching skills found, generating...")
            generated = self._generator.generate(user_input, context)
            self._registry.register(generated)
            skills = [generated]

        # Step 3: Create SDLC sprint
        sprint = self._tracker.plan(user_input, skills)

        # Step 4: Get first task
        next_tasks = self._tracker.get_next_tasks()
        if not next_tasks:
            return AgentResponse(
                success=False,
                message="No tasks to execute",
                sprint_id=sprint.id,
            )

        task = next_tasks[0]
        self._tracker.start_task(task.id)

        # Step 5: Find the skill for this task
        skill = self._registry.get(task.skill_ref) or skills[0]

        # Step 6: Generate optimized prompt
        prompt = self._prompt_gen.generate(skill, context, agent_type)
        skill_md = skill.to_skill_md()

        return AgentResponse(
            success=True,
            message=f"Ready to execute: {task.title}",
            skill_instructions=skill_md,
            prompt=prompt,
            board_state=self._tracker.get_board_markdown(),
            task_id=task.id,
            sprint_id=sprint.id,
            metadata={
                "skill_name": skill.name,
                "role": skill.role.value,
                "category": skill.category,
                "total_tasks": len(sprint.task_ids),
            },
        )

    def get_task_instructions(
        self,
        task_id: str,
        agent_type: str = "antigravity",
    ) -> AgentResponse:
        """Get instructions for a specific task.

        Args:
            task_id: Task ID from the board.
            agent_type: Target agent type.

        Returns:
            AgentResponse with skill instructions.
        """
        task = self._tracker.board.tasks.get(task_id)
        if not task:
            return AgentResponse(success=False, message=f"Task not found: {task_id}")

        skill = self._registry.get(task.skill_ref)
        if not skill:
            return AgentResponse(
                success=False,
                message=f"Skill not found: {task.skill_ref}",
            )

        self._tracker.start_task(task_id)
        prompt = self._prompt_gen.generate(skill, agent_type=agent_type)

        return AgentResponse(
            success=True,
            message=f"Instructions for: {task.title}",
            skill_instructions=skill.to_skill_md(),
            prompt=prompt,
            task_id=task_id,
            metadata={"skill_name": skill.name},
        )

    def submit_output(
        self,
        task_id: str,
        output: str,
        score: Optional[float] = None,
    ) -> AgentResponse:
        """Submit task output for review and scoring.

        Args:
            task_id: Task ID.
            output: Agent's output text.
            score: Optional review score (0.0-1.0).

        Returns:
            AgentResponse with review result.
        """
        task = self._tracker.board.tasks.get(task_id)
        if not task:
            return AgentResponse(success=False, message=f"Task not found: {task_id}")

        # Store output
        output_dir = self._data_dir / "outputs"
        output_dir.mkdir(parents=True, exist_ok=True)
        output_path = output_dir / f"{task_id}.md"
        output_path.write_text(output, encoding="utf-8")

        # Submit to tracker
        updated_task = self._tracker.submit_output(
            task_id, str(output_path), score
        )

        # Update skill metadata
        if task.skill_ref:
            self._registry.update_metadata(
                task.skill_ref,
                success=(updated_task.status == TaskStatus.DONE),
                score=score,
            )

        # Generate review prompt if no score provided
        review_prompt = ""
        if score is None:
            skill = self._registry.get(task.skill_ref)
            if skill:
                review_prompt = self._prompt_gen.generate_review_prompt(output, skill)

        return AgentResponse(
            success=True,
            message=f"Task {task_id}: {updated_task.status.value}",
            prompt=review_prompt,
            board_state=self._tracker.get_board_markdown(),
            task_id=task_id,
            metadata={
                "status": updated_task.status.value,
                "score": score,
                "retry_count": updated_task.retry_count,
            },
        )

    def get_board(self) -> str:
        """Get current board state as markdown."""
        return self._tracker.get_board_markdown()

    def search_skills(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Search the skill registry.

        Args:
            query: Search query.
            limit: Max results.

        Returns:
            List of skill summaries.
        """
        skills = self._registry.search(query, limit=limit)
        return [
            {
                "name": s.name,
                "description": s.description[:100],
                "role": s.role.value,
                "category": s.category,
                "tags": s.tags,
                "success_rate": s.metadata.success_rate,
            }
            for s in skills
        ]

    def generate_skill(
        self, description: str, context: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """Generate a new skill from description.

        Args:
            description: Task description.
            context: Optional context.

        Returns:
            Generated skill summary.
        """
        skill = self._generator.generate(description, context)
        self._registry.register(skill)
        return {
            "name": skill.name,
            "role": skill.role.value,
            "category": skill.category,
            "steps": len(skill.workflow_steps),
            "skill_md": skill.to_skill_md(),
        }

    # ==========================================================================
    # Enhanced Pipeline Methods (Phases 1-6)
    # ==========================================================================

    def process_request_enhanced(
        self,
        user_input: str,
        context: Optional[Dict[str, Any]] = None,
        agent_type: str = "antigravity",
    ) -> AgentResponse:
        """Process a request using the full E2E pipeline.

        Pipeline:
        1. Domain Detection (Reasoner)
        2. Research Phase (ResearchAgent + RAG)
        3. Prompt Optimization (PromptLab A/B testing)
        4. Task Design (SkillGenerator + SDLC)
        5. Self-Learning (SelfImprovementEngine)

        Args:
            user_input: User's natural language request.
            context: Optional project context.
            agent_type: Target agent type.

        Returns:
            AgentResponse with enhanced instructions.
        """
        context = context or {}
        pipeline_meta: Dict[str, Any] = {}

        # Phase 1: Domain Detection
        domain_result = self._reasoner.detect_domain(user_input, context)
        domain_name = domain_result.domain.name if domain_result.domain else "general"
        context["domain"] = domain_name
        pipeline_meta["domain"] = domain_name
        pipeline_meta["domain_confidence"] = domain_result.confidence
        logger.info(f"Domain detected: {domain_name} ({domain_result.confidence:.2f})")

        # Phase 2: Research
        research_context = ""
        if self._researcher:
            try:
                research_result = self._researcher.research(
                    query=user_input, context=context
                )
                research_context = research_result.combined_context
                pipeline_meta["research_sources"] = research_result.total_sources
            except Exception as e:
                logger.warning(f"Research phase failed: {e}")

        # Phase 3: Prompt Optimization
        try:
            prompt_result = self._prompt_lab.optimize(
                query=user_input,
                context=context,
                research_context=research_context,
            )
            optimized_prompt = prompt_result.winner.content if prompt_result.winner else user_input
            pipeline_meta["prompt_strategy"] = (
                prompt_result.winner.metadata.get("strategy", "unknown")
                if prompt_result.winner else "direct"
            )
            pipeline_meta["prompt_score"] = (
                prompt_result.winner.score if prompt_result.winner else 0
            )
        except Exception as e:
            logger.warning(f"Prompt optimization failed: {e}")
            optimized_prompt = user_input

        # Phase 4: Skill + Task Design (reuse existing flow)
        skills = self._registry.search(user_input, domain=domain_name, limit=5)
        if not skills:
            skills = self._registry.search(user_input, limit=5)
        if not skills:
            generated = self._generator.generate(user_input, context)
            self._registry.register(generated)
            skills = [generated]

        sprint = self._tracker.plan(user_input, skills)
        next_tasks = self._tracker.get_next_tasks()
        if not next_tasks:
            return AgentResponse(
                success=False,
                message="No tasks to execute",
                sprint_id=sprint.id,
            )

        task = next_tasks[0]
        self._tracker.start_task(task.id)
        skill = self._registry.get(task.skill_ref) or skills[0]
        skill_md = skill.to_skill_md()

        # Store artifacts
        self._artifacts.store(
            type=ArtifactType.REQUEST,
            name=f"request-{task.id[:8]}",
            content=user_input,
            source_agent=agent_type,
            task_id=task.id,
        )
        self._artifacts.store(
            type=ArtifactType.PROMPT,
            name=f"prompt-{task.id[:8]}",
            content=optimized_prompt,
            source_agent="prompt_lab",
            task_id=task.id,
        )

        # Phase 6: Record for self-learning
        if self._improvement_engine:
            self._improvement_engine.record_execution(
                task=user_input,
                success=True,
                domain=domain_name,
                strategy=pipeline_meta.get("prompt_strategy", ""),
            )

        return AgentResponse(
            success=True,
            message=f"Ready to execute: {task.title}",
            skill_instructions=skill_md,
            prompt=optimized_prompt,
            board_state=self._tracker.get_board_markdown(),
            task_id=task.id,
            sprint_id=sprint.id,
            metadata={
                "skill_name": skill.name,
                "role": skill.role.value,
                "category": skill.category,
                "total_tasks": len(sprint.task_ids),
                "pipeline": pipeline_meta,
            },
        )

    def research(self, query: str) -> Dict[str, Any]:
        """Run the research pipeline only.

        Args:
            query: Research query.

        Returns:
            Research results dictionary.
        """
        if not self._researcher:
            return {"error": "Research not enabled"}

        result = self._researcher.research(query)
        return {
            "query": result.query,
            "rag_results": len(result.rag_results),
            "web_results": len(result.web_results),
            "context": result.combined_context[:2000],
        }

    def learn_report(self) -> str:
        """Generate a self-improvement report.

        Returns:
            Markdown report string.
        """
        if not self._improvement_engine:
            return "Self-learning not enabled"
        return self._improvement_engine.generate_report_markdown()

    @property
    def domain_registry(self) -> DomainRegistry:
        """Get the domain registry."""
        return self._domain_registry

    @property
    def knowledge_base(self) -> Optional[KnowledgeBase]:
        """Get the knowledge base."""
        return self._knowledge_base

    @property
    def swarm(self) -> Optional[SwarmOrchestrator]:
        """Get the swarm orchestrator."""
        return self._swarm

    @property
    def artifact_manager(self) -> ArtifactManager:
        """Get the artifact manager."""
        return self._artifacts

    @property
    def llm_router(self) -> LLMRouter:
        """Get the LLM router for direct provider access."""
        return self._llm_router
