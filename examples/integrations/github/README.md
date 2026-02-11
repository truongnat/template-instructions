# GitHub Integration Example

This example demonstrates how to integrate SDLC Kit with GitHub for automated code review, issue triage, and repository management. It shows how agents can interact with GitHub's API to streamline development workflows.

## Overview

This integration enables:
- **Automated Code Review**: AI-powered review of pull requests
- **Issue Triage**: Automatic categorization and prioritization of issues
- **Documentation Updates**: Automated documentation generation and updates
- **Workflow Automation**: Trigger workflows based on GitHub events

## Features

### 1. Automated Pull Request Review
- Fetch open pull requests with specific labels
- Analyze code changes for quality, security, and best practices
- Post constructive review comments
- Suggest improvements and identify issues

### 2. Issue Management
- Automatically triage new issues
- Categorize by type (bug, feature, documentation, etc.)
- Assign priority based on keywords and context
- Apply appropriate labels

### 3. Documentation Automation
- Generate documentation from code changes
- Update README and API docs automatically
- Ensure documentation stays in sync with code

### 4. Workflow Triggers
- Respond to GitHub webhooks
- Trigger workflows on PR creation, issue updates, etc.
- Integrate with CI/CD pipelines

## Prerequisites

### 1. GitHub Personal Access Token

Create a GitHub Personal Access Token with the following scopes:
- `repo` - Full control of private repositories
- `read:org` - Read org and team membership
- `write:discussion` - Write access to discussions

**Steps to create token**:
1. Go to GitHub Settings → Developer settings → Personal access tokens
2. Click "Generate new token (classic)"
3. Select the required scopes
4. Copy the token and save it securely

### 2. Environment Configuration

Set up your environment variables:

```bash
# .env file
GITHUB_TOKEN=ghp_your_token_here
GITHUB_WEBHOOK_SECRET=your_webhook_secret
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/YOUR/WEBHOOK/URL
```

### 3. SDLC Kit Installation

```bash
pip install -r requirements.txt
```

## Configuration

### Repository Settings

Edit `config.yaml` to configure your repository:

```yaml
github:
  repository:
    owner: "your-organization"
    name: "your-repository"
    default_branch: "main"
```

### Review Criteria

Customize review criteria in `config.yaml`:

```yaml
pull_requests:
  criteria:
    min_approvals: 1
    require_tests: true
    require_documentation: true
    check_security: true
```

### Issue Triage Rules

Configure automatic issue triage:

```yaml
issues:
  priority_rules:
    critical:
      keywords: ["crash", "security", "data-loss"]
      labels: ["critical", "urgent"]
```

## Running the Integration

### Method 1: Manual Workflow Execution

```bash
# Review all open pull requests
python -m agentic_sdlc.cli workflow run \
  examples/integrations/github/workflow.yaml \
  --config examples/integrations/github/config.yaml

# Review specific PR
python -m agentic_sdlc.cli workflow run \
  examples/integrations/github/workflow.yaml \
  --config examples/integrations/github/config.yaml \
  --pr-number 123
```

### Method 2: Webhook Integration

Set up a webhook endpoint to trigger workflows automatically:

```python
# webhook_server.py
from flask import Flask, request, jsonify
from agentic_sdlc.orchestration.engine.workflow_engine import WorkflowEngine
import yaml
import hmac
import hashlib

app = Flask(__name__)

def verify_signature(payload, signature, secret):
    """Verify GitHub webhook signature"""
    expected = 'sha256=' + hmac.new(
        secret.encode(),
        payload,
        hashlib.sha256
    ).hexdigest()
    return hmac.compare_digest(expected, signature)

@app.route('/webhook/github', methods=['POST'])
def github_webhook():
    # Verify webhook signature
    signature = request.headers.get('X-Hub-Signature-256')
    if not verify_signature(request.data, signature, WEBHOOK_SECRET):
        return jsonify({'error': 'Invalid signature'}), 401
    
    # Parse webhook payload
    event = request.headers.get('X-GitHub-Event')
    payload = request.json
    
    # Trigger appropriate workflow
    if event == 'pull_request':
        if payload['action'] in ['opened', 'synchronize']:
            # Load workflow
            with open('examples/integrations/github/workflow.yaml') as f:
                workflow_config = yaml.safe_load(f)
            
            # Execute workflow
            engine = WorkflowEngine(workflow_config)
            result = engine.execute(context={'pr': payload['pull_request']})
            
            return jsonify({'status': 'success', 'workflow_id': result.id})
    
    return jsonify({'status': 'ignored'})

if __name__ == '__main__':
    app.run(port=5000)
```

