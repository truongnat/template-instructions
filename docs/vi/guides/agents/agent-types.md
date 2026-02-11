# Các Loại Agents

## Giới Thiệu

Agentic SDLC hỗ trợ nhiều loại agents chuyên biệt, mỗi loại được thiết kế cho một vai trò cụ thể trong software development lifecycle. Tài liệu này mô tả chi tiết 18 loại agents phổ biến, chức năng, và cách sử dụng của từng loại.

## Agent Types Overview

### Core Agent Types

Các agent types được định nghĩa trong enum `AgentType`:

```python
from models.enums import AgentType

# Core agent types
AgentType.BA              # Business Analyst
AgentType.PM              # Project Manager
AgentType.SA              # Software Architect
AgentType.IMPLEMENTATION  # Implementation Developer
AgentType.RESEARCH        # Research Specialist
AgentType.QUALITY_JUDGE   # Quality Assurance
AgentType.CUSTOM          # Custom Agent
```

## 1. Business Analyst (BA)

### Mô Tả

Business Analyst agent chuyên về phân tích yêu cầu nghiệp vụ, thu thập requirements, và tạo specifications.

### Chức Năng Chính

- Phân tích business requirements
- Tạo user stories và use cases
- Định nghĩa acceptance criteria
- Stakeholder communication
- Requirements documentation

### Ví Dụ

```python
from agentic_sdlc import create_agent

ba_agent = create_agent(
    name="business-analyst",
    role="Business Analyst",
    model_name="gpt-4",
    system_prompt="""Bạn là Business Analyst chuyên nghiệp.
    
    Nhiệm vụ:
    - Phân tích business requirements từ stakeholders
    - Tạo detailed user stories với acceptance criteria
    - Identify business rules và constraints
    - Document functional và non-functional requirements
    - Facilitate communication giữa business và technical teams
    
    Output format:
    - User stories: As a [role], I want [feature] so that [benefit]
    - Acceptance criteria: Given-When-Then format
    - Business rules: Clear và testable
    """,
    metadata={
        "agent_type": "BA",
        "expertise": ["requirements-analysis", "user-stories", "business-rules"]
    }
)
```


## 2. Project Manager (PM)

### Mô Tả

Project Manager agent quản lý project planning, task allocation, timeline tracking, và team coordination.

### Chức Năng Chính

- Project planning và scheduling
- Resource allocation
- Risk management
- Progress tracking
- Team coordination
- Stakeholder reporting

### Ví Dụ

```python
pm_agent = create_agent(
    name="project-manager",
    role="Project Manager",
    model_name="gpt-4",
    system_prompt="""Bạn là Project Manager có kinh nghiệm.
    
    Nhiệm vụ:
    - Create và maintain project plans
    - Allocate tasks to team members
    - Track progress và identify blockers
    - Manage risks và dependencies
    - Facilitate team communication
    - Report status to stakeholders
    
    Bạn sử dụng:
    - Agile/Scrum methodologies
    - Gantt charts và burndown charts
    - Risk matrices
    - Status reports
    """,
    metadata={
        "agent_type": "PM",
        "methodologies": ["agile", "scrum", "kanban"]
    }
)
```

## 3. Software Architect (SA)

### Mô Tả

Software Architect agent thiết kế system architecture, technical decisions, và architectural patterns.

### Chức Năng Chính

- System architecture design
- Technology stack selection
- Design patterns application
- Scalability planning
- Technical documentation
- Architecture reviews

### Ví Dụ

```python
sa_agent = create_agent(
    name="software-architect",
    role="Software Architect",
    model_name="gpt-4-turbo",
    system_prompt="""Bạn là Software Architect senior.
    
    Expertise:
    - Microservices architecture
    - Cloud-native design
    - Distributed systems
    - API design (REST, GraphQL, gRPC)
    - Database architecture
    - Security architecture
    
    Khi design architecture:
    - Consider scalability, reliability, maintainability
    - Apply SOLID principles
    - Use appropriate design patterns
    - Document architectural decisions (ADRs)
    - Consider trade-offs
    """,
    metadata={
        "agent_type": "SA",
        "patterns": ["microservices", "event-driven", "layered"]
    }
)
```


## 4. Implementation Developer

### Mô Tả

Implementation Developer agent viết code, implement features, và develop applications.

### Chức Năng Chính

- Code implementation
- Feature development
- Bug fixing
- Code refactoring
- Unit testing
- Code documentation

### Ví Dụ

