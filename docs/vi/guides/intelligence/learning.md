# Học Tập (Learning)

**Phiên bản**: 3.0.0  
**Cập nhật lần cuối**: 11/02/2026


## Giới Thiệu

Learner là một component quan trọng trong Intelligence Layer của Agentic SDLC, cho phép hệ thống học hỏi từ các execution thành công và thất bại, sau đó áp dụng kiến thức đó để cải thiện hiệu suất trong tương lai. Component này giúp hệ thống trở nên thông minh hơn theo thời gian thông qua việc lưu trữ và truy xuất các patterns từ lịch sử thực thi.

## Yêu Cầu Tiên Quyết

- Đã cài đặt Agentic SDLC v3.0.0 hoặc cao hơn
- Hiểu biết cơ bản về agents và workflows
- Python 3.8+

## Mục Tiêu Học Tập

Sau khi hoàn thành tài liệu này, bạn sẽ có thể:
- Sử dụng Learner để lưu trữ execution results
- Học từ các thành công và thất bại
- Tìm kiếm các execution tương tự để tái sử dụng kiến thức
- Tích hợp learning vào workflows của bạn

## Khái Niệm Cơ Bản

### Learner là gì?

Learner là một component cho phép hệ thống:
- **Học từ thành công**: Lưu trữ các execution thành công để tái sử dụng patterns
- **Học từ thất bại**: Ghi nhận lỗi và cách khắc phục để tránh lặp lại
- **Tìm kiếm tương tự**: Truy xuất các execution tương tự dựa trên context
- **Cải thiện liên tục**: Tự động cải thiện hiệu suất theo thời gian

### Cách Hoạt Động

1. **Recording**: Ghi lại thông tin về mỗi execution (input, output, context, result)
2. **Storage**: Lưu trữ dữ liệu trong knowledge base
3. **Retrieval**: Tìm kiếm các execution tương tự khi cần
4. **Application**: Áp dụng kiến thức đã học vào execution mới

## Sử Dụng Learner

### Khởi Tạo Learner

```python
from agentic_sdlc.intelligence import Learner

# Tạo Learner instance
learner = Learner(
    storage_path="./learning_data",  # Đường dẫn lưu trữ knowledge base
    similarity_threshold=0.7,         # Ngưỡng similarity cho retrieval
    max_history=1000                  # Số lượng execution tối đa lưu trữ
)
```text

### Học Từ Thành Công

Khi một execution thành công, bạn có thể lưu trữ thông tin để tái sử dụng sau này:

```python
from agentic_sdlc.intelligence import Learner
from agentic_sdlc.orchestration import Agent, create_agent

# Tạo agent và learner
agent = create_agent(
    name="code_reviewer",
    role="REVIEWER",
    model_name="gpt-4"
)

learner = Learner(storage_path="./learning_data")

# Thực thi task
task = {
    "type": "code_review",
    "file": "src/main.py",
    "language": "python"
}

result = agent.execute(task)

# Nếu thành công, học từ execution này
if result.success:
    learner.learn_success(
        task_type="code_review",
        context={
            "file": task["file"],
            "language": task["language"],
            "complexity": "medium"
        },
        input_data=task,
        output_data=result.output,
        metadata={
            "execution_time": result.execution_time,
            "model_used": "gpt-4",
            "agent_name": "code_reviewer"
        }
    )
    print("✓ Đã học từ execution thành công")
```text

### Học Từ Thất Bại

Việc học từ lỗi cũng quan trọng như học từ thành công:

```python
from agentic_sdlc.intelligence import Learner

learner = Learner(storage_path="./learning_data")

# Thực thi task
try:
    result = agent.execute(task)
    
    if not result.success:
        # Học từ thất bại
        learner.learn_error(
            task_type="code_review",
            context={
                "file": task["file"],
                "language": task["language"]
            },
            error_type=result.error_type,
            error_message=result.error_message,
            input_data=task,
            solution={
                "action": "retry_with_simpler_prompt",
                "details": "Simplified the review criteria"
            },
            metadata={
                "attempt_number": 1,
                "agent_name": "code_reviewer"
            }
        )
        print("✓ Đã học từ lỗi và lưu giải pháp")
        
except Exception as e:
    # Học từ exception
    learner.learn_error(
        task_type="code_review",
        context={"file": task["file"]},
        error_type=type(e).__name__,
        error_message=str(e),
        input_data=task,
        solution={
            "action": "check_file_exists",
            "details": "Verify file path before execution"
        }
    )
    print(f"✓ Đã học từ exception: {type(e).__name__}")
```text