Run the webhook server:

```bash
python webhook_server.py
```

### Method 3: Scheduled Execution

Use cron or a task scheduler to run reviews periodically:

```bash
# crontab entry - run every hour
0 * * * * cd /path/to/sdlc-kit && python -m agentic_sdlc.cli workflow run examples/integrations/github/workflow.yaml
```

## Usage Examples

### Example 1: Review Open Pull Requests

```python
from agentic_sdlc.orchestration.engine.workflow_engine import WorkflowEngine
import yaml

# Load configuration
with open('examples/integrations/github/workflow.yaml') as f:
    workflow_config = yaml.safe_load(f)

with open('examples/integrations/github/config.yaml') as f:
    github_config = yaml.safe_load(f)

# Execute workflow
engine = WorkflowEngine(workflow_config, config=github_config)
result = engine.execute()

print(f"Reviewed {result.prs_reviewed} pull requests")
print(f"Posted {result.comments_posted} comments")
```

### Example 2: Triage New Issues

```python
from agentic_sdlc.integrations.github import GitHubClient
from agentic_sdlc.orchestration.agents import IssueTriagerAgent

# Initialize GitHub client
client = GitHubClient(token=GITHUB_TOKEN)

# Get new issues
issues = client.get_issues(state='open', labels=['needs-triage'])

# Initialize triager agent
triager = IssueTriagerAgent()

# Triage each issue
for issue in issues:
    result = triager.triage(issue)
    
    # Apply labels
    client.add_labels(issue.number, result.labels)
    
    # Add comment
    if result.comment:
        client.create_comment(issue.number, result.comment)
    
    print(f"Triaged issue #{issue.number}: {result.category} - {result.priority}")
```

### Example 3: Automated Documentation Updates

```python
from agentic_sdlc.integrations.github import GitHubClient
from agentic_sdlc.orchestration.agents import DocumentationAgent

client = GitHubClient(token=GITHUB_TOKEN)
doc_agent = DocumentationAgent()

# Get recent code changes
commits = client.get_commits(since='2024-01-01')

# Generate documentation updates
updates = doc_agent.generate_updates(commits)

# Create PR with documentation updates
if updates:
    branch = client.create_branch('docs/auto-update')
    
    for file_path, content in updates.items():
        client.update_file(branch, file_path, content)
    
    pr = client.create_pull_request(
        title='docs: Automated documentation updates',
        body='This PR contains automated documentation updates based on recent code changes.',
        head=branch,
        base='main'
    )
    
    print(f"Created PR #{pr.number} with documentation updates")
```

## Workflow Tasks Explained

### Task 1: Fetch Pull Requests
Retrieves open pull requests that need review based on labels and filters.

**Configuration**:
```yaml
github_config:
  repository: "owner/repo"
  state: "open"
  labels: ["needs-review"]
```

### Task 2: Review Code Changes
Analyzes code changes using AI agents to identify issues and suggest improvements.

**Review Criteria**:
- Code quality and style
- Security vulnerabilities
- Test coverage
- Documentation completeness

### Task 3: Post Review Comments
Posts constructive feedback as PR comments.

**Comment Types**:
- Approval comments
- Change requests
- Suggestions
- Questions

### Task 4: Triage Issues
Automatically categorizes and prioritizes new issues.

**Triage Process**:
1. Analyze issue title and description
2. Identify issue type (bug, feature, etc.)
3. Assign priority based on keywords
4. Apply appropriate labels
5. Suggest assignees

### Task 5: Update Documentation
Generates and updates documentation based on code changes.

**Documentation Types**:
- API documentation
- README updates
- Code comments
- Architecture diagrams

## Customization

### Custom Review Rules

Add custom review rules in your agent configuration:

```python
# custom_reviewer.py
from agentic_sdlc.orchestration.agents import CodeReviewAgent

class CustomReviewer(CodeReviewAgent):
    def review_rules(self):
        return [
            self.check_naming_conventions,
            self.check_error_handling,
            self.check_test_coverage,
            self.check_security_patterns,
            # Add your custom rules
            self.check_company_standards,
        ]
    
    def check_company_standards(self, code):
        """Custom rule for company-specific standards"""
        issues = []
        # Your custom logic here
        return issues
```

