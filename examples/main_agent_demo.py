#!/usr/bin/env python3
"""
MainAgent Demonstration Script

This script demonstrates the capabilities of the MainAgent class including:
- Natural language request parsing
- Intent detection and entity extraction
- Conversation context management
- Ambiguous request handling with clarification
"""

import sys
import os

# Add the project root to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from agentic_sdlc.orchestration import MainAgent, UserRequest
from datetime import datetime


def demo_request_processing():
    """Demonstrate request processing capabilities"""
    print("=" * 60)
    print("MainAgent Request Processing Demo")
    print("=" * 60)
    
    # Initialize the MainAgent
    agent = MainAgent()
    
    # Test cases with different types of requests
    test_requests = [
        "Create a new Python web application with Django framework",
        "Design a scalable microservices architecture for an enterprise e-commerce platform using Java Spring Boot, PostgreSQL, and AWS",
        "I need something for my project, maybe some kind of system",
        "Implement user authentication with JWT tokens and password hashing",
        "Research the latest trends in machine learning for natural language processing",
        "Review the code quality and suggest improvements"
    ]
    
    for i, content in enumerate(test_requests, 1):
        print(f"\n--- Test Request {i} ---")
        print(f"Request: {content}")
        
        # Create user request
        request = UserRequest(
            user_id="demo_user",
            content=content,
            timestamp=datetime.now()
        )
        
        try:
            # Process the request
            result = agent.process_request(request)
            
            print(f"Intent: {request.intent}")
            print(f"Confidence: {request.confidence:.2f}")
            print(f"Complexity: {request.metadata.get('complexity', 'unknown')}")
            print(f"Should Proceed: {result.should_proceed}")
            print(f"Workflow Type: {result.workflow_type}")
            
            # Show extracted entities
            entities = request.metadata.get('entities', {})
            if entities:
                print("Extracted Entities:")
                for category, items in entities.items():
                    print(f"  {category}: {items}")
            
            # Show keywords
            keywords = request.metadata.get('keywords', [])
            if keywords:
                print(f"Keywords: {', '.join(keywords[:10])}")  # Show first 10 keywords
            
            # Show clarifications if needed
            if result.required_clarifications:
                print("Required Clarifications:")
                for clarification in result.required_clarifications:
                    print(f"  - {clarification}")
            
            # Show suggested next steps
            if result.suggested_next_steps:
                print("Suggested Next Steps:")
                for step in result.suggested_next_steps[:3]:  # Show first 3 steps
                    print(f"  - {step}")
                    
        except Exception as e:
            print(f"Error processing request: {e}")
        
        print("-" * 40)


def demo_context_management():
    """Demonstrate conversation context management"""
    print("\n" + "=" * 60)
    print("MainAgent Context Management Demo")
    print("=" * 60)
    
    agent = MainAgent()
    
    # Simulate a conversation with multiple requests
    conversation_requests = [
        "Create a Python project",
        "Add authentication to the project",
        "Include a REST API",
        "Add unit tests for the authentication"
    ]
    
    context = None
    
    for i, content in enumerate(conversation_requests, 1):
        print(f"\n--- Conversation Turn {i} ---")
        print(f"Request: {content}")
        
        # Create request with existing context (if any)
        request = UserRequest(
            user_id="conversation_user",
            content=content,
            context=context
        )
        
        # Process the request
        result = agent.process_request(request)
        
        # Update context for next request
        context = request.context
        
        print(f"Intent: {request.intent}")
        print(f"Confidence: {request.confidence:.2f}")
        print(f"Interaction Count: {context.interaction_count}")
        print(f"Context Keys: {list(context.context_data.keys())}")
        
        # Show accumulated keywords
        accumulated_keywords = context.context_data.get("accumulated_keywords", [])
        if accumulated_keywords:
            print(f"Accumulated Keywords: {', '.join(accumulated_keywords[-10:])}")  # Last 10 keywords
        
        print("-" * 40)


def demo_clarification_handling():
    """Demonstrate ambiguous request clarification"""
    print("\n" + "=" * 60)
    print("MainAgent Clarification Handling Demo")
    print("=" * 60)
    
    agent = MainAgent()
    
    # Test with increasingly ambiguous requests
    ambiguous_requests = [
        "I need something",
        "Maybe create some kind of system",
        "Do something with the thing",
        "Help me with my project"
    ]
    
    for i, content in enumerate(ambiguous_requests, 1):
        print(f"\n--- Ambiguous Request {i} ---")
        print(f"Request: {content}")
        
        request = UserRequest(
            user_id="clarification_user",
            content=content
        )
        
        # Process the request
        result = agent.process_request(request)
        
        print(f"Intent: {request.intent}")
        print(f"Confidence: {request.confidence:.2f}")
        print(f"Requires Clarification: {not result.should_proceed}")
        
        if result.required_clarifications:
            print("Clarification Questions:")
            for question in result.required_clarifications:
                print(f"  - {question}")
        
        # Demonstrate clarification request
        if not result.should_proceed:
            clarified = agent.request_clarification(request)
            print(f"Suggested Approach: {clarified.suggested_approach}")
        
        print("-" * 40)


if __name__ == "__main__":
    print("MainAgent Demonstration")
    print("This demo shows the capabilities of the MainAgent class")
    
    try:
        demo_request_processing()
        demo_context_management()
        demo_clarification_handling()
        
        print("\n" + "=" * 60)
        print("Demo completed successfully!")
        print("=" * 60)
        
    except Exception as e:
        print(f"Demo failed with error: {e}")
        import traceback
        traceback.print_exc()