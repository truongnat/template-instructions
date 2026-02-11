# Automated Testing với Test Generation và Self-Healing

**Phiên bản**: 3.0.0  
**Cập nhật lần cuối**: 11/02/2026


**Phiên bản:** 1.0.0  
**Cập nhật lần cuối:** 2026-02-11  
**Danh mục:** advanced

---

## Tổng Quan

Use case này minh họa cách xây dựng hệ thống testing tự động thông minh, có khả năng tự động generate tests, execute tests, phát hiện flaky tests, và tự động fix broken tests (self-healing). Hệ thống giúp maintain high test coverage và reliability với minimal manual effort.

---

## Kịch Bản

### Bối Cảnh

Một team phát triển web application với 200,000 lines of code đang gặp vấn đề với test suite: test coverage thấp (45%), nhiều flaky tests, và tests thường xuyên break khi code changes. Việc maintain tests tốn nhiều thời gian hơn cả việc viết code mới. Team muốn một giải pháp tự động hóa testing process.

### Các Tác Nhân

- **Test Generator Agent**: Tự động generate unit tests, integration tests từ code
- **Test Executor Agent**: Execute tests và collect results
- **Flaky Test Detector Agent**: Phát hiện và analyze flaky tests
- **Test Healer Agent**: Tự động fix broken tests khi code changes
- **Coverage Analyzer Agent**: Analyze test coverage và identify gaps
- **Test Optimizer Agent**: Optimize test suite để giảm execution time

### Mục Tiêu

- Tăng test coverage từ 45% lên 85%
- Tự động generate tests cho new code
- Phát hiện và fix flaky tests
- Tự động update tests khi code changes
- Giảm test execution time từ 30 phút xuống 10 phút
- Giảm manual test maintenance effort 70%

---

## Vấn Đề

Testing truyền thống gặp các vấn đề:

1. **Low coverage**: Developers không có thời gian viết đủ tests
2. **Flaky tests**: Tests fail randomly, gây frustration và waste time
3. **Brittle tests**: Tests break easily khi code changes
4. **Slow execution**: Test suite chạy quá lâu, slow down development
5. **High maintenance cost**: Maintaining tests tốn nhiều effort
6. **Lack of consistency**: Test quality varies across codebase

---

## Giải Pháp

Xây dựng intelligent testing system với các capabilities:
- Tự động generate comprehensive tests từ code analysis
- Detect và fix flaky tests automatically
- Self-healing tests adapt to code changes
- Optimize test execution với smart parallelization
- Continuous coverage monitoring và gap identification

---

## Kiến Trúc

**Intelligent Automated Testing System**

```mermaid
flowchart TB
    Code[Code Changes] --> CoverageAnalyzer[Coverage Analyzer Agent]
    
    CoverageAnalyzer --> Gaps[Coverage Gaps]
    Gaps --> TestGenerator[Test Generator Agent]
    
    TestGenerator --> NewTests[Generated Tests]
    NewTests --> TestExecutor[Test Executor Agent]
    
    TestExecutor --> Results[Test Results]
    Results --> FlakyDetector[Flaky Test Detector Agent]
    
    FlakyDetector --> FlakyTests{Flaky Tests?}
    FlakyTests -->|Yes| TestHealer[Test Healer Agent]
    FlakyTests -->|No| Continue[Continue]
    
    TestHealer --> FixedTests[Fixed Tests]
    FixedTests --> TestExecutor
    
    Results --> FailedTests{Failed Tests?}
    FailedTests -->|Yes| Analyze[Analyze Failures]
    FailedTests -->|No| Success[All Pass]
    
    Analyze --> CodeChange{Code Changed?}
    CodeChange -->|Yes| TestHealer
    CodeChange -->|No| Alert[Alert Team]
    
    Success --> TestOptimizer[Test Optimizer Agent]
    TestOptimizer --> OptimizedSuite[Optimized Test Suite]
```text

---

## Triển Khai

### Bước 1: Implement Test Generator