### Custom Issue Labels

Configure custom label mappings:

```yaml
issues:
  labels:
    bug: ["bug", "defect", "error"]
    feature: ["enhancement", "feature-request", "new-feature"]
    performance: ["performance", "optimization", "slow"]
    # Add your custom labels
    technical-debt: ["tech-debt", "refactor", "cleanup"]
```

### Custom Notifications

Add custom notification handlers:

```python
# custom_notifier.py
from agentic_sdlc.integrations.notifications import NotificationHandler

class CustomNotifier(NotificationHandler):
    def send(self, event, data):
        if event == 'pr_reviewed':
            # Send to your custom notification system
            self.send_to_teams(data)
        elif event == 'issue_triaged':
            self.send_to_jira(data)
```

## Best Practices

1. **Rate Limiting**: Respect GitHub's API rate limits (5000 requests/hour for authenticated requests)
2. **Webhook Security**: Always verify webhook signatures
3. **Token Security**: Store tokens securely, never commit to repository
4. **Error Handling**: Implement retry logic for transient failures
5. **Logging**: Enable detailed logging for debugging
6. **Testing**: Test integration in a sandbox repository first
7. **Monitoring**: Monitor API usage and workflow execution

## Troubleshooting

### Authentication Errors

**Problem**: `401 Unauthorized` errors

**Solutions**:
- Verify `GITHUB_TOKEN` is set correctly
- Check token has required scopes
- Ensure token hasn't expired
- Regenerate token if necessary

### Rate Limit Exceeded

**Problem**: `403 Rate limit exceeded` errors

**Solutions**:
- Implement exponential backoff
- Cache API responses
- Reduce polling frequency
- Use conditional requests with ETags

### Webhook Not Triggering

**Problem**: Workflows not triggered by webhooks

**Solutions**:
- Verify webhook URL is accessible
- Check webhook secret matches
- Review webhook event types
- Check server logs for errors

### Review Comments Not Posted

**Problem**: Agent reviews but comments don't appear

**Solutions**:
- Verify token has `write` permissions
- Check PR is not locked
- Ensure comment format is valid
- Review API response for errors

## Security Considerations

1. **Token Storage**: Use environment variables or secret management systems
2. **Webhook Signatures**: Always verify webhook signatures
3. **Input Validation**: Validate all data from GitHub API
4. **Least Privilege**: Use tokens with minimum required scopes
5. **Audit Logging**: Log all API interactions for security audits
6. **Secret Scanning**: Enable GitHub secret scanning
7. **Dependency Updates**: Keep dependencies up to date

## Performance Optimization

### Caching

Enable caching to reduce API calls:

```python
from agentic_sdlc.integrations.github import GitHubClient

client = GitHubClient(
    token=GITHUB_TOKEN,
    cache_enabled=True,
    cache_ttl=300  # 5 minutes
)
```

### Parallel Processing

Process multiple PRs in parallel:

```python
from concurrent.futures import ThreadPoolExecutor

def review_pr(pr_number):
    # Review logic here
    pass

with ThreadPoolExecutor(max_workers=5) as executor:
    executor.map(review_pr, pr_numbers)
```

### Conditional Requests

Use ETags to avoid unnecessary data transfer:

```python
response = client.get_pull_request(
    pr_number,
    etag=cached_etag
)

if response.status_code == 304:
    # Use cached data
    pass
```

## Related Examples

- **Basic Workflow**: `examples/basic-workflow/` - Simple workflow basics
- **Multi-Agent Workflow**: `examples/multi-agent-workflow/` - Agent collaboration
- **Slack Integration**: `examples/integrations/slack/` - Slack notifications

## Additional Resources

- [GitHub API Documentation](https://docs.github.com/en/rest)
- [GitHub Webhooks Guide](https://docs.github.com/en/webhooks)
- [SDLC Kit Integration Guide](../../docs/INTEGRATIONS.md)
- [Security Best Practices](../../docs/SECURITY.md)

## Support

For issues or questions:
- Check [Troubleshooting Guide](../../docs/TROUBLESHOOTING.md)
- Review [GitHub Issues](https://github.com/your-org/sdlc-kit/issues)
- Join our community discussions

---

**Automate your GitHub workflows!** 🚀