### Tìm Kiếm Execution Tương Tự

Trước khi thực thi một task mới, bạn có thể tìm kiếm các execution tương tự để tái sử dụng kiến thức:

```python
from agentic_sdlc.intelligence import Learner

learner = Learner(storage_path="./learning_data")

# Task mới cần thực thi
new_task = {
    "type": "code_review",
    "file": "src/utils.py",
    "language": "python"
}

# Tìm các execution tương tự
similar_executions = learner.find_similar(
    task_type="code_review",
    context={
        "language": "python",
        "complexity": "medium"
    },
    limit=5  # Lấy top 5 kết quả tương tự nhất
)

# Sử dụng kiến thức từ execution tương tự
if similar_executions:
    print(f"Tìm thấy {len(similar_executions)} execution tương tự:")
    
    for i, execution in enumerate(similar_executions, 1):
        print(f"\n{i}. Similarity: {execution.similarity_score:.2f}")
        print(f"   Task: {execution.task_type}")
        print(f"   Success: {execution.success}")
        print(f"   Execution time: {execution.metadata.get('execution_time', 'N/A')}")
        
        # Nếu có lỗi đã biết, hiển thị giải pháp
        if not execution.success and execution.solution:
            print(f"   Known error: {execution.error_type}")
            print(f"   Solution: {execution.solution['action']}")
    
    # Áp dụng best practice từ execution thành công nhất
    best_execution = similar_executions[0]
    if best_execution.success:
        print(f"\n✓ Áp dụng pattern từ execution thành công tương tự")
        # Sử dụng cùng configuration hoặc approach
else:
    print("Không tìm thấy execution tương tự, thực thi như bình thường")
```text

## Ví Dụ Thực Tế

### Ví Dụ 1: Self-Improving Code Review Agent

```python
from agentic_sdlc.intelligence import Learner
from agentic_sdlc.orchestration import create_agent

class SelfImprovingReviewer:
    """Code reviewer agent tự cải thiện qua thời gian."""
    
    def __init__(self):
        self.agent = create_agent(
            name="smart_reviewer",
            role="REVIEWER",
            model_name="gpt-4"
        )
        self.learner = Learner(storage_path="./reviewer_knowledge")
    
    def review_code(self, file_path: str, language: str):
        """Review code với learning capability."""
        
        # Tìm kiếm kiến thức từ review tương tự
        similar = self.learner.find_similar(
            task_type="code_review",
            context={"language": language},
            limit=3
        )
        
        # Chuẩn bị context từ kiến thức đã học
        learned_context = ""
        if similar:
            learned_context = "Dựa trên các review trước:\n"
            for exec in similar:
                if exec.success:
                    learned_context += f"- Đã review thành công {exec.context.get('file', 'file')}\n"
        
        # Thực thi review
        task = {
            "type": "code_review",
            "file": file_path,
            "language": language,
            "learned_context": learned_context
        }
        
        try:
            result = self.agent.execute(task)
            
            if result.success:
                # Học từ thành công
                self.learner.learn_success(
                    task_type="code_review",
                    context={
                        "file": file_path,
                        "language": language,
                        "issues_found": len(result.output.get("issues", []))
                    },
                    input_data=task,
                    output_data=result.output,
                    metadata={
                        "execution_time": result.execution_time,
                        "quality_score": result.output.get("quality_score", 0)
                    }
                )
                return result.output
            else:
                # Học từ thất bại
                self.learner.learn_error(
                    task_type="code_review",
                    context={"file": file_path, "language": language},
                    error_type="ReviewFailed",
                    error_message=result.error_message,
                    input_data=task,
                    solution={"action": "retry_with_more_context"}
                )
                return None
                
        except Exception as e:
            # Học từ exception
            self.learner.learn_error(
                task_type="code_review",
                context={"file": file_path},
                error_type=type(e).__name__,
                error_message=str(e),
                input_data=task,
                solution={"action": "validate_file_path"}
            )
            raise

# Sử dụng
reviewer = SelfImprovingReviewer()

# Review nhiều files - agent sẽ học và cải thiện
files = ["src/main.py", "src/utils.py", "src/models.py"]
for file in files:
    print(f"\nReviewing {file}...")
    result = reviewer.review_code(file, "python")
    if result:
        print(f"✓ Review completed: {len(result.get('issues', []))} issues found")
```text