```python
from agentic_sdlc import create_agent, AgentType
import ast
import inspect

class TestGenerator:
    """Automatically generate tests from code analysis."""
    
    def __init__(self):
        self.generator_agent = create_agent(
            name="test_generator",
            role=AgentType.TESTER,
            model_name="gpt-4",
            system_prompt="""Bạn là expert test engineer. Generate comprehensive 
            unit tests và integration tests từ code analysis. Tests phải cover:
            - Happy paths
            - Edge cases
            - Error conditions
            - Boundary values
            Follow testing best practices và use appropriate assertions.""",
            tools=["ast_parser", "code_analyzer"]
        )
    
    def generate_tests_for_function(self, function_code: str, function_name: str):
        """Generate tests for a function."""
        # Analyze function
        analysis = self._analyze_function(function_code)
        
        # Generate tests using AI
        tests = self.generator_agent.execute(
            task=f"""Generate comprehensive tests for this function:
            
            ```python
            {function_code}
            ```python
            
            Function analysis:
            - Parameters: {analysis['parameters']}
            - Return type: {analysis['return_type']}
            - Complexity: {analysis['complexity']}
            - Edge cases: {analysis['edge_cases']}
            
            Generate tests covering:
            1. Normal cases với valid inputs
            2. Edge cases (empty, null, boundary values)
            3. Error cases (invalid inputs, exceptions)
            4. Integration scenarios if applicable
            
            Use pytest framework với clear test names và assertions."""
        )
        
        return tests.test_code
    
    def generate_tests_for_class(self, class_code: str, class_name: str):
        """Generate tests for a class."""
        # Parse class
        tree = ast.parse(class_code)
        class_node = tree.body[0]
        
        # Extract methods
        methods = [
            node.name for node in ast.walk(class_node)
            if isinstance(node, ast.FunctionDef) and not node.name.startswith('_')
        ]
        
        # Generate tests
        tests = self.generator_agent.execute(
            task=f"""Generate comprehensive test class for:
            
            ```python
            {class_code}
            ```python
            
            Class: {class_name}
            Public methods: {methods}
            
            Generate test class với:
            1. Setup và teardown methods
            2. Tests cho mỗi public method
            3. Tests cho method interactions
            4. Tests cho state management
            5. Mock external dependencies
            
            Use pytest fixtures và clear test organization."""
        )
        
        return tests.test_code
    
    def _analyze_function(self, function_code: str):
        """Analyze function to identify test scenarios."""
        tree = ast.parse(function_code)
        func = tree.body[0]
        
        # Extract parameters
        parameters = [arg.arg for arg in func.args.args]
        
        # Estimate complexity
        complexity = len(list(ast.walk(func)))
        
        # Identify edge cases
        edge_cases = []
        for node in ast.walk(func):
            if isinstance(node, ast.If):
                edge_cases.append("conditional branch")
            elif isinstance(node, ast.For) or isinstance(node, ast.While):
                edge_cases.append("loop")
            elif isinstance(node, ast.Try):
                edge_cases.append("exception handling")
        
        return {
            "parameters": parameters,
            "return_type": "unknown",  # Would need type hints
            "complexity": complexity,
            "edge_cases": edge_cases
        }
```

### Bước 2: Implement Flaky Test Detection

```python
from collections import defaultdict
import statistics

class FlakyTestDetector:
    """Detect flaky tests using statistical analysis."""
    
    def __init__(self):
        self.test_history = defaultdict(list)
        self.detector_agent = create_agent(
            name="flaky_detector",
            role=AgentType.TESTER,
            model_name="gpt-4",
            system_prompt="""Bạn là expert trong detecting và analyzing flaky tests. 
            Analyze test execution history, identify patterns, và determine root causes 
            of flakiness. Suggest fixes để make tests more reliable."""
        )
    
    def record_test_result(self, test_name: str, passed: bool, execution_time: float):
        """Record test execution result."""
        self.test_history[test_name].append({
            "passed": passed,
            "execution_time": execution_time,
            "timestamp": datetime.now()
        })
    
    def detect_flaky_tests(self, min_executions: int = 10):
        """Detect flaky tests from execution history."""
        flaky_tests = []
        
        for test_name, history in self.test_history.items():
            if len(history) < min_executions:
                continue
            
            # Calculate flakiness metrics
            pass_rate = sum(1 for r in history if r["passed"]) / len(history)
            execution_times = [r["execution_time"] for r in history]
            time_variance = statistics.stdev(execution_times) if len(execution_times) > 1 else 0
            
            # Identify flaky tests
            # Flaky if: pass rate between 20% and 80%, or high time variance
            is_flaky = (0.2 < pass_rate < 0.8) or (time_variance > statistics.mean(execution_times) * 0.5)
            
            if is_flaky:
                # Use AI to analyze root cause
                analysis = self.detector_agent.execute(
                    task=f"""Analyze this flaky test:
                    
                    Test: {test_name}
                    Pass rate: {pass_rate:.2%}
                    Executions: {len(history)}
                    Avg time: {statistics.mean(execution_times):.2f}s
                    Time variance: {time_variance:.2f}s
                    
                    Recent results:
                    {self._format_recent_results(history[-10:])}
                    
                    Identify:
                    1. Root cause of flakiness
                    2. Patterns in failures
                    3. Suggested fixes
                    4. Whether to skip, fix, or rewrite test"""
                )
                
                flaky_tests.append({
                    "test_name": test_name,
                    "pass_rate": pass_rate,
                    "root_cause": analysis.root_cause,
                    "suggested_fix": analysis.suggested_fix,
                    "action": analysis.action
                })
        
        return flaky_tests
    
    def _format_recent_results(self, results):
        """Format recent test results for analysis."""
        formatted = []
        for r in results:
            status = "✅ PASS" if r["passed"] else "❌ FAIL"
            formatted.append(f"{status} - {r['execution_time']:.2f}s - {r['timestamp']}")
        return "\n".join(formatted)
```text

