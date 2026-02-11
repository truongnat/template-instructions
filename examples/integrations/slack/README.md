# Slack Integration Example

This example demonstrates how to integrate SDLC Kit with Slack for real-time notifications, alerts, and team collaboration. It shows how to send workflow updates, status reports, and alerts to Slack channels automatically.

## Overview

This integration enables:
- **Workflow Notifications**: Real-time updates on workflow execution
- **Status Reports**: Automated daily and weekly reports
- **Alert System**: Critical alerts for errors and failures
- **Interactive Messages**: Buttons and actions for workflow control
- **Thread Management**: Organized conversations using threads

## Features

### 1. Workflow Notifications
- Start notifications when workflows begin
- Progress updates during execution
- Completion notifications with summary
- Error alerts for failures

### 2. Status Reports
- Daily workflow execution summaries
- Weekly performance reports
- Success rate tracking
- Error analysis and trends

### 3. Alert System
- Critical alerts for workflow failures
- Task timeout warnings
- Error notifications with details
- Configurable severity levels

### 4. Interactive Features
- Approve/reject buttons for workflows
- View details links
- Slash commands for workflow control
- Thread-based discussions

## Prerequisites

### 1. Slack Workspace Setup

You need a Slack workspace with appropriate permissions to:
- Create incoming webhooks
- Install Slack apps
- Post to channels

### 2. Slack App Configuration

**Option A: Incoming Webhooks (Simple)**

1. Go to https://api.slack.com/apps
2. Create a new app or select existing
3. Enable "Incoming Webhooks"
4. Add webhook to your workspace
5. Copy the webhook URL

**Option B: Bot Token (Advanced)**

1. Go to https://api.slack.com/apps
2. Create a new app
3. Add Bot Token Scopes:
   - `chat:write` - Send messages
   - `chat:write.public` - Send to public channels
   - `files:write` - Upload files
   - `reactions:write` - Add reactions
4. Install app to workspace
5. Copy the Bot User OAuth Token

### 3. Environment Configuration

Set up your environment variables:

```bash
# .env file

# Simple webhook (recommended for basic notifications)
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/YOUR/WEBHOOK/URL

# Bot token (for advanced features)
SLACK_BOT_TOKEN=xoxb-your-bot-token-here

# Optional: Slack signing secret for interactive features
SLACK_SIGNING_SECRET=your-signing-secret
```

### 4. SDLC Kit Installation

```bash
pip install -r requirements.txt
```

## Configuration

### Channel Setup

Edit `config.yaml` to configure your channels:

```yaml
slack:
  channels:
    notifications: "#dev-notifications"
    alerts: "#dev-alerts"
    status: "#dev-status"
    reports: "#dev-reports"
```

### Notification Settings

Customize which notifications to send:

```yaml
notifications:
  enabled:
    workflow_start: true
    workflow_complete: true
    workflow_error: true
    task_complete: false  # Disable noisy notifications
    task_error: true
```

### Quiet Hours

Configure quiet hours to avoid notifications during off-hours:

```yaml
quiet_hours:
  enabled: true
  start: "22:00"  # 10 PM
  end: "08:00"    # 8 AM
  timezone: "America/New_York"
  exceptions:
    - "critical_alert"  # Always send critical alerts
```

## Running the Integration

### Method 1: Standalone Workflow

Run the Slack integration workflow:

```bash
python -m agentic_sdlc.cli workflow run \
  examples/integrations/slack/workflow.yaml \
  --config examples/integrations/slack/config.yaml
```

### Method 2: Integrate with Existing Workflows

Add Slack notifications to any workflow:

```python
from agentic_sdlc.integrations.slack import SlackNotifier
from agentic_sdlc.orchestration.engine.workflow_engine import WorkflowEngine

# Initialize Slack notifier
notifier = SlackNotifier(webhook_url=SLACK_WEBHOOK_URL)

# Create workflow engine with Slack integration
engine = WorkflowEngine(
    workflow_config,
    notifiers=[notifier]
)

# Workflow events will automatically send Slack notifications
result = engine.execute()
```

### Method 3: Manual Notifications

Send custom notifications:

```python
from agentic_sdlc.integrations.slack import SlackClient

client = SlackClient(webhook_url=SLACK_WEBHOOK_URL)

# Send simple message
client.send_message(
    channel="#dev-notifications",
    text="Deployment completed successfully! :rocket:"
)

# Send rich message with blocks
client.send_blocks(
    channel="#dev-status",
    blocks=[
        {
            "type": "header",
            "text": {
                "type": "plain_text",
                "text": "Workflow Status Update"
            }
        },
        {
            "type": "section",
            "fields": [
                {"type": "mrkdwn", "text": "*Status:*\nCompleted"},
                {"type": "mrkdwn", "text": "*Duration:*\n5m 32s"}
            ]
        }
    ]
)
```