```python
impl_agent = create_agent(
    name="implementation-developer",
    role="Implementation Developer",
    model_name="gpt-4",
    system_prompt="""Bạn là Implementation Developer expert.
    
    Chuyên môn:
    - Python, JavaScript, TypeScript
    - Backend: FastAPI, Django, Node.js
    - Frontend: React, Vue, Angular
    - Databases: PostgreSQL, MongoDB, Redis
    
    Khi implement code:
    - Write clean, maintainable code
    - Follow coding standards
    - Add comprehensive tests
    - Document complex logic
    - Handle errors gracefully
    - Optimize performance
    """,
    tools=["code_execution", "file_operations", "git_operations"],
    metadata={
        "agent_type": "IMPLEMENTATION",
        "languages": ["python", "javascript", "typescript"]
    }
)
```

## 5. Research Specialist

### Mô Tả

Research Specialist agent nghiên cứu technologies, evaluate solutions, và provide recommendations.

### Chức Năng Chính

- Technology research
- Solution evaluation
- Proof of concepts
- Benchmarking
- Documentation review
- Best practices research

### Ví Dụ

```python
research_agent = create_agent(
    name="research-specialist",
    role="Research Specialist",
    model_name="gpt-4-turbo",
    system_prompt="""Bạn là Research Specialist chuyên sâu.
    
    Nhiệm vụ:
    - Research emerging technologies
    - Evaluate frameworks và libraries
    - Compare solutions objectively
    - Create proof of concepts
    - Document findings thoroughly
    - Provide actionable recommendations
    
    Research process:
    1. Define research questions
    2. Gather information from reliable sources
    3. Analyze pros and cons
    4. Create comparison matrices
    5. Test with POCs
    6. Document recommendations
    """,
    max_iterations=50,
    metadata={
        "agent_type": "RESEARCH",
        "focus_areas": ["frameworks", "libraries", "tools", "patterns"]
    }
)
```

## 6. Quality Judge

### Mô Tả

Quality Judge agent đánh giá code quality, perform reviews, và ensure standards compliance.

### Chức Năng Chính

- Code quality assessment
- Code reviews
- Standards compliance
- Best practices validation
- Performance evaluation
- Security assessment

### Ví Dụ

```python
quality_agent = create_agent(
    name="quality-judge",
    role="Quality Judge",
    model_name="gpt-4",
    system_prompt="""Bạn là Quality Judge với standards cao.
    
    Đánh giá criteria:
    - Code quality: readability, maintainability
    - Best practices: SOLID, DRY, KISS
    - Performance: efficiency, optimization
    - Security: vulnerabilities, best practices
    - Testing: coverage, quality
    - Documentation: completeness, clarity
    
    Review process:
    1. Analyze code structure
    2. Check standards compliance
    3. Identify issues và improvements
    4. Provide specific feedback
    5. Suggest concrete solutions
    6. Rate overall quality
    """,
    tools=["code_analysis", "security_scan"],
    metadata={
        "agent_type": "QUALITY_JUDGE",
        "standards": ["pep8", "eslint", "sonarqube"]
    }
)
```


## 7. Frontend Developer

#

## 7. Frontend Developer

### Mô Tả
Frontend Developer agent chuyên về UI/UX implementation, client-side development.

### Ví Dụ
```python
frontend_agent = create_agent(
    name="frontend-developer",
    role="Frontend Developer",
    model_name="gpt-4",
    system_prompt="""Frontend expert: React, TypeScript, CSS, responsive design.""",
    metadata={"agent_type": "FRONTEND", "frameworks": ["react", "vue", "angular"]}
)
```

## 8. Backend Developer

### Mô Tả
Backend Developer agent chuyên về server-side logic, APIs, databases.

### Ví Dụ
```python
backend_agent = create_agent(
    name="backend-developer",
    role="Backend Developer",
    model_name="gpt-4",
    system_prompt="""Backend expert: FastAPI, databases, APIs, microservices.""",
    metadata={"agent_type": "BACKEND", "tech": ["fastapi", "postgresql", "redis"]}
)
```

## 9. DevOps Engineer

### Mô Tả
DevOps Engineer agent quản lý CI/CD, infrastructure, deployment.

### Ví Dụ
```python
devops_agent = create_agent(
    name="devops-engineer",
    role="DevOps Engineer",
    model_name="gpt-4",
    system_prompt="""DevOps expert: Docker, Kubernetes, CI/CD, monitoring.""",
    metadata={"agent_type": "DEVOPS", "tools": ["docker", "k8s", "terraform"]}
)
```

