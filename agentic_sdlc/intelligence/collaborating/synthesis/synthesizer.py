"""
Output Synthesizer - Aggregate and synthesize outputs from multiple agents.

Part of Layer 2: Intelligence Layer.

Inspired by Swarms MixtureOfAgents (MoA) pattern - combines outputs from
multiple expert agents into a unified, coherent recommendation.
"""

import json
import sys
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional

# Set UTF-8 encoding for Windows console
if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except Exception:
        pass


@dataclass
class SynthesisInput:
    """Input for synthesis from a single role."""
    role: str
    output: str
    confidence: float = 1.0
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class SynthesisResult:
    """Result of output synthesis."""
    synthesized_output: str
    inputs: List[SynthesisInput]
    strategy: str
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "synthesized_output": self.synthesized_output,
            "inputs": [
                {"role": i.role, "output": i.output, "confidence": i.confidence}
                for i in self.inputs
            ],
            "strategy": self.strategy,
            "timestamp": self.timestamp,
            "metadata": self.metadata
        }


class SynthesisStrategy:
    """Base class for synthesis strategies."""
    
    name: str = "base"
    
    def synthesize(self, inputs: List[SynthesisInput]) -> str:
        raise NotImplementedError


class ConcatenateStrategy(SynthesisStrategy):
    """
    Simple concatenation of all outputs.
    
    Useful for: Collecting diverse perspectives without merging.
    """
    
    name = "concatenate"
    
    def __init__(self, separator: str = "\n\n---\n\n"):
        self.separator = separator
    
    def synthesize(self, inputs: List[SynthesisInput]) -> str:
        sections = []
        for inp in inputs:
            sections.append(f"{inp.role}:\n{inp.output}")
        return self.separator.join(sections)


class WeightedMergeStrategy(SynthesisStrategy):
    """
    Merge outputs with weighted importance.
    
    Useful for: Prioritizing certain roles' outputs over others.
    """
    
    name = "weighted_merge"
    
    def __init__(self, role_weights: Optional[Dict[str, float]] = None):
        self.role_weights = role_weights or {}
    
    def synthesize(self, inputs: List[SynthesisInput]) -> str:
        # Sort by weight (higher weight first)
        weighted_inputs = sorted(
            inputs,
            key=lambda x: self.role_weights.get(x.role, 1.0) * x.confidence,
            reverse=True
        )
        
        sections = []
        for inp in weighted_inputs:
            weight = self.role_weights.get(inp.role, 1.0)
            importance = "Primary" if weight > 1.5 else "Secondary" if weight > 1.0 else "Supporting"
            sections.append(f"### [{importance}] {inp.role}\n\n{inp.output}")
        
        return "\n\n".join(sections)


class ConsensusStrategy(SynthesisStrategy):
    """
    Find consensus points across all outputs.
    
    Useful for: Design reviews, security assessments.
    """
    
    name = "consensus"
    
    def __init__(self, keyword_weight: float = 0.5):
        self.keyword_weight = keyword_weight
    
    def synthesize(self, inputs: List[SynthesisInput]) -> str:
        # Extract key points from each output
        all_points = []
        for inp in inputs:
            lines = inp.output.split('\n')
            for line in lines:
                line = line.strip()
                if line and len(line) > 10:  # Filter short lines
                    all_points.append((inp.role, line))
        
        # Group similar points (simple keyword matching)
        # In production, this would use embeddings for semantic similarity
        
        result = ["# Synthesized Analysis", ""]
        result.append("## Individual Contributions")
        for inp in inputs:
            result.append(f"\n### {inp.role}")
            result.append(inp.output[:500] + "..." if len(inp.output) > 500 else inp.output)
        
        result.append("\n## Summary")
        result.append(f"Combined analysis from {len(inputs)} roles: {', '.join(i.role for i in inputs)}")
        
        return "\n".join(result)


class TemplateStrategy(SynthesisStrategy):
    """
    Synthesize using a custom template.
    
    Useful for: Structured outputs like reports, ADRs.
    """
    
    name = "template"
    
    def __init__(self, template: str):
        """
        Initialize with a template.
        
        Template placeholders:
        - {ROLE_NAME}: Output from specific role
        - {ALL_OUTPUTS}: All outputs concatenated
        - {ROLE_LIST}: Comma-separated list of roles
        """
        self.template = template
    
    def synthesize(self, inputs: List[SynthesisInput]) -> str:
        result = self.template
        
        # Replace role-specific placeholders
        for inp in inputs:
            placeholder = "{" + inp.role.upper() + "}"
            result = result.replace(placeholder, inp.output)
        
        # Replace {ALL_OUTPUTS}
        all_outputs = "\n\n".join(f"**{i.role}:**\n{i.output}" for i in inputs)
        result = result.replace("{ALL_OUTPUTS}", all_outputs)
        
        # Replace {ROLE_LIST}
        role_list = ", ".join(i.role for i in inputs)
        result = result.replace("{ROLE_LIST}", role_list)
        
        return result


