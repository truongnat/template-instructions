"""
Senior Developer Workflow Example - Agentic SDLC

This example demonstrates a high-level workflow typical for a Senior Developer:
1. Researching best practices and existing project context (RAG).
2. Domain-aware reasoning and task analysis.
3. Orchestrating a swarm of agents (Researcher -> Developer -> Reviewer).
4. Generating artifacts (Implementation Plan, Code, Review Report).
5. Self-improvement analysis for future tasks.
"""

import sys
from pathlib import Path

# Add src to path if running from repo root
sys.path.append(str(Path(__file__).parent.parent / "src"))

from agentic_sdlc import AgentBridge, AgentRole
from agentic_sdlc.core.logging import setup_logging

# Initialize logging
setup_logging(level="INFO")

def senior_developer_workflow():
    # 1. Initialize the Bridge
    # A senior dev wants cross-provider stability, so we let the router 
    # auto-select (Gemini -> OpenAI -> Anthropic)
    bridge = AgentBridge(
        project_dir=Path("."),
        project_name="SeniorAuthUpgrade",
        enable_research=True,
        enable_swarm=True,
        enable_learning=True
    )

    print("🚀 Starting Senior Developer Workflow: 'Migrate to OAuth2/OIDC'")

    # 2. Add Project Context to Knowledge Base (RAG)
    # Seniors ensure the agent knows the existing architecture first.
    if bridge.knowledge_base:
        print("\n📚 Ingesting architecture documents...")
        # Imagine we have security docs and architecture ADRs
        # bridge.knowledge_base.ingest_directory("docs/arch")
        pass

    # 3. Process Request with Enhanced Pipeline
    # This flow: Detects Domain -> Researches RAG -> Optimizes Prompt -> Executes Swarm
    request_summary = (
        "Upgrade the current internal session-based auth to a secure OAuth2/OIDC flow using FastAPI. "
        "Ensure compatibility with existing user database and follow OWASP Top 10 security guidelines."
    )
    
    print(f"\n🧠 Analyzing and executing request: {request_summary}")
    
    response = bridge.process_request_enhanced(request_summary)

    if response.success:
        # 4. Inspect Results & Artifacts
        print("\n✅ Workflow Completed Successfully!")
        print(f"🔹 Detected Technical Domain: {response.metadata.get('domain')}")
        print(f"🔹 LLM Provider Used: {response.metadata.get('llm_provider')}")
        
        # Access generated artifacts
        artifacts = bridge.artifact_manager.list_by_task(task_id=response.task_id)
        print(f"\n📄 Generated Artifacts ({len(artifacts)}):")
        for art in artifacts:
            print(f"   - {art.type}: {art.name} ({art.id})")

        # 5. Generate a Review & Improvement Report
        # Seniors care about "how did we do" and "how to do it better next time"
        if bridge._improvement_engine:
            print("\n📈 Generating Self-Improvement Report...")
            report = bridge.learn_report()
            print("\n--- Improvement Report Highlights ---")
            print('\n'.join(report.split('\n')[:10])) # Print first 10 lines
            print("-------------------------------------")
            
    else:
        print(f"\n❌ Workflow Failed: {response.error}")

if __name__ == "__main__":
    senior_developer_workflow()