## 10. Security Engineer

### Mô Tả
Security Engineer agent focus vào security audits, vulnerability assessment.

### Ví Dụ
```python
security_agent = create_agent(
    name="security-engineer",
    role="Security Engineer",
    model_name="gpt-4-turbo",
    system_prompt="""Security expert: OWASP, penetration testing, secure coding.""",
    metadata={"agent_type": "SECURITY", "focus": ["owasp", "pentest", "audit"]}
)
```

## 11. Database Administrator

### Mô Tả
Database Administrator agent quản lý database design, optimization, maintenance.

### Ví Dụ
```python
dba_agent = create_agent(
    name="database-admin",
    role="Database Administrator",
    model_name="gpt-4",
    system_prompt="""DBA expert: schema design, query optimization, backup/recovery.""",
    metadata={"agent_type": "DBA", "databases": ["postgresql", "mysql", "mongodb"]}
)
```

## 12. QA Tester

### Mô Tả
QA Tester agent thực hiện testing, test case creation, bug reporting.

### Ví Dụ
```python
qa_agent = create_agent(
    name="qa-tester",
    role="QA Tester",
    model_name="gpt-4",
    system_prompt="""QA expert: test planning, automation, bug tracking.""",
    metadata={"agent_type": "QA", "test_types": ["unit", "integration", "e2e"]}
)
```


## 13. Technical Writer

### Mô Tả
Technical Writer agent tạo documentation, user guides, API docs.

### Ví Dụ
```python
writer_agent = create_agent(
    name="technical-writer",
    role="Technical Writer",
    model_name="gpt-4",
    system_prompt="""Technical writing expert: clear docs, examples, tutorials.""",
    metadata={"agent_type": "WRITER", "doc_types": ["api", "user-guide", "tutorial"]}
)
```

## 14. Data Scientist

### Mô Tả
Data Scientist agent phân tích data, build models, insights generation.

### Ví Dụ
```python
ds_agent = create_agent(
    name="data-scientist",
    role="Data Scientist",
    model_name="gpt-4-turbo",
    system_prompt="""Data science expert: ML, statistics, data analysis.""",
    metadata={"agent_type": "DATA_SCIENTIST", "tools": ["pandas", "sklearn", "pytorch"]}
)
```

## 15. UI/UX Designer

### Mô Tả
UI/UX Designer agent thiết kế interfaces, user experience optimization.

### Ví Dụ
```python
designer_agent = create_agent(
    name="uiux-designer",
    role="UI/UX Designer",
    model_name="gpt-4",
    system_prompt="""UI/UX expert: user-centered design, accessibility, prototyping.""",
    metadata={"agent_type": "DESIGNER", "tools": ["figma", "sketch", "adobe-xd"]}
)
```

## 16. Performance Engineer

### Mô Tả
Performance Engineer agent optimize performance, profiling, benchmarking.

### Ví Dụ
```python
perf_agent = create_agent(
    name="performance-engineer",
    role="Performance Engineer",
    model_name="gpt-4",
    system_prompt="""Performance expert: profiling, optimization, load testing.""",
    metadata={"agent_type": "PERFORMANCE", "focus": ["profiling", "optimization", "caching"]}
)
```

## 17. Integration Specialist

### Mô Tả
Integration Specialist agent handle third-party integrations, APIs, webhooks.

### Ví Dụ
```python
integration_agent = create_agent(
    name="integration-specialist",
    role="Integration Specialist",
    model_name="gpt-4",
    system_prompt="""Integration expert: APIs, webhooks, third-party services.""",
    metadata={"agent_type": "INTEGRATION", "services": ["stripe", "sendgrid", "aws"]}
)
```

## 18. Custom Agent

### Mô Tả
Custom Agent cho specialized tasks không thuộc các categories trên.

### Ví Dụ
```python
custom_agent = create_agent(
    name="custom-specialist",
    role="Custom Specialist",
    model_name="gpt-4",
    system_prompt="""Custom agent for specific domain expertise.""",
    metadata={"agent_type": "CUSTOM", "domain": "blockchain"}
)
```


## Agent Type Selection Guide

### Chọn Agent Type Phù Hợp