class LLMSynthesisStrategy(SynthesisStrategy):
    """
    Use an LLM to synthesize outputs.
    
    This is the most powerful strategy, similar to Swarms MixtureOfAgents
    aggregator agent.
    """
    
    name = "llm"
    
    def __init__(
        self,
        llm_callback: Optional[Callable[[str], str]] = None,
        synthesis_prompt: Optional[str] = None
    ):
        self.llm_callback = llm_callback
        self.synthesis_prompt = synthesis_prompt or self._default_prompt()
    
    def _default_prompt(self) -> str:
        return """You are a synthesis agent. Your job is to combine and synthesize
the following outputs from multiple expert agents into a unified, coherent response.

Identify:
1. Common themes and consensus points
2. Unique insights from each agent
3. Any conflicts or contradictions
4. Actionable recommendations

Expert Outputs:
{ALL_OUTPUTS}

Synthesize these into a comprehensive, well-organized response:"""
    
    def synthesize(self, inputs: List[SynthesisInput]) -> str:
        # Format outputs for LLM
        all_outputs = "\n\n".join(
            f"### {inp.role} (confidence: {inp.confidence})\n{inp.output}"
            for inp in inputs
        )
        
        prompt = self.synthesis_prompt.replace("{ALL_OUTPUTS}", all_outputs)
        
        if self.llm_callback:
            return self.llm_callback(prompt)
        else:
            # Fallback to simple concatenation if no LLM
            return ConcatenateStrategy().synthesize(inputs)


