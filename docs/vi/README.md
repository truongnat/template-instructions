# Tài Liệu Agentic SDLC v3.0.0 - Tiếng Việt

Chào mừng bạn đến với tài liệu tiếng Việt cho Agentic SDLC - một Python SDK toàn diện cho phát triển phần mềm được hỗ trợ bởi AI.

## 🎯 Bắt Đầu Nhanh

Nếu bạn mới bắt đầu với Agentic SDLC, hãy làm theo các bước sau:

1. **Cài đặt**: Xem [Hướng dẫn cài đặt](getting-started/installation.md)
2. **Cấu hình**: Thiết lập [cấu hình cơ bản](getting-started/configuration.md)
3. **Tạo Agent đầu tiên**: Xem [ví dụ Simple Agent](examples/basic/02-simple-agent.py)
4. **Xây dựng Workflow**: Xem [ví dụ Basic Workflow](examples/basic/03-basic-workflow.py)
5. **Khám phá Use Cases**: Bắt đầu với [Automated Code Review](use-cases/automated-code-review.md)

## 📋 Cheat Sheet

### Các Lệnh CLI Thường Dùng
```bash
# Khởi tạo project mới
agentic init my-project

# Xem cấu hình hiện tại
agentic config show

# Chạy workflow
agentic run workflow.yaml

# Liệt kê agents
agentic agent list
```text

### Code Snippets Cơ Bản

**Tạo Agent:**
```python
from agentic_sdlc import create_agent

agent = create_agent(
    name="my-agent",
    role="developer",
    model_name="gpt-4"
)
```text

**Tạo Workflow:**
```python
from agentic_sdlc import WorkflowBuilder

workflow = WorkflowBuilder("my-workflow") \
    .add_step("analyze", agent="analyzer") \
    .add_step("implement", agent="developer") \
    .build()
```

**Xem thêm**: [Ví dụ Configuration](examples/basic/01-configuration.py) | [CLI Commands](guides/cli/commands.md)

## 🗺️ Lộ Trình Học Tập

### 🟢 Beginner (Người Mới Bắt Đầu)
Bắt đầu với các khái niệm cơ bản và ví dụ đơn giản:
- [Cài Đặt](getting-started/installation.md) → [Cấu Hình](getting-started/configuration.md)
- [Tổng Quan về Agents](guides/agents/overview.md) → [Tạo Agents](guides/agents/creating-agents.md)
- [Tổng Quan về Workflows](guides/workflows/overview.md) → [Xây Dựng Workflows](guides/workflows/building-workflows.md)
- **Ví dụ**: [Configuration](examples/basic/01-configuration.py), [Simple Agent](examples/basic/02-simple-agent.py), [Basic Workflow](examples/basic/03-basic-workflow.py)

### 🟡 Intermediate (Trung Cấp)
Khám phá các tính năng nâng cao và patterns:
- [Các Loại Agents](guides/agents/agent-types.md) → [Agent Lifecycle](guides/agents/agent-lifecycle.md)
- [Workflow Patterns](guides/workflows/workflow-patterns.md) → [Intelligence Features](guides/intelligence/learning.md)
- [Plugin System](guides/plugins/overview.md) → [Tạo Plugins](guides/plugins/creating-plugins.md)
- **Ví dụ**: [Multi-Agent](examples/intermediate/05-multi-agent.py), [Intelligence Features](examples/intermediate/06-intelligence.py), [Plugin Dev](examples/intermediate/07-plugin-dev.py)
- **Use Cases**: [Automated Code Review](use-cases/automated-code-review.md), [CI/CD Automation](use-cases/ci-cd-automation.md)

### 🔴 Advanced (Nâng Cao)
Tối ưu hóa và triển khai production:
- [Workflows Nâng Cao](guides/workflows/advanced-workflows.md) → [Performance Tuning](guides/advanced/performance.md)
- [Scalability](guides/advanced/scalability.md) → [Security](guides/advanced/security.md) → [Deployment](guides/advanced/deployment.md)
- **Ví dụ**: [Complex Workflow](examples/advanced/09-complex-workflow.py), [Distributed System](examples/advanced/10-distributed.py), [Production Setup](examples/advanced/12-production.py)
- **Use Cases**: [Distributed System](use-cases/distributed-system.md), [Custom Workflow](use-cases/custom-workflow.md)

