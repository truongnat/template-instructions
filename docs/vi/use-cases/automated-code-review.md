# Đánh Giá Code Tự Động với Multi-Agent Workflow

**Phiên bản**: 3.0.0  
**Cập nhật lần cuối**: 11/02/2026


**Phiên bản:** 1.0.0  
**Cập nhật lần cuối:** 2026-02-11  
**Danh mục:** intermediate

---

## Tổng Quan

Use case này minh họa cách xây dựng hệ thống đánh giá code tự động sử dụng multi-agent workflow trong Agentic SDLC. Hệ thống sử dụng nhiều agent chuyên biệt để phân tích code từ nhiều góc độ khác nhau: chất lượng code, security, performance, và best practices.

---

## Kịch Bản

### Bối Cảnh

Một team phát triển phần mềm có 10 developers đang làm việc trên một dự án lớn. Mỗi ngày có hàng chục pull requests được tạo ra, và việc review thủ công tốn rất nhiều thời gian. Team muốn tự động hóa quá trình review ban đầu để các senior developers có thể tập trung vào những vấn đề phức tạp hơn.

### Các Tác Nhân

- **Code Analyzer Agent**: Phân tích chất lượng code, complexity, và maintainability
- **Security Reviewer Agent**: Kiểm tra các lỗ hổng bảo mật và security best practices
- **Performance Reviewer Agent**: Đánh giá performance implications và optimization opportunities
- **Style Checker Agent**: Kiểm tra coding standards và formatting
- **Documentation Reviewer Agent**: Đánh giá chất lượng documentation và comments
- **Coordinator Agent**: Điều phối các agent và tổng hợp kết quả

### Mục Tiêu

- Tự động hóa quá trình code review ban đầu
- Phát hiện issues sớm trước khi human review
- Giảm thời gian review từ 2 giờ xuống còn 15 phút
- Đảm bảo consistency trong code review process
- Cung cấp feedback chi tiết và actionable cho developers

### Ràng Buộc

- Phải tích hợp với GitHub/GitLab API
- Kết quả review phải được post lên pull request dưới dạng comments
- Hệ thống phải xử lý được các ngôn ngữ: Python, JavaScript, TypeScript
- Thời gian review không được vượt quá 5 phút cho mỗi PR

---

## Vấn Đề

Việc code review thủ công gặp phải các vấn đề:

1. **Tốn thời gian**: Mỗi PR cần 1-2 giờ để review kỹ lưỡng
2. **Không nhất quán**: Các reviewer khác nhau có thể có standards khác nhau
3. **Bỏ sót issues**: Con người dễ bỏ sót các lỗi nhỏ hoặc security issues
4. **Bottleneck**: Senior developers trở thành bottleneck khi có nhiều PRs
5. **Feedback chậm**: Developers phải đợi lâu mới nhận được feedback

---

## Giải Pháp

Xây dựng một multi-agent system với các agent chuyên biệt, mỗi agent chịu trách nhiệm một khía cạnh của code review. Các agent làm việc song song để tăng tốc độ, và kết quả được tổng hợp bởi Coordinator Agent.

**Ưu điểm:**
- Review nhanh chóng và nhất quán
- Phát hiện issues toàn diện từ nhiều góc độ
- Giải phóng thời gian cho senior developers
- Feedback tức thì cho developers
- Có thể scale dễ dàng khi team phát triển

---

## Kiến Trúc

**Kiến trúc Multi-Agent Code Review System**

```mermaid
flowchart TB
    PR[Pull Request] --> Coordinator[Coordinator Agent]
    Coordinator --> CodeAnalyzer[Code Analyzer Agent]
    Coordinator --> SecurityReviewer[Security Reviewer Agent]
    Coordinator --> PerfReviewer[Performance Reviewer Agent]
    Coordinator --> StyleChecker[Style Checker Agent]
    Coordinator --> DocReviewer[Documentation Reviewer Agent]
    
    CodeAnalyzer --> Results[Results Aggregator]
    SecurityReviewer --> Results
    PerfReviewer --> Results
    StyleChecker --> Results
    DocReviewer --> Results
    
    Results --> Coordinator
    Coordinator --> Report[Review Report]
    Report --> GitHub[GitHub/GitLab Comment]
```text

---

## Triển Khai

### Bước 1: Cấu hình hệ thống

Đầu tiên, cấu hình các agents và workflow:

```python
from agentic_sdlc import create_agent, WorkflowBuilder, AgentType
from agentic_sdlc.intelligence import TeamCoordinator

# Tạo các specialized agents
code_analyzer = create_agent(
    name="code_analyzer",
    role=AgentType.CODE_REVIEWER,
    model_name="gpt-4",
    system_prompt="""Bạn là một code analyzer chuyên nghiệp. 
    Phân tích code về: complexity, maintainability, code smells, 
    và đề xuất improvements. Đánh giá theo thang điểm 1-10.""",
    tools=["ast_parser", "complexity_analyzer"]
)

security_reviewer = create_agent(
    name="security_reviewer",
    role=AgentType.SECURITY_EXPERT,
    model_name="gpt-4",
    system_prompt="""Bạn là security expert. Kiểm tra code về: 
    SQL injection, XSS, authentication issues, data exposure, 
    và các security vulnerabilities. Đánh giá mức độ nghiêm trọng.""",
    tools=["security_scanner", "vulnerability_checker"]
)

performance_reviewer = create_agent(
    name="performance_reviewer",
    role=AgentType.PERFORMANCE_ENGINEER,
    model_name="gpt-4",
    system_prompt="""Bạn là performance engineer. Phân tích code về: 
    time complexity, space complexity, database queries, 
    caching opportunities, và optimization suggestions.""",
    tools=["profiler", "query_analyzer"]
)

style_checker = create_agent(
    name="style_checker",
    role=AgentType.CODE_REVIEWER,
    model_name="gpt-3.5-turbo",
    system_prompt="""Bạn là style checker. Kiểm tra code về: 
    naming conventions, formatting, PEP 8 compliance, 
    và coding standards.""",
    tools=["linter", "formatter"]
)

doc_reviewer = create_agent(
    name="doc_reviewer",
    role=AgentType.DOCUMENTATION_WRITER,
    model_name="gpt-3.5-turbo",
    system_prompt="""Bạn là documentation reviewer. Đánh giá: 
    docstrings, comments, README updates, API documentation, 
    và code clarity.""",
    tools=["doc_parser"]
)

coordinator = create_agent(
    name="coordinator",
    role=AgentType.PROJECT_MANAGER,
    model_name="gpt-4",
    system_prompt="""Bạn là coordinator. Tổng hợp kết quả từ các agents, 
    tạo summary report, và quyết định approve/reject PR.""",
    tools=["report_generator"]
)
```text

### Bước 2: Xây dựng workflow

Tạo workflow để điều phối các agents:

```python
# Xây dựng code review workflow
workflow = WorkflowBuilder("automated_code_review") \
    .add_step(
        name="fetch_pr_changes",
        action="fetch_github_pr",
        parameters={
            "repo": "${repo}",
            "pr_number": "${pr_number}"
        }
    ) \
    .add_step(
        name="parallel_review",
        action="parallel_agent_execution",
        parameters={
            "agents": [
                {
                    "agent": code_analyzer,
                    "task": "Analyze code quality and complexity"
                },
                {
                    "agent": security_reviewer,
                    "task": "Review security vulnerabilities"
                },
                {
                    "agent": performance_reviewer,
                    "task": "Analyze performance implications"
                },
                {
                    "agent": style_checker,
                    "task": "Check coding style and standards"
                },
                {
                    "agent": doc_reviewer,
                    "task": "Review documentation quality"
                }
            ],
            "input": "${pr_changes}"
        },
        dependencies=["fetch_pr_changes"]
    ) \
    .add_step(
        name="aggregate_results",
        action="agent_execution",
        parameters={
            "agent": coordinator,
            "task": "Aggregate review results and create summary",
            "input": "${parallel_review.results}"
        },
        dependencies=["parallel_review"]
    ) \
    .add_step(
        name="post_review_comment",
        action="post_github_comment",
        parameters={
            "repo": "${repo}",
            "pr_number": "${pr_number}",
            "comment": "${aggregate_results.summary}"
        },
        dependencies=["aggregate_results"]
    ) \
    .build()
```text

### Bước 3: Tích hợp với GitHub

Thiết lập GitHub webhook để trigger workflow:

```python
from flask import Flask, request
from agentic_sdlc import WorkflowRunner

app = Flask(__name__)
runner = WorkflowRunner()

@app.route('/webhook/github', methods=['POST'])
def github_webhook():
    """Handle GitHub webhook for pull request events."""
    payload = request.json
    
    # Chỉ xử lý pull request events
    if payload.get('action') not in ['opened', 'synchronize']:
        return {'status': 'ignored'}, 200
    
    # Extract PR information
    pr_number = payload['pull_request']['number']
    repo = payload['repository']['full_name']
    
    # Execute workflow
    result = runner.run(
        workflow=workflow,
        context={
            'repo': repo,
            'pr_number': pr_number,
            'pr_changes': payload['pull_request']['diff_url']
        }
    )
    
    return {'status': 'success', 'workflow_id': result.id}, 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
```text

### Bước 4: Tùy chỉnh review criteria

Cấu hình các tiêu chí review cụ thể:

```python
# Cấu hình review criteria
review_config = {
    "code_quality": {
        "max_complexity": 10,
        "min_test_coverage": 80,
        "max_function_length": 50,
        "max_file_length": 500
    },
    "security": {
        "block_on_critical": True,
        "warn_on_medium": True,
        "check_dependencies": True
    },
    "performance": {
        "check_n_plus_one": True,
        "check_memory_leaks": True,
        "max_query_time": 100  # ms
    },
    "style": {
        "enforce_pep8": True,
        "max_line_length": 100,
        "require_type_hints": True
    },
    "documentation": {
        "require_docstrings": True,
        "require_readme_update": True,
        "min_comment_ratio": 0.1
    }
}

# Apply configuration to agents
code_analyzer.config.update(review_config["code_quality"])
security_reviewer.config.update(review_config["security"])
performance_reviewer.config.update(review_config["performance"])
style_checker.config.update(review_config["style"])
doc_reviewer.config.update(review_config["documentation"])
```text

### Bước 5: Xử lý kết quả và reporting

Tạo format cho review report:

```python
def format_review_report(results):
    """Format review results into a comprehensive report."""
    report = "## 🤖 Automated Code Review Report\n\n"
    
    # Overall score
    overall_score = calculate_overall_score(results)
    report += f"**Overall Score:** {overall_score}/10\n\n"
    
    # Code Quality
    report += "### 📊 Code Quality\n"
    report += format_section(results['code_analyzer'])
    
    # Security
    report += "\n### 🔒 Security\n"
    report += format_section(results['security_reviewer'])
    
    # Performance
    report += "\n### ⚡ Performance\n"
    report += format_section(results['performance_reviewer'])
    
    # Style
    report += "\n### 🎨 Code Style\n"
    report += format_section(results['style_checker'])
    
    # Documentation
    report += "\n### 📝 Documentation\n"
    report += format_section(results['doc_reviewer'])
    
    # Recommendation
    report += "\n### ✅ Recommendation\n"
    if overall_score >= 8:
        report += "✅ **APPROVED** - Code meets quality standards\n"
    elif overall_score >= 6:
        report += "⚠️ **NEEDS IMPROVEMENT** - Address issues before merge\n"
    else:
        report += "❌ **REJECTED** - Significant issues must be fixed\n"
    
    return report

def format_section(agent_result):
    """Format individual agent result."""
    section = f"**Score:** {agent_result['score']}/10\n\n"
    
    if agent_result['issues']:
        section += "**Issues Found:**\n"
        for issue in agent_result['issues']:
            severity_emoji = {
                'critical': '🔴',
                'high': '🟠',
                'medium': '🟡',
                'low': '🟢'
            }
            emoji = severity_emoji.get(issue['severity'], '⚪')
            section += f"- {emoji} {issue['message']} (Line {issue['line']})\n"
    else:
        section += "✅ No issues found\n"
    
    if agent_result['suggestions']:
        section += "\n**Suggestions:**\n"
        for suggestion in agent_result['suggestions']:
            section += f"- 💡 {suggestion}\n"
    
    return section + "\n"
```

---

## Kết Quả

### Kết Quả Đạt Được

- **Thời gian review giảm 88%**: Từ 2 giờ xuống còn 15 phút
- **Phát hiện issues tăng 45%**: Các agent phát hiện được nhiều issues mà human reviewers thường bỏ sót
- **Consistency tăng 100%**: Mọi PR đều được review theo cùng một standard
- **Developer satisfaction tăng 60%**: Feedback nhanh chóng và chi tiết
- **Senior developer time freed**: 70% thời gian được giải phóng cho các công việc quan trọng hơn

### Các Chỉ Số

- **Average review time**: 12 phút
- **Issues detected per PR**: 8.5 (trước đây: 5.9)
- **False positive rate**: 12%
- **Developer adoption rate**: 95%
- **PRs reviewed per day**: 45 (trước đây: 15)

---

## Bài Học Kinh Nghiệm

- **Parallel execution là key**: Chạy các agents song song giảm thời gian review đáng kể
- **Specialized agents hiệu quả hơn**: Mỗi agent tập trung vào một domain cho kết quả tốt hơn
- **Configuration flexibility quan trọng**: Mỗi project có standards khác nhau, cần flexible config
- **Human review vẫn cần thiết**: Automated review là bước đầu, complex issues vẫn cần human judgment
- **Feedback quality quan trọng hơn quantity**: Cần filter và prioritize issues để tránh overwhelm developers
- **Integration với existing tools**: Tích hợp tốt với GitHub/GitLab giúp adoption dễ dàng hơn
- **Continuous improvement**: Thu thập feedback từ developers để cải thiện agents liên tục

---

## Tài Liệu Liên Quan

- [Hướng dẫn tạo Agents](../guides/agents/creating-agents.md)
- [Xây dựng Workflows](../guides/workflows/building-workflows.md)
- [Intelligence Features](../guides/intelligence/collaboration.md)
- [GitHub Integration](./github-integration.md)

**Tags:** code-review, multi-agent, automation, ci-cd, github

---

*Use case này là một phần của Agentic SDLC v1.0.0*