## Usage Examples

### Example 1: Workflow Start Notification

```python
from agentic_sdlc.integrations.slack import SlackNotifier

notifier = SlackNotifier(webhook_url=SLACK_WEBHOOK_URL)

# Send workflow start notification
notifier.notify_workflow_start(
    workflow_name="data-pipeline",
    workflow_version="1.0.0",
    started_by="john.doe",
    channel="#dev-notifications"
)
```

Output in Slack:
```
🚀 Workflow Started
Name: data-pipeline
Version: 1.0.0
Started by: john.doe
Time: 2024-01-15 10:30:00
```

### Example 2: Error Alert

```python
# Send critical error alert
notifier.send_alert(
    severity="critical",
    message="Workflow failed: data-pipeline",
    details={
        "error": "Database connection timeout",
        "task": "load-data",
        "timestamp": "2024-01-15 10:35:00"
    },
    mentions=["@oncall", "@team-lead"],
    channel="#dev-alerts"
)
```

Output in Slack:
```
🚨 ALERT
Severity: critical
Message: Workflow failed: data-pipeline
Details:
  • Error: Database connection timeout
  • Task: load-data
  • Timestamp: 2024-01-15 10:35:00

@oncall @team-lead
```

### Example 3: Status Report

```python
# Generate and send daily report
from agentic_sdlc.integrations.slack import ReportGenerator

generator = ReportGenerator()
report = generator.generate_daily_report()

notifier.send_report(
    report=report,
    channel="#dev-reports"
)
```

Output in Slack:
```
📊 Daily Workflow Report - January 15, 2024

Workflows Executed: 24
Success Rate: 91.7% (22/24)
Average Duration: 8m 45s
Errors: 2

Top Failures:
1. data-pipeline (timeout)
2. ml-training (out of memory)

Recommendations:
• Increase timeout for data-pipeline
• Optimize memory usage in ml-training
```

### Example 4: Interactive Approval

```python
# Send approval request with buttons
notifier.send_approval_request(
    workflow_name="production-deployment",
    details={
        "version": "2.1.0",
        "changes": "Bug fixes and performance improvements",
        "risk_level": "low"
    },
    approvers=["@team-lead", "@devops"],
    channel="#dev-approvals"
)
```

Output in Slack:
```
🔔 Approval Required: production-deployment

Version: 2.1.0
Changes: Bug fixes and performance improvements
Risk Level: low

@team-lead @devops

[Approve] [Reject] [View Details]
```

## Workflow Tasks Explained

### Task 1: Workflow Started Notification
Sends a notification when the workflow begins execution.

### Task 2: Generate Status Report
Collects workflow metrics and generates a status report.

### Task 3: Send Status Update
Posts the status report to the configured Slack channel.

### Task 4: Check for Errors
Validates workflow execution and checks for errors.

### Task 5: Send Alert if Errors
Sends critical alerts if errors are detected.

### Task 6: Workflow Completed Notification
Sends a completion notification with summary.

## Message Formatting

### Simple Text Messages

```python
client.send_message(
    channel="#dev-notifications",
    text="Simple text message"
)
```

### Rich Messages with Blocks

```python
client.send_blocks(
    channel="#dev-status",
    blocks=[
        {
            "type": "header",
            "text": {"type": "plain_text", "text": "Header"}
        },
        {
            "type": "section",
            "text": {"type": "mrkdwn", "text": "*Bold* and _italic_"}
        },
        {
            "type": "divider"
        },
        {
            "type": "section",
            "fields": [
                {"type": "mrkdwn", "text": "*Field 1:*\nValue 1"},
                {"type": "mrkdwn", "text": "*Field 2:*\nValue 2"}
            ]
        }
    ]
)
```

### Messages with Attachments

```python
client.send_message(
    channel="#dev-notifications",
    text="Workflow completed",
    attachments=[
        {
            "color": "#36a64f",
            "title": "Workflow Details",
            "fields": [
                {"title": "Status", "value": "Success", "short": True},
                {"title": "Duration", "value": "5m 32s", "short": True}
            ]
        }
    ]
)
```

## Customization

### Custom Message Templates

Create custom templates in `config.yaml`:

```yaml
formatting:
  templates:
    custom_alert: |
      :warning: *Custom Alert*
      *Type:* {alert_type}
      *Message:* {message}
      *Action Required:* {action}
```

Use the template:

```python
notifier.send_template(
    template="custom_alert",
    data={
        "alert_type": "Performance Degradation",
        "message": "API response time increased by 50%",
        "action": "Review recent deployments"
    },
    channel="#dev-alerts"
)
```

### Custom Alert Rules

Define custom alert rules:

```yaml
alerts:
  rules:
    - name: "high_memory_usage"
      severity: "high"
      condition: "memory_usage > 90"
      channel: "#dev-alerts"
      message: "Memory usage critical: {memory_usage}%"
```

### Custom Slash Commands

Implement custom slash commands:

```python
from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/slack/commands/workflow-status', methods=['POST'])
def workflow_status():
    # Parse Slack command
    user_id = request.form['user_id']
    channel_id = request.form['channel_id']
    
    # Get workflow status
    status = get_workflow_status()
    
    # Return response
    return jsonify({
        "response_type": "in_channel",
        "text": f"Current workflow status: {status}"
    })
```

## Best Practices

1. **Channel Organization**: Use separate channels for different notification types
2. **Rate Limiting**: Avoid flooding channels with too many messages
3. **Quiet Hours**: Respect team's off-hours unless critical
4. **Thread Usage**: Use threads to keep conversations organized
5. **Emoji Usage**: Use emoji for quick visual identification
6. **Mention Sparingly**: Only mention users for important alerts
7. **Rich Formatting**: Use Block Kit for better readability

## Troubleshooting

### Messages Not Appearing

**Problem**: Messages not showing up in Slack

**Solutions**:
- Verify webhook URL is correct
- Check bot has permission to post to channel
- Ensure channel name includes `#` prefix
- Review Slack API rate limits
- Check for error responses from Slack API

### Webhook URL Invalid

**Problem**: `invalid_webhook_url` error

**Solutions**:
- Regenerate webhook URL in Slack app settings
- Verify URL is complete and not truncated
- Check URL is set in environment variable
- Test webhook with curl:
  ```bash
  curl -X POST -H 'Content-type: application/json' \
    --data '{"text":"Test message"}' \
    YOUR_WEBHOOK_URL
  ```

### Bot Not Posting

**Problem**: Bot token authentication fails

**Solutions**:
- Verify bot token starts with `xoxb-`
- Check bot has required scopes
- Reinstall app to workspace if needed
- Verify bot is invited to channel

### Rate Limit Errors

**Problem**: `rate_limited` errors from Slack

**Solutions**:
- Implement exponential backoff
- Reduce message frequency
- Batch notifications
- Use rate limiting configuration:
  ```yaml
  rate_limit:
    enabled: true
    max_messages_per_minute: 10
  ```

## Security Considerations

1. **Token Storage**: Store tokens securely in environment variables
2. **Webhook Security**: Don't expose webhook URLs publicly
3. **Signing Verification**: Verify Slack request signatures for interactive features
4. **Sensitive Data**: Don't include sensitive data in messages
5. **Channel Permissions**: Use private channels for sensitive notifications
6. **Audit Logging**: Log all Slack API interactions
7. **Token Rotation**: Rotate tokens periodically

## Performance Optimization

### Async Notifications

Send notifications asynchronously to avoid blocking:

```python
import asyncio
from agentic_sdlc.integrations.slack import AsyncSlackClient

async def send_notifications():
    client = AsyncSlackClient(webhook_url=SLACK_WEBHOOK_URL)
    
    tasks = [
        client.send_message("#channel1", "Message 1"),
        client.send_message("#channel2", "Message 2"),
        client.send_message("#channel3", "Message 3")
    ]
    
    await asyncio.gather(*tasks)

asyncio.run(send_notifications())
```

### Message Batching

Batch multiple updates into single message:

```python
# Instead of sending 10 separate messages
for task in tasks:
    notifier.send_message(f"Task {task.id} completed")

# Send one summary message
summary = "\n".join([f"✓ Task {t.id} completed" for t in tasks])
notifier.send_message(f"Tasks completed:\n{summary}")
```

### Caching

Cache frequently accessed data:

```python
from functools import lru_cache

@lru_cache(maxsize=100)
def get_channel_id(channel_name):
    # Cache channel ID lookups
    return client.get_channel_id(channel_name)
```

## Related Examples

- **Basic Workflow**: `examples/basic-workflow/` - Simple workflow basics
- **Multi-Agent Workflow**: `examples/multi-agent-workflow/` - Agent collaboration
- **GitHub Integration**: `examples/integrations/github/` - GitHub automation

## Additional Resources

- [Slack API Documentation](https://api.slack.com/)
- [Block Kit Builder](https://app.slack.com/block-kit-builder)
- [Slack App Management](https://api.slack.com/apps)
- [SDLC Kit Integration Guide](../../docs/INTEGRATIONS.md)

## Support

For issues or questions:
- Check [Troubleshooting Guide](../../docs/TROUBLESHOOTING.md)
- Review [GitHub Issues](https://github.com/your-org/sdlc-kit/issues)
- Join our community discussions

---

**Stay connected with your team!** 💬
