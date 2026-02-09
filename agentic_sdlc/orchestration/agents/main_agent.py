"""
Main Agent implementation for the Multi-Agent Orchestration System

This module implements the MainAgent class which serves as the primary interface
for user interaction and request processing. It handles natural language request
parsing, conversation context management, and ambiguous request clarification.
"""

import re
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from uuid import uuid4

from ..models import (
    UserRequest, ConversationContext, ClarifiedRequest, WorkflowInitiation,
    TaskType, DataFormat
)
from ..exceptions.agent import (
    AgentError, AgentInitializationError, AgentExecutionError
)
from ..utils.logging import StructuredLogger
from ..utils.validation import ValidationResult
from ..utils.audit_trail import get_audit_trail, OrchestrationAuditTrail


@dataclass
class RequestParsingResult:
    """Result of request parsing operation"""
    intent: str
    confidence: float
    entities: Dict[str, Any] = field(default_factory=dict)
    keywords: List[str] = field(default_factory=list)
    complexity: str = "medium"  # low, medium, high
    requires_clarification: bool = False
    clarification_questions: List[str] = field(default_factory=list)
    
    def __post_init__(self):
        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError("Confidence must be between 0.0 and 1.0")


@dataclass
class ContextStore:
    """In-memory context storage for conversations"""
    contexts: Dict[str, ConversationContext] = field(default_factory=dict)
    max_contexts: int = 1000
    cleanup_interval_hours: int = 24
    last_cleanup: datetime = field(default_factory=datetime.now)
    
    def store_context(self, context: ConversationContext):
        """Store a conversation context"""
        self.contexts[context.conversation_id] = context
        self._cleanup_if_needed()
    
    def get_context(self, conversation_id: str) -> Optional[ConversationContext]:
        """Retrieve a conversation context"""
        return self.contexts.get(conversation_id)
    
    def update_context(self, conversation_id: str, updates: Dict[str, Any]):
        """Update context data"""
        if conversation_id in self.contexts:
            context = self.contexts[conversation_id]
            for key, value in updates.items():
                context.add_context(key, value)
    
    def _cleanup_if_needed(self):
        """Clean up old contexts if needed"""
        now = datetime.now()
        if (now - self.last_cleanup).total_seconds() > self.cleanup_interval_hours * 3600:
            self._cleanup_old_contexts()
            self.last_cleanup = now
        elif len(self.contexts) > self.max_contexts:
            # Also cleanup if we exceed max contexts
            self._cleanup_old_contexts()
    
    def _cleanup_old_contexts(self):
        """Remove old inactive contexts"""
        if self.cleanup_interval_hours > 0:
            cutoff_time = datetime.now() - timedelta(hours=self.cleanup_interval_hours)
            to_remove = [
                conv_id for conv_id, context in self.contexts.items()
                if context.last_interaction < cutoff_time
            ]
            
            for conv_id in to_remove:
                del self.contexts[conv_id]
        
        # If still too many contexts, remove oldest ones
        if len(self.contexts) > self.max_contexts:
            sorted_contexts = sorted(
                self.contexts.items(),
                key=lambda x: x[1].last_interaction
            )
            excess_count = len(self.contexts) - self.max_contexts
            for conv_id, _ in sorted_contexts[:excess_count]:
                del self.contexts[conv_id]