class OutputSynthesizer:
    """
    Aggregate and synthesize outputs from multiple agents.
    
    Inspired by Swarms MixtureOfAgents (MoA) - combines diverse expert
    outputs into unified recommendations.
    
    Use cases:
    - Design Review: Combine SA + UIUX + SECA outputs
    - Code Review: Merge DEV + TESTER + SECA feedback
    - Research: Synthesize multiple research agent findings
    
    Example:
        synthesizer = OutputSynthesizer()
        
        # Add outputs from concurrent execution
        synthesizer.add_input("SA", architecture_analysis)
        synthesizer.add_input("UIUX", ui_design)
        synthesizer.add_input("SECA", security_review)
        
        # Synthesize with LLM (or fallback to template)
        result = synthesizer.synthesize(strategy="llm")
    """

    def __init__(self, storage_dir: Optional[Path] = None):
        """Initialize the synthesizer."""
        self.storage_dir = storage_dir or Path(".brain/synthesizer")
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        
        self._inputs: List[SynthesisInput] = []
        self._strategies: Dict[str, SynthesisStrategy] = {
            "concatenate": ConcatenateStrategy(),
            "weighted": WeightedMergeStrategy(),
            "consensus": ConsensusStrategy(),
        }
        self._llm_callback: Optional[Callable[[str], str]] = None
        self.history: List[SynthesisResult] = []

    def set_llm_callback(self, callback: Callable[[str], str]) -> None:
        """Set the LLM callback for intelligent synthesis."""
        self._llm_callback = callback
        self._strategies["llm"] = LLMSynthesisStrategy(llm_callback=callback)

    def add_strategy(self, name: str, strategy: SynthesisStrategy) -> None:
        """Add a custom synthesis strategy."""
        self._strategies[name] = strategy

    def add_input(
        self,
        role: str,
        output: str,
        confidence: float = 1.0,
        metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Add an input for synthesis.
        
        Args:
            role: The role/agent that produced this output
            output: The output text
            confidence: Confidence score (0-1)
            metadata: Optional additional metadata
        """
        self._inputs.append(SynthesisInput(
            role=role,
            output=output,
            confidence=confidence,
            metadata=metadata or {}
        ))

    def add_inputs_from_concurrent(self, concurrent_result: Dict[str, Any]) -> None:
        """
        Add inputs from a ConcurrentExecutor result.
        
        Args:
            concurrent_result: Result dict from ConcurrentExecutor.run()
        """
        for role, result in concurrent_result.get("results", {}).items():
            if result.get("success", False):
                self.add_input(
                    role=role,
                    output=result.get("output", ""),
                    confidence=1.0 if result["success"] else 0.5
                )

    def clear_inputs(self) -> None:
        """Clear all inputs."""
        self._inputs = []

    def synthesize(self, strategy: str = "concatenate") -> SynthesisResult:
        """
        Synthesize all inputs using the specified strategy.
        
        Args:
            strategy: Strategy name ("concatenate", "weighted", "consensus", "llm")
            
        Returns:
            SynthesisResult with the synthesized output
        """
        if not self._inputs:
            return SynthesisResult(
                synthesized_output="No inputs to synthesize",
                inputs=[],
                strategy=strategy
            )
        
        strategy_impl = self._strategies.get(strategy)
        if not strategy_impl:
            # Fallback to concatenate
            strategy_impl = self._strategies["concatenate"]
            strategy = "concatenate"
        
        synthesized = strategy_impl.synthesize(self._inputs)
        
        result = SynthesisResult(
            synthesized_output=synthesized,
            inputs=self._inputs.copy(),
            strategy=strategy,
            metadata={"input_count": len(self._inputs)}
        )
        
        self.history.append(result)
        self._save_result(result)
        
        return result

    def synthesize_with_template(self, template: str) -> SynthesisResult:
        """
        Synthesize using a custom template.
        
        Args:
            template: Template string with placeholders
            
        Returns:
            SynthesisResult
        """
        strategy = TemplateStrategy(template)
        synthesized = strategy.synthesize(self._inputs)
        
        result = SynthesisResult(
            synthesized_output=synthesized,
            inputs=self._inputs.copy(),
            strategy="template",
            metadata={"template_length": len(template)}
        )
        
        self.history.append(result)
        return result

    def synthesize_design_review(self) -> SynthesisResult:
        """
        Specialized synthesis for design reviews.
        
        Combines outputs from SA, UIUX, SECA, PO roles.
        """
        template = """# Design Review Synthesis

## Architecture Analysis (SA)
{SA}

## UI/UX Design (UIUX)
{UIUX}

## Security Considerations (SECA)
{SECA}

## Product Requirements (PO)
{PO}

## Combined Recommendations

Based on input from: {ROLE_LIST}

{ALL_OUTPUTS}
"""
        return self.synthesize_with_template(template)

    def _save_result(self, result: SynthesisResult) -> None:
        """Save synthesis result to storage."""
        try:
            filename = f"synthesis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            filepath = self.storage_dir / filename
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(result.to_dict(), f, indent=2, ensure_ascii=False)
        except Exception:
            pass  # Silently ignore storage errors

    def get_stats(self) -> Dict[str, Any]:
        """Get synthesis statistics."""
        return {
            "total_syntheses": len(self.history),
            "pending_inputs": len(self._inputs),
            "available_strategies": list(self._strategies.keys()),
            "llm_enabled": self._llm_callback is not None
        }


def main():
    """CLI entry point."""
    import argparse
    from pathlib import Path
    
    parser = argparse.ArgumentParser(description="Output synthesizer")
    parser.add_argument("--inputs", type=str, help="JSON string of inputs: [{'role': '...', 'output': '...'}]")
    parser.add_argument("--file", type=str, help="JSON file containing inputs")
    parser.add_argument("--concurrent-result", type=str, help="JSON file from ConcurrentExecutor")
    parser.add_argument("--strategy", type=str, default="concatenate", help="Strategy to use")
    parser.add_argument("--template", type=str, help="Custom template for synthesis")
    parser.add_argument("--test", action="store_true", help="Run test synthesis")
    parser.add_argument("--stats", action="store_true", help="Show statistics")
    
    args = parser.parse_args()
    synthesizer = OutputSynthesizer()
    
    if args.inputs:
        inputs = json.loads(args.inputs)
        for inp in inputs:
            synthesizer.add_input(inp["role"], inp["output"], inp.get("confidence", 1.0))
            
    elif args.file:
        with open(args.file, 'r', encoding='utf-8') as f:
            inputs = json.load(f)
            for inp in inputs:
                synthesizer.add_input(inp["role"], inp["output"], inp.get("confidence", 1.0))
                
    elif args.concurrent_result:
        with open(args.concurrent_result, 'r', encoding='utf-8') as f:
            result = json.load(f)
            synthesizer.add_inputs_from_concurrent(result)
            
    if args.test:
        # Add mock inputs
        synthesizer.add_input("SA", "Architecture analysis...")
        synthesizer.add_input("UIUX", "UI design analysis...")
        synthesizer.add_input("SECA", "Security review analysis...")
        
    if args.stats:
        print(json.dumps(synthesizer.get_stats(), indent=2))
        return

    if synthesizer._inputs:
        if args.template:
            result = synthesizer.synthesize_with_template(args.template)
        else:
            result = synthesizer.synthesize(strategy=args.strategy)
        print(json.dumps(result.to_dict(), indent=2, ensure_ascii=False))
    else:
        if not args.stats:
            parser.print_help()


if __name__ == "__main__":
    main()