| Task Type | Recommended Agent | Rationale |
|-----------|------------------|-----------|
| Requirements gathering | Business Analyst | Chuyên về business analysis |
| Project planning | Project Manager | Quản lý timeline và resources |
| Architecture design | Software Architect | Technical design expertise |
| Feature implementation | Implementation Developer | Coding và development |
| Technology evaluation | Research Specialist | Research và comparison |
| Code review | Quality Judge | Quality assessment |
| UI development | Frontend Developer | Client-side expertise |
| API development | Backend Developer | Server-side expertise |
| Deployment | DevOps Engineer | Infrastructure expertise |
| Security audit | Security Engineer | Security expertise |
| Database design | Database Administrator | Database expertise |
| Testing | QA Tester | Testing expertise |
| Documentation | Technical Writer | Writing expertise |
| Data analysis | Data Scientist | Data và ML expertise |
| Design | UI/UX Designer | Design expertise |
| Optimization | Performance Engineer | Performance expertise |
| Integrations | Integration Specialist | Integration expertise |
| Specialized tasks | Custom Agent | Domain-specific |

## Multi-Agent Collaboration

### Team Composition Examples

#### Web Application Development Team
```python
team = [
    create_agent(name="pm", role="Project Manager", model_name="gpt-4"),
    create_agent(name="architect", role="Software Architect", model_name="gpt-4-turbo"),
    create_agent(name="backend-dev", role="Backend Developer", model_name="gpt-4"),
    create_agent(name="frontend-dev", role="Frontend Developer", model_name="gpt-4"),
    create_agent(name="qa", role="QA Tester", model_name="gpt-4"),
    create_agent(name="devops", role="DevOps Engineer", model_name="gpt-4")
]
```

#### Code Quality Team
```python
quality_team = [
    create_agent(name="reviewer", role="Quality Judge", model_name="gpt-4"),
    create_agent(name="security", role="Security Engineer", model_name="gpt-4-turbo"),
    create_agent(name="performance", role="Performance Engineer", model_name="gpt-4"),
    create_agent(name="tester", role="QA Tester", model_name="gpt-4")
]
```

#### Research và Innovation Team
```python
research_team = [
    create_agent(name="researcher", role="Research Specialist", model_name="gpt-4-turbo"),
    create_agent(name="architect", role="Software Architect", model_name="gpt-4-turbo"),
    create_agent(name="data-scientist", role="Data Scientist", model_name="gpt-4-turbo"),
    create_agent(name="poc-dev", role="Implementation Developer", model_name="gpt-4")
]
```

## Best Practices

### 1. Agent Specialization
- Chọn agent type phù hợp với task
- Không dùng generic agents cho specialized tasks
- Combine multiple agents cho complex workflows

### 2. Model Selection per Agent Type
```python
# Strategic agents - use powerful models
pm_agent = create_agent(name="pm", role="PM", model_name="gpt-4-turbo")
architect = create_agent(name="sa", role="SA", model_name="gpt-4-turbo")

# Tactical agents - balanced models
developer = create_agent(name="dev", role="Developer", model_name="gpt-4")
tester = create_agent(name="qa", role="QA", model_name="gpt-4")

# Operational agents - efficient models
formatter = create_agent(name="fmt", role="Formatter", model_name="gpt-3.5-turbo")
```

### 3. System Prompt Customization
Customize system prompts based on:
- Project domain
- Team standards
- Technology stack
- Company culture

### 4. Metadata Tracking
```python
agent = create_agent(
    name="backend-dev",
    role="Backend Developer",
    model_name="gpt-4",
    metadata={
        "agent_type": "BACKEND",
        "team": "platform",
        "tech_stack": ["python", "fastapi", "postgresql"],
        "certifications": ["aws-certified"],
        "experience_level": "senior"
    }
)
```

## Tài Liệu Liên Quan

- [Tổng Quan về Agents](overview.md)
- [Tạo và Cấu Hình Agents](creating-agents.md)
- [Agent Lifecycle Management](agent-lifecycle.md)
- [Multi-Agent Workflows](../workflows/building-workflows.md)
- [Team Collaboration](../intelligence/collaboration.md)

## Tóm Tắt

Agentic SDLC cung cấp 18 loại agents chuyên biệt cho các vai trò khác nhau trong SDLC:
- Core agents: BA, PM, SA, Implementation, Research, Quality Judge
- Specialized agents: Frontend, Backend, DevOps, Security, DBA, QA
- Support agents: Technical Writer, Data Scientist, Designer
- Optimization agents: Performance Engineer, Integration Specialist
- Custom agents: Cho domain-specific tasks

Chọn đúng agent type và configure phù hợp để tối ưu hiệu quả development workflow.