class NLPProcessor:
    """Natural Language Processing utilities for request parsing"""
    
    # Intent patterns for common request types
    INTENT_PATTERNS = {
        "create_project": [
            r"create\s+(?:a\s+)?(?:new\s+)?project",
            r"start\s+(?:a\s+)?(?:new\s+)?project",
            r"initialize\s+project",
            r"setup\s+project",
            r"create\s+(?:a\s+)?(?:new\s+)?\w+\s+(?:web\s+)?application",
            r"build\s+(?:a\s+)?(?:new\s+)?\w+\s+project"
        ],
        "analyze_requirements": [
            r"analyze\s+requirements",
            r"review\s+requirements",
            r"requirements\s+analysis",
            r"understand\s+requirements"
        ],
        "design_architecture": [
            r"design\s+(?:the\s+)?architecture",
            r"create\s+(?:the\s+)?architecture",
            r"architectural\s+design",
            r"system\s+design",
            r"design\s+(?:a\s+)?(?:scalable\s+)?(?:microservices\s+)?architecture",
            r"design\s+(?:a\s+)?\w+\s+(?:database|schema)",
            r"create\s+(?:a\s+)?\w+\s+(?:database|schema)"
        ],
        "implement_feature": [
            r"implement\s+(?:a\s+)?feature",
            r"build\s+(?:a\s+)?feature",
            r"develop\s+(?:a\s+)?feature",
            r"code\s+(?:a\s+)?feature",
            r"implement\s+\w+",
            r"add\s+\w+\s+(?:feature|functionality)",
            r"create\s+\w+\s+(?:feature|functionality)"
        ],
        "test_system": [
            r"test\s+(?:the\s+)?system",
            r"run\s+tests",
            r"testing\s+",
            r"quality\s+assurance"
        ],
        "research_topic": [
            r"research\s+",
            r"investigate\s+",
            r"find\s+information",
            r"look\s+up"
        ],
        "review_code": [
            r"review\s+(?:the\s+)?code",
            r"code\s+review",
            r"check\s+(?:the\s+)?code",
            r"audit\s+(?:the\s+)?code"
        ],
        "generate_documentation": [
            r"generate\s+(?:documentation|docs)",
            r"create\s+(?:documentation|docs)",
            r"document\s+",
            r"write\s+documentation"
        ]
    }
    
    # Complexity indicators
    COMPLEXITY_INDICATORS = {
        "high": [
            "enterprise", "scalable", "distributed", "microservices",
            "complex", "advanced", "sophisticated", "comprehensive",
            "multi-tier", "high-performance", "fault-tolerant"
        ],
        "low": [
            "simple", "basic", "minimal", "quick", "small",
            "prototype", "poc", "demo", "example"
        ]
    }
    
    # Ambiguity indicators
    AMBIGUITY_INDICATORS = [
        "something", "anything", "whatever", "some kind of",
        "maybe", "perhaps", "possibly", "might", "could",
        "not sure", "don't know", "unclear", "vague"
    ]
    
    @classmethod
    def parse_request(cls, content: str) -> RequestParsingResult:
        """Parse a natural language request"""
        content_lower = content.lower().strip()
        
        # Handle edge cases with very short content
        if len(content_lower) <= 2:
            return RequestParsingResult(
                intent="general_request",
                confidence=0.2,  # Low confidence for very short content
                entities={},
                keywords=[],
                complexity="low",
                requires_clarification=True,
                clarification_questions=["Could you provide more details about what you'd like to accomplish?"]
            )
        
        # Extract intent
        intent, confidence = cls._extract_intent(content_lower)
        
        # Extract entities and keywords
        entities = cls._extract_entities(content)
        keywords = cls._extract_keywords(content_lower)
        
        # Determine complexity
        complexity = cls._determine_complexity(content_lower)
        
        # Check for ambiguity
        requires_clarification, clarification_questions = cls._check_ambiguity(
            content_lower, intent, entities
        )
        
        return RequestParsingResult(
            intent=intent,
            confidence=confidence,
            entities=entities,
            keywords=keywords,
            complexity=complexity,
            requires_clarification=requires_clarification,
            clarification_questions=clarification_questions
        )
    
    @classmethod
    def _extract_intent(cls, content: str) -> Tuple[str, float]:
        """Extract intent from content"""
        best_intent = "general_request"
        best_confidence = 0.3
        
        for intent, patterns in cls.INTENT_PATTERNS.items():
            for pattern in patterns:
                if re.search(pattern, content):
                    # Calculate confidence based on pattern specificity and match quality
                    confidence = min(0.9, 0.6 + len(pattern) / 100)
                    if confidence > best_confidence:
                        best_intent = intent
                        best_confidence = confidence
        
        # Boost confidence for clear, specific requests
        if len(content.split()) >= 3 and best_confidence > 0.3:
            best_confidence = min(0.95, best_confidence + 0.1)
        
        return best_intent, best_confidence
    
    @classmethod
    def _extract_entities(cls, content: str) -> Dict[str, Any]:
        """Extract entities from content"""
        entities = {}
        
        # Extract technology mentions (case-insensitive)
        tech_patterns = {
            "languages": r"\b(python|java|javascript|typescript|go|rust|c\+\+|c#|node\.?js)\b",
            "frameworks": r"\b(react|angular|vue|django|flask|spring|express)\b",
            "databases": r"\b(mysql|postgresql|mongodb|redis|elasticsearch)\b",
            "platforms": r"\b(aws|azure|gcp|docker|kubernetes|heroku)\b"
        }
        
        for category, pattern in tech_patterns.items():
            matches = re.findall(pattern, content, re.IGNORECASE)
            if matches:
                # Convert to lowercase for consistency
                entities[category] = [match.lower() for match in set(matches)]
        
        # Extract project names (capitalized words or quoted strings)
        project_names = re.findall(r'"([^"]+)"|\'([^\']+)\'|\b([A-Z][a-zA-Z]+(?:\s+[A-Z][a-zA-Z]+)*)\b', content)
        if project_names:
            entities["project_names"] = [name for group in project_names for name in group if name]
        
        # Extract numbers (for estimates, versions, etc.)
        numbers = re.findall(r'\b\d+(?:\.\d+)?\b', content)
        if numbers:
            entities["numbers"] = [float(n) if '.' in n else int(n) for n in numbers]
        
        return entities
    
    @classmethod
    def _extract_keywords(cls, content: str) -> List[str]:
        """Extract important keywords from content"""
        # Remove common stop words
        stop_words = {
            "the", "a", "an", "and", "or", "but", "in", "on", "at", "to", "for",
            "of", "with", "by", "is", "are", "was", "were", "be", "been", "have",
            "has", "had", "do", "does", "did", "will", "would", "could", "should",
            "may", "might", "can", "must", "shall", "this", "that", "these", "those"
        }
        
        # Extract words (alphanumeric sequences)
        words = re.findall(r'\b[a-zA-Z][a-zA-Z0-9]*\b', content)
        
        # Filter out stop words and short words
        keywords = [
            word for word in words
            if len(word) > 2 and word.lower() not in stop_words
        ]
        
        # Remove duplicates while preserving order
        seen = set()
        unique_keywords = []
        for keyword in keywords:
            if keyword.lower() not in seen:
                seen.add(keyword.lower())
                unique_keywords.append(keyword)
        
        return unique_keywords[:20]  # Limit to top 20 keywords
    
    @classmethod
    def _determine_complexity(cls, content: str) -> str:
        """Determine request complexity"""
        high_score = sum(1 for indicator in cls.COMPLEXITY_INDICATORS["high"] if indicator in content)
        low_score = sum(1 for indicator in cls.COMPLEXITY_INDICATORS["low"] if indicator in content)
        
        if high_score > low_score:
            return "high"
        elif low_score > high_score:
            return "low"
        else:
            # Default to medium, but check content length as additional indicator
            if len(content) > 500:
                return "high"
            elif len(content) < 100:
                return "low"
            else:
                return "medium"
    
    @classmethod
    def _check_ambiguity(cls, content: str, intent: str, entities: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """Check if request is ambiguous and generate clarification questions"""
        requires_clarification = False
        questions = []
        
        # Check for ambiguity indicators
        ambiguity_count = sum(1 for indicator in cls.AMBIGUITY_INDICATORS if indicator in content)
        if ambiguity_count > 0:
            requires_clarification = True
            questions.append("Could you provide more specific details about what you'd like to accomplish?")
        
        # Check for very short or vague content
        if len(content.split()) < 3:
            requires_clarification = True
            questions.append("Could you provide more details about your request?")
        
        # Intent-specific clarification checks (only for unclear cases)
        if intent == "create_project" and not entities.get("project_names") and len(content.split()) < 5:
            requires_clarification = True
            questions.append("What would you like to name this project?")
        
        if intent == "implement_feature" and len(content.split()) < 6:
            requires_clarification = True
            questions.append("Could you describe the feature requirements in more detail?")
        
        if intent == "design_architecture" and not entities.get("languages") and not entities.get("frameworks") and len(content.split()) < 5:
            requires_clarification = True
            questions.append("What technologies or frameworks would you like to use?")
        
        # Check for missing critical information
        if "deadline" in content.lower() and not entities.get("numbers"):
            requires_clarification = True
            questions.append("What is your target deadline or timeline?")
        
        if "budget" in content.lower() and not entities.get("numbers"):
            requires_clarification = True
            questions.append("What is your budget or resource constraints?")
        
        return requires_clarification, questions


class MainAgent:
    """
    Main Agent for user interaction and request processing
    
    This agent serves as the primary interface for users, handling natural language
    request parsing, conversation context management, and request clarification.
    """
    
    def __init__(self, agent_id: Optional[str] = None):
        """Initialize the MainAgent"""
        self.agent_id = agent_id or str(uuid4())
        self.logger = StructuredLogger(
            name=f"orchestration.agents.MainAgent",
            component="MainAgent",
            agent_id=self.agent_id
        )
        
        # Initialize audit trail
        self.audit_trail = get_audit_trail()
        
        # Initialize context storage
        self.context_store = ContextStore()
        
        # Initialize NLP processor
        self.nlp_processor = NLPProcessor()
        
        # Configuration
        self.min_confidence_threshold = 0.5
        self.max_clarification_attempts = 3
        
        self.logger.info("MainAgent initialized", agent_id=self.agent_id)
        self.audit_trail.log_agent_event(
            agent_id=self.agent_id,
            event="MainAgent initialized",
            category="agent_lifecycle",
            severity="info",
            metadata={"min_confidence_threshold": self.min_confidence_threshold}
        )
    
    def process_request(self, request: UserRequest) -> WorkflowInitiation:
        """
        Process a user request and determine if workflow initiation is needed
        
        Args:
            request: The user request to process
            
        Returns:
            WorkflowInitiation: Result indicating whether to proceed with workflow
            
        Raises:
            AgentExecutionError: If request processing fails
        """
        start_time = datetime.now()
        
        try:
            self.logger.info(
                "Processing user request",
                request_id=request.id,
                user_id=request.user_id,
                content_length=len(request.content)
            )
            
            # Get or create conversation context
            context = self._get_or_create_context(request)
            
            # Log request received with full audit trail
            self.audit_trail.log_request_received(request, context)
            
            # Parse the request
            parsing_result = self.nlp_processor.parse_request(request.content)
            
            # Calculate processing duration
            processing_duration_ms = int((datetime.now() - start_time).total_seconds() * 1000)
            
            # Update request with parsed information
            request.intent = parsing_result.intent
            request.confidence = parsing_result.confidence
            request.metadata.update({
                "entities": parsing_result.entities,
                "keywords": parsing_result.keywords,
                "complexity": parsing_result.complexity
            })
            
            # Log the request processing with audit trail
            self.audit_trail.log_request_processing(
                request, parsing_result, processing_duration_ms, context
            )
            
            # Log the request with full context (existing logging)
            self._log_request(request, context, parsing_result)
            
            # Check if clarification is needed
            clarification_needed = (
                parsing_result.requires_clarification or 
                parsing_result.confidence < self.min_confidence_threshold
            )
            
            if clarification_needed:
                workflow_initiation = self._handle_clarification_needed(request, parsing_result, context)
            else:
                # Determine workflow initiation
                workflow_initiation = self._determine_workflow_initiation(request, parsing_result, context)
            
            # Log workflow decision with audit trail
            self.audit_trail.log_workflow_decision(request, workflow_initiation, context)
            
            # Update context with the interaction
            self._update_context_after_processing(context, request, workflow_initiation)
            
            self.logger.info(
                "Request processing completed",
                request_id=request.id,
                should_proceed=workflow_initiation.should_proceed,
                workflow_type=workflow_initiation.workflow_type,
                processing_duration_ms=processing_duration_ms
            )
            
            # Log successful completion
            self.audit_trail.log_agent_event(
                agent_id=self.agent_id,
                event="Request processing completed",
                category="request_processing",
                request_id=request.id,
                user_id=request.user_id,
                severity="info",
                metadata={
                    "processing_duration_ms": processing_duration_ms,
                    "should_proceed": workflow_initiation.should_proceed,
                    "workflow_type": workflow_initiation.workflow_type,
                    "confidence": parsing_result.confidence,
                    "complexity": parsing_result.complexity
                }
            )
            
            return workflow_initiation
            
        except Exception as e:
            # Calculate processing duration for error case
            processing_duration_ms = int((datetime.now() - start_time).total_seconds() * 1000)
            
            self.logger.error(
                "Failed to process request",
                request_id=request.id,
                error=str(e),
                error_type=type(e).__name__,
                processing_duration_ms=processing_duration_ms
            )
            
            # Log error with audit trail
            self.audit_trail.log_error(
                error=e,
                request_id=request.id,
                user_id=request.user_id,
                agent_id=self.agent_id,
                operation="request_processing",
                context={
                    "processing_duration_ms": processing_duration_ms,
                    "content_length": len(request.content)
                }
            )
            
            raise AgentExecutionError(
                f"Failed to process request: {str(e)}",
                agent_id=self.agent_id,
                task_id=request.id,
                execution_phase="request_processing",
                cause=e
            )
    
    def maintain_context(self, conversation_id: str, context: ConversationContext) -> None:
        """
        Maintain conversation context across multiple interactions
        
        Args:
            conversation_id: Unique identifier for the conversation
            context: The conversation context to maintain
        """
        try:
            self.context_store.store_context(context)
            
            self.logger.debug(
                "Context maintained",
                conversation_id=conversation_id,
                interaction_count=context.interaction_count
            )
            
            # Log context maintenance with audit trail
            self.audit_trail.log_agent_event(
                agent_id=self.agent_id,
                event="Context maintained",
                category="context_management",
                user_id=context.user_id,
                severity="debug",
                metadata={
                    "conversation_id": conversation_id,
                    "interaction_count": context.interaction_count,
                    "context_keys_count": len(context.context_data),
                    "session_duration_minutes": int(
                        (context.last_interaction - context.session_start).total_seconds() / 60
                    )
                }
            )
            
        except Exception as e:
            self.logger.error(
                "Failed to maintain context",
                conversation_id=conversation_id,
                error=str(e)
            )
            
            # Log error with audit trail
            self.audit_trail.log_error(
                error=e,
                user_id=context.user_id,
                agent_id=self.agent_id,
                operation="context_maintenance",
                context={"conversation_id": conversation_id}
            )
            
            raise AgentExecutionError(
                f"Failed to maintain context: {str(e)}",
                agent_id=self.agent_id,
                execution_phase="context_maintenance",
                cause=e
            )
    
    def request_clarification(self, ambiguous_request: UserRequest) -> ClarifiedRequest:
        """
        Handle ambiguous requests by requesting clarification
        
        Args:
            ambiguous_request: The ambiguous user request
            
        Returns:
            ClarifiedRequest: Clarified request with additional information
        """
        start_time = datetime.now()
        
        try:
            self.logger.info(
                "Requesting clarification for ambiguous request",
                request_id=ambiguous_request.id,
                confidence=ambiguous_request.confidence
            )
            
            # Log clarification request start
            self.audit_trail.log_agent_event(
                agent_id=self.agent_id,
                event="Clarification requested",
                category="clarification",
                request_id=ambiguous_request.id,
                user_id=ambiguous_request.user_id,
                severity="info",
                metadata={
                    "original_confidence": ambiguous_request.confidence,
                    "content_length": len(ambiguous_request.content)
                }
            )
            
            # Parse the request to get clarification questions
            parsing_result = self.nlp_processor.parse_request(ambiguous_request.content)
            
            # Create clarified request with questions
            clarified_request = ClarifiedRequest(
                original_request=ambiguous_request,
                clarified_content=ambiguous_request.content,
                extracted_requirements=self._extract_requirements_from_parsing(parsing_result),
                identified_constraints=self._extract_constraints_from_parsing(parsing_result),
                suggested_approach=self._suggest_approach_from_intent(parsing_result.intent),
                confidence=parsing_result.confidence
            )
            
            # Calculate processing duration
            processing_duration_ms = int((datetime.now() - start_time).total_seconds() * 1000)
            
            self.logger.info(
                "Clarification request created",
                request_id=ambiguous_request.id,
                requirements_count=len(clarified_request.extracted_requirements),
                constraints_count=len(clarified_request.identified_constraints),
                processing_duration_ms=processing_duration_ms
            )
            
            # Log clarification completion
            self.audit_trail.log_agent_event(
                agent_id=self.agent_id,
                event="Clarification request created",
                category="clarification",
                request_id=ambiguous_request.id,
                user_id=ambiguous_request.user_id,
                severity="info",
                metadata={
                    "processing_duration_ms": processing_duration_ms,
                    "requirements_count": len(clarified_request.extracted_requirements),
                    "constraints_count": len(clarified_request.identified_constraints),
                    "suggested_approach": clarified_request.suggested_approach,
                    "final_confidence": clarified_request.confidence
                }
            )
            
            return clarified_request
            
        except Exception as e:
            processing_duration_ms = int((datetime.now() - start_time).total_seconds() * 1000)
            
            self.logger.error(
                "Failed to request clarification",
                request_id=ambiguous_request.id,
                error=str(e),
                processing_duration_ms=processing_duration_ms
            )
            
            # Log error with audit trail
            self.audit_trail.log_error(
                error=e,
                request_id=ambiguous_request.id,
                user_id=ambiguous_request.user_id,
                agent_id=self.agent_id,
                operation="clarification_request",
                context={"processing_duration_ms": processing_duration_ms}
            )
            
            raise AgentExecutionError(
                f"Failed to request clarification: {str(e)}",
                agent_id=self.agent_id,
                task_id=ambiguous_request.id,
                execution_phase="clarification_request",
                cause=e
            )
    
    def get_context_summary(self, conversation_id: str) -> Optional[Dict[str, Any]]:
        """Get a summary of the conversation context"""
        context = self.context_store.get_context(conversation_id)
        if not context:
            return None
        
        return {
            "conversation_id": context.conversation_id,
            "user_id": context.user_id,
            "session_start": context.session_start.isoformat(),
            "last_interaction": context.last_interaction.isoformat(),
            "interaction_count": context.interaction_count,
            "context_keys": list(context.context_data.keys()),
            "preferences": context.preferences
        }
    
    def get_request_audit_trail(self, request_id: str) -> List[Dict[str, Any]]:
        """
        Get complete audit trail for a specific request
        
        Args:
            request_id: The request ID to get audit trail for
            
        Returns:
            List of audit entries for the request
        """
        try:
            entries = self.audit_trail.get_request_trail(request_id)
            return [entry.to_dict() for entry in entries]
        except Exception as e:
            self.logger.error(
                "Failed to retrieve request audit trail",
                request_id=request_id,
                error=str(e)
            )
            return []
    
    def get_user_activity_summary(self, user_id: str, days: int = 7) -> Dict[str, Any]:
        """
        Get user activity summary for compliance and debugging
        
        Args:
            user_id: The user ID to get activity for
            days: Number of days to look back
            
        Returns:
            Summary of user activity
        """
        try:
            entries = self.audit_trail.get_user_activity(user_id, days)
            
            # Aggregate statistics
            request_count = len([e for e in entries if e.entry_type == "request"])
            processing_count = len([e for e in entries if e.entry_type == "processing"])
            workflow_count = len([e for e in entries if e.entry_type == "workflow"])
            error_count = len([e for e in entries if e.severity == "error"])
            
            # Calculate average processing time
            processing_times = [
                e.processing_duration_ms for e in entries 
                if e.processing_duration_ms is not None
            ]
            avg_processing_time = sum(processing_times) / len(processing_times) if processing_times else 0
            
            return {
                "user_id": user_id,
                "period_days": days,
                "total_entries": len(entries),
                "request_count": request_count,
                "processing_count": processing_count,
                "workflow_count": workflow_count,
                "error_count": error_count,
                "average_processing_time_ms": avg_processing_time,
                "recent_activity": [
                    {
                        "timestamp": entry.timestamp.isoformat(),
                        "action": entry.action,
                        "category": entry.category,
                        "severity": entry.severity
                    }
                    for entry in entries[:10]  # Last 10 activities
                ]
            }
        except Exception as e:
            self.logger.error(
                "Failed to retrieve user activity summary",
                user_id=user_id,
                error=str(e)
            )
            return {
                "user_id": user_id,
                "error": str(e),
                "total_entries": 0
            }
    
    def _get_or_create_context(self, request: UserRequest) -> ConversationContext:
        """Get existing context or create new one"""
        if request.context:
            context = request.context
            self.context_store.store_context(context)
        else:
            # Create new context
            context = ConversationContext(
                user_id=request.user_id,
                session_start=request.timestamp
            )
            request.context = context
            self.context_store.store_context(context)
        
        context.update_interaction()
        return context
    
    def _log_request(self, request: UserRequest, context: ConversationContext, parsing_result: RequestParsingResult):
        """Log request with full context and audit trail"""
        self.logger.info(
            "User request logged",
            request_id=request.id,
            user_id=request.user_id,
            conversation_id=context.conversation_id,
            intent=parsing_result.intent,
            confidence=parsing_result.confidence,
            complexity=parsing_result.complexity,
            entities_count=len(parsing_result.entities),
            keywords_count=len(parsing_result.keywords),
            requires_clarification=parsing_result.requires_clarification,
            timestamp=request.timestamp.isoformat(),
            content_preview=request.content[:100] + "..." if len(request.content) > 100 else request.content
        )
    
    def _handle_clarification_needed(
        self, 
        request: UserRequest, 
        parsing_result: RequestParsingResult, 
        context: ConversationContext
    ) -> WorkflowInitiation:
        """Handle cases where clarification is needed"""
        
        # Check if we've already asked for clarification too many times
        clarification_count = context.context_data.get("clarification_attempts", 0)
        
        if clarification_count >= self.max_clarification_attempts:
            # Proceed with best effort
            self.logger.warning(
                "Maximum clarification attempts reached, proceeding with best effort",
                request_id=request.id,
                clarification_attempts=clarification_count
            )
            
            workflow_initiation = WorkflowInitiation(
                request_id=request.id,
                should_proceed=True,
                workflow_type=self._map_intent_to_workflow_type(parsing_result.intent),
                estimated_complexity=parsing_result.complexity,
                required_clarifications=[],
                suggested_next_steps=["Proceed with available information", "Request additional details during execution"]
            )
        else:
            # Increment clarification attempts
            context.add_context("clarification_attempts", clarification_count + 1)
            
            # Only require clarification if we actually have questions to ask
            clarification_questions = parsing_result.clarification_questions
            if not clarification_questions:
                clarification_questions = ["Please provide more specific details about your request."]
            
            workflow_initiation = WorkflowInitiation(
                request_id=request.id,
                should_proceed=False,
                workflow_type=None,
                estimated_complexity=parsing_result.complexity,
                required_clarifications=clarification_questions,
                suggested_next_steps=["Please provide the requested clarifications", "Resubmit your request with more details"]
            )
        
        # Update context even when clarification is needed
        self._update_context_after_processing(context, request, workflow_initiation)
        
        return workflow_initiation
    
    def _determine_workflow_initiation(
        self, 
        request: UserRequest, 
        parsing_result: RequestParsingResult, 
        context: ConversationContext
    ) -> WorkflowInitiation:
        """Determine if and how to initiate a workflow"""
        
        # Map intent to workflow type
        workflow_type = self._map_intent_to_workflow_type(parsing_result.intent)
        
        # Determine if we should proceed
        should_proceed = (
            parsing_result.confidence >= self.min_confidence_threshold and
            not parsing_result.requires_clarification and
            workflow_type is not None
        )
        
        # Generate suggested next steps
        suggested_next_steps = self._generate_next_steps(parsing_result, context)
        
        return WorkflowInitiation(
            request_id=request.id,
            should_proceed=should_proceed,
            workflow_type=workflow_type,
            estimated_complexity=parsing_result.complexity,
            required_clarifications=[],
            suggested_next_steps=suggested_next_steps
        )
    
    def _update_context_after_processing(
        self, 
        context: ConversationContext, 
        request: UserRequest, 
        workflow_initiation: WorkflowInitiation
    ):
        """Update context after processing a request"""
        context.add_context("last_request_id", request.id)
        context.add_context("last_intent", request.intent)
        context.add_context("last_workflow_type", workflow_initiation.workflow_type)
        context.add_context("last_complexity", workflow_initiation.estimated_complexity)
        
        # Store entities for future reference
        if request.metadata.get("entities"):
            context.add_context("recent_entities", request.metadata["entities"])
        
        # Store keywords for context building
        if request.metadata.get("keywords"):
            existing_keywords = context.context_data.get("accumulated_keywords", [])
            new_keywords = request.metadata["keywords"]
            # Keep last 50 keywords to avoid memory bloat
            all_keywords = (existing_keywords + new_keywords)[-50:]
            context.add_context("accumulated_keywords", all_keywords)
    
    def _map_intent_to_workflow_type(self, intent: str) -> Optional[str]:
        """Map parsed intent to workflow type"""
        intent_mapping = {
            "create_project": "project_creation",
            "analyze_requirements": "requirements_analysis",
            "design_architecture": "architecture_design",
            "implement_feature": "feature_implementation",
            "test_system": "testing_workflow",
            "research_topic": "research_workflow",
            "review_code": "code_review",
            "generate_documentation": "documentation_generation",
            "general_request": "general_workflow"
        }
        
        return intent_mapping.get(intent)
    
    def _generate_next_steps(self, parsing_result: RequestParsingResult, context: ConversationContext) -> List[str]:
        """Generate suggested next steps based on parsing result"""
        steps = []
        
        if parsing_result.intent == "create_project":
            steps.extend([
                "Initialize project structure",
                "Set up development environment",
                "Create initial documentation"
            ])
        elif parsing_result.intent == "analyze_requirements":
            steps.extend([
                "Gather stakeholder requirements",
                "Create user stories",
                "Define acceptance criteria"
            ])
        elif parsing_result.intent == "design_architecture":
            steps.extend([
                "Analyze system requirements",
                "Design component architecture",
                "Create technical specifications"
            ])
        elif parsing_result.intent == "implement_feature":
            steps.extend([
                "Break down feature into tasks",
                "Implement core functionality",
                "Add tests and documentation"
            ])
        else:
            steps.extend([
                "Analyze request requirements",
                "Create execution plan",
                "Begin implementation"
            ])
        
        # Add complexity-specific steps
        if parsing_result.complexity == "high":
            steps.insert(0, "Conduct detailed planning session")
            steps.append("Set up monitoring and quality gates")
        elif parsing_result.complexity == "low":
            steps.insert(0, "Quick feasibility check")
        
        return steps
    
    def _extract_requirements_from_parsing(self, parsing_result: RequestParsingResult) -> List[str]:
        """Extract requirements from parsing result"""
        requirements = []
        
        # Add entity-based requirements
        if "languages" in parsing_result.entities:
            requirements.append(f"Use programming languages: {', '.join(parsing_result.entities['languages'])}")
        
        if "frameworks" in parsing_result.entities:
            requirements.append(f"Use frameworks: {', '.join(parsing_result.entities['frameworks'])}")
        
        if "databases" in parsing_result.entities:
            requirements.append(f"Use databases: {', '.join(parsing_result.entities['databases'])}")
        
        # Add intent-based requirements
        if parsing_result.intent == "create_project":
            requirements.append("Create a new project structure")
            requirements.append("Set up version control")
        elif parsing_result.intent == "implement_feature":
            requirements.append("Implement the requested feature")
            requirements.append("Include appropriate tests")
        
        return requirements
    
    def _extract_constraints_from_parsing(self, parsing_result: RequestParsingResult) -> List[str]:
        """Extract constraints from parsing result"""
        constraints = []
        
        # Add complexity-based constraints
        if parsing_result.complexity == "high":
            constraints.append("High complexity project requiring careful planning")
            constraints.append("May require multiple specialized agents")
        elif parsing_result.complexity == "low":
            constraints.append("Simple project with minimal requirements")
        
        # Add entity-based constraints
        if "numbers" in parsing_result.entities:
            numbers = parsing_result.entities["numbers"]
            if any(n < 10 for n in numbers):
                constraints.append("Time-sensitive project with tight deadlines")
        
        return constraints
    
    def _suggest_approach_from_intent(self, intent: str) -> str:
        """Suggest an approach based on the identified intent"""
        approach_mapping = {
            "create_project": "Use a structured project creation workflow with PM, BA, and SA agents",
            "analyze_requirements": "Deploy BA agent for comprehensive requirements analysis",
            "design_architecture": "Engage SA agent for technical architecture design",
            "implement_feature": "Use implementation agent with appropriate testing support",
            "test_system": "Deploy quality judge and testing agents for comprehensive validation",
            "research_topic": "Utilize research agent with knowledge base integration",
            "review_code": "Engage quality judge agent for code review and analysis",
            "generate_documentation": "Use documentation generation workflow with multiple agent collaboration",
            "general_request": "Analyze request further and deploy appropriate specialized agents"
        }
        
        return approach_mapping.get(intent, "Analyze request and determine optimal agent deployment strategy")