### Ví Dụ 2: Learning-Enhanced Test Generator

```python
from agentic_sdlc.intelligence import Learner
from agentic_sdlc.orchestration import create_agent

def generate_tests_with_learning(source_file: str):
    """Generate tests và học từ kết quả."""
    
    agent = create_agent(
        name="test_generator",
        role="TESTER",
        model_name="gpt-4"
    )
    
    learner = Learner(storage_path="./test_gen_knowledge")
    
    # Tìm patterns từ test generation trước
    similar = learner.find_similar(
        task_type="test_generation",
        context={"language": "python"},
        limit=5
    )
    
    # Phân tích patterns thành công
    best_practices = []
    common_errors = []
    
    for exec in similar:
        if exec.success:
            # Lấy best practices từ generation thành công
            if "test_coverage" in exec.metadata:
                coverage = exec.metadata["test_coverage"]
                if coverage > 80:
                    best_practices.append({
                        "pattern": exec.output_data.get("pattern", ""),
                        "coverage": coverage
                    })
        else:
            # Lấy common errors để tránh
            common_errors.append({
                "error": exec.error_type,
                "solution": exec.solution
            })
    
    # Generate tests với kiến thức đã học
    task = {
        "type": "test_generation",
        "source_file": source_file,
        "best_practices": best_practices,
        "avoid_errors": common_errors
    }
    
    result = agent.execute(task)
    
    # Học từ kết quả
    if result.success:
        learner.learn_success(
            task_type="test_generation",
            context={
                "source_file": source_file,
                "language": "python"
            },
            input_data=task,
            output_data=result.output,
            metadata={
                "test_count": result.output.get("test_count", 0),
                "test_coverage": result.output.get("coverage", 0),
                "execution_time": result.execution_time
            }
        )
        print(f"✓ Generated {result.output.get('test_count', 0)} tests")
        print(f"✓ Coverage: {result.output.get('coverage', 0)}%")
    else:
        learner.learn_error(
            task_type="test_generation",
            context={"source_file": source_file},
            error_type=result.error_type,
            error_message=result.error_message,
            input_data=task,
            solution={"action": "simplify_test_cases"}
        )
        print(f"✗ Generation failed: {result.error_message}")
    
    return result

# Sử dụng
result = generate_tests_with_learning("src/calculator.py")
```text

### Ví Dụ 3: Adaptive Error Recovery

```python
from agentic_sdlc.intelligence import Learner

def execute_with_adaptive_recovery(agent, task, max_retries=3):
    """Thực thi task với error recovery dựa trên learning."""
    
    learner = Learner(storage_path="./error_recovery")
    
    for attempt in range(max_retries):
        try:
            result = agent.execute(task)
            
            if result.success:
                # Học từ thành công
                learner.learn_success(
                    task_type=task["type"],
                    context=task.get("context", {}),
                    input_data=task,
                    output_data=result.output,
                    metadata={"attempts": attempt + 1}
                )
                return result
            else:
                # Tìm giải pháp từ lỗi tương tự
                similar_errors = learner.find_similar(
                    task_type=task["type"],
                    context={
                        "error_type": result.error_type,
                        **task.get("context", {})
                    },
                    limit=3
                )
                
                # Áp dụng giải pháp đã biết
                if similar_errors:
                    for error_exec in similar_errors:
                        if error_exec.solution:
                            print(f"Áp dụng giải pháp: {error_exec.solution['action']}")
                            # Modify task dựa trên solution
                            task = apply_solution(task, error_exec.solution)
                            break
                
                # Học từ lỗi này
                learner.learn_error(
                    task_type=task["type"],
                    context=task.get("context", {}),
                    error_type=result.error_type,
                    error_message=result.error_message,
                    input_data=task,
                    solution={"action": "retry_with_modification", "attempt": attempt + 1}
                )
                
        except Exception as e:
            # Học từ exception
            learner.learn_error(
                task_type=task["type"],
                context=task.get("context", {}),
                error_type=type(e).__name__,
                error_message=str(e),
                input_data=task,
                solution={"action": "handle_exception", "attempt": attempt + 1}
            )
            
            if attempt == max_retries - 1:
                raise
    
    return None

def apply_solution(task, solution):
    """Áp dụng solution vào task."""
    # Implementation để modify task dựa trên solution
    modified_task = task.copy()
    # Apply modifications based on solution
    return modified_task
```text

