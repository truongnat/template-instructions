#!/usr/bin/env python3
"""
WorkflowEngine Demo

This script demonstrates the WorkflowEngine functionality including:
- Request evaluation and workflow matching
- Pattern matching and ranking algorithms
- Workflow plan generation and prerequisite validation
- Integration with the MainAgent for complete request processing
"""

import sys
import json
from datetime import datetime
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from agentic_sdlc.orchestration.engine.workflow_engine import WorkflowEngine, WorkflowTemplate, WorkflowCategory
from agentic_sdlc.orchestration.agents.main_agent import MainAgent
from agentic_sdlc.orchestration.models import (
    UserRequest, ConversationContext, ClarifiedRequest, OrchestrationPattern, AgentType
)


def create_sample_requests():
    """Create sample user requests for demonstration"""
    
    requests = [
        {
            "content": "Create a new Python web application with Django and user authentication",
            "intent": "create_project",
            "entities": {
                "languages": ["python"],
                "frameworks": ["django"],
                "features": ["authentication"]
            },
            "complexity": "high"
        },
        {
            "content": "Implement a REST API endpoint for user registration",
            "intent": "implement_feature",
            "entities": {
                "languages": ["python"],
                "frameworks": ["django", "rest"],
                "features": ["api", "registration"]
            },
            "complexity": "medium"
        },
        {
            "content": "Research best practices for microservices architecture",
            "intent": "research_topic",
            "entities": {
                "topics": ["microservices", "architecture"],
                "scope": ["best practices"]
            },
            "complexity": "medium"
        },
        {
            "content": "Review the authentication module code for security issues",
            "intent": "review_code",
            "entities": {
                "modules": ["authentication"],
                "focus": ["security"]
            },
            "complexity": "medium"
        },
        {
            "content": "Generate API documentation for the user management system",
            "intent": "generate_documentation",
            "entities": {
                "systems": ["user management"],
                "doc_types": ["api"]
            },
            "complexity": "low"
        }
    ]
    
    user_requests = []
    for i, req_data in enumerate(requests):
        user_request = UserRequest(
            user_id=f"demo_user_{i}",
            content=req_data["content"],
            intent=req_data["intent"],
            confidence=0.85,
            metadata={
                "entities": req_data["entities"],
                "complexity": req_data["complexity"]
            }
        )
        
        clarified_request = ClarifiedRequest(
            original_request=user_request,
            clarified_content=req_data["content"],
            confidence=0.85
        )
        
        user_requests.append(clarified_request)
    
    return user_requests


def demonstrate_workflow_engine():
    """Demonstrate WorkflowEngine functionality"""
    
    print("🚀 WorkflowEngine Demo")
    print("=" * 50)
    
    # Initialize the WorkflowEngine
    print("\n1. Initializing WorkflowEngine...")
    engine = WorkflowEngine()
    
    print(f"   ✓ Engine initialized with ID: {engine.engine_id}")
    print(f"   ✓ Loaded {len(engine.templates)} default workflow templates")
    
    # List available templates
    print("\n2. Available Workflow Templates:")
    templates = engine.list_templates()
    for template in templates:
        print(f"   • {template.name} ({template.category.value})")
        print(f"     Pattern: {template.pattern.value}")
        print(f"     Agents: {[agent.value for agent in template.required_agents]}")
        print(f"     Duration: {template.estimated_duration_hours}h")
        print()
    
    # Create sample requests
    print("3. Processing Sample Requests:")
    print("-" * 30)
    
    sample_requests = create_sample_requests()
    
    for i, request in enumerate(sample_requests, 1):
        print(f"\n📝 Request {i}: {request.original_request.content}")
        print(f"   Intent: {request.original_request.intent}")
        print(f"   Complexity: {request.original_request.metadata.get('complexity')}")
        
        try:
            # Evaluate request against workflows
            matches = engine.evaluate_request(request)
            
            if matches:
                print(f"   ✓ Found {len(matches)} workflow matches")
                
                # Show top 3 matches
                for j, match in enumerate(matches[:3], 1):
                    template = engine.get_template(match.workflow_id)
                    print(f"     {j}. {template.name if template else match.workflow_id}")
                    print(f"        Relevance: {match.relevance_score:.2f}")
                    print(f"        Confidence: {match.confidence:.2f}")
                    print(f"        Duration: {match.estimated_duration}min")
                
                # Select optimal workflow
                plan = engine.select_optimal_workflow(matches)
                print(f"   🎯 Selected: {engine.get_template(matches[0].workflow_id).name}")
                print(f"      Plan ID: {plan.id}")
                print(f"      Agents: {[agent.agent_type.value for agent in plan.agents]}")
                print(f"      Pattern: {plan.pattern.value}")
                
                # Validate prerequisites
                validation = engine.validate_prerequisites(plan)
                if validation.is_valid:
                    print(f"   ✅ Prerequisites validated (setup: {validation.estimated_setup_time}min)")
                else:
                    print(f"   ⚠️  Missing prerequisites: {validation.missing_prerequisites}")
                    if validation.warnings:
                        print(f"      Warnings: {validation.warnings}")
            else:
                print("   ❌ No matching workflows found")
                
        except Exception as e:
            print(f"   ❌ Error processing request: {str(e)}")
    
    # Show engine metrics
    print("\n4. Engine Performance Metrics:")
    print("-" * 30)
    metrics = engine.get_metrics()
    
    print(f"   Total Evaluations: {metrics['total_evaluations']}")
    print(f"   Successful Matches: {metrics['successful_matches']}")
    print(f"   Success Rate: {metrics['success_rate']:.1%}")
    print(f"   Avg Evaluation Time: {metrics['average_evaluation_time_ms']:.1f}ms")
    print(f"   Template Count: {metrics['template_count']}")
    print(f"   Cache Size: {metrics['cache_size']}")