## Mục Lục

### 🚀 Bắt Đầu
- [Cài Đặt](getting-started/installation.md) - Hướng dẫn cài đặt SDK và CLI
  - *Liên quan*: [Troubleshooting](troubleshooting/common-errors.md), [Configuration](getting-started/configuration.md)
- [Cấu Hình](getting-started/configuration.md) - Thiết lập cấu hình hệ thống
  - *Liên quan*: [Ví dụ Configuration](examples/basic/01-configuration.py), [CLI Commands](guides/cli/commands.md)
- [Quick Start](getting-started/quick-start.md) - Bắt đầu nhanh với ví dụ đơn giản
  - *Liên quan*: [Simple Agent](examples/basic/02-simple-agent.py), [Basic Workflow](examples/basic/03-basic-workflow.py)
- [Workflow Đầu Tiên](getting-started/first-workflow.md) - Tạo workflow đầu tiên của bạn
  - *Liên quan*: [Xây Dựng Workflows](guides/workflows/building-workflows.md), [Workflow Patterns](guides/workflows/workflow-patterns.md)

### 📚 Hướng Dẫn

#### Agents
- [Tổng Quan về Agents](guides/agents/overview.md) - Giới thiệu về Agent system
  - *Liên quan*: [Các Loại Agents](guides/agents/agent-types.md), [API Reference](api-reference/orchestration/agent.md)
- [Tạo và Cấu Hình Agents](guides/agents/creating-agents.md) - Hướng dẫn tạo agents
  - *Liên quan*: [Simple Agent Example](examples/basic/02-simple-agent.py), [Multi-Agent Example](examples/intermediate/05-multi-agent.py)
- [Các Loại Agents](guides/agents/agent-types.md) - 18 loại agents có sẵn
  - *Liên quan*: [Agent Lifecycle](guides/agents/agent-lifecycle.md), [Use Cases](use-cases/README.md)
- [Quản Lý Lifecycle](guides/agents/agent-lifecycle.md) - Quản lý vòng đời agent
  - *Liên quan*: [Monitoring](guides/intelligence/monitoring.md), [Debugging](troubleshooting/debugging.md)

#### Workflows
- [Tổng Quan về Workflows](guides/workflows/overview.md) - Giới thiệu về Workflow system
  - *Liên quan*: [Workflow Diagrams](diagrams/workflows.md), [API Reference](api-reference/orchestration/workflow.md)
- [Xây Dựng Workflows](guides/workflows/building-workflows.md) - Hướng dẫn xây dựng workflows
  - *Liên quan*: [Basic Workflow Example](examples/basic/03-basic-workflow.py), [Workflow Patterns](guides/workflows/workflow-patterns.md)
- [Workflow Patterns](guides/workflows/workflow-patterns.md) - Các patterns phổ biến
  - *Liên quan*: [Advanced Workflows](guides/workflows/advanced-workflows.md), [Use Cases](use-cases/README.md)
- [Workflows Nâng Cao](guides/workflows/advanced-workflows.md) - Conditional execution, error handling
  - *Liên quan*: [Complex Workflow Example](examples/advanced/09-complex-workflow.py), [Error Handling](examples/basic/04-error-handling.py)

#### Intelligence Features
- [Learning](guides/intelligence/learning.md) - Learner và learning features
  - *Liên quan*: [Intelligence Example](examples/intermediate/06-intelligence.py), [Learner API](api-reference/intelligence/learner.md)
- [Monitoring](guides/intelligence/monitoring.md) - Monitor và metrics
  - *Liên quan*: [Monitor API](api-reference/intelligence/monitor.md), [Debugging](troubleshooting/debugging.md)