## Best Practices

### 1. Lưu Trữ Context Đầy Đủ

```python
# ✓ Tốt: Context đầy đủ
learner.learn_success(
    task_type="code_review",
    context={
        "language": "python",
        "file_type": "module",
        "complexity": "high",
        "lines_of_code": 500,
        "has_tests": True
    },
    input_data=task,
    output_data=result
)

# ✗ Không tốt: Context thiếu
learner.learn_success(
    task_type="code_review",
    context={},
    input_data=task,
    output_data=result
)
```text

### 2. Sử Dụng Metadata Có Ý Nghĩa

```python
# ✓ Tốt: Metadata hữu ích
learner.learn_success(
    task_type="test_generation",
    context=context,
    input_data=task,
    output_data=result,
    metadata={
        "execution_time": 2.5,
        "test_count": 15,
        "coverage": 85,
        "model_used": "gpt-4",
        "timestamp": datetime.now().isoformat()
    }
)
```text

### 3. Học Từ Cả Thành Công Và Thất Bại

```python
# Luôn học từ cả hai trường hợp
if result.success:
    learner.learn_success(...)
else:
    learner.learn_error(...)
```text

### 4. Định Kỳ Dọn Dẹp Knowledge Base

```python
# Xóa các execution cũ hoặc không còn relevant
learner.cleanup(
    older_than_days=90,
    keep_successful=True,
    keep_errors_with_solutions=True
)
```text

### 5. Sử Dụng Similarity Threshold Phù Hợp

```python
# Điều chỉnh threshold dựa trên use case
learner = Learner(
    storage_path="./learning_data",
    similarity_threshold=0.8  # Cao hơn = kết quả chính xác hơn nhưng ít hơn
)
```text

## Troubleshooting

### Không Tìm Thấy Execution Tương Tự

**Nguyên nhân**: Similarity threshold quá cao hoặc context không match

**Giải pháp**:
```python
# Giảm similarity threshold
learner = Learner(similarity_threshold=0.6)

# Hoặc sử dụng context rộng hơn
similar = learner.find_similar(
    task_type="code_review",
    context={"language": "python"},  # Bỏ các field quá specific
    limit=10
)
```text

### Knowledge Base Quá Lớn

**Nguyên nhân**: Lưu trữ quá nhiều execution

**Giải pháp**:
```python
# Giới hạn số lượng execution
learner = Learner(max_history=500)

# Hoặc cleanup định kỳ
learner.cleanup(older_than_days=30)
```text

### Learning Chậm

**Nguyên nhân**: Storage I/O hoặc similarity computation

**Giải pháp**:
```python
# Sử dụng in-memory cache
learner = Learner(
    storage_path="./learning_data",
    use_cache=True,
    cache_size=100
)
```

## Tài Liệu Liên Quan

- [Monitoring](monitoring.md) - Theo dõi metrics và health
- [Reasoning](reasoning.md) - Phân tích và ra quyết định
- [Collaboration](collaboration.md) - Phối hợp giữa các agents
- [Workflows](../workflows/overview.md) - Xây dựng workflows
- [API Reference - Learner](../../api-reference/intelligence/learner.md)