### Bước 3: Implement Self-Healing Tests

```python
class TestHealer:
    """Automatically fix broken tests when code changes."""
    
    def __init__(self):
        self.healer_agent = create_agent(
            name="test_healer",
            role=AgentType.TESTER,
            model_name="gpt-4",
            system_prompt="""Bạn là expert trong fixing broken tests. 
            Analyze test failures, understand code changes, và update tests 
            to work với new code while maintaining test intent. Preserve 
            test coverage và assertions.""",
            tools=["diff_analyzer", "test_parser"]
        )
    
    def heal_broken_tests(
        self,
        failed_tests: list,
        code_changes: dict
    ):
        """Automatically fix broken tests after code changes."""
        healed_tests = []
        
        for test in failed_tests:
            # Analyze failure
            failure_analysis = self._analyze_failure(test)
            
            # Check if failure is due to code changes
            related_changes = self._find_related_changes(
                test["test_file"],
                code_changes
            )
            
            if not related_changes:
                # Not related to code changes, skip
                continue
            
            # Use AI to fix test
            fixed_test = self.healer_agent.execute(
                task=f"""Fix this broken test:
                
                Test file: {test['test_file']}
                Test name: {test['test_name']}
                
                Original test:
                ```python
                {test['test_code']}
                ```python
                
                Failure:
                {test['failure_message']}
                
                Related code changes:
                {self._format_changes(related_changes)}
                
                Update test to:
                1. Work với new code
                2. Maintain original test intent
                3. Keep assertions meaningful
                4. Follow same testing patterns
                
                Provide updated test code."""
            )
            
            healed_tests.append({
                "test_name": test["test_name"],
                "original_code": test["test_code"],
                "fixed_code": fixed_test.updated_code,
                "changes_made": fixed_test.changes_made,
                "confidence": fixed_test.confidence
            })
        
        return healed_tests
    
    def _analyze_failure(self, test):
        """Analyze test failure to understand root cause."""
        failure_msg = test["failure_message"]
        
        # Categorize failure type
        if "AssertionError" in failure_msg:
            failure_type = "assertion_failed"
        elif "AttributeError" in failure_msg:
            failure_type = "missing_attribute"
        elif "TypeError" in failure_msg:
            failure_type = "type_mismatch"
        else:
            failure_type = "unknown"
        
        return {
            "type": failure_type,
            "message": failure_msg
        }
    
    def _find_related_changes(self, test_file, code_changes):
        """Find code changes related to test file."""
        # Extract module being tested
        test_module = test_file.replace("test_", "").replace("_test", "")
        
        # Find related changes
        related = []
        for change in code_changes:
            if test_module in change["file"]:
                related.append(change)
        
        return related
```

### Bước 4: Implement Test Optimizer

```python
class TestOptimizer:
    """Optimize test suite execution."""
    
    def __init__(self):
        self.optimizer_agent = create_agent(
            name="test_optimizer",
            role=AgentType.PERFORMANCE_ENGINEER,
            model_name="gpt-4",
            system_prompt="""Bạn là test optimization expert. 
            Analyze test suite, identify slow tests, suggest parallelization 
            strategies, và optimize test execution order."""
        )
    
    def optimize_test_suite(self, test_suite: list):
        """Optimize test suite for faster execution."""
        # Analyze test execution times
        slow_tests = [t for t in test_suite if t["execution_time"] > 5.0]
        
        # Group tests by dependencies
        test_groups = self._group_tests_by_dependencies(test_suite)
        
        # Use AI to create optimization plan
        optimization_plan = self.optimizer_agent.execute(
            task=f"""Optimize this test suite:
            
            Total tests: {len(test_suite)}
            Total time: {sum(t['execution_time'] for t in test_suite):.2f}s
            Slow tests: {len(slow_tests)}
            
            Test groups:
            {self._format_test_groups(test_groups)}
            
            Suggest:
            1. Parallelization strategy
            2. Test execution order
            3. Tests to optimize or split
            4. Caching opportunities
            5. Setup/teardown optimizations"""
        )
        
        return optimization_plan
    
    def _group_tests_by_dependencies(self, test_suite):
        """Group tests by their dependencies."""
        groups = {
            "unit": [],
            "integration": [],
            "e2e": []
        }
        
        for test in test_suite:
            if "integration" in test["name"].lower():
                groups["integration"].append(test)
            elif "e2e" in test["name"].lower() or "end_to_end" in test["name"].lower():
                groups["e2e"].append(test)
            else:
                groups["unit"].append(test)
        
        return groups
```text