- [Reasoning](guides/intelligence/reasoning.md) - Reasoner và decision making
  - *Liên quan*: [Reasoner API](api-reference/intelligence/reasoner.md), [Intelligent Project Mgmt](use-cases/intelligent-project-mgmt.md)
- [Collaboration](guides/intelligence/collaboration.md) - Team collaboration
  - *Liên quan*: [Collaborator API](api-reference/intelligence/collaborator.md), [Multi-Agent Example](examples/intermediate/05-multi-agent.py)
- [Integrated Example](guides/intelligence/integrated-example.md) - Ví dụ tích hợp tất cả features
  - *Liên quan*: [Complex Workflow](examples/advanced/09-complex-workflow.py), [Custom Workflow Use Case](use-cases/custom-workflow.md)

#### Plugins
- [Tổng Quan Plugin System](guides/plugins/overview.md) - Giới thiệu plugin system
  - *Liên quan*: [Plugin API](api-reference/plugins/base.md), [Plugin Registry](api-reference/plugins/registry.md)
- [Tạo Plugins](guides/plugins/creating-plugins.md) - Hướng dẫn tạo plugins
  - *Liên quan*: [Plugin Dev Example](examples/intermediate/07-plugin-dev.py), [Best Practices](guides/plugins/best-practices.md)
- [Ví Dụ Plugins](guides/plugins/plugin-examples.md) - Các ví dụ plugin phức tạp
  - *Liên quan*: [Creating Plugins](guides/plugins/creating-plugins.md), [Integration Example](examples/advanced/11-integration.py)
- [Best Practices](guides/plugins/best-practices.md) - Best practices cho plugin development
  - *Liên quan*: [Error Handling](examples/basic/04-error-handling.py), [Testing](examples/basic/14-testing.py)

#### CLI
- [Tổng Quan CLI](guides/cli/overview.md) - Giới thiệu Command-Line Interface
  - *Liên quan*: [Installation](getting-started/installation.md), [Configuration](getting-started/configuration.md)
- [Command Reference](guides/cli/commands.md) - Tham khảo đầy đủ các lệnh CLI
  - *Liên quan*: [CLI Examples](guides/cli/examples.md), [CLI Usage Example](examples/intermediate/08-cli-usage.sh)
- [Ví Dụ CLI](guides/cli/examples.md) - Các ví dụ sử dụng CLI thực tế
  - *Liên quan*: [Commands](guides/cli/commands.md), [CI/CD Automation](use-cases/ci-cd-automation.md)

#### Advanced Topics
- [Performance Tuning](guides/advanced/performance.md) - Tối ưu hóa performance
  - *Liên quan*: [Caching Example](examples/intermediate/15-caching.py), [Production Setup](examples/advanced/12-production.py)
- [Scalability](guides/advanced/scalability.md) - Chiến lược scaling
  - *Liên quan*: [Distributed System](examples/advanced/10-distributed.py), [Distributed Use Case](use-cases/distributed-system.md)
- [Security](guides/advanced/security.md) - Best practices về bảo mật
  - *Liên quan*: [Configuration](getting-started/configuration.md), [Production Setup](examples/advanced/12-production.py)
- [Deployment](guides/advanced/deployment.md) - Hướng dẫn triển khai
  - *Liên quan*: [Production Setup](examples/advanced/12-production.py), [CI/CD Automation](use-cases/ci-cd-automation.md)

### 💡 Các Trường Hợp Sử Dụng

Khám phá 8 use cases thực tế với code hoàn chỉnh:

- [Automated Code Review](use-cases/automated-code-review.md) - Multi-agent code review workflow
  - *Liên quan*: [Multi-Agent Example](examples/intermediate/05-multi-agent.py), [GitHub Integration](use-cases/github-integration.md)
- [CI/CD Automation](use-cases/ci-cd-automation.md) - Tích hợp với GitHub Actions/GitLab CI
  - *Liên quan*: [CLI Examples](guides/cli/examples.md), [Deployment](guides/advanced/deployment.md)