def demonstrate_custom_template():
    """Demonstrate adding custom workflow templates"""
    
    print("\n5. Custom Workflow Template Demo:")
    print("-" * 35)
    
    engine = WorkflowEngine()
    
    # Create a custom template
    custom_template = WorkflowTemplate(
        name="AI Model Training Workflow",
        description="Train and evaluate machine learning models with data preprocessing",
        category=WorkflowCategory.DEVELOPMENT,
        pattern=OrchestrationPattern.PARALLEL_EXECUTION,
        required_agents=[AgentType.RESEARCH, AgentType.IMPLEMENTATION, AgentType.QUALITY_JUDGE],
        optional_agents=[AgentType.BA],
        prerequisites=["training_data", "compute_resources", "model_requirements"],
        estimated_duration_hours=24,
        complexity_levels=["high"],
        intent_keywords=["train", "model", "machine learning", "ai", "ml"],
        entity_requirements={
            "technologies": ["tensorflow", "pytorch", "scikit-learn"],
            "data_types": ["tabular", "image", "text"]
        },
        success_criteria=[
            "Model trained successfully",
            "Performance metrics meet requirements",
            "Model validated on test data",
            "Deployment artifacts created"
        ]
    )
    
    # Add the custom template
    engine.add_template(custom_template)
    print(f"   ✓ Added custom template: {custom_template.name}")
    
    # Test with a relevant request
    ml_request = ClarifiedRequest(
        original_request=UserRequest(
            user_id="ml_user",
            content="Train a machine learning model using TensorFlow for image classification",
            intent="train_model",
            confidence=0.9,
            metadata={
                "entities": {
                    "technologies": ["tensorflow"],
                    "data_types": ["image"],
                    "tasks": ["classification"]
                },
                "complexity": "high"
            }
        ),
        clarified_content="Train a machine learning model using TensorFlow for image classification",
        confidence=0.9
    )
    
    print(f"   📝 Testing with ML request: {ml_request.original_request.content}")
    
    matches = engine.evaluate_request(ml_request)
    if matches:
        top_match = matches[0]
        template = engine.get_template(top_match.workflow_id)
        print(f"   🎯 Best match: {template.name}")
        print(f"      Relevance: {top_match.relevance_score:.2f}")
        print(f"      Confidence: {top_match.confidence:.2f}")
        
        if template.id == custom_template.id:
            print("   ✅ Custom template was selected as the best match!")
        else:
            print("   ℹ️  Different template was selected")
    else:
        print("   ❌ No matches found")


def demonstrate_integration_with_main_agent():
    """Demonstrate integration between MainAgent and WorkflowEngine"""
    
    print("\n6. MainAgent + WorkflowEngine Integration:")
    print("-" * 40)
    
    # Initialize MainAgent
    main_agent = MainAgent()
    print(f"   ✓ MainAgent initialized: {main_agent.agent_id}")
    
    # Create a user request
    user_request = UserRequest(
        user_id="integration_user",
        content="I want to build a scalable web API for a social media platform with real-time features",
        timestamp=datetime.now()
    )
    
    print(f"   📝 User Request: {user_request.content}")
    
    try:
        # Process request through MainAgent
        workflow_initiation = main_agent.process_request(user_request)
        
        print(f"   🔍 MainAgent Analysis:")
        print(f"      Should Proceed: {workflow_initiation.should_proceed}")
        print(f"      Workflow Type: {workflow_initiation.workflow_type}")
        print(f"      Complexity: {workflow_initiation.estimated_complexity}")
        
        if workflow_initiation.required_clarifications:
            print(f"      Clarifications: {workflow_initiation.required_clarifications}")
        
        if workflow_initiation.suggested_next_steps:
            print(f"      Next Steps:")
            for step in workflow_initiation.suggested_next_steps:
                print(f"        • {step}")
        
        # If MainAgent suggests proceeding, we could integrate with WorkflowEngine here
        if workflow_initiation.should_proceed:
            print("   ✅ Ready for WorkflowEngine integration")
        else:
            print("   ⚠️  Requires clarification before workflow execution")
            
    except Exception as e:
        print(f"   ❌ Error in MainAgent processing: {str(e)}")


def main():
    """Main demo function"""
    
    try:
        demonstrate_workflow_engine()
        demonstrate_custom_template()
        demonstrate_integration_with_main_agent()
        
        print("\n" + "=" * 50)
        print("🎉 WorkflowEngine Demo Complete!")
        print("\nKey Features Demonstrated:")
        print("• Workflow template matching and ranking")
        print("• Pattern-based orchestration planning")
        print("• Prerequisite validation")
        print("• Custom template creation")
        print("• Performance metrics tracking")
        print("• MainAgent integration")
        
    except Exception as e:
        print(f"\n❌ Demo failed with error: {str(e)}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())