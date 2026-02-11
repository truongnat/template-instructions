"""
Ví Dụ 11: External Integrations (Tích Hợp External Tools)

Setup Instructions:
1. Cài đặt: pip install agentic-sdlc requests
2. Cấu hình API tokens cho GitHub, Slack, Jira
3. Chạy: python 11-integration.py

Dependencies:
- agentic-sdlc>=3.0.0
- requests
- PyGithub
- slack-sdk

Expected Output:
- Tích hợp với GitHub API
- Tích hợp với Slack
- Tích hợp với Jira
- Webhook handling
"""

import os
import requests
from dotenv import load_dotenv

load_dotenv()


def github_integration():
    """Tích hợp với GitHub."""
    from github import Github
    
    # Initialize GitHub client
    g = Github(os.getenv("GITHUB_TOKEN"))
    
    # Get repository
    repo = g.get_repo("user/repo")
    
    print("✓ GitHub integration")
    print(f"  Repository: {repo.full_name}")
    print(f"  Stars: {repo.stargazers_count}")
    
    # Create issue
    issue = repo.create_issue(
        title="Automated issue from Agentic SDLC",
        body="This issue was created by an agent",
        labels=["automated", "agent-created"]
    )
    
    print(f"  ✓ Created issue #{issue.number}")
    
    # Create pull request
    # pr = repo.create_pull(
    #     title="Automated PR",
    #     body="Changes from agent",
    #     head="feature-branch",
    #     base="main"
    # )
    
    return repo


def slack_integration():
    """Tích hợp với Slack."""
    from slack_sdk import WebClient
    from slack_sdk.errors import SlackApiError
    
    client = WebClient(token=os.getenv("SLACK_BOT_TOKEN"))
    
    print("\n✓ Slack integration")
    
    try:
        # Post message
        response = client.chat_postMessage(
            channel="#general",
            text="Hello from Agentic SDLC agent!",
            blocks=[
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": "*Agent Notification*\nTask completed successfully!"
                    }
                }
            ]
        )
        
        print(f"  ✓ Message sent to {response['channel']}")
        
        # Upload file
        # response = client.files_upload(
        #     channels="#general",
        #     file="report.pdf",
        #     title="Agent Report"
        # )
        
    except SlackApiError as e:
        print(f"  ✗ Error: {e.response['error']}")
    
    return client


def jira_integration():
    """Tích hợp với Jira."""
    from jira import JIRA
    
    # Initialize Jira client
    jira = JIRA(
        server=os.getenv("JIRA_SERVER"),
        basic_auth=(
            os.getenv("JIRA_EMAIL"),
            os.getenv("JIRA_API_TOKEN")
        )
    )
    
    print("\n✓ Jira integration")
    
    # Create issue
    issue = jira.create_issue(
        project="PROJ",
        summary="Automated task from agent",
        description="This task was created by Agentic SDLC agent",
        issuetype={"name": "Task"}
    )
    
    print(f"  ✓ Created issue: {issue.key}")
    
    # Add comment
    jira.add_comment(issue, "Agent is working on this task")
    
    # Transition issue
    # jira.transition_issue(issue, "In Progress")
    
    return jira


def webhook_handler():
    """Handle webhooks from external services."""
    from flask import Flask, request, jsonify
    
    app = Flask(__name__)
    
    @app.route('/webhook/github', methods=['POST'])
    def github_webhook():
        """Handle GitHub webhook."""
        data = request.json
        event = request.headers.get('X-GitHub-Event')
        
        print(f"  Received GitHub event: {event}")
        
        if event == 'push':
            # Handle push event
            commits = data.get('commits', [])
            print(f"  Push with {len(commits)} commits")
        
        elif event == 'pull_request':
            # Handle PR event
            action = data.get('action')
            pr_number = data['pull_request']['number']
            print(f"  PR #{pr_number} {action}")
        
        return jsonify({"status": "received"})
    
    @app.route('/webhook/slack', methods=['POST'])
    def slack_webhook():
        """Handle Slack webhook."""
        data = request.json
        
        if data.get('type') == 'url_verification':
            # Respond to Slack verification
            return jsonify({"challenge": data['challenge']})
        
        # Handle event
        event = data.get('event', {})
        print(f"  Received Slack event: {event.get('type')}")
        
        return jsonify({"status": "received"})
    
    print("\n✓ Webhook handlers configured")
    print("  Endpoints:")
    print("    - POST /webhook/github")
    print("    - POST /webhook/slack")
    
    return app


def api_integration_workflow():
    """Workflow tích hợp nhiều APIs."""
    from agentic_sdlc.orchestration.workflow import WorkflowBuilder, WorkflowStep
    
    builder = WorkflowBuilder(name="api-integration-workflow")
    
    # Step 1: Fetch data from GitHub
    builder.add_step(WorkflowStep(
        name="fetch_github_issues",
        action="github_api",
        description="Fetch issues from GitHub",
        parameters={
            "repo": "user/repo",
            "state": "open",
            "labels": ["bug"]
        }
    ))
    
    # Step 2: Analyze issues
    builder.add_step(WorkflowStep(
        name="analyze_issues",
        action="analyze",
        description="Analyze issues",
        parameters={"issues": "{{fetch_github_issues.output}}"},
        dependencies=["fetch_github_issues"]
    ))
    
    # Step 3: Create Jira tickets
    builder.add_step(WorkflowStep(
        name="create_jira_tickets",
        action="jira_api",
        description="Create Jira tickets",
        parameters={
            "project": "PROJ",
            "issues": "{{analyze_issues.output}}"
        },
        dependencies=["analyze_issues"]
    ))
    
    # Step 4: Notify on Slack
    builder.add_step(WorkflowStep(
        name="notify_slack",
        action="slack_api",
        description="Send Slack notification",
        parameters={
            "channel": "#dev-team",
            "message": "Created {{create_jira_tickets.count}} Jira tickets"
        },
        dependencies=["create_jira_tickets"]
    ))
    
    workflow = builder.build()
    
    print("\n✓ API integration workflow")
    print("  Flow: GitHub -> Analyze -> Jira -> Slack")
    
    return workflow


if __name__ == "__main__":
    print("=" * 60)
    print("VÍ DỤ: EXTERNAL INTEGRATIONS")
    print("=" * 60)
    
    github_integration()
    slack_integration()
    jira_integration()
    webhook_handler()
    api_integration_workflow()
    
    print("\n" + "=" * 60)
    print("✓ Hoàn thành!")
    print("=" * 60)