- [Intelligent Project Management](use-cases/intelligent-project-mgmt.md) - Task analysis và complexity estimation
  - *Liên quan*: [Reasoning](guides/intelligence/reasoning.md), [Collaboration](guides/intelligence/collaboration.md)
- [Automated Testing](use-cases/automated-testing.md) - Test generation và self-healing
  - *Liên quan*: [Testing Example](examples/basic/14-testing.py), [Workflows](guides/workflows/overview.md)
- [GitHub Integration](use-cases/github-integration.md) - Tích hợp với GitHub API
  - *Liên quan*: [Integration Example](examples/advanced/11-integration.py), [Automated Code Review](use-cases/automated-code-review.md)
- [Slack Integration](use-cases/slack-integration.md) - Tích hợp với Slack API
  - *Liên quan*: [Integration Example](examples/advanced/11-integration.py), [Collaboration](guides/intelligence/collaboration.md)
- [Custom Workflow](use-cases/custom-workflow.md) - End-to-end workflow từ requirements đến deployment
  - *Liên quan*: [Complex Workflow](examples/advanced/09-complex-workflow.py), [Advanced Workflows](guides/workflows/advanced-workflows.md)
- [Distributed System](use-cases/distributed-system.md) - Scaling và load balancing
  - *Liên quan*: [Distributed Example](examples/advanced/10-distributed.py), [Scalability](guides/advanced/scalability.md)

*Xem thêm*: [Use Cases Overview](use-cases/README.md)

### 📝 Ví Dụ Code

15+ ví dụ code runnable với comments chi tiết:

#### Basic Examples (Cơ Bản)
- [Configuration](examples/basic/01-configuration.py) - Thiết lập cấu hình
  - *Liên quan*: [Configuration Guide](getting-started/configuration.md), [Config API](api-reference/core/config.md)
- [Simple Agent](examples/basic/02-simple-agent.py) - Tạo agent đơn giản
  - *Liên quan*: [Creating Agents](guides/agents/creating-agents.md), [Agent API](api-reference/orchestration/agent.md)
- [Basic Workflow](examples/basic/03-basic-workflow.py) - Workflow cơ bản
  - *Liên quan*: [Building Workflows](guides/workflows/building-workflows.md), [Workflow API](api-reference/orchestration/workflow.md)
- [Error Handling](examples/basic/04-error-handling.py) - Xử lý lỗi
  - *Liên quan*: [Common Errors](troubleshooting/common-errors.md), [Exceptions API](api-reference/core/exceptions.md)
- [Testing](examples/basic/14-testing.py) - Testing strategies
  - *Liên quan*: [Automated Testing Use Case](use-cases/automated-testing.md), [Best Practices](guides/plugins/best-practices.md)

#### Intermediate Examples (Trung Cấp)
- [Multi-Agent System](examples/intermediate/05-multi-agent.py) - Hệ thống multi-agent
  - *Liên quan*: [Agent Types](guides/agents/agent-types.md), [Collaboration](guides/intelligence/collaboration.md)
- [Intelligence Features](examples/intermediate/06-intelligence.py) - Sử dụng intelligence features
  - *Liên quan*: [Learning](guides/intelligence/learning.md), [Monitoring](guides/intelligence/monitoring.md), [Reasoning](guides/intelligence/reasoning.md)
- [Plugin Development](examples/intermediate/07-plugin-dev.py) - Phát triển plugin
  - *Liên quan*: [Creating Plugins](guides/plugins/creating-plugins.md), [Plugin API](api-reference/plugins/base.md)
- [CLI Usage](examples/intermediate/08-cli-usage.sh) - Sử dụng CLI
  - *Liên quan*: [CLI Commands](guides/cli/commands.md), [CLI Examples](guides/cli/examples.md)
- [Model Client](examples/intermediate/13-model-client.py) - Cấu hình LLM providers
  - *Liên quan*: [Configuration](getting-started/configuration.md), [ModelClient API](api-reference/orchestration/model-client.md)