### Bước 5: Integrate Everything into Workflow

```python
from agentic_sdlc import WorkflowBuilder

# Build automated testing workflow
testing_workflow = WorkflowBuilder("automated_testing") \
    .add_step(
        name="analyze_coverage",
        action="agent_execution",
        parameters={
            "agent": coverage_analyzer,
            "task": "Analyze test coverage và identify gaps"
        }
    ) \
    .add_step(
        name="generate_missing_tests",
        action="agent_execution",
        parameters={
            "agent": test_generator,
            "task": "Generate tests for uncovered code",
            "input": "${analyze_coverage.gaps}"
        },
        dependencies=["analyze_coverage"],
        condition="${analyze_coverage.coverage < 0.85}"
    ) \
    .add_step(
        name="execute_tests",
        action="run_tests",
        parameters={
            "test_suite": "all",
            "parallel": True,
            "max_workers": 4
        },
        dependencies=["generate_missing_tests"]
    ) \
    .add_step(
        name="detect_flaky_tests",
        action="agent_execution",
        parameters={
            "agent": flaky_detector,
            "task": "Detect và analyze flaky tests",
            "input": "${execute_tests.results}"
        },
        dependencies=["execute_tests"]
    ) \
    .add_step(
        name="heal_broken_tests",
        action="agent_execution",
        parameters={
            "agent": test_healer,
            "task": "Fix broken tests",
            "input": {
                "failed_tests": "${execute_tests.failed}",
                "code_changes": "${git.recent_changes}"
            }
        },
        dependencies=["execute_tests"],
        condition="${execute_tests.has_failures}"
    ) \
    .add_step(
        name="optimize_suite",
        action="agent_execution",
        parameters={
            "agent": test_optimizer,
            "task": "Optimize test suite execution",
            "input": "${execute_tests.performance_data}"
        },
        dependencies=["execute_tests"]
    ) \
    .build()
```

---

## Kết Quả

### Kết Quả Đạt Được

- **Test coverage tăng 89%**: Từ 45% lên 85% nhờ automated test generation
- **Flaky tests giảm 92%**: Từ 50 flaky tests xuống còn 4
- **Test maintenance time giảm 75%**: Self-healing tests tự động adapt to changes
- **Test execution time giảm 67%**: Từ 30 phút xuống 10 phút với optimization
- **Developer productivity tăng**: Spend 80% less time on test maintenance
- **Bug detection tăng 45%**: Better test coverage catches more bugs early

### Các Chỉ Số

- **Test coverage**: 85% (trước: 45%)
- **Flaky test rate**: 0.8% (trước: 10%)
- **Test execution time**: 10 phút (trước: 30 phút)
- **Auto-healed tests**: 78% of broken tests fixed automatically
- **Test generation rate**: 150 tests/week generated automatically
- **Maintenance effort**: 6 hours/week (trước: 24 hours/week)

---

## Bài Học Kinh Nghiệm

- **AI-generated tests are good starting point**: Cần human review nhưng save significant time
- **Flaky test detection is critical**: Identifying và fixing flaky tests improves reliability dramatically
- **Self-healing has limits**: Some test failures require human judgment
- **Test optimization pays off**: Faster tests encourage developers to run them more often
- **Coverage is not everything**: Quality of tests matters more than quantity
- **Continuous monitoring essential**: Test suite health needs ongoing attention
- **Balance automation và control**: Some test decisions still need human oversight

---

## Tài Liệu Liên Quan

- [Tạo Agents](../guides/agents/creating-agents.md)
- [Xây dựng Workflows](../guides/workflows/building-workflows.md)
- [Intelligence Features](../guides/intelligence/learning.md)

**Tags:** testing, automation, test-generation, self-healing, quality-assurance

---

*Use case này là một phần của Agentic SDLC v1.0.0*