- [Caching](examples/intermediate/15-caching.py) - Caching strategies
  - *Liên quan*: [Performance Tuning](guides/advanced/performance.md), [Production Setup](examples/advanced/12-production.py)

#### Advanced Examples (Nâng Cao)
- [Complex Workflow](examples/advanced/09-complex-workflow.py) - Workflow phức tạp
  - *Liên quan*: [Advanced Workflows](guides/workflows/advanced-workflows.md), [Custom Workflow Use Case](use-cases/custom-workflow.md)
- [Distributed System](examples/advanced/10-distributed.py) - Hệ thống phân tán
  - *Liên quan*: [Scalability](guides/advanced/scalability.md), [Distributed Use Case](use-cases/distributed-system.md)
- [External Integrations](examples/advanced/11-integration.py) - Tích hợp external tools
  - *Liên quan*: [GitHub Integration](use-cases/github-integration.md), [Slack Integration](use-cases/slack-integration.md)
- [Production Setup](examples/advanced/12-production.py) - Thiết lập production
  - *Liên quan*: [Deployment](guides/advanced/deployment.md), [Security](guides/advanced/security.md), [Performance](guides/advanced/performance.md)

### 🔍 API Reference

Tham khảo đầy đủ cho tất cả public APIs:

- [Core](api-reference/core/) - Config, Exceptions, Logging
  - *Liên quan*: [Configuration Guide](getting-started/configuration.md), [Error Handling](examples/basic/04-error-handling.py)
- [Infrastructure](api-reference/infrastructure/) - WorkflowEngine, ExecutionEngine, Lifecycle
  - *Liên quan*: [Workflows](guides/workflows/overview.md), [Agent Lifecycle](guides/agents/agent-lifecycle.md)
- [Intelligence](api-reference/intelligence/) - Learner, Monitor, Reasoner, Collaborator
  - *Liên quan*: [Intelligence Features](guides/intelligence/learning.md), [Intelligence Example](examples/intermediate/06-intelligence.py)
- [Orchestration](api-reference/orchestration/) - Agent, Workflow, ModelClient
  - *Liên quan*: [Agents](guides/agents/overview.md), [Workflows](guides/workflows/overview.md)
- [Plugins](api-reference/plugins/) - Plugin Base, Registry
  - *Liên quan*: [Plugin System](guides/plugins/overview.md), [Plugin Dev Example](examples/intermediate/07-plugin-dev.py)

### 📊 Sơ Đồ

Sơ đồ trực quan giúp hiểu kiến trúc và data flow:

- [Architecture](diagrams/architecture.md) - Sơ đồ kiến trúc hệ thống tổng thể
  - *Liên quan*: [Getting Started](getting-started/installation.md), [API Reference](api-reference/)
- [Workflows](diagrams/workflows.md) - Sơ đồ workflow sequences
  - *Liên quan*: [Workflow Guides](guides/workflows/overview.md), [Workflow Patterns](guides/workflows/workflow-patterns.md)
- [Agent Interaction](diagrams/agent-interaction.md) - Sơ đồ tương tác giữa agents
  - *Liên quan*: [Multi-Agent Example](examples/intermediate/05-multi-agent.py), [Collaboration](guides/intelligence/collaboration.md)
- [Data Flow](diagrams/data-flow.md) - Sơ đồ luồng dữ liệu
  - *Liên quan*: [Architecture](diagrams/architecture.md), [Infrastructure API](api-reference/infrastructure/)

### 🔧 Troubleshooting

Hướng dẫn xử lý lỗi và debug:

- [Common Errors](troubleshooting/common-errors.md) - 10+ lỗi phổ biến và cách khắc phục
  - *Liên quan*: [Error Handling Example](examples/basic/04-error-handling.py), [Exceptions API](api-reference/core/exceptions.md)
- [Debugging Guide](troubleshooting/debugging.md) - Debug logging và log interpretation
  - *Liên quan*: [Monitoring](guides/intelligence/monitoring.md), [Logging API](api-reference/core/logging.md)
- [FAQ](troubleshooting/faq.md) - Frequently Asked Questions
  - *Liên quan*: [Installation](getting-started/installation.md), [Configuration](getting-started/configuration.md)

### 🔄 Migration

Hướng dẫn nâng cấp từ phiên bản cũ:

- [From v2.x](migration/from-v2.md) - Breaking changes và deprecated features
  - *Liên quan*: [Upgrade Guide](migration/upgrade-guide.md), [Configuration](getting-started/configuration.md)
- [Upgrade Guide](migration/upgrade-guide.md) - Import path mapping và config changes
  - *Liên quan*: [From v2.x](migration/from-v2.md), [Installation](getting-started/installation.md)

## 🔗 Tài Nguyên Bổ Sung

### Tài Liệu Kỹ Thuật
- [Glossary](glossary.yaml) - Danh sách thuật ngữ kỹ thuật tiếng Việt
- [CONTRIBUTING.md](CONTRIBUTING.md) - Hướng dẫn đóng góp vào tài liệu

### Liên Kết Nhanh
- **Beginner**: [Installation](getting-started/installation.md) → [Simple Agent](examples/basic/02-simple-agent.py) → [Basic Workflow](examples/basic/03-basic-workflow.py)
- **Intermediate**: [Multi-Agent](examples/intermediate/05-multi-agent.py) → [Intelligence Features](examples/intermediate/06-intelligence.py) → [Automated Code Review](use-cases/automated-code-review.md)
- **Advanced**: [Complex Workflow](examples/advanced/09-complex-workflow.py) → [Distributed System](examples/advanced/10-distributed.py) → [Production Setup](examples/advanced/12-production.py)

### Tìm Kiếm Theo Chủ Đề
- **Agents**: [Overview](guides/agents/overview.md) | [Creating](guides/agents/creating-agents.md) | [Types](guides/agents/agent-types.md) | [Lifecycle](guides/agents/agent-lifecycle.md) | [API](api-reference/orchestration/agent.md)
- **Workflows**: [Overview](guides/workflows/overview.md) | [Building](guides/workflows/building-workflows.md) | [Patterns](guides/workflows/workflow-patterns.md) | [Advanced](guides/workflows/advanced-workflows.md) | [API](api-reference/orchestration/workflow.md)
- **Intelligence**: [Learning](guides/intelligence/learning.md) | [Monitoring](guides/intelligence/monitoring.md) | [Reasoning](guides/intelligence/reasoning.md) | [Collaboration](guides/intelligence/collaboration.md) | [API](api-reference/intelligence/)
- **Plugins**: [Overview](guides/plugins/overview.md) | [Creating](guides/plugins/creating-plugins.md) | [Examples](guides/plugins/plugin-examples.md) | [Best Practices](guides/plugins/best-practices.md) | [API](api-reference/plugins/)
- **CLI**: [Overview](guides/cli/overview.md) | [Commands](guides/cli/commands.md) | [Examples](guides/cli/examples.md)
- **Advanced**: [Performance](guides/advanced/performance.md) | [Scalability](guides/advanced/scalability.md) | [Security](guides/advanced/security.md) | [Deployment](guides/advanced/deployment.md)

## Thuật Ngữ Kỹ Thuật

Tài liệu này sử dụng các thuật ngữ kỹ thuật bằng tiếng Việt với thuật ngữ tiếng Anh trong ngoặc. Xem [Glossary](glossary.yaml) để biết danh sách đầy đủ các thuật ngữ.

## Đóng Góp

Để đóng góp vào tài liệu này, vui lòng xem [CONTRIBUTING.md](CONTRIBUTING.md).

## Phiên Bản

- **Version**: 3.0.0
- **Last Updated**: 2026-02-11

## Liên Hệ

- **Repository**: https://github.com/truongnat/agentic-sdlc
- **Issues**: https://github.com/truongnat/agentic-sdlc/issues
- **Documentation**: https://github.com/truongnat/agentic-sdlc#readme